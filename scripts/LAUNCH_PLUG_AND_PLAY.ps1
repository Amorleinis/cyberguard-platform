# ONE-CLICK LAUNCHER - Plug and Play Platform Demo
# Automatically installs dependencies and runs demo with real data

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "THREAT INTELLIGENCE PLATFORM - ONE-CLICK LAUNCHER" -ForegroundColor Cyan
Write-Host "Plug and Play Demo with Real Data" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$baseDir = "c:\Users\allue\OneDrive\Desktop\datasets"
$dataDir = Join-Path $baseDir "data\plug_and_play"

# Create data directory
if (!(Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
    Write-Host "✓ Created data directory" -ForegroundColor Green
}

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Menu
Write-Host "Choose demo to run:" -ForegroundColor Yellow
Write-Host "1. Intelligence Engine (CVE Analysis with real data)" -ForegroundColor White
Write-Host "2. Detection Engine (Threat Detection with real data)" -ForegroundColor White
Write-Host "3. Complete Platform (All engines end-to-end)" -ForegroundColor White
Write-Host "4. Install dependencies only" -ForegroundColor White
Write-Host "0. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice"

function Install-Dependencies {
    param($minimal = $false)
    
    Write-Host ""
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    
    if ($minimal) {
        # Minimal deps for basic demo
        Write-Host "Installing core dependencies..." -ForegroundColor Gray
        pip install --quiet requests python-dateutil
    } else {
        # Full dependencies
        Write-Host "Installing all dependencies (this may take a few minutes)..." -ForegroundColor Gray
        pip install --quiet -r (Join-Path $baseDir "requirements.txt")
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "⚠ Some dependencies failed to install" -ForegroundColor Yellow
        Write-Host "  Demo will run with available features" -ForegroundColor Gray
    }
}

function Run-Demo {
    param($scriptName)
    
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host "RUNNING DEMO: $scriptName" -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host ""
    
    $scriptPath = Join-Path $baseDir $scriptName
    python $scriptPath
    
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host "DEMO COMPLETE" -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor Cyan
}

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Intelligence Engine Demo" -ForegroundColor Green
        Write-Host "This will analyze real CVE data from your workspace" -ForegroundColor Gray
        
        $install = Read-Host "Install dependencies first? (Y/N)"
        if ($install -eq "Y" -or $install -eq "y") {
            Install-Dependencies -minimal $true
        }
        
        Run-Demo "demo_intelligence_plug_and_play.py"
        
        Write-Host ""
        Write-Host "What happened:" -ForegroundColor Yellow
        Write-Host "  ✓ Scanned workspace for CVE data" -ForegroundColor Gray
        Write-Host "  ✓ Loaded real CVE files automatically" -ForegroundColor Gray
        Write-Host "  ✓ Analyzed CVEs and extracted IOCs" -ForegroundColor Gray
        Write-Host "  ✓ Saved results to: $dataDir\intelligence.db" -ForegroundColor Gray
    }
    
    "2" {
        Write-Host ""
        Write-Host "Detection Engine Demo" -ForegroundColor Green
        Write-Host "This will detect threats in real security event data" -ForegroundColor Gray
        
        $install = Read-Host "Install dependencies first? (Y/N)"
        if ($install -eq "Y" -or $install -eq "y") {
            Install-Dependencies -minimal $false
        }
        
        Run-Demo "demo_detection_plug_and_play.py"
        
        Write-Host ""
        Write-Host "What happened:" -ForegroundColor Yellow
        Write-Host "  ✓ Scanned workspace for threat data" -ForegroundColor Gray
        Write-Host "  ✓ Loaded real security events" -ForegroundColor Gray
        Write-Host "  ✓ Analyzed events for threats" -ForegroundColor Gray
        Write-Host "  ✓ Saved results to: $dataDir\detection.db" -ForegroundColor Gray
    }
    
    "3" {
        Write-Host ""
        Write-Host "Complete Platform Demo" -ForegroundColor Green
        Write-Host "This will run end-to-end threat lifecycle with all engines" -ForegroundColor Gray
        
        $install = Read-Host "Install dependencies first? (Y/N)"
        if ($install -eq "Y" -or $install -eq "y") {
            Install-Dependencies -minimal $false
        }
        
        Run-Demo "PLUG_AND_PLAY_DEMO.py"
        
        Write-Host ""
        Write-Host "What happened:" -ForegroundColor Yellow
        Write-Host "  ✓ Loaded all available real data" -ForegroundColor Gray
        Write-Host "  ✓ Ran Intelligence → Prevention workflow" -ForegroundColor Gray
        Write-Host "  ✓ Ran Detection → Response → Isolation workflow" -ForegroundColor Gray
        Write-Host "  ✓ Generated complete platform metrics" -ForegroundColor Gray
        Write-Host "  ✓ Saved all results to: $dataDir\" -ForegroundColor Gray
    }
    
    "4" {
        Write-Host ""
        Write-Host "Installing dependencies..." -ForegroundColor Green
        Install-Dependencies -minimal $false
        Write-Host ""
        Write-Host "Dependencies installed!" -ForegroundColor Green
        Write-Host "Run this script again to execute demos." -ForegroundColor Gray
    }
    
    "0" {
        Write-Host "Exited." -ForegroundColor Yellow
        exit
    }
    
    default {
        Write-Host "Invalid choice!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  • Check databases in: $dataDir" -ForegroundColor Gray
Write-Host "  • Explore your data files that were processed" -ForegroundColor Gray
Write-Host "  • Run .\install_unified.ps1 for full installation" -ForegroundColor Gray
Write-Host "  • Read QUICKSTART.md for more examples" -ForegroundColor Gray
Write-Host ""

Read-Host "Press Enter to exit"
