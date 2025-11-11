"""
Database models for CyberGuard Platform
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Subscription info
    subscription_plan = Column(String, default="free")  # free, professional, enterprise
    subscription_status = Column(String, default="active")
    subscription_expires_at = Column(DateTime)
    
    # API key
    api_key = Column(String, unique=True, index=True)
    
    # Relationships
    threats = relationship("Threat", back_populates="user")
    licenses = relationship("License", back_populates="user")

class Threat(Base):
    """Threat detection model"""
    __tablename__ = "threats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Threat details
    threat_type = Column(String, index=True)  # malware, phishing, ransomware, etc.
    severity = Column(String, index=True)  # critical, high, medium, low
    status = Column(String, default="detected")  # detected, blocked, quarantined, resolved
    
    # Source information
    source_ip = Column(String)
    destination_ip = Column(String)
    source_port = Column(Integer)
    destination_port = Column(Integer)
    
    # Additional details
    description = Column(Text)
    file_path = Column(String)
    process_name = Column(String)
    hash_value = Column(String)
    
    # Timestamps
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="threats")

class License(Base):
    """License key model"""
    __tablename__ = "licenses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # License details
    license_key = Column(String, unique=True, index=True, nullable=False)
    plan = Column(String)  # professional, enterprise, unlimited
    is_active = Column(Boolean, default=True)
    
    # Activation
    activated_at = Column(DateTime)
    expires_at = Column(DateTime)
    max_devices = Column(Integer, default=1)
    devices_used = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="licenses")

class SystemMetric(Base):
    """System metrics model"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Metrics
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_usage = Column(Float)
    network_traffic = Column(Float)
    active_threats = Column(Integer, default=0)
    blocked_threats = Column(Integer, default=0)
    
    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

class AuditLog(Base):
    """Audit log for security events"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Event details
    event_type = Column(String, index=True)  # login, logout, threat_detected, settings_changed
    event_description = Column(Text)
    ip_address = Column(String)
    user_agent = Column(String)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
