# CyberGuard Enterprise Platform - Multi-Platform Application Suite

Complete cybersecurity platform with Web, Mobile, and Desktop applications.

## 🌐 Platform Overview

### 1. Web Application (React)
- **Technology**: React 18, TypeScript, Material-UI
- **Features**: Dashboard, Threat Monitoring, Analytics, Payment Portal
- **Deployment**: Vercel, Netlify, AWS Amplify

### 2. Mobile Application (React Native)
- **Platforms**: iOS, Android
- **Features**: Real-time Alerts, Threat Monitoring, Push Notifications
- **Deployment**: App Store, Google Play

### 3. Desktop Application (Electron)
- **Platform**: Windows, macOS, Linux
- **Features**: System Tray, Local Protection, File Scanning
- **Deployment**: Standalone installers

### 4. Backend API (FastAPI)
- **Technology**: Python FastAPI, PostgreSQL, Redis
- **Features**: REST API, WebSocket, Authentication, Payment Processing
- **Deployment**: Docker, Kubernetes, AWS/Azure

---

## 📁 Project Structure

```
cyberguard-platform/
├── web/                          # React Web Application
│   ├── public/
│   ├── src/
│   │   ├── components/          # Reusable components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API services
│   │   ├── hooks/               # Custom hooks
│   │   ├── store/               # State management (Redux)
│   │   └── App.tsx
│   ├── package.json
│   └── tsconfig.json
│
├── mobile/                       # React Native Mobile App
│   ├── android/                 # Android specific
│   ├── ios/                     # iOS specific
│   ├── src/
│   │   ├── screens/             # Screen components
│   │   ├── components/          # Reusable components
│   │   ├── navigation/          # Navigation setup
│   │   ├── services/            # API services
│   │   └── App.tsx
│   ├── package.json
│   └── app.json
│
├── desktop/                      # Electron Desktop App
│   ├── main/                    # Main process
│   ├── renderer/                # Renderer process (React)
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.tsx
│   ├── package.json
│   └── electron-builder.yml
│
├── backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── api/                 # API routes
│   │   ├── core/                # Core functionality
│   │   ├── models/              # Database models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── shared/                       # Shared code/types
│   └── types/                   # TypeScript types
│
└── docs/                        # Documentation
    ├── WEB_APP.md
    ├── MOBILE_APP.md
    ├── DESKTOP_APP.md
    └── API.md
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- React Native development environment (for mobile)
- Docker (optional)

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

Backend runs on: http://localhost:8000

### 2. Web Application Setup

```bash
# Navigate to web app
cd web

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with API URL

# Start development server
npm start
```

Web app runs on: http://localhost:3000

### 3. Mobile Application Setup

```bash
# Navigate to mobile app
cd mobile

# Install dependencies
npm install

# iOS setup (macOS only)
cd ios && pod install && cd ..

# Start Metro bundler
npm start

# Run on iOS
npm run ios

# Run on Android
npm run android
```

### 4. Desktop Application Setup

```bash
# Navigate to desktop app
cd desktop

# Install dependencies
npm install

# Start development
npm run dev

