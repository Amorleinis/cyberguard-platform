# CyberGuard Enterprise Platform - Quick Start Guide

## 🚀 One-Command Launch

Launch all platform components with a single command:

```powershell
.\start-platform.ps1
```

This will automatically start:
- ✅ Backend API (FastAPI)
- ✅ Web Application (Dashboard)
- ✅ Desktop Application (PyQt5)

> Prereq: Use Python 3.11. Create and activate the venv, then copy `.env.example` to `.env` before the first run:
> ```powershell
> py -3.11 -m venv .venv
> .\.venv\Scripts\Activate.ps1
> copy .env.example .env
> pip install -r backend\requirements.txt
> pip install -r desktop\requirements.txt
> ```

> Optional: Seed an admin user (uses env vars ADMIN_EMAIL/ADMIN_PASSWORD):
> ```powershell
> cd backend\scripts
> ..\..\.venv\Scripts\python seed_admin.py
> ```

### Backend + Postgres via Docker Compose
- Copy `.env.example` to `.env` and set `SECRET_KEY`, `DATABASE_URL` (e.g., `postgresql+psycopg2://cyberguard:cyberguard@db:5432/cyberguard`), `CORS_ALLOW_ORIGINS`
- Bring up services: `docker compose -f docker-compose.backend.yml up --build`
- Seed admin in container: `docker compose -f docker-compose.backend.yml exec backend python scripts/seed_admin.py`
- Health: http://localhost:8000/health | Docs: http://localhost:8000/api/docs

## 📦 Individual Components

### Backend API
```powershell
cd backend
..\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
- **URL**: http://localhost:8000
- **Docs**: http://localhost:8000/api/docs

### Web Application
```powershell
cd web
python -m http.server 3000
```
- **URL**: http://localhost:3000
- **Login**: Any credentials (demo mode)

### Desktop Application
```powershell
cd desktop
python cyberguard_desktop.py
```
- **GUI**: PyQt5 window + system tray

## 🛠️ First Time Setup

### Install Backend Dependencies
```powershell
cd backend
pip install -r requirements.txt
```

### Install Desktop Dependencies
```powershell
cd desktop
pip install -r requirements.txt
```

## 📚 Platform Architecture

```
CyberGuard Platform
├── Backend API (FastAPI)
│   ├── REST API endpoints
│   ├── WebSocket for real-time updates
│   ├── JWT authentication
│   └── Database integration
│
├── Web Application (HTML/CSS/JS)
│   ├── Dashboard with live stats
│   ├── Threat monitoring
│   ├── Protection controls
│   └── Settings management
│
└── Desktop Application (PyQt5)
    ├── System tray integration
    ├── Real-time monitoring
    ├── Local threat scanning
    └── Background protection
```

## 🔧 Configuration

### Backend API Settings
Edit `backend/app/main.py`:
```python
# Change port
uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Web Application Settings
In the web app Settings tab:
- Configure Backend API URL
- Default: http://localhost:8000

### Desktop Application Settings
In the desktop app Settings tab:
- Configure Backend API URL
- Default: http://localhost:8000

## 🌐 Access URLs

| Component | URL | Description |
|-----------|-----|-------------|
| Backend API | http://localhost:8000 | REST API server |
| API Docs | http://localhost:8000/api/docs | Swagger UI |
| Web App | http://localhost:3000 | Dashboard |
| WebSocket | ws://localhost:8000/ws/threats | Real-time updates |

## ✨ Features

### Backend API
- 20+ REST endpoints
- WebSocket real-time updates
- JWT authentication structure
- Payment integration
- License management
- Threat detection APIs

### Web Application
- Modern dark-themed UI
- Real-time dashboard
- Threat monitoring
- System resource meters
- Protection toggles
- Payment portal
- Settings management

### Desktop Application
- System tray integration
- Real-time threat alerts
- CPU/Memory/Disk monitoring
- Quick & full scans
- Protection controls
- Background monitoring

## 🔒 Security

### Demo Mode
- Web app accepts any login credentials
- Desktop app connects without auth
- Backend API is open (add JWT later)

### Production Setup
1. Configure PostgreSQL database
2. Enable JWT authentication
3. Set up HTTPS/TLS
4. Configure environment variables
5. Enable CORS restrictions

## 📱 Mobile Application (Coming Soon)

React Native mobile app for iOS/Android:
- Push notifications
- Biometric authentication
- Real-time threat alerts
- Remote monitoring

## 🧪 Testing

### Test Backend API
```powershell
# Health check
curl http://localhost:8000/health

# Get dashboard data
curl http://localhost:8000/api/v1/dashboard

# Get threats
curl http://localhost:8000/api/v1/threats
```

### Test WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/threats');
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process by PID
taskkill /PID <PID> /F
```

### Backend Won't Start
```powershell
# Reinstall dependencies
pip install --upgrade -r backend/requirements.txt
```

### Desktop App Won't Launch
```powershell
# Reinstall PyQt5
pip uninstall PyQt5
pip install PyQt5==5.15.10
```

### WebSocket Connection Failed
1. Make sure backend is running
2. Check firewall settings
3. Verify WebSocket URL in settings

## 📊 Development Roadmap

- [x] Backend API (FastAPI)
- [x] Web Application
- [x] Desktop Application
- [ ] Mobile Application (React Native)
- [ ] Database Integration (PostgreSQL)
- [ ] JWT Authentication
- [ ] Payment Processing
- [ ] Production Deployment

## 📄 License

© 2025 CyberGuard Industries - All Rights Reserved

## 🤝 Support

For issues or questions:
- Email: lance.ceo@cyberguard.industries
- Phone: (515) 445-8147
