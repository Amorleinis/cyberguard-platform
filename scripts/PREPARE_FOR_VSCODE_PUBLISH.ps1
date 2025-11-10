# Publish Packages to GitHub via VS Code
# This script initializes git repos for each package

$baseDir = "c:\Users\allue\OneDrive\Desktop\datasets"

$engines = @(
    @{folder="intelligence"; repo="threat-intelligence-engine"},
    @{folder="prevention"; repo="threat-prevention-engine"},
    @{folder="detection"; repo="threat-detection-engine"},
    @{folder="response"; repo="incident-response-engine"},
    @{folder="isolation"; repo="threat-isolation-engine"},
    @{folder="mitigation"; repo="threat-mitigation-engine"},
    @{folder="recovery"; repo="system-recovery-engine"}
)

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "PREPARING PACKAGES FOR GITHUB (VS CODE)" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

foreach ($engine in $engines) {
    $enginePath = Join-Path $baseDir $engine.folder
    
    Write-Host "[$($engine.folder)]" -ForegroundColor Yellow
    
    Push-Location $enginePath
    
    # Initialize git if not already
    if (!(Test-Path ".git")) {
        git init
        Write-Host "  [OK] Git initialized" -ForegroundColor Green
    } else {
        Write-Host "  [OK] Git already initialized" -ForegroundColor Green
    }
    
    # Create/update .gitignore
    if (!(Test-Path ".gitignore")) {
        @"
__pycache__/
*.py[cod]
*`$py.class
*.so
.Python
*.egg-info/
dist/
build/
*.egg
venv/
env/
.vscode/
.idea/
*.db
*.sqlite
*.log
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
        Write-Host "  [OK] .gitignore created" -ForegroundColor Green
    }
    
    # Stage all files
    git add -A
    
    # Commit
    $status = git status --porcelain
    if ($status) {
        git commit -m "Initial commit: CyberGuard Industries - $($engine.repo)"
        Write-Host "  [OK] Files committed" -ForegroundColor Green
    } else {
        Write-Host "  [OK] Already committed" -ForegroundColor Green
    }
    
    Pop-Location
    Write-Host ""
}

Write-Host "=" * 80 -ForegroundColor Green
Write-Host "READY FOR VS CODE PUBLISH" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Green
Write-Host ""
Write-Host "Next steps in VS Code:" -ForegroundColor Cyan
Write-Host ""
Write-Host "For each engine folder:" -ForegroundColor White
Write-Host "  1. Open the folder in VS Code (File > Open Folder)" -ForegroundColor Gray
Write-Host "  2. Click Source Control icon (left sidebar)" -ForegroundColor Gray
Write-Host "  3. Click 'Publish to GitHub' button" -ForegroundColor Gray
Write-Host "  4. Choose 'Publish to GitHub public repository'" -ForegroundColor Gray
Write-Host "  5. Name it: cyberguard-industries/<repo-name>" -ForegroundColor Gray
Write-Host ""
Write-Host "Repository names to use:" -ForegroundColor Yellow
foreach ($engine in $engines) {
    Write-Host "  - cyberguard-industries/$($engine.repo)" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "Or create them all at once:" -ForegroundColor Yellow
Write-Host "  1. Go to: https://github.com/new" -ForegroundColor Gray
Write-Host "  2. Create organization: 'cyberguard-industries'" -ForegroundColor Gray
Write-Host "  3. Then publish each folder from VS Code" -ForegroundColor Gray
Write-Host ""
