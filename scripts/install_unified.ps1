# Installation Script for Unified Bundle
# Installs the complete Threat Intelligence Platform with all engines

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Threat Intelligence Platform" -ForegroundColor Cyan
Write-Host "Unified Bundle Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = "c:\Users\allue\OneDrive\Desktop\datasets"

Write-Host "This will install the complete Threat Intelligence Platform" -ForegroundColor Yellow
Write-Host "including all 7 engines and the orchestration layer." -ForegroundColor Yellow
Write-Host ""
Write-Host "Components to be installed:" -ForegroundColor Green
Write-Host "  ✓ Intelligence Engine" -ForegroundColor Gray
Write-Host "  ✓ Prevention Engine" -ForegroundColor Gray
Write-Host "  ✓ Detection Engine" -ForegroundColor Gray
Write-Host "  ✓ Response Engine" -ForegroundColor Gray
Write-Host "  ✓ Isolation Engine" -ForegroundColor Gray
Write-Host "  ✓ Mitigation Engine" -ForegroundColor Gray
Write-Host "  ✓ Recovery Engine" -ForegroundColor Gray
Write-Host "  ✓ Platform Orchestrator" -ForegroundColor Gray
Write-Host ""

$install = Read-Host "Do you want to proceed? (Y/N)"

if ($install -ne "Y" -and $install -ne "y") {
    Write-Host "Installation cancelled." -ForegroundColor Yellow
    exit
}

Write-Host "`nStep 1: Checking dependencies..." -ForegroundColor Cyan
$reqFile = Join-Path $baseDir "requirements.txt"
if (Test-Path $reqFile) {
    Write-Host "Found requirements.txt" -ForegroundColor Green
} else {
    Write-Host "Warning: requirements.txt not found" -ForegroundColor Yellow
}

Write-Host "`nStep 2: Installing dependencies..." -ForegroundColor Cyan
Push-Location $baseDir

Write-Host "Installing Python packages (this may take a few minutes)..." -ForegroundColor Gray
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Some dependencies failed to install" -ForegroundColor Yellow
    Write-Host "You can continue, but some features may not work" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (Y/N)"
    if ($continue -ne "Y" -and $continue -ne "y") {
        Pop-Location
        exit
    }
}

Write-Host "`nStep 3: Installing Threat Intelligence Platform..." -ForegroundColor Cyan
pip install -e .

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "Installation Successful!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "The Threat Intelligence Platform is now installed." -ForegroundColor Green
    Write-Host ""
    Write-Host "Quick Start:" -ForegroundColor Yellow
    Write-Host "  python" -ForegroundColor Gray
    Write-Host "  >>> from orchestration.threat_platform_orchestrator import ThreatIntelligencePlatform" -ForegroundColor Gray
    Write-Host "  >>> platform = ThreatIntelligencePlatform(base_dir='./data')" -ForegroundColor Gray
    Write-Host "  >>> platform.get_platform_status()" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Documentation:" -ForegroundColor Yellow
    Write-Host "  - Full Guide: README.md" -ForegroundColor Gray
    Write-Host "  - Quick Start: QUICKSTART.md" -ForegroundColor Gray
    Write-Host "  - Installation: INSTALLATION.md" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  python example_unified_bundle.py" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Testing:" -ForegroundColor Yellow
    Write-Host "  python validate_engines.py" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "Installation Failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the error messages above." -ForegroundColor Red
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  - Python version must be 3.8 or higher" -ForegroundColor Gray
    Write-Host "  - pip must be up to date: pip install --upgrade pip" -ForegroundColor Gray
    Write-Host "  - Some packages require C++ build tools" -ForegroundColor Gray
}

Pop-Location

Write-Host ""
Read-Host "Press Enter to exit"
