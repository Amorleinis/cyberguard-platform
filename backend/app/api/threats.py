"""
Threats API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from ..core.database import get_db
from ..models.database import User, Threat
from ..schemas.schemas import ThreatCreate, ThreatResponse
from .auth import get_current_user

router = APIRouter(prefix="/threats", tags=["Threats"])


@router.get("/", response_model=List[ThreatResponse])
async def get_threats(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of threats for current user"""
    query = db.query(Threat).filter(Threat.user_id == current_user.id)
    
    if severity:
        query = query.filter(Threat.severity == severity)
    
    if status:
        query = query.filter(Threat.status == status)
    
    threats = query.order_by(desc(Threat.detected_at)).offset(skip).limit(limit).all()
    return threats


@router.get("/stats")
async def get_threat_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get threat statistics for current user"""
    total_threats = db.query(func.count(Threat.id)).filter(
        Threat.user_id == current_user.id
    ).scalar()
    
    active_threats = db.query(func.count(Threat.id)).filter(
        Threat.user_id == current_user.id,
        Threat.status == "active"
    ).scalar()
    
    blocked_threats = db.query(func.count(Threat.id)).filter(
        Threat.user_id == current_user.id,
        Threat.status == "blocked"
    ).scalar()
    
    critical_threats = db.query(func.count(Threat.id)).filter(
        Threat.user_id == current_user.id,
        Threat.severity == "critical"
    ).scalar()
    
    # Get counts by severity
    severity_counts = db.query(
        Threat.severity,
        func.count(Threat.id).label('count')
    ).filter(
        Threat.user_id == current_user.id
    ).group_by(Threat.severity).all()
    
    # Get counts by type
    type_counts = db.query(
        Threat.threat_type,
        func.count(Threat.id).label('count')
    ).filter(
        Threat.user_id == current_user.id
    ).group_by(Threat.threat_type).all()
    
    return {
        "total_threats": total_threats or 0,
        "active_threats": active_threats or 0,
        "blocked_threats": blocked_threats or 0,
        "critical_threats": critical_threats or 0,
        "detection_rate": round((blocked_threats / total_threats * 100) if total_threats > 0 else 0, 1),
        "by_severity": {item.severity: item.count for item in severity_counts},
        "by_type": {item.threat_type: item.count for item in type_counts}
    }


@router.get("/{threat_id}", response_model=ThreatResponse)
async def get_threat(
    threat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific threat by ID"""
    threat = db.query(Threat).filter(
        Threat.id == threat_id,
        Threat.user_id == current_user.id
    ).first()
    
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    
    return threat


@router.post("/", response_model=ThreatResponse, status_code=201)
async def create_threat(
    threat_data: ThreatCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new threat (typically called by detection engines)"""
    threat = Threat(
        user_id=current_user.id,
        **threat_data.model_dump()
    )
    
    db.add(threat)
    db.commit()
    db.refresh(threat)
    
    return threat


@router.patch("/{threat_id}/status")
async def update_threat_status(
    threat_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update threat status (e.g., block, resolve, investigate)"""
    threat = db.query(Threat).filter(
        Threat.id == threat_id,
        Threat.user_id == current_user.id
    ).first()
    
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    
    threat.status = status
    
    if status == "resolved":
        from datetime import datetime
        threat.resolved_at = datetime.now()
    
    db.commit()
    
    return {"message": "Threat status updated", "threat_id": threat_id, "status": status}


@router.delete("/{threat_id}")
async def delete_threat(
    threat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a threat"""
    threat = db.query(Threat).filter(
        Threat.id == threat_id,
        Threat.user_id == current_user.id
    ).first()
    
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    
    db.delete(threat)
    db.commit()
    
    return {"message": "Threat deleted", "threat_id": threat_id}
