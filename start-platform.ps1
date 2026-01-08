# CyberGuard Platform Launcher
Write-Host "Starting CyberGuard Enterprise Platform..." -ForegroundColor Cyan

# Start Backend
Write-Host "`n[1/3] Starting Backend API..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; ..\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
Start-Sleep -Seconds 3

# Start Web
Write-Host "[2/3] Starting Web Application..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd web; python -m http.server 3000"
Start-Sleep -Seconds 2

# Start Desktop
Write-Host "[3/3] Starting Desktop Application..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd desktop; python cyberguard_desktop.py"
Start-Sleep -Seconds 2

# Open browser
Write-Host "`nOpening web browser..." -ForegroundColor Green
Start-Process "http://localhost:3000"

Write-Host "`nAll components started successfully!" -ForegroundColor Green
Write-Host "Backend API:   http://localhost:8000" -ForegroundColor Cyan
Write-Host "Web App:       http://localhost:3000" -ForegroundColor Cyan
Write-Host "Desktop App:   Running (check system tray)" -ForegroundColor Cyan
Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")