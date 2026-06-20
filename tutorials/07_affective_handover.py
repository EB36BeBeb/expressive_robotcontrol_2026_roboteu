#!/usr/bin/env python3
"""
Affective Reaction Motion Generator
====================================
[Kinematics Fix: 극단적 제어 및 논문 엄격 준수]
- V(Volume): Z(높이)와 R(거리)를 0~30cm까지 극단적으로 변화시킴.
- J(Jerk): 계단형(Step) 프로파일을 도입하여 극단적으로 뚝뚝 끊기는 모션 구현.
- 갸우뚱 모션 제거: 논문 수식(P -> Jerk)에 없는 임의의 감정 표현을 배제함.
"""

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import (
    ParameterDescriptor,
    FloatingPointRange,
    SetParametersResult,
)
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
import math
import time
import argparse


def quintic(alpha):
    """가장 매끄러운(smooth) 5차 다항식 보간"""
    a = max(0.0, min(1.0, alpha))
    return 6.0 * a**5 - 15.0 * a**4 + 10.0 * a**3


def trembling_profile(alpha):
    """이동 중 속도가 불안정하게 요동치며 떠는(Trembling) 보간 프로파일"""
    smooth = quintic(alpha)
    a = max(0.0, min(1.0, alpha))

    # 50Hz 제어 주기에 맞춘 12Hz 진동 (이동하는 동안 요동침)
    f = 12.0
    A = 0.015  # 진폭을 대폭 줄여 미세한 경련처럼 보이게 함 (기존 0.05)

    # 시작과 끝에서는 오차가 없도록 Envelope(포락선) 적용
    envelope = math.sin(math.pi * a)
    val = smooth + A * envelope * math.sin(2.0 * math.pi * f * a)

    return max(0.0, min(1.0, val))


def interpolate(alpha, jerk_level):
    """J값에 따라 부드러운 움직임과 불안정한 떨림을 블렌딩"""
    smooth = quintic(alpha)
    trembling = trembling_profile(alpha)
    return (1.0 - jerk_level) * smooth + jerk_level * trembling


def solve_3link_ik(R_target, Z_target, alpha):
    """정면(alpha=0.0)을 바라보면서 R, Z를 도달하는 역기구학"""
    L1 = 0.250  # J2 ~ J3
    L2 = 0.201  # J3 ~ J5
    L3 = 0.100  # J5 ~ Tip

    R_w = R_target - L3 * math.cos(alpha)
    Z_w = Z_target - L3 * math.sin(alpha)

    D2 = R_w**2 + Z_w**2
    D = math.sqrt(D2)

    # 작업 영역 클램핑
    if D > L1 + L2:
        D = L1 + L2 - 0.001
        D2 = D**2
    elif D < abs(L1 - L2):
        D = abs(L1 - L2) + 0.001
        D2 = D**2

    cos_theta3 = (D2 - L1**2 - L2**2) / (2 * L1 * L2)
    cos_theta3 = max(-1.0, min(1.0, cos_theta3))
    theta3 = math.acos(cos_theta3)

    beta = math.atan2(Z_w, R_w)
    cos_gamma = (L1**2 + D2 - L2**2) / (2 * L1 * D)
    cos_gamma = max(-1.0, min(1.0, cos_gamma))
    gamma = math.acos(cos_gamma)

    phi2 = beta + gamma

    # URDF 각도 변환 (0도일 때 수직 상승)
    theta2 = (math.pi / 2.0) - phi2
    theta5 = (math.pi / 2.0) - alpha - theta2 - theta3

    return theta2, theta3, theta5


