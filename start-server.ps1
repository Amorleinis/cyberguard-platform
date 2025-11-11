# CyberGuard Platform - Start Server and Test Authentication
# This script starts the backend server and tests the authentication system

Write-Host "`n" -NoNewline
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " CyberGuard Platform - Server Starter" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to backend directory
$backendPath = Join-Path $PSScriptRoot "backend"
Set-Location $backendPath

Write-Host "[1/4] Starting FastAPI server..." -ForegroundColor Yellow
Write-Host "      Port: 8000" -ForegroundColor Gray
Write-Host "      Mode: Development (auto-reload)" -ForegroundColor Gray
Write-Host ""

# Start server in background
$job = Start-Job -ScriptBlock {
    param($path)
    Set-Location $path
    python -m uvicorn app.main:app --reload --port 8000
} -ArgumentList $backendPath

# Wait for server to start
Write-Host "[2/4] Waiting for server to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test if server is running
$serverRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/dashboard" -UseBasicParsing -TimeoutSec 2
    if ($response.StatusCode -eq 200) {
        $serverRunning = $true
        Write-Host "      ✓ Server is running!" -ForegroundColor Green
    }
} catch {
    Write-Host "      ✗ Server failed to start" -ForegroundColor Red
    Write-Host "      Error: $_" -ForegroundColor Red
    Stop-Job $job
    Remove-Job $job
    exit 1
}

Write-Host ""
Write-Host "[3/4] Testing authentication..." -ForegroundColor Yellow

# Test admin login
try {
    $body = @{
        username = 'admin@cyberguard.com'
        password = 'admin123'
    }
    
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -Body $body -ContentType 'application/x-www-form-urlencoded'
    
    Write-Host "      ✓ Admin login successful!" -ForegroundColor Green
    Write-Host "      Token: $($loginResponse.access_token.Substring(0, 20))..." -ForegroundColor Gray
    
    # Get user profile
    $headers = @{
        Authorization = "Bearer $($loginResponse.access_token)"
    }
    
    $userProfile = Invoke-RestMethod -Uri "http://localhost:8000/auth/me" -Headers $headers
    Write-Host "      ✓ User: $($userProfile.email)" -ForegroundColor Green
    Write-Host "      ✓ Plan: $($userProfile.subscription_plan)" -ForegroundColor Green
    
    # Get threat stats
    $threatStats = Invoke-RestMethod -Uri "http://localhost:8000/threats/stats" -Headers $headers
    Write-Host "      ✓ Threats: $($threatStats.total_threats) total" -ForegroundColor Green
    
} catch {
    Write-Host "      ✗ Authentication test failed" -ForegroundColor Red
    Write-Host "      Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "[4/4] Server URLs:" -ForegroundColor Yellow
Write-Host "      API:         http://localhost:8000" -ForegroundColor Cyan
Write-Host "      Swagger UI:  http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host "      ReDoc:       http://localhost:8000/api/redoc" -ForegroundColor Cyan
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host " Server is running! Press Ctrl+C to stop" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Credentials:" -ForegroundColor White
Write-Host "  Admin:  admin@cyberguard.com / admin123" -ForegroundColor Gray
Write-Host "  User:   user@example.com / password123" -ForegroundColor Gray
Write-Host ""

# Keep script running and show server output
try {
    while ($true) {
        Receive-Job $job -Wait
    }
} finally {
    Write-Host "`nStopping server..." -ForegroundColor Yellow
    Stop-Job $job
    Remove-Job $job
    Write-Host "Server stopped." -ForegroundColor Green
}
