"""
Database initialization script
Creates tables and seeds initial data
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import engine, Base, SessionLocal
from app.models.database import User, Threat, License, SystemMetric
from app.core.security import get_password_hash, generate_api_key
from datetime import datetime, timedelta
import argparse

def drop_tables():
    """Drop all tables"""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✓ Tables dropped")

def create_tables():
    """Create all tables"""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")

def seed_data():
    """Seed initial data"""
    print("Seeding initial data...")
    
    db = SessionLocal()
    
    try:
        # Create admin user
        admin = User(
            email="admin@cyberguard.com",
            username="admin",
            full_name="Administrator",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True,
            subscription_plan="enterprise",
            subscription_status="active",
            subscription_expires_at=datetime.utcnow() + timedelta(days=365),
            api_key=generate_api_key()
        )
        db.add(admin)
        
        # Create test user
        user = User(
            email="user@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_superuser=False,
            subscription_plan="professional",
            subscription_status="active",
            subscription_expires_at=datetime.utcnow() + timedelta(days=30),
            api_key=generate_api_key()
        )
        db.add(user)
        
        db.commit()
        
        # Create sample threats for demo
        threats = [
            Threat(
                user_id=1,
                threat_type="malware",
                severity="critical",
                status="blocked",
                source_ip="192.168.1.100",
                description="Trojan detected in download folder",
                detected_at=datetime.utcnow() - timedelta(hours=2)
            ),
            Threat(
                user_id=1,
                threat_type="phishing",
                severity="high",
                status="blocked",
                source_ip="203.0.113.45",
                description="Phishing attempt via email",
                detected_at=datetime.utcnow() - timedelta(hours=5)
            ),
            Threat(
                user_id=1,
                threat_type="ddos",
                severity="medium",
                status="monitoring",
                source_ip="198.51.100.23",
                description="Potential DDoS attack detected",
                detected_at=datetime.utcnow() - timedelta(minutes=30)
            )
        ]
        
        for threat in threats:
            db.add(threat)
        
        # Create sample license
        license = License(
            user_id=1,
            license_key="CGRD-ENT-" + generate_api_key()[:16].upper(),
            plan="enterprise",
            is_active=True,
            activated_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=365),
            max_devices=10,
            devices_used=1
        )
        db.add(license)
        
        db.commit()
        
        print(f"✓ Created admin user: admin@cyberguard.com (password: admin123)")
        print(f"✓ Created test user: user@example.com (password: password123)")
        print(f"✓ Created {len(threats)} sample threats")
        print(f"✓ Created enterprise license")
        
    except Exception as e:
        print(f"✗ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Initialize CyberGuard database")
    parser.add_argument("--drop", action="store_true", help="Drop existing tables")
    parser.add_argument("--seed", action="store_true", help="Seed initial data")
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("  CyberGuard Database Initialization")
    print("="*60 + "\n")
    
    if args.drop:
        response = input("Are you sure you want to drop all tables? (yes/no): ")
        if response.lower() == "yes":
            drop_tables()
        else:
            print("Aborted.")
            return
    
    create_tables()
    
    if args.seed:
        seed_data()
    
    print("\n" + "="*60)
    print("  Database initialization complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
