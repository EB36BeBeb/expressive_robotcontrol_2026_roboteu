# Windows Host용 VcXsrv (X Server) 설치 스크립트

# 한글 깨짐 방지: 콘솔 인코딩을 UTF-8로 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   Installing VcXsrv (X Server) via winget..." -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# winget이 설치되어 있는지 확인
if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "VcXsrv 설치를 시작합니다..."
    winget install --id=marha.VcXsrv -e --source winget
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[성공] VcXsrv 설치가 완료되었습니다." -ForegroundColor Green
        Write-Host "이제 'XLaunch'를 실행하고 다음과 같이 설정하세요:" -ForegroundColor Yellow
        Write-Host "1. Multiple windows 선택"
        Write-Host "2. Display number: 0"
        Write-Host "3. Start no client 선택"
        Write-Host "4. 'Disable access control' 체크 (필수!)" -ForegroundColor Red
        Write-Host "5. 'Save configuration'을 눌러 바탕화면에 저장해두면 편리합니다."
    } else {
        Write-Host "`n[오류] 설치 중 문제가 발생했습니다. 수동으로 설치를 시도하세요." -ForegroundColor Red
    }
} else {
    Write-Host "`n[오류] winget을 찾을 수 없습니다. 다음 링크에서 수동으로 설치하세요:" -ForegroundColor Red
    Write-Host "https://sourceforge.net/projects/vcxsrv/"
}

pause
