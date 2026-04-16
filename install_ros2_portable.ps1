# install_ros2_portable.ps1
# 이 스크립트는 관리자 권한 없이 현재 폴더에 ROS 2(Humble)를 휴대용으로 설치합니다.
# RoboStack(Conda-forge) 기반으로 구축되어 시스템을 오염시키지 않으며 매우 안전하고 빠른 방식입니다.


# 한글 깨짐 방지: 콘솔 인코딩을 UTF-8로 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

$ErrorActionPreference = "Stop"

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  ROS 2 Portable Installation (Windows) via RoboStack  " -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "현재 폴더에 시스템 환경 변수 변경 없이 ROS 2를 로컬 설치합니다.`n"

# 경로 설정
$BASE_DIR = $PWD.Path
$MAMBA_DIR = Join-Path $BASE_DIR ".micromamba"
$ENV_DIR = Join-Path $BASE_DIR "ros2_env"

# 1. 디렉토리 생성
if (-not (Test-Path -Path $MAMBA_DIR)) {
    New-Item -ItemType Directory -Force -Path $MAMBA_DIR | Out-Null
}

# 2. Micromamba 다운로드
Write-Host "[1/3] Micromamba(패키지 매니저) 다운로드 중..." -ForegroundColor Yellow
$mambaUrl = "https://micro.mamba.pm/api/micromamba/win-64/latest"
$mambaArchive = Join-Path $MAMBA_DIR "micromamba.tar.bz2"
Invoke-WebRequest -Uri $mambaUrl -OutFile $mambaArchive

# 3. Micromamba 압축 해제 (Windows 10 이상 최소 Windows 10 build 17063+ 내장 tar 활용)
Write-Host "`n[2/3] Micromamba 압축 해제 중..." -ForegroundColor Yellow
Set-Location $MAMBA_DIR
tar -xf micromamba.tar.bz2
$MAMBA_EXE = Join-Path $MAMBA_DIR "Library\bin\micromamba.exe"
Set-Location $BASE_DIR

# 4. ROS 2 환경 설치
Write-Host "`n[3/3] RoboStack을 통한 ROS 2 Humble 다운로드 및 환경 구성 중... (시간이 다소 소요될 수 있습니다)" -ForegroundColor Yellow
$env:MAMBA_ROOT_PREFIX = $MAMBA_DIR
& $MAMBA_EXE create -p $ENV_DIR -c conda-forge -c robostack-staging ros-humble-desktop python=3.10 -y

# 5. 실행 및 활성화 스크립트(Shortcut) 생성
Write-Host "`n환경 활성화 스크립트 생성 중..." -ForegroundColor Yellow
$ActivateScript = "activate_ros2.ps1"
$ScriptContent = @"
`$env:MAMBA_ROOT_PREFIX = `"$MAMBA_DIR`"
& `"$MAMBA_EXE`" shell hook -s powershell | Out-String | Invoke-Expression
micromamba activate `"$ENV_DIR`"
Write-Host `"=========================================`" -ForegroundColor Cyan
Write-Host `" ROS 2 Humble 환경이 활성화되었습니다!`" -ForegroundColor Green
Write-Host `" (종료하려면 터미널을 닫거나 'micromamba deactivate'를 입력하세요)`"
Write-Host `"=========================================`" -ForegroundColor Cyan
"@

Set-Content -Path $ActivateScript -Value $ScriptContent -Encoding UTF8

Write-Host "`n=====================================================" -ForegroundColor Cyan
Write-Host "설치가 성공적으로 완료되었습니다!" -ForegroundColor Green
Write-Host "이제 다음 명령어를 실행하여 ROS 2 환경을 시작하세요:"
Write-Host ".\$ActivateScript" -ForegroundColor Yellow
Write-Host "=====================================================" -ForegroundColor Cyan
