# install_ros2_portable.ps1
# This script installs ROS 2 (Humble) portably in the current folder without requiring admin privileges.
# It uses RoboStack (Conda-forge), preventing system contamination. It is very safe and fast.


# Prevent encoding issues: Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

$ErrorActionPreference = "Stop"

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  ROS 2 Portable Installation (Windows) via RoboStack  " -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "Locally installing ROS 2 in the current folder without modifying system variables.`n"

# Paths configuration
$BASE_DIR = $PWD.Path
$MAMBA_DIR = Join-Path $BASE_DIR ".micromamba"
$ENV_DIR = Join-Path $BASE_DIR "ros2_env"

# 1. Create directories
if (-not (Test-Path -Path $MAMBA_DIR)) {
    New-Item -ItemType Directory -Force -Path $MAMBA_DIR | Out-Null
}

# 2. Download Micromamba
Write-Host "[1/3] Downloading Micromamba (package manager)..." -ForegroundColor Yellow
$mambaUrl = "https://micro.mamba.pm/api/micromamba/win-64/latest"
$mambaArchive = Join-Path $MAMBA_DIR "micromamba.tar.bz2"
Invoke-WebRequest -Uri $mambaUrl -OutFile $mambaArchive

# 3. Extract Micromamba (uses built-in tar for Windows 10 build 17063+)
Write-Host "`n[2/3] Extracting Micromamba..." -ForegroundColor Yellow
Set-Location $MAMBA_DIR
tar -xf micromamba.tar.bz2
$MAMBA_EXE = Join-Path $MAMBA_DIR "Library\bin\micromamba.exe"
Set-Location $BASE_DIR

# 4. Install ROS 2 Environment
Write-Host "`n[3/3] Downloading ROS 2 Humble via RoboStack and configuring environment... (This might take a while)" -ForegroundColor Yellow
$env:MAMBA_ROOT_PREFIX = $MAMBA_DIR
& $MAMBA_EXE create -p $ENV_DIR -c conda-forge -c robostack-staging ros-humble-desktop python=3.10 -y

# 5. Create Activation Script (Shortcut)
Write-Host "`nCreating environment activation script..." -ForegroundColor Yellow
$ActivateScript = "activate_ros2.ps1"
$ScriptContent = @"
`$env:MAMBA_ROOT_PREFIX = `"$MAMBA_DIR`"
& `"$MAMBA_EXE`" shell hook -s powershell | Out-String | Invoke-Expression
micromamba activate `"$ENV_DIR`"
Write-Host `"=========================================`" -ForegroundColor Cyan
Write-Host `" ROS 2 Humble environment activated!`" -ForegroundColor Green
Write-Host `" (To exit, close the terminal or type 'micromamba deactivate')`"
Write-Host `"=========================================`" -ForegroundColor Cyan
"@

Set-Content -Path $ActivateScript -Value $ScriptContent -Encoding UTF8

Write-Host "`n=====================================================" -ForegroundColor Cyan
Write-Host "Installation completed successfully!" -ForegroundColor Green
Write-Host "Now run the following command to start the ROS 2 environment:"
Write-Host ".\$ActivateScript" -ForegroundColor Yellow
Write-Host "=====================================================" -ForegroundColor Cyan
