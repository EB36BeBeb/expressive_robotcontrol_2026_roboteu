# VcXsrv (X Server) Installation Script for Windows Host

# Prevent encoding issues: Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   Installing VcXsrv (X Server) via winget..." -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# Check if winget is installed
if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "Starting VcXsrv installation..."
    winget install --id=marha.VcXsrv -e --source winget
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[Success] VcXsrv installation is complete." -ForegroundColor Green
        Write-Host "Now run 'XLaunch' and configure it as follows:" -ForegroundColor Yellow
        Write-Host "1. Choose 'Multiple windows'"
        Write-Host "2. Display number: -1"
        Write-Host "3. Choose 'Start no client'"
        Write-Host "4. Check 'Disable access control' (Required!)" -ForegroundColor Red
        Write-Host "5. It's convenient to press 'Save configuration' to save it on the desktop."
    } else {
        Write-Host "`n[Error] A problem occurred during installation. Please try manual installation." -ForegroundColor Red
    }
} else {
    Write-Host "`n[Error] winget not found. Please install manually from the following link:" -ForegroundColor Red
    Write-Host "https://sourceforge.net/projects/vcxsrv/"
}

pause