# Build for Windows
npm run build:win
```

---

## 🎨 Technology Stack

### Web Application
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Material-UI (MUI)** - Component library
- **Redux Toolkit** - State management
- **React Router** - Navigation
- **Chart.js** - Data visualization
- **Axios** - HTTP client
- **Socket.io Client** - Real-time updates

### Mobile Application
- **React Native** - Cross-platform framework
- **TypeScript** - Type safety
- **React Navigation** - Navigation
- **Redux Toolkit** - State management
- **React Native Paper** - UI components
- **Axios** - HTTP client
- **React Native Push Notification** - Push notifications

### Desktop Application
- **Electron** - Desktop framework
- **React** - UI framework
- **TypeScript** - Type safety
- **Material-UI** - Component library
- **IPC** - Inter-process communication
- **Auto-updater** - Automatic updates

### Backend API
- **FastAPI** - Web framework
- **PostgreSQL** - Database
- **Redis** - Caching & sessions
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **JWT** - Authentication
- **WebSocket** - Real-time communication
- **Celery** - Background tasks

---

## 🔑 Key Features

### Web Application Features
✅ User authentication (login, register, 2FA)
✅ Dashboard with threat overview
✅ Real-time threat monitoring
✅ Threat analytics & reports
✅ User management
✅ Payment & subscription management
✅ License activation
✅ Settings & configuration
✅ Dark/light theme
✅ Responsive design

### Mobile Application Features
✅ Push notifications for threats
✅ Real-time threat alerts
✅ Dashboard overview
✅ Quick actions
✅ Biometric authentication
✅ Offline mode
✅ Settings sync
✅ Location-based features

### Desktop Application Features
✅ System tray integration
✅ Real-time file scanning
✅ Local threat detection
✅ Automatic updates
✅ Background protection
✅ Windows notifications
✅ Quick access menu
✅ Resource monitoring

### Backend API Features
✅ RESTful API
✅ WebSocket for real-time updates
✅ JWT authentication
✅ Role-based access control (RBAC)
✅ Rate limiting
✅ API versioning
✅ Payment processing integration
✅ License management
✅ Threat intelligence feeds
✅ ML model serving
✅ Background job processing

---

## 🔒 Security Features

### Authentication & Authorization
- JWT with refresh tokens
- Password hashing (bcrypt)
- 2FA support (TOTP)
- Session management
- API key authentication
- OAuth2 integration (Google, GitHub)

### Data Security
- HTTPS/TLS encryption
- Data encryption at rest
- Secure password storage
- CORS configuration
- CSRF protection
- SQL injection prevention

### API Security
- Rate limiting
- Input validation
- API versioning
- Request signing
- IP whitelisting (optional)

---

## 📱 API Endpoints

### Authentication
```
POST   /api/v1/auth/register          # Register new user
POST   /api/v1/auth/login             # Login
POST   /api/v1/auth/refresh           # Refresh token
POST   /api/v1/auth/logout            # Logout
GET    /api/v1/auth/me                # Get current user
```

### Threats
```
GET    /api/v1/threats                # List threats
GET    /api/v1/threats/{id}           # Get threat details
POST   /api/v1/threats/scan           # Trigger scan
GET    /api/v1/threats/stats          # Get statistics
```

### Users
```
GET    /api/v1/users                  # List users (admin)
GET    /api/v1/users/{id}             # Get user
PUT    /api/v1/users/{id}             # Update user
DELETE /api/v1/users/{id}             # Delete user
```

### Payments
```
GET    /api/v1/payments               # List payments
POST   /api/v1/payments/checkout      # Create checkout
GET    /api/v1/payments/subscriptions # Get subscriptions
POST   /api/v1/payments/cancel        # Cancel subscription
```

### Licenses
```
GET    /api/v1/licenses               # List licenses
POST   /api/v1/licenses/generate      # Generate license
POST   /api/v1/licenses/activate      # Activate license
GET    /api/v1/licenses/validate      # Validate license
```

### WebSocket
```
WS     /ws/threats                    # Real-time threat updates
WS     /ws/notifications              # Real-time notifications
```

---

## 🎯 Environment Variables

### Backend (.env)
```bash
# Application
APP_NAME=CyberGuard Enterprise Platform
APP_VERSION=1.0.0
DEBUG=false
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/cyberguard
REDIS_URL=redis://localhost:6379/0

# Authentication
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Payment
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password

# Storage
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=cyberguard-storage
```

### Web App (.env.local)
```bash
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WS_URL=ws://localhost:8000/ws
REACT_APP_STRIPE_PUBLIC_KEY=pk_test_...
```

### Mobile App (.env)
```bash
API_URL=http://localhost:8000/api/v1
WS_URL=ws://localhost:8000/ws
```

### Desktop App (.env)
```bash
MAIN_API_URL=http://localhost:8000/api/v1
WS_URL=ws://localhost:8000/ws
```

---

## 🚀 Deployment

### Web Application
**Vercel** (Recommended)
```bash
npm install -g vercel
cd web
vercel
```

**Netlify**
```bash
cd web
npm run build
netlify deploy --prod --dir=build
```

### Mobile Application
**iOS (App Store)**
```bash
cd mobile/ios
fastlane release
```

**Android (Google Play)**
```bash
cd mobile/android
./gradlew bundleRelease
```

### Desktop Application
**Windows**
```bash
cd desktop
npm run build:win
# Output: dist/CyberGuard-Setup-1.0.0.exe
```

### Backend API
**Docker**
```bash
cd backend
docker build -t cyberguard-api .
docker run -p 8000:8000 cyberguard-api
```

**Kubernetes**
```bash
kubectl apply -f k8s/
```

---

## 📊 Performance

### Targets
- **Web App**: First Contentful Paint < 1.5s
- **Mobile App**: Launch time < 2s
- **Desktop App**: Startup time < 1s
- **Backend API**: Response time < 100ms

### Optimization
- Code splitting (web)
- Lazy loading
- Image optimization
- Caching strategies
- Database indexing
- Connection pooling

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app tests/
```

### Web Tests
```bash
cd web
npm test
npm run test:coverage
```

### Mobile Tests
```bash
cd mobile
npm test
```

### Desktop Tests
```bash
cd desktop
npm test
```

---

## 📚 Documentation

- **Web App**: `docs/WEB_APP.md`
- **Mobile App**: `docs/MOBILE_APP.md`
- **Desktop App**: `docs/DESKTOP_APP.md`
- **Backend API**: `docs/API.md`
- **Deployment**: `docs/DEPLOYMENT.md`

---

## 🤝 Support

- **Documentation**: https://docs.cyberguard-platform.com
- **Email**: support@cyberguard-platform.com
- **Discord**: https://discord.gg/cyberguard

---

## 📄 License

MIT License - See LICENSE file

---

**Built with ❤️ by CyberGuard Industries**
