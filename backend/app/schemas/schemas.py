"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    subscription_plan: str
    subscription_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None

# Threat schemas
class ThreatBase(BaseModel):
    threat_type: str
    severity: str
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    description: Optional[str] = None

class ThreatCreate(ThreatBase):
    pass

class ThreatResponse(ThreatBase):
    id: int
    status: str
    detected_at: datetime
    user_id: int
    
    class Config:
        from_attributes = True

# License schemas
class LicenseBase(BaseModel):
    plan: str

class LicenseCreate(LicenseBase):
    max_devices: int = 1

class LicenseResponse(LicenseBase):
    id: int
    license_key: str
    is_active: bool
    activated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    max_devices: int
    devices_used: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# System metrics schemas
class SystemMetricCreate(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_traffic: float
    active_threats: int = 0
    blocked_threats: int = 0

class SystemMetricResponse(SystemMetricCreate):
    id: int
    recorded_at: datetime
    
    class Config:
        from_attributes = True
