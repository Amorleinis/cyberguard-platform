# CyberGuard Enterprise Platform - Windows Installer
# PowerShell installation script for Windows systems

param(
    [string]$Edition = "core",
    [string]$InstallPath = "$env:ProgramFiles\CyberGuard",
    [switch]$Silent = $false
)

$ErrorActionPreference = "Stop"
$VERSION = "2.0.0"

# Banner
function Show-Banner {
    Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           CyberGuard Enterprise Platform v$VERSION              ║
║           Windows Installation Script                         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan
}

# Print step
function Write-Step {
    param([string]$Message)
    Write-Host "`n[•] $Message" -ForegroundColor Cyan
}

# Print success
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

# Print error
function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

# Print warning
function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

# Check administrator privileges
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check Python installation
function Test-Python {
    Write-Step "Checking Python installation..."
    
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            
            if ($major -ge 3 -and $minor -ge 8) {
                Write-Success "Python $pythonVersion detected"
                return $true
            } else {
                Write-ErrorMsg "Python 3.8+ required. Found: $pythonVersion"
                return $false
            }
        }
    } catch {
        Write-ErrorMsg "Python not found. Please install Python 3.8+ from python.org"
        return $false
    }
}

# Check system requirements
function Test-SystemRequirements {
    Write-Step "Checking system requirements..."
    
    # Check Windows version
    $osVersion = [System.Environment]::OSVersion.Version
    Write-Success "Windows Version: $($osVersion.Major).$($osVersion.Minor)"
    
    # Check available disk space
    $drive = (Get-Item $InstallPath -ErrorAction SilentlyContinue).PSDrive.Name
    if (-not $drive) {
        $drive = "C"
    }
    
    $disk = Get-PSDrive $drive
    $freeGB = [math]::Round($disk.Free / 1GB, 2)
    
    if ($freeGB -lt 10) {
        Write-Warning "Low disk space: ${freeGB}GB available (10GB recommended)"
    } else {
        Write-Success "Disk space: ${freeGB}GB available"
    }
    
    # Check memory
    $memory = (Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum).Sum / 1GB
    Write-Success "RAM: ${memory}GB"
    
    return $true
}

# Create installation directory
function New-InstallDirectory {
    Write-Step "Creating installation directory..."
    
    if (Test-Path $InstallPath) {
        Write-Warning "Installation directory already exists: $InstallPath"
    } else {
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
        Write-Success "Created: $InstallPath"
    }
    
    return $true
}

# Download platform files
function Get-PlatformFiles {
    Write-Step "Downloading CyberGuard platform..."
    
    $repoUrl = "https://github.com/Amorleinis/recovery/archive/refs/heads/main.zip"
    $zipPath = "$env:TEMP\cyberguard-main.zip"
    
    try {
        Invoke-WebRequest -Uri $repoUrl -OutFile $zipPath -UseBasicParsing
        Write-Success "Downloaded platform files"
        
        # Extract
        Write-Step "Extracting files..."
        Expand-Archive -Path $zipPath -DestinationPath $env:TEMP -Force
        
        # Copy to install directory
        $extractedPath = "$env:TEMP\recovery-main"
        Copy-Item -Path "$extractedPath\*" -Destination $InstallPath -Recurse -Force
        
        Write-Success "Files extracted to $InstallPath"
        
        # Cleanup
        Remove-Item $zipPath -Force
        Remove-Item $extractedPath -Recurse -Force
        
        return $true
    } catch {
        Write-ErrorMsg "Failed to download platform: $_"
        return $false
    }
}

# Create virtual environment
function New-VirtualEnvironment {
    Write-Step "Creating virtual environment..."
    
    Push-Location $InstallPath
    
    try {
        python -m venv .venv
        Write-Success "Virtual environment created"
        return $true
    } catch {
        Write-ErrorMsg "Failed to create virtual environment: $_"
        return $false
    } finally {
        Pop-Location
    }
}

