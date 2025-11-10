# Upload Individual Engine Packages to GitHub
# Creates separate GitHub repositories for each engine

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "GITHUB UPLOAD - INDIVIDUAL ENGINE PACKAGES" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$baseDir = "c:\Users\allue\OneDrive\Desktop\datasets"
$engines = @(
    @{name="intelligence"; repo="threat-intelligence-engine"; desc="CVE Analysis and Threat Intelligence Engine"},
    @{name="prevention"; repo="threat-prevention-engine"; desc="Threat Prevention and IOC Blocking Engine"},
    @{name="detection"; repo="threat-detection-engine"; desc="Threat Detection and Anomaly Analysis Engine"},
    @{name="response"; repo="incident-response-engine"; desc="Incident Response and Threat Containment Engine"},
    @{name="isolation"; repo="threat-isolation-engine"; desc="Threat Isolation and Network Segmentation Engine"},
    @{name="mitigation"; repo="threat-mitigation-engine"; desc="Threat Mitigation and Remediation Engine"},
    @{name="recovery"; repo="system-recovery-engine"; desc="System Recovery and Restoration Engine"}
)

# Check if git is installed
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
$gitVersion = git --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Git is not installed!" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}
Write-Host "Git found: $gitVersion" -ForegroundColor Green
Write-Host ""

# Check if gh CLI is installed
$ghVersion = gh --version 2>&1
$hasGhCli = $LASTEXITCODE -eq 0

if ($hasGhCli) {
    Write-Host "GitHub CLI found: " -ForegroundColor Green -NoNewline
    Write-Host ($ghVersion | Select-Object -First 1)
    Write-Host ""
    
    # Check authentication
    $authStatus = gh auth status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "GitHub authentication: OK" -ForegroundColor Green
    } else {
        Write-Host "GitHub CLI not authenticated!" -ForegroundColor Yellow
        Write-Host "Run: gh auth login" -ForegroundColor White
        $continue = Read-Host "Continue without auto-creating repos? (Y/N)"
        if ($continue -ne "Y" -and $continue -ne "y") {
            exit 0
        }
    }
} else {
    Write-Host "GitHub CLI not found (optional)" -ForegroundColor Yellow
    Write-Host "Install from: https://cli.github.com/" -ForegroundColor Gray
    Write-Host "Repositories will need to be created manually on GitHub" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "PREPARING PACKAGES FOR UPLOAD" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

foreach ($engine in $engines) {
    $enginePath = Join-Path $baseDir $engine.name
    
    Write-Host "[$($engine.name.ToUpper())]" -ForegroundColor Cyan
    Write-Host "  Directory: $enginePath" -ForegroundColor Gray
    Write-Host "  Repository: $($engine.repo)" -ForegroundColor Gray
    
    # Check if directory exists
    if (!(Test-Path $enginePath)) {
        Write-Host "  ERROR: Directory not found!" -ForegroundColor Red
        continue
    }
    
    # Navigate to engine directory
    Push-Location $enginePath
    
    # Initialize git if not already
    if (!(Test-Path ".git")) {
        Write-Host "  Initializing Git repository..." -ForegroundColor Yellow
        git init | Out-Null
        Write-Host "  [OK] Git initialized" -ForegroundColor Green
    } else {
        Write-Host "  [OK] Git repository exists" -ForegroundColor Green
    }
    
    # Create .gitignore if it doesn't exist
    if (!(Test-Path ".gitignore")) {
        Write-Host "  Creating .gitignore..." -ForegroundColor Yellow
        @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/
*.egg

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
        Write-Host "  [OK] .gitignore created" -ForegroundColor Green
    }
    
    # Create LICENSE if it doesn't exist
    if (!(Test-Path "LICENSE")) {
        Write-Host "  Creating LICENSE (MIT)..." -ForegroundColor Yellow
        @"
MIT License

Copyright (c) 2025 Threat Intelligence Platform

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"@ | Out-File -FilePath "LICENSE" -Encoding UTF8
        Write-Host "  [OK] LICENSE created" -ForegroundColor Green
    }
    
    # Stage all files
    Write-Host "  Staging files..." -ForegroundColor Yellow
    git add -A
    
    # Check if there are changes to commit
    $status = git status --porcelain
    if ($status) {
        Write-Host "  Committing changes..." -ForegroundColor Yellow
        git commit -m "Initial commit: $($engine.desc)" | Out-Null
        Write-Host "  [OK] Changes committed" -ForegroundColor Green
    } else {
        Write-Host "  [OK] No changes to commit" -ForegroundColor Green
    }
    
    Pop-Location
    Write-Host ""
}

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "NEXT STEPS" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

if ($hasGhCli -and $LASTEXITCODE -eq 0) {
    Write-Host "Option 1: Auto-create repositories with GitHub CLI" -ForegroundColor Green
    Write-Host ""
    foreach ($engine in $engines) {
        Write-Host "cd $($engine.name)" -ForegroundColor White
        Write-Host "gh repo create $($engine.repo) --public --source=. --description=`"$($engine.desc)`" --push" -ForegroundColor Cyan
        Write-Host ""
    }
    Write-Host ""
    Write-Host "Run these commands? (Y/N): " -ForegroundColor Yellow -NoNewline
    $autoCreate = Read-Host
    
    if ($autoCreate -eq "Y" -or $autoCreate -eq "y") {
        Write-Host ""
        Write-Host "Creating repositories..." -ForegroundColor Cyan
        Write-Host ""
        
        foreach ($engine in $engines) {
            $enginePath = Join-Path $baseDir $engine.name
            Push-Location $enginePath
            
            Write-Host "Creating: $($engine.repo)" -ForegroundColor Yellow
            gh repo create $engine.repo --public --source=. --description="$($engine.desc)" --push
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK] Repository created and pushed!" -ForegroundColor Green
            } else {
                Write-Host "[WARNING] Failed to create repository" -ForegroundColor Yellow
            }
            
            Pop-Location
            Write-Host ""
        }
        
        Write-Host "=" * 80 -ForegroundColor Green
        Write-Host "UPLOAD COMPLETE!" -ForegroundColor Green
        Write-Host "=" * 80 -ForegroundColor Green
    }
} else {
    Write-Host "Manual Upload Instructions:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "For each engine:" -ForegroundColor White
    Write-Host "  1. Create repository on GitHub: https://github.com/new" -ForegroundColor Gray
    Write-Host "  2. Navigate to engine directory: cd <engine-name>" -ForegroundColor Gray
    Write-Host "  3. Add remote: git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git" -ForegroundColor Gray
    Write-Host "  4. Push: git branch -M main && git push -u origin main" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "Suggested repository names:" -ForegroundColor White
    foreach ($engine in $engines) {
        Write-Host "  - $($engine.repo)" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "After upload, users can install with:" -ForegroundColor Yellow
Write-Host "  pip install git+https://github.com/YOUR_USERNAME/REPO_NAME" -ForegroundColor White
Write-Host ""
