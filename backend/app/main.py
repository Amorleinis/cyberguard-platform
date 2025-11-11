"""
CyberGuard Enterprise Platform - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import json

# Create FastAPI app
app = FastAPI(
    title="CyberGuard Enterprise Platform API",
    description="Multi-platform cybersecurity threat detection and response system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "CyberGuard Enterprise Platform API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/api/docs",
            "health": "/health",
            "api": "/api/v1"
        }
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "operational",
            "database": "operational",
            "cache": "operational",
            "websocket": "operational"
        }
    }

# API v1 routes
from fastapi import APIRouter

api_v1_router = APIRouter(prefix="/api/v1")

# Authentication routes
@api_v1_router.post("/auth/register")
async def register(email: str, password: str, name: str):
    """Register new user"""
    return {
        "success": True,
        "message": "User registered successfully",
        "user": {
            "id": "usr_demo123",
            "email": email,
            "name": name,
            "created_at": datetime.now().isoformat()
        }
    }

@api_v1_router.post("/auth/login")
async def login(email: str, password: str):
    """User login"""
    return {
        "success": True,
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "refresh_token_here",
        "token_type": "bearer",
        "expires_in": 1800,
        "user": {
            "id": "usr_demo123",
            "email": email,
            "name": "Demo User",
            "role": "user"
        }
    }

@api_v1_router.get("/auth/me")
async def get_current_user():
    """Get current user info"""
    return {
        "id": "usr_demo123",
        "email": "user@example.com",
        "name": "Demo User",
        "role": "user",
        "subscription": "professional",
        "created_at": "2025-01-01T00:00:00Z"
    }

# Threat routes
@api_v1_router.get("/threats")
async def list_threats(limit: int = 10, offset: int = 0):
    """List detected threats"""
    threats = []
    for i in range(limit):
        threats.append({
            "id": f"thr_{i+offset+1:06d}",
            "type": ["malware", "phishing", "ransomware", "ddos"][i % 4],
            "severity": ["critical", "high", "medium", "low"][i % 4],
            "status": ["blocked", "quarantined", "monitoring"][i % 3],
            "source_ip": f"192.168.1.{100+i}",
            "detected_at": datetime.now().isoformat(),
            "description": f"Suspicious activity detected from IP address"
        })
    
    return {
        "threats": threats,
        "total": 1500,
        "limit": limit,
        "offset": offset
    }

@api_v1_router.get("/threats/stats")
async def threat_stats():
    """Get threat statistics"""
    return {
        "total_threats": 15234,
        "threats_today": 342,
        "threats_blocked": 14891,
        "threats_quarantined": 267,
        "threats_monitoring": 76,
        "by_severity": {
            "critical": 1523,
            "high": 4872,
            "medium": 6234,
            "low": 2605
        },
        "by_type": {
            "malware": 5678,
            "phishing": 3421,
            "ransomware": 2134,
            "ddos": 1876,
            "other": 2125
        },
        "detection_rate": 95.7,
        "false_positive_rate": 2.3
    }

# Dashboard routes
@api_v1_router.get("/dashboard")
async def get_dashboard():
    """Get dashboard overview"""
    return {
        "overview": {
            "total_threats": 15234,
            "threats_today": 342,
            "active_threats": 12,
            "blocked_threats": 14891
        },
        "realtime": {
            "cpu_usage": 34.5,
            "memory_usage": 42.1,
            "network_traffic": 156.7,
            "active_connections": 1247
        },
        "recent_threats": [
            {
                "id": "thr_000001",
                "type": "malware",
                "severity": "critical",
                "source_ip": "192.168.1.100",
                "detected_at": datetime.now().isoformat()
            }
        ]
    }

# User routes
@api_v1_router.get("/users")
async def list_users():
    """List all users (admin only)"""
    return {
        "users": [
            {
                "id": "usr_000001",
                "email": "admin@cyberguard.com",
                "name": "Admin User",
                "role": "admin",
                "subscription": "unlimited",
                "created_at": "2025-01-01T00:00:00Z"
            }
        ],
        "total": 1
    }

# Payment routes
@api_v1_router.get("/payments/subscriptions")
async def get_subscriptions():
    """Get user subscriptions"""
    return {
        "subscriptions": [
            {
                "id": "sub_demo123",
                "plan": "professional",
                "status": "active",
                "amount": 499.00,
                "currency": "USD",
                "interval": "month",
                "current_period_start": "2025-01-01T00:00:00Z",
                "current_period_end": "2025-02-01T00:00:00Z",
                "cancel_at_period_end": False
            }
        ]
    }

@api_v1_router.post("/payments/checkout")
async def create_checkout(plan: str, interval: str = "month"):
    """Create payment checkout session"""
    return {
        "success": True,
        "checkout_url": "https://checkout.stripe.com/pay/...",
        "session_id": "cs_demo123",
        "plan": plan,
        "amount": 499.00 if plan == "professional" else 2999.00
    }

# License routes
@api_v1_router.post("/licenses/generate")
async def generate_license(plan: str, email: str):
    """Generate new license key"""
    import hashlib
    import time
    
    # Generate license key
    key_data = f"{plan}:{email}:{time.time()}"
    key_hash = hashlib.md5(key_data.encode()).hexdigest()
    license_key = f"CGEP-{key_hash[:4].upper()}-{key_hash[4:8].upper()}-{key_hash[8:12].upper()}-{key_hash[12:16].upper()}"
    
    return {
        "success": True,
        "license_key": license_key,
        "plan": plan,
        "email": email,
        "generated_at": datetime.now().isoformat(),
        "expires_at": None,
        "max_activations": 10 if plan == "professional" else -1
    }

@api_v1_router.post("/licenses/activate")
async def activate_license(license_key: str, machine_id: str):
    """Activate license on machine"""
    return {
        "success": True,
        "message": "License activated successfully",
        "license_key": license_key,
        "machine_id": machine_id,
        "activated_at": datetime.now().isoformat()
    }

# Settings routes
@api_v1_router.get("/settings")
async def get_settings():
    """Get user settings"""
    return {
        "notifications": {
            "email_alerts": True,
            "push_notifications": True,
            "sms_alerts": False
        },
        "security": {
            "two_factor_enabled": False,
            "auto_block_threats": True,
            "quarantine_suspicious": True
        },
        "preferences": {
            "theme": "dark",
            "language": "en",
            "timezone": "America/New_York"
        }
    }

@api_v1_router.put("/settings")
async def update_settings(settings: dict):
    """Update user settings"""
    return {
        "success": True,
        "message": "Settings updated successfully",
        "settings": settings
    }

# Include API router
app.include_router(api_v1_router)

# WebSocket endpoint for real-time threat updates
@app.websocket("/ws/threats")
async def websocket_threats(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send threat updates every 5 seconds
            import asyncio
            await asyncio.sleep(5)
            
            threat_update = {
                "type": "threat_detected",
                "threat": {
                    "id": f"thr_{int(datetime.now().timestamp())}",
                    "type": "malware",
                    "severity": "high",
                    "source_ip": "192.168.1.100",
                    "detected_at": datetime.now().isoformat()
                }
            }
            
            await manager.send_personal_message(json.dumps(threat_update), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# WebSocket endpoint for notifications
@app.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url)
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🛡️  CYBERGUARD ENTERPRISE PLATFORM - API SERVER")
    print("="*70)
    print("\nAPI Server:    http://localhost:8000")
    print("API Docs:      http://localhost:8000/api/docs")
    print("Health Check:  http://localhost:8000/health")
    print("WebSocket:     ws://localhost:8000/ws/threats")
    print("\nPress Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