# Install dependencies
function Install-Dependencies {
    param([string]$Edition)
    
    Write-Step "Installing $Edition dependencies..."
    
    Push-Location $InstallPath
    
    $pipCmd = ".\.venv\Scripts\pip.exe"
    
    $requirementsMap = @{
        'core' = @('requirements.txt')
        'ml' = @('requirements.txt', 'requirements-ml.txt')
        'performance' = @('requirements.txt', 'requirements-performance.txt')
        'enterprise' = @('requirements.txt', 'requirements-ml.txt', 'requirements-performance.txt')
        'dev' = @('requirements.txt', 'requirements-dev.txt')
    }
    
    $files = $requirementsMap[$Edition]
    
    try {
        foreach ($reqFile in $files) {
            if (Test-Path $reqFile) {
                Write-Host "   Installing from $reqFile..." -ForegroundColor Gray
                & $pipCmd install -r $reqFile --quiet
                Write-Success "$reqFile installed"
            } else {
                Write-Warning "$reqFile not found, skipping..."
            }
        }
        return $true
    } catch {
        Write-ErrorMsg "Failed to install dependencies: $_"
        return $false
    } finally {
        Pop-Location
    }
}

# Create Windows service
function New-WindowsService {
    Write-Step "Configuring Windows service..."
    
    $serviceName = "CyberGuardMonitor"
    $serviceExists = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    
    if ($serviceExists) {
        Write-Warning "Service already exists: $serviceName"
        return $true
    }
    
    try {
        $pythonExe = "$InstallPath\.venv\Scripts\python.exe"
        $scriptPath = "$InstallPath\scripts\active_threat_monitor.py"
        
        # Create service wrapper script
        $wrapperScript = @"
import sys
import os
import servicemanager
import win32serviceutil
import win32service

class CyberGuardService(win32serviceutil.ServiceFramework):
    _svc_name_ = "CyberGuardMonitor"
    _svc_display_name_ = "CyberGuard Threat Monitor"
    _svc_description_ = "Real-time threat monitoring and detection service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.is_running = False

    def SvcDoRun(self):
        self.is_running = True
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.PYS_SERVICE_STARTED,
                            (self._svc_name_, ''))
        self.main()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_running = False

    def main(self):
        import subprocess
        subprocess.run([r"$pythonExe", r"$scriptPath"])

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(CyberGuardService)
"@
        
        $serviceScript = "$InstallPath\scripts\windows_service.py"
        $wrapperScript | Out-File -FilePath $serviceScript -Encoding UTF8
        
        Write-Success "Service configuration created"
        Write-Warning "To install service, run: python $serviceScript install"
        
        return $true
    } catch {
        Write-ErrorMsg "Failed to configure service: $_"
        return $false
    }
}

# Create start menu shortcuts
function New-StartMenuShortcuts {
    Write-Step "Creating Start Menu shortcuts..."
    
    $shortcutPath = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\CyberGuard"
    
    if (-not (Test-Path $shortcutPath)) {
        New-Item -ItemType Directory -Path $shortcutPath -Force | Out-Null
    }
    
    $shell = New-Object -ComObject WScript.Shell
    
    # Dashboard shortcut
    $dashboardShortcut = $shell.CreateShortcut("$shortcutPath\CyberGuard Dashboard.lnk")
    $dashboardShortcut.TargetPath = "$InstallPath\.venv\Scripts\python.exe"
    $dashboardShortcut.Arguments = "$InstallPath\scripts\cli.py start dashboard"
    $dashboardShortcut.WorkingDirectory = $InstallPath
    $dashboardShortcut.Save()
    
    # Monitor shortcut
    $monitorShortcut = $shell.CreateShortcut("$shortcutPath\CyberGuard Monitor.lnk")
    $monitorShortcut.TargetPath = "$InstallPath\.venv\Scripts\python.exe"
    $monitorShortcut.Arguments = "$InstallPath\scripts\cli.py start monitor"
    $monitorShortcut.WorkingDirectory = $InstallPath
    $monitorShortcut.Save()
    
    Write-Success "Start Menu shortcuts created"
    return $true
}

