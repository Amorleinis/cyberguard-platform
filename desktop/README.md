# CyberGuard Desktop Application

Professional Windows desktop application for the CyberGuard Enterprise Platform.

## Features

✅ **Modern PyQt5 Interface** with dark theme
✅ **System Tray Integration** - Runs in background
✅ **Real-time Threat Monitoring** via WebSocket
✅ **Dashboard** with live statistics
✅ **Protection Controls** - Enable/disable features
✅ **Quick & Full Scans**
✅ **System Resource Monitoring** (CPU, Memory, Disk)
✅ **Threat History** with filtering
✅ **API Integration** with FastAPI backend

## Installation

```powershell
# Install dependencies
pip install -r requirements.txt

# Run the application
python cyberguard_desktop.py
```

## Usage

### Run from Command Line
```powershell
python cyberguard_desktop.py
```

### Create Executable (Optional)
```powershell
# Install PyInstaller
pip install pyinstaller

# Create standalone executable
pyinstaller --onefile --windowed --name="CyberGuard" cyberguard_desktop.py
```

## Features Overview

### Dashboard Tab
- Active threat count
- Blocked threats today
- System health status
- Last scan time
- CPU, Memory, Disk usage meters
- Quick actions (Scan, Update)

### Threats Tab
- Real-time threat list
- Severity levels (Critical, High, Medium, Low)
- Threat type and description
- Timestamp
- Refresh and clear history

### Protection Tab
- Real-time protection toggle
- Network monitoring toggle
- File system protection toggle
- Overall protection status

### Settings Tab
- Backend API URL configuration
- About information
- Application version

## System Tray

The application minimizes to system tray with these options:
- **Show** - Restore window
- **Hide** - Minimize to tray
- **Quick Scan** - Start quick scan
- **Quit** - Exit application

## Backend Connection

The desktop app connects to:
- **REST API**: `http://localhost:8000/api/v1`
- **WebSocket**: `ws://localhost:8000/ws/threats`

Configure the backend URL in Settings if different.

## Keyboard Shortcuts

- `Ctrl+Q` - Quit application
- `Ctrl+R` - Refresh threats
- `Ctrl+S` - Start quick scan

## Requirements

- Python 3.8+
- PyQt5
- Active internet connection
- CyberGuard backend API running

## Troubleshooting

### Application won't start
```powershell
# Reinstall PyQt5
pip uninstall PyQt5
pip install PyQt5==5.15.10
```

### Can't connect to backend
1. Check backend is running: `python backend/app/main.py`
2. Verify API URL in Settings tab
3. Check firewall settings

### System tray icon not showing
- This is a PyQt5 limitation on some Windows versions
- Application still works normally

## Building for Distribution

### Create Windows Installer
```powershell
# Install NSIS (Nullsoft Scriptable Install System)
# Then create installer script

pyinstaller --onefile --windowed ^
  --name="CyberGuard Desktop" ^
  --icon=icon.ico ^
  --add-data="assets;assets" ^
  cyberguard_desktop.py
```

## License

© 2025 CyberGuard Industries - All Rights Reserved