class AffectiveReactionAnimator(Node):
    def __init__(self, P, A, D):
        super().__init__("affective_reaction_animator")
        self.publisher_ = self.create_publisher(JointState, "joint_states", 10)
        self.timer_period = 0.02
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.start_time = time.time()

        self.joint_names = [
            "joint_1",
            "joint_2",
            "joint_3",
            "joint_4",
            "joint_5",
            "joint_a",
            "joint_b",
        ]

        pad_range = FloatingPointRange(from_value=-1.0, to_value=1.0, step=0.1)
        self.declare_parameter(
            "P",
            float(P),
            ParameterDescriptor(
                description="Pleasure (-1~1)", floating_point_range=[pad_range]
            ),
        )
        self.declare_parameter(
            "A",
            float(A),
            ParameterDescriptor(
                description="Arousal (-1~1)", floating_point_range=[pad_range]
            ),
        )
        self.declare_parameter(
            "D",
            float(D),
            ParameterDescriptor(
                description="Dominance (-1~1)", floating_point_range=[pad_range]
            ),
        )

        self.add_on_set_parameters_callback(self._on_param_change)
        self._cycle_start = time.time()
        self._pad_pending = False

        # 엎드린 초기 자세 (자연스러운 똬리 틀기)
        # 관절이 겹치지 않는 거리(R=0.22)를 유지하면서, 머리 높이를 바닥에 아주 가깝게(Z=-0.08) 낮추어
        # 바닥에 바짝 엎드린 웅크림 자세를 계산합니다. (실제 지상고 약 4~5cm)
        h_t2, h_t3, h_t5 = solve_3link_ik(0.22, -0.08, 0.0)
        self.home_pos = [0.0, h_t2, h_t3, 0.0, h_t5, 0.01, 0.01]

        self._update_motion_params()

    def _on_param_change(self, params):
        changed = False
        for param in params:
            if param.name in ("P", "A", "D"):
                changed = True
        if changed:
            self._pad_pending = True
        return SetParametersResult(successful=True)

    def _update_motion_params(self):
        P = self.get_parameter("P").value
        A = self.get_parameter("A").value
        D = self.get_parameter("D").value
        self.P, self.A, self.D = P, A, D

        # J, V, G 매핑 (논문 수식 엄격 준수)
        self.J = (1.0 - P) / 2.0
        self.V = (1.0 + A) / 2.0
        self.G = (1.0 + D) / 2.0

        self.cycle_time = 14.0 - 8.0 * self.V

        # 1. Gaze (G) -> Base Yaw 제어
        # G=1(정면 응시) -> 0.0 rad, G=0(회피) -> 0.5 rad (가볍게 옆으로 고개 돌림)
        gaze_yaw = 0.5 * (1.0 - self.G)

        # 2. Volume (V) -> 머리 높이(Z) 및 도달 거리(R) 극대화
        # V=1(흥분/과시) -> 극도로 높게(Z=0.20), 멀리(R=0.30) 뻗음 (엄청난 팽창)
        # V=0(웅크림/위축) -> 바닥에 닿을 듯 말 듯 매우 낮게(Z=-0.08), 가깝게(R=0.22) 뻗음
        target_Z = -0.08 + 0.28 * self.V
        target_R = 0.22 + 0.08 * self.V

        # 3. Task: "나를 봐 줘!" -> 머리(손끝) 각도는 무조건 정면(0.0)으로 고정
        alpha = 0.0

        # 역기구학 도출
        t2, t3, t5 = solve_3link_ik(target_R, target_Z, alpha)

        # 4. Gaze (G) 증폭 -> 빈 관절(joint_4)을 시선 회피(Aversion) 동작에 추가 매핑
        # G=1(당당함/지배적) -> 0.0 rad (고개를 꼿꼿이 세움)
        # G=0(위축/복종) -> 0.6 rad (약 34도. 자연스럽게 얼굴을 비스듬히 돌려 시선 회피)
        head_tilt = 0.6 * (1.0 - self.G)

        self.target_pos = [
            gaze_yaw,  # joint_1 (Gaze: 좌우 시선 회피)
            t2,  # joint_2 (Volume: 높이/팽창)
            t3,  # joint_3 (Volume: 높이/팽창)
            head_tilt,  # joint_4 (Gaze 증폭: 얼굴 완전히 비틀기)
            t5,  # joint_5 (Pitch: 정면 응시 유지)
            0.01,  # joint_a
            0.01,  # joint_b
        ]

    def timer_callback(self):
        now = time.time()
        elapsed = now - self._cycle_start
        cycle_t = elapsed % self.cycle_time

        if self._pad_pending and elapsed >= self.cycle_time:
            self._update_motion_params()
            self._cycle_start = now
            self._pad_pending = False
            cycle_t = 0.0

        current_pos = [0.0] * 7
        t1 = self.cycle_time * 0.4
        t2 = self.cycle_time * 0.6

        if cycle_t < t1:
            alpha = cycle_t / t1
            blend = interpolate(alpha, self.J)
            for i in range(7):
                current_pos[i] = self.home_pos[i] + blend * (
                    self.target_pos[i] - self.home_pos[i]
                )
        elif cycle_t < t2:
            for i in range(7):
                current_pos[i] = self.target_pos[i]
        else:
            alpha = (cycle_t - t2) / (self.cycle_time - t2)
            blend = interpolate(alpha, self.J)
            for i in range(7):
                current_pos[i] = self.target_pos[i] + blend * (
                    self.home_pos[i] - self.target_pos[i]
                )

        msg = JointState()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names

        # J값에 비례하는 실시간 유기적 떨림(Shivering) 추가
        # 멈춰있을 때조차도 극도의 분노나 공포(J=1) 상태면 온몸을 부들부들 떱니다.
        final_pos = [0.0] * 7
        for i in range(7):
            # 관절마다 떨림의 위상(Phase)을 다르게 주어 기계적이지 않게 만듦
            phase_offset = i * 1.2
            # 50Hz 타이머에서 부드럽게 떨리기 좋은 12Hz 노이즈 적용
            # 진폭을 0.008(약 0.45도)로 대폭 줄여 미세한 경련(Shivering) 구현
            jitter = (
                self.J * 0.008 * math.sin(2.0 * math.pi * 12.0 * now + phase_offset)
            )
            final_pos[i] = current_pos[i] + jitter

        msg.position = final_pos
        self.publisher_.publish(msg)


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--pad", type=float, nargs=3, default=[0.0, 0.0, 0.0])
    parsed, remaining = parser.parse_known_args()
    P, A, D = [max(-1.0, min(1.0, val)) for val in parsed.pad]

    rclpy.init(args=remaining)
    animator = AffectiveReactionAnimator(P, A, D)
    try:
        rclpy.spin(animator)
    except KeyboardInterrupt:
        pass
    finally:
        animator.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
