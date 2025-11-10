# Install Git and GitHub CLI for Windows
# Downloads and installs both tools needed for GitHub upload

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "INSTALLING GIT AND GITHUB CLI" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Check if winget is available
Write-Host "Checking for winget (Windows Package Manager)..." -ForegroundColor Yellow
$wingetExists = Get-Command winget -ErrorAction SilentlyContinue

if ($wingetExists) {
    Write-Host "[OK] winget found - using automated installation" -ForegroundColor Green
    Write-Host ""
    
    # Install Git
    Write-Host "Installing Git..." -ForegroundColor Cyan
    winget install --id Git.Git -e --source winget --silent --accept-package-agreements --accept-source-agreements
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Git installed successfully" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Git may already be installed or installation had issues" -ForegroundColor Yellow
    }
    Write-Host ""
    
    # Install GitHub CLI
    Write-Host "Installing GitHub CLI..." -ForegroundColor Cyan
    winget install --id GitHub.cli -e --source winget --silent --accept-package-agreements --accept-source-agreements
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] GitHub CLI installed successfully" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] GitHub CLI may already be installed or installation had issues" -ForegroundColor Yellow
    }
    Write-Host ""
    
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host "INSTALLATION COMPLETE" -ForegroundColor Green
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Close and reopen PowerShell to use git and gh commands" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Close this PowerShell window" -ForegroundColor White
    Write-Host "  2. Open a new PowerShell window" -ForegroundColor White
    Write-Host "  3. Navigate to: cd c:\Users\allue\OneDrive\Desktop\datasets" -ForegroundColor White
    Write-Host "  4. Run: gh auth login" -ForegroundColor White
    Write-Host "  5. Then run the GitHub upload script" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host "[INFO] winget not available - using manual download method" -ForegroundColor Yellow
    Write-Host ""
    
    # Manual download URLs
    $gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe"
    $ghUrl = "https://github.com/cli/cli/releases/download/v2.40.1/gh_2.40.1_windows_amd64.msi"
    
    $downloadDir = Join-Path $env:TEMP "git_gh_installers"
    if (!(Test-Path $downloadDir)) {
        New-Item -ItemType Directory -Path $downloadDir -Force | Out-Null
    }
    
    # Download Git
    Write-Host "Downloading Git installer..." -ForegroundColor Cyan
    $gitInstaller = Join-Path $downloadDir "git-installer.exe"
    try {
        Invoke-WebRequest -Uri $gitUrl -OutFile $gitInstaller -UseBasicParsing
        Write-Host "[OK] Git installer downloaded" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to download Git: $_" -ForegroundColor Red
    }
    Write-Host ""
    
    # Download GitHub CLI
    Write-Host "Downloading GitHub CLI installer..." -ForegroundColor Cyan
    $ghInstaller = Join-Path $downloadDir "gh-installer.msi"
    try {
        Invoke-WebRequest -Uri $ghUrl -OutFile $ghInstaller -UseBasicParsing
        Write-Host "[OK] GitHub CLI installer downloaded" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to download GitHub CLI: $_" -ForegroundColor Red
    }
    Write-Host ""
    
    # Run installers
    Write-Host "=" * 80 -ForegroundColor Yellow
    Write-Host "RUNNING INSTALLERS" -ForegroundColor Yellow
    Write-Host "=" * 80 -ForegroundColor Yellow
    Write-Host ""
    
    if (Test-Path $gitInstaller) {
        Write-Host "Installing Git (this may take a minute)..." -ForegroundColor Cyan
        Start-Process -FilePath $gitInstaller -ArgumentList "/VERYSILENT /NORESTART" -Wait
        Write-Host "[OK] Git installation complete" -ForegroundColor Green
        Write-Host ""
    }
    
    if (Test-Path $ghInstaller) {
        Write-Host "Installing GitHub CLI..." -ForegroundColor Cyan
        Start-Process msiexec.exe -ArgumentList "/i `"$ghInstaller`" /quiet /norestart" -Wait
        Write-Host "[OK] GitHub CLI installation complete" -ForegroundColor Green
        Write-Host ""
    }
    
    # Cleanup
    Write-Host "Cleaning up installers..." -ForegroundColor Gray
    Remove-Item -Recurse -Force $downloadDir -ErrorAction SilentlyContinue
    Write-Host ""
    
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host "INSTALLATION COMPLETE" -ForegroundColor Green
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Close and reopen PowerShell to use git and gh commands" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Close this PowerShell window" -ForegroundColor White
    Write-Host "  2. Open a new PowerShell window" -ForegroundColor White
    Write-Host "  3. Navigate to: cd c:\Users\allue\OneDrive\Desktop\datasets" -ForegroundColor White
    Write-Host "  4. Verify installation: git --version" -ForegroundColor White
    Write-Host "  5. Verify installation: gh --version" -ForegroundColor White
    Write-Host "  6. Run: gh auth login" -ForegroundColor White
    Write-Host "  7. Then run the GitHub upload script" -ForegroundColor White
    Write-Host ""
}

Write-Host "Press Enter to exit..." -ForegroundColor Gray
Read-Host
