import sys


def check_mujoco():
    print("Checking MuJoCo installation...")
    try:
        import mujoco

        print(f"MuJoCo version {mujoco.__version__} is installed!")

        # Simple simulation test (no GUI yet)
        model = mujoco.MjModel.from_xml_string(
            "<mujoco><worldbody><body><geom type='sphere' size='.1'/></body></worldbody></mujoco>"
        )
        data = mujoco.MjData(model)
        mujoco.mj_step(model, data)
        print("Successfully loaded a simple model and stepped the simulation.")

        print("\nTo test MuJoCo GUI, you can try: python3 -m mujoco.viewer")
        print("Note: This requires an X server (like VcXsrv) running on Windows.")

    except ImportError:
        print("\n[ERROR] MuJoCo is not installed.")
        print("Please run: pip install mujoco")
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")


if __name__ == "__main__":
    check_mujoco()
