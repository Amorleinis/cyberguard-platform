# Installation Script for Individual Engines
# Allows you to install specific engines based on your needs

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Threat Intelligence Platform" -ForegroundColor Cyan
Write-Host "Individual Engine Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = "c:\Users\allue\OneDrive\Desktop\datasets"

Write-Host "Available Engines:" -ForegroundColor Yellow
Write-Host "1. Intelligence Engine (CVE analysis, IOC extraction)"
Write-Host "2. Prevention Engine (IOC blocking, patch management)"
Write-Host "3. Detection Engine (ML-based threat detection)"
Write-Host "4. Response Engine (Incident management)"
Write-Host "5. Isolation Engine (Network segmentation, quarantine)"
Write-Host "6. Mitigation Engine (Vulnerability remediation)"
Write-Host "7. Recovery Engine (Backup/restore, business continuity)"
Write-Host "8. Install ALL engines separately"
Write-Host "0. Exit"
Write-Host ""

$choice = Read-Host "Select engine to install (0-8)"

function Install-Engine {
    param($engineName, $enginePath)
    
    Write-Host "`nInstalling $engineName..." -ForegroundColor Green
    
    Push-Location $enginePath
    
    # Install the engine
    $result = pip install -e .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $engineName installed successfully!" -ForegroundColor Green
        
        # Check if README exists
        $readmePath = Join-Path $enginePath "README.md"
        if (Test-Path $readmePath) {
            Write-Host "  Documentation: $readmePath" -ForegroundColor Gray
        }
    } else {
        Write-Host "✗ Failed to install $engineName" -ForegroundColor Red
    }
    
    Pop-Location
}

switch ($choice) {
    "1" {
        Install-Engine "Intelligence Engine" (Join-Path $baseDir "intelligence")
        Write-Host "`nNext steps:" -ForegroundColor Yellow
        Write-Host "  from intelligence import ThreatIntelligenceEngine"
        Write-Host "  engine = ThreatIntelligenceEngine(db_path='intel.db')"
    }
    "2" {
        Install-Engine "Prevention Engine" (Join-Path $baseDir "prevention")
        Write-Host "`nNext steps:" -ForegroundColor Yellow
        Write-Host "  from prevention import ThreatPreventionEngine"
        Write-Host "  engine = ThreatPreventionEngine(db_path='prev.db')"
    }
    "3" {
        Install-Engine "Detection Engine" (Join-Path $baseDir "detection")
        Write-Host "`nNext steps:" -ForegroundColor Yellow
        Write-Host "  from detection import ThreatDetectionEngine"
        Write-Host "  engine = ThreatDetectionEngine(db_path='detect.db')"
    }
    "4" {
        Install-Engine "Response Engine" (Join-Path $baseDir "response")
        Write-Host "`nNext steps:" -ForegroundColor Yellow
        Write-Host "  from response import ThreatResponseEngine"
        Write-Host "  engine = ThreatResponseEngine(db_path='response.db')"
    }
    "5" {
        Install-Engine "Isolation Engine" (Join-Path $baseDir "isolation")
        Write-Host "`nNext steps:" -ForegroundColor Yellow
        Write-Host "  from isolation import ThreatIsolationEngine"
        Write-Host "  engine = ThreatIsolationEngine()"
    }
    "6" {
        Install-Engine "Mitigation Engine" (Join-Path $baseDir "mitigation")
        Write-Host "`nNext steps:" -ForegroundColor Yellow
        Write-Host "  from mitigation import ThreatMitigationEngine"
        Write-Host "  engine = ThreatMitigationEngine()"
    }
    "7" {
        Install-Engine "Recovery Engine" (Join-Path $baseDir "recovery")
        Write-Host "`nNext steps:" -ForegroundColor Yellow
        Write-Host "  from recovery import ThreatRecoveryEngine"
        Write-Host "  engine = ThreatRecoveryEngine()"
    }
    "8" {
        Write-Host "`nInstalling all engines..." -ForegroundColor Green
        Install-Engine "Intelligence Engine" (Join-Path $baseDir "intelligence")
        Install-Engine "Prevention Engine" (Join-Path $baseDir "prevention")
        Install-Engine "Detection Engine" (Join-Path $baseDir "detection")
        Install-Engine "Response Engine" (Join-Path $baseDir "response")
        Install-Engine "Isolation Engine" (Join-Path $baseDir "isolation")
        Install-Engine "Mitigation Engine" (Join-Path $baseDir "mitigation")
        Install-Engine "Recovery Engine" (Join-Path $baseDir "recovery")
        
        Write-Host "`n========================================" -ForegroundColor Green
        Write-Host "All engines installed successfully!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
    }
    "0" {
        Write-Host "Installation cancelled." -ForegroundColor Yellow
        exit
    }
    default {
        Write-Host "Invalid choice. Please run the script again." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "See individual README.md files for usage examples." -ForegroundColor Gray
