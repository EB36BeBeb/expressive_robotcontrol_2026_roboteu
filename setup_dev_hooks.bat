@echo off
echo ==========================================
echo    Installing Git Hooks for Team Devs
echo ==========================================

python -m pip install pre-commit black flake8
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install pre-commit. Please ensure Python is installed.
    pause
    exit /b 1
)

python -m pre_commit install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to register git hooks.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Pre-commit hooks are successfully installed!
echo Now, 'black' and 'flake8' will automatically run every time you 'git commit'.
pause