# Create firewall rules
function New-FirewallRules {
    Write-Step "Configuring Windows Firewall..."
    
    try {
        # Dashboard port 5000
        New-NetFirewallRule -DisplayName "CyberGuard Dashboard" `
            -Direction Inbound `
            -Protocol TCP `
            -LocalPort 5000 `
            -Action Allow `
            -ErrorAction SilentlyContinue | Out-Null
        
        # API port 8000
        New-NetFirewallRule -DisplayName "CyberGuard API" `
            -Direction Inbound `
            -Protocol TCP `
            -LocalPort 8000 `
            -Action Allow `
            -ErrorAction SilentlyContinue | Out-Null
        
        # Mobile API port 9000
        New-NetFirewallRule -DisplayName "CyberGuard Mobile API" `
            -Direction Inbound `
            -Protocol TCP `
            -LocalPort 9000 `
            -Action Allow `
            -ErrorAction SilentlyContinue | Out-Null
        
        Write-Success "Firewall rules configured"
        return $true
    } catch {
        Write-Warning "Could not configure firewall rules (requires administrator)"
        return $true
    }
}

# Create desktop icon
function New-DesktopIcon {
    Write-Step "Creating desktop shortcut..."
    
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $shell = New-Object -ComObject WScript.Shell
    
    $shortcut = $shell.CreateShortcut("$desktopPath\CyberGuard Dashboard.lnk")
    $shortcut.TargetPath = "$InstallPath\.venv\Scripts\python.exe"
    $shortcut.Arguments = "$InstallPath\scripts\cli.py start dashboard"
    $shortcut.WorkingDirectory = $InstallPath
    $shortcut.Save()
    
    Write-Success "Desktop shortcut created"
    return $true
}

# Print next steps
function Show-NextSteps {
    Write-Host "`n" + ("="*70) -ForegroundColor Cyan
    Write-Host "✓ Installation Complete!" -ForegroundColor Green
    Write-Host ("="*70) -ForegroundColor Cyan
    
    Write-Host "`nNext Steps:`n" -ForegroundColor Yellow
    
    Write-Host "  1. Open CyberGuard Dashboard from Start Menu" -ForegroundColor White
    Write-Host "     Or run: " -NoNewline
    Write-Host "cd `"$InstallPath`"; .\.venv\Scripts\python.exe scripts\cli.py start dashboard" -ForegroundColor Gray
    
    Write-Host "`n  2. View platform status:" -ForegroundColor White
    Write-Host "     " -NoNewline
    Write-Host "cd `"$InstallPath`"; .\.venv\Scripts\python.exe scripts\cli.py status" -ForegroundColor Gray
    
    Write-Host "`n  3. Access web dashboard:" -ForegroundColor White
    Write-Host "     " -NoNewline
    Write-Host "http://localhost:5000" -ForegroundColor Gray
    
    Write-Host "`n  4. View documentation:" -ForegroundColor White
    Write-Host "     " -NoNewline
    Write-Host "$InstallPath\README_ULTIMATE.md" -ForegroundColor Gray
    
    Write-Host "`nInstallation Directory: " -NoNewline -ForegroundColor Yellow
    Write-Host $InstallPath -ForegroundColor White
    
    Write-Host "`n" + ("="*70) + "`n" -ForegroundColor Cyan
}

# Main installation process
function Start-Installation {
    Show-Banner
    
    Write-Host "Welcome to the CyberGuard Enterprise Platform installer!" -ForegroundColor White
    Write-Host "This will install CyberGuard to: $InstallPath`n" -ForegroundColor Gray
    
    if (-not $Silent) {
        # Prompt for edition
        Write-Host "Select Edition:" -ForegroundColor Yellow
        Write-Host "  1. Core (Free - Basic features)"
        Write-Host "  2. Professional (ML + Analytics)"
        Write-Host "  3. Enterprise (Full features)"
        Write-Host "  4. Development (All features + dev tools)"
        
        $choice = Read-Host "`nEnter choice [1-4] (default: 1)"
        if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "1" }
        
        $editionMap = @{
            '1' = 'core'
            '2' = 'ml'
            '3' = 'enterprise'
            '4' = 'dev'
        }
        
        $Edition = $editionMap[$choice]
    }
    
    Write-Host "`nInstalling $($Edition.ToUpper()) Edition...`n" -ForegroundColor Green
    
    # Check administrator
    if (-not (Test-Administrator)) {
        Write-Warning "Not running as administrator. Some features may be limited."
        Write-Host "Consider running: " -NoNewline
        Write-Host "Start-Process powershell -Verb runAs" -ForegroundColor Gray
        Write-Host ""
    }
    
    # Run installation steps
    $steps = @(
        { Test-Python },
        { Test-SystemRequirements },
        { New-InstallDirectory },
        { Get-PlatformFiles },
        { New-VirtualEnvironment },
        { Install-Dependencies $Edition },
        { New-StartMenuShortcuts },
        { New-DesktopIcon }
    )
    
    if (Test-Administrator) {
        $steps += { New-WindowsService }
        $steps += { New-FirewallRules }
    }
    
    foreach ($step in $steps) {
        if (-not (& $step)) {
            Write-ErrorMsg "`nInstallation failed!"
            exit 1
        }
    }
    
    Show-NextSteps
}

# Run installer
try {
    Start-Installation
} catch {
    Write-ErrorMsg "Installation error: $_"
    exit 1
}
