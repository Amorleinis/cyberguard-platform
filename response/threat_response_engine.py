"""
Threat Response Module

This module provides comprehensive threat response capabilities including:
- Automated incident response workflows
- Manual response playbook execution
- Evidence collection and forensics
- Stakeholder communication and notifications
- Response action tracking and documentation
- Integration with SOAR platforms
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import sqlite3
from collections import defaultdict
from enum import Enum
import asyncio
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IncidentStatus(Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"

class ResponseAction(Enum):
    ISOLATE = "isolate"
    BLOCK = "block"
    COLLECT_EVIDENCE = "collect_evidence"
    NOTIFY = "notify"
    ESCALATE = "escalate"
    INVESTIGATE = "investigate"
    REMEDIATE = "remediate"
    DOCUMENT = "document"

class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class Incident:
    """Security incident record"""
    incident_id: str
    title: str
    description: str
    severity: str
    priority: Priority
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[str]
    alert_ids: List[str]
    affected_assets: List[str]
    iocs: List[str]
    mitre_tactics: List[str]
    mitre_techniques: List[str]
    timeline: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    response_actions: List[Dict[str, Any]]
    stakeholders_notified: List[str]
    estimated_impact: str
    containment_status: str
    resolution_summary: Optional[str]
    lessons_learned: Optional[str]

@dataclass
class ResponsePlaybook:
    """Incident response playbook"""
    playbook_id: str
    name: str
    description: str
    trigger_conditions: Dict[str, Any]
    steps: List[Dict[str, Any]]
    estimated_duration: int  # minutes
    required_roles: List[str]
    automation_level: str  # manual, semi-automated, automated
    success_criteria: List[str]
    created_at: datetime
    updated_at: datetime
    usage_count: int
    success_rate: float

@dataclass
class ResponseAction:
    """Individual response action"""
    action_id: str
    incident_id: str
    action_type: str
    description: str
    assigned_to: str
    status: str  # pending, in_progress, completed, failed
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_duration: int  # minutes
    actual_duration: Optional[int]
    prerequisites: List[str]
    outputs: Dict[str, Any]
    automation_script: Optional[str]
    manual_instructions: Optional[str]

@dataclass
class Evidence:
    """Digital evidence collected during incident response"""
    evidence_id: str
    incident_id: str
    evidence_type: str  # log, file, memory_dump, network_capture, screenshot
    source_system: str
    collection_method: str
    file_path: str
    file_hash: str
    file_size: int
    collected_at: datetime
    collected_by: str
    chain_of_custody: List[Dict[str, Any]]
    analysis_results: Optional[Dict[str, Any]]

@dataclass
class Stakeholder:
    """Incident stakeholder"""
    stakeholder_id: str
    name: str
    role: str
    email: str
    phone: Optional[str]
    notification_preferences: Dict[str, bool]
    escalation_threshold: str
    alternate_contacts: List[str]

class ThreatResponseEngine:
    """
    Threat Response Engine
    
    Manages the complete incident response lifecycle including:
    - Incident creation and tracking
    - Response playbook execution
    - Evidence collection and forensics
    - Stakeholder communication
    - Response action automation
    """
    
    def __init__(self, data_dir: str = "../../../", config_path: str = None):
        self.data_dir = Path(data_dir)
        self.config_path = config_path
        
        # Initialize local storage
        self.db_path = self.data_dir / "threat_response.db"
        self._init_local_db()
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize response components
        self.incidents = {}
        self.playbooks = {}
        self.stakeholders = {}
        self.active_responses = {}
        
        # Load existing data
        self._load_response_data()
        
        # Initialize default playbooks
        self._create_default_playbooks()
        
        logger.info("Threat Response Engine initialized")
    
    def _init_local_db(self):
        """Initialize local SQLite database for response data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Incidents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT UNIQUE NOT NULL,
                title TEXT,
                description TEXT,
                severity TEXT,
                priority TEXT,
                status TEXT,
                created_at TEXT,
                updated_at TEXT,
                assigned_to TEXT,
                alert_ids_json TEXT,
                affected_assets_json TEXT,
                iocs_json TEXT,
                mitre_tactics_json TEXT,
                mitre_techniques_json TEXT,
                timeline_json TEXT,
                evidence_json TEXT,
                response_actions_json TEXT,
                stakeholders_notified_json TEXT,
                estimated_impact TEXT,
                containment_status TEXT,
                resolution_summary TEXT,
                lessons_learned TEXT
            )
        ''')
        
        # Playbooks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playbooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playbook_id TEXT UNIQUE NOT NULL,
                name TEXT,
                description TEXT,
                trigger_conditions_json TEXT,
                steps_json TEXT,
                estimated_duration INTEGER,
                required_roles_json TEXT,
                automation_level TEXT,
                success_criteria_json TEXT,
                created_at TEXT,
                updated_at TEXT,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0
            )
        ''')
        
        # Response actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS response_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_id TEXT UNIQUE NOT NULL,
                incident_id TEXT,
                action_type TEXT,
                description TEXT,
                assigned_to TEXT,
                status TEXT,
                created_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                estimated_duration INTEGER,
                actual_duration INTEGER,
                prerequisites_json TEXT,
                outputs_json TEXT,
                automation_script TEXT,
                manual_instructions TEXT
            )
        ''')
        
        # Evidence table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evidence_id TEXT UNIQUE NOT NULL,
                incident_id TEXT,
                evidence_type TEXT,
                source_system TEXT,
                collection_method TEXT,
                file_path TEXT,
                file_hash TEXT,
                file_size INTEGER,
                collected_at TEXT,
                collected_by TEXT,
                chain_of_custody_json TEXT,
                analysis_results_json TEXT
            )
        ''')
        
        # Stakeholders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stakeholders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stakeholder_id TEXT UNIQUE NOT NULL,
                name TEXT,
                role TEXT,
                email TEXT,
                phone TEXT,
                notification_preferences_json TEXT,
                escalation_threshold TEXT,
                alternate_contacts_json TEXT
            )
        ''')
        
        # Communication log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS communication_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT,
                communication_type TEXT,
                recipient TEXT,
                subject TEXT,
                content TEXT,
                sent_at TEXT,
                delivery_status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load response configuration"""
        default_config = {
            'sla_times': {
                'critical': 15,  # minutes to respond
                'high': 60,
                'medium': 240,
                'low': 1440
            },
            'escalation_thresholds': {
                'critical': 30,  # minutes before escalation
                'high': 120,
                'medium': 480,
                'low': 2880
            },
            'notification_settings': {
                'email_enabled': True,
                'sms_enabled': False,
                'webhook_enabled': True,
                'slack_enabled': False
            },
            'evidence_collection': {
                'auto_collect_logs': True,
                'auto_collect_memory': False,
                'auto_collect_network': True,
                'retention_days': 365
            },
            'automation_settings': {
                'auto_isolate_critical': True,
                'auto_block_iocs': True,
                'auto_collect_evidence': True,
                'require_approval_for': ['system_shutdown', 'network_isolation']
            },
            'integration': {
                'soar_platform': None,
                'ticketing_system': None,
                'chat_platform': None
            }
        }
        
        # Load user configuration if available
        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config file: {e}")
        
        return default_config
    
    def _load_response_data(self):
        """Load existing response data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Load incidents
            incidents_df = pd.read_sql_query("SELECT * FROM incidents", conn)
            for _, row in incidents_df.iterrows():
                incident = Incident(
                    incident_id=row['incident_id'],
                    title=row['title'],
                    description=row['description'],
                    severity=row['severity'],
                    priority=Priority(row['priority']),
                    status=IncidentStatus(row['status']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    assigned_to=row['assigned_to'],
                    alert_ids=json.loads(row['alert_ids_json'] or '[]'),
                    affected_assets=json.loads(row['affected_assets_json'] or '[]'),
                    iocs=json.loads(row['iocs_json'] or '[]'),
                    mitre_tactics=json.loads(row['mitre_tactics_json'] or '[]'),
                    mitre_techniques=json.loads(row['mitre_techniques_json'] or '[]'),
                    timeline=json.loads(row['timeline_json'] or '[]'),
                    evidence=json.loads(row['evidence_json'] or '[]'),
                    response_actions=json.loads(row['response_actions_json'] or '[]'),
                    stakeholders_notified=json.loads(row['stakeholders_notified_json'] or '[]'),
                    estimated_impact=row['estimated_impact'] or '',
                    containment_status=row['containment_status'] or 'pending',
                    resolution_summary=row['resolution_summary'],
                    lessons_learned=row['lessons_learned']
                )
                self.incidents[row['incident_id']] = incident
            
            # Load playbooks
            playbooks_df = pd.read_sql_query("SELECT * FROM playbooks", conn)
            for _, row in playbooks_df.iterrows():
                playbook = ResponsePlaybook(
                    playbook_id=row['playbook_id'],
                    name=row['name'],
                    description=row['description'],
                    trigger_conditions=json.loads(row['trigger_conditions_json'] or '{}'),
                    steps=json.loads(row['steps_json'] or '[]'),
                    estimated_duration=row['estimated_duration'],
                    required_roles=json.loads(row['required_roles_json'] or '[]'),
                    automation_level=row['automation_level'],
                    success_criteria=json.loads(row['success_criteria_json'] or '[]'),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    usage_count=row['usage_count'],
                    success_rate=row['success_rate']
                )
                self.playbooks[row['playbook_id']] = playbook
            
            # Load stakeholders
            stakeholders_df = pd.read_sql_query("SELECT * FROM stakeholders", conn)
            for _, row in stakeholders_df.iterrows():
                stakeholder = Stakeholder(
                    stakeholder_id=row['stakeholder_id'],
                    name=row['name'],
                    role=row['role'],
                    email=row['email'],
                    phone=row['phone'],
                    notification_preferences=json.loads(row['notification_preferences_json'] or '{}'),
                    escalation_threshold=row['escalation_threshold'],
                    alternate_contacts=json.loads(row['alternate_contacts_json'] or '[]')
                )
                self.stakeholders[row['stakeholder_id']] = stakeholder
            
            conn.close()
            logger.info(f"Loaded {len(self.incidents)} incidents and {len(self.playbooks)} playbooks")
            
        except Exception as e:
            logger.error(f"Error loading response data: {e}")
    
    def create_incident_from_alert(self, alert_data: Dict[str, Any]) -> str:
        """
        Create incident from threat alert
        
        Args:
            alert_data: Alert information dictionary
            
        Returns:
            Incident ID
        """
        incident_id = f"INC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Determine priority based on severity and confidence
        priority = self._calculate_incident_priority(alert_data)
        
        # Extract relevant information from alert
        affected_assets = alert_data.get('affected_assets', [])
        iocs = alert_data.get('indicators', [])
        mitre_tactics = alert_data.get('mitre_tactics', [])
        mitre_techniques = alert_data.get('mitre_techniques', [])
        
        # Create incident
        incident = Incident(
            incident_id=incident_id,
            title=f"Security Incident: {alert_data.get('title', 'Unknown Threat')}",
            description=alert_data.get('description', ''),
            severity=alert_data.get('severity', 'Medium'),
            priority=priority,
            status=IncidentStatus.NEW,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            assigned_to=None,
            alert_ids=[alert_data.get('alert_id', '')],
            affected_assets=affected_assets,
            iocs=iocs,
            mitre_tactics=mitre_tactics,
            mitre_techniques=mitre_techniques,
            timeline=[{
                'timestamp': datetime.now().isoformat(),
                'event': 'incident_created',
                'description': 'Incident created from threat alert',
                'user': 'system'
            }],
            evidence=[],
            response_actions=[],
            stakeholders_notified=[],
            estimated_impact=alert_data.get('estimated_impact', 'Unknown'),
            containment_status='pending',
            resolution_summary=None,
            lessons_learned=None
        )
        
        # Store incident
        self.incidents[incident_id] = incident
        self._cache_incident(incident)
        
        # Auto-assign based on severity
        if priority in [Priority.CRITICAL, Priority.HIGH]:
            self._auto_assign_incident(incident_id)
        
        # Trigger initial response
        self._trigger_initial_response(incident_id)
        
        # Send notifications
        self._notify_stakeholders(incident_id, 'incident_created')
        
        logger.info(f"Created incident {incident_id} from alert {alert_data.get('alert_id')}")
        return incident_id
    
    def execute_response_playbook(self, incident_id: str, playbook_id: str = None) -> bool:
        """
        Execute response playbook for incident
        
        Args:
            incident_id: Incident to respond to
            playbook_id: Specific playbook to use, or None for auto-selection
            
        Returns:
            Success status
        """
        if incident_id not in self.incidents:
            logger.error(f"Incident {incident_id} not found")
            return False
        
        incident = self.incidents[incident_id]
        
        # Select playbook if not specified
        if not playbook_id:
            playbook_id = self._select_playbook_for_incident(incident)
        
        if playbook_id not in self.playbooks:
            logger.error(f"Playbook {playbook_id} not found")
            return False
        
        playbook = self.playbooks[playbook_id]
        
        try:
            # Update incident status
            incident.status = IncidentStatus.IN_PROGRESS
            self._add_timeline_entry(incident_id, 'playbook_started', f'Started playbook: {playbook.name}')
            
            # Execute playbook steps
            for i, step in enumerate(playbook.steps):
                success = self._execute_playbook_step(incident_id, step, i)
                
                if not success and step.get('required', True):
                    logger.error(f"Required step {i} failed in playbook {playbook_id}")
                    return False
            
            # Update playbook statistics
            playbook.usage_count += 1
            playbook.success_rate = (playbook.success_rate * (playbook.usage_count - 1) + 1.0) / playbook.usage_count
            self._cache_playbook(playbook)
            
            # Update incident
            self._add_timeline_entry(incident_id, 'playbook_completed', f'Completed playbook: {playbook.name}')
            
            logger.info(f"Successfully executed playbook {playbook_id} for incident {incident_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error executing playbook {playbook_id}: {e}")
            self._add_timeline_entry(incident_id, 'playbook_failed', f'Playbook failed: {str(e)}')
            return False
    
    def collect_evidence(self, incident_id: str, evidence_type: str, 
                        source_system: str, collection_method: str = "automated") -> str:
        """
        Collect digital evidence for incident
        
        Args:
            incident_id: Incident ID
            evidence_type: Type of evidence to collect
            source_system: System to collect from
            collection_method: Method used for collection
            
        Returns:
            Evidence ID
        """
        evidence_id = f"EVD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Perform evidence collection based on type
        collection_result = self._perform_evidence_collection(
            evidence_type, source_system, collection_method
        )
        
        if not collection_result:
            logger.error(f"Failed to collect evidence from {source_system}")
            return None
        
        # Create evidence record
        evidence = Evidence(
            evidence_id=evidence_id,
            incident_id=incident_id,
            evidence_type=evidence_type,
            source_system=source_system,
            collection_method=collection_method,
            file_path=collection_result.get('file_path', ''),
            file_hash=collection_result.get('file_hash', ''),
            file_size=collection_result.get('file_size', 0),
            collected_at=datetime.now(),
            collected_by=collection_result.get('collected_by', 'system'),
            chain_of_custody=[{
                'timestamp': datetime.now().isoformat(),
                'action': 'collected',
                'user': collection_result.get('collected_by', 'system'),
                'notes': f'Evidence collected via {collection_method}'
            }],
            analysis_results=None
        )
        
        # Store evidence
        self._cache_evidence(evidence)
        
        # Update incident
        incident = self.incidents[incident_id]
        incident.evidence.append({
            'evidence_id': evidence_id,
            'type': evidence_type,
            'collected_at': datetime.now().isoformat()
        })
        
        self._add_timeline_entry(
            incident_id, 
            'evidence_collected', 
            f'Collected {evidence_type} evidence from {source_system}'
        )
        
        logger.info(f"Collected evidence {evidence_id} for incident {incident_id}")
        return evidence_id
    
    def escalate_incident(self, incident_id: str, escalation_reason: str) -> bool:
        """
        Escalate incident to higher tier
        
        Args:
            incident_id: Incident to escalate
            escalation_reason: Reason for escalation
            
        Returns:
            Success status
        """
        if incident_id not in self.incidents:
            logger.error(f"Incident {incident_id} not found")
            return False
        
        incident = self.incidents[incident_id]
        
        # Update incident status and priority
        incident.status = IncidentStatus.ESCALATED
        
        # Increase priority if possible
        if incident.priority == Priority.LOW:
            incident.priority = Priority.MEDIUM
        elif incident.priority == Priority.MEDIUM:
            incident.priority = Priority.HIGH
        elif incident.priority == Priority.HIGH:
            incident.priority = Priority.CRITICAL
        
        # Add to timeline
        self._add_timeline_entry(
            incident_id,
            'incident_escalated',
            f'Incident escalated: {escalation_reason}'
        )
        
        # Notify higher-tier stakeholders
        self._notify_escalation_stakeholders(incident_id, escalation_reason)
        
        # Re-assign to appropriate team
        self._auto_assign_incident(incident_id)
        
        logger.info(f"Escalated incident {incident_id}: {escalation_reason}")
        return True
    
    def resolve_incident(self, incident_id: str, resolution_summary: str,
                        lessons_learned: str = None) -> bool:
        """
        Resolve incident with summary and lessons learned
        
        Args:
            incident_id: Incident to resolve
            resolution_summary: Summary of resolution actions
            lessons_learned: Optional lessons learned
            
        Returns:
            Success status
        """
        if incident_id not in self.incidents:
            logger.error(f"Incident {incident_id} not found")
            return False
        
        incident = self.incidents[incident_id]
        
        # Update incident
        incident.status = IncidentStatus.RESOLVED
        incident.resolution_summary = resolution_summary
        incident.lessons_learned = lessons_learned
        incident.updated_at = datetime.now()
        
        # Add to timeline
        self._add_timeline_entry(
            incident_id,
            'incident_resolved',
            f'Incident resolved: {resolution_summary}'
        )
        
        # Generate incident report
        self._generate_incident_report(incident_id)
        
        # Notify stakeholders
        self._notify_stakeholders(incident_id, 'incident_resolved')
        
        # Update cache
        self._cache_incident(incident)
        
        logger.info(f"Resolved incident {incident_id}")
        return True
    
    def get_incident_metrics(self, time_period: int = 30) -> Dict[str, Any]:
        """
        Get incident response metrics for specified time period
        
        Args:
            time_period: Number of days to analyze
            
        Returns:
            Metrics dictionary
        """
        start_date = datetime.now() - timedelta(days=time_period)
        
        # Filter incidents by time period
        recent_incidents = [
            incident for incident in self.incidents.values()
            if incident.created_at >= start_date
        ]
        
        if not recent_incidents:
            return {'message': 'No incidents in time period'}
        
        # Calculate metrics
        total_incidents = len(recent_incidents)
        
        # Status distribution
        status_counts = {}
        for status in IncidentStatus:
            count = len([i for i in recent_incidents if i.status == status])
            status_counts[status.value] = count
        
        # Priority distribution
        priority_counts = {}
        for priority in Priority:
            count = len([i for i in recent_incidents if i.priority == priority])
            priority_counts[priority.value] = count
        
        # Response times
        resolved_incidents = [i for i in recent_incidents if i.status == IncidentStatus.RESOLVED]
        response_times = []
        
        for incident in resolved_incidents:
            resolution_time = None
            for entry in incident.timeline:
                if entry.get('event') == 'incident_resolved':
                    resolution_time = datetime.fromisoformat(entry['timestamp']) - incident.created_at
                    break
            
            if resolution_time:
                response_times.append(resolution_time.total_seconds() / 60)  # Convert to minutes
        
        # Calculate averages
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # SLA compliance
        sla_breaches = 0
        for incident in resolved_incidents:
            sla_time = self.config['sla_times'].get(incident.priority.value, 1440)
            
            for entry in incident.timeline:
                if entry.get('event') == 'incident_resolved':
                    resolution_time = datetime.fromisoformat(entry['timestamp']) - incident.created_at
                    if resolution_time.total_seconds() / 60 > sla_time:
                        sla_breaches += 1
                    break
        
        sla_compliance = (len(resolved_incidents) - sla_breaches) / len(resolved_incidents) * 100 if resolved_incidents else 100
        
        metrics = {
            'time_period_days': time_period,
            'total_incidents': total_incidents,
            'status_distribution': status_counts,
            'priority_distribution': priority_counts,
            'resolved_incidents': len(resolved_incidents),
            'average_response_time_minutes': round(avg_response_time, 2),
            'sla_compliance_percentage': round(sla_compliance, 2),
            'sla_breaches': sla_breaches,
            'escalation_rate': len([i for i in recent_incidents if i.status == IncidentStatus.ESCALATED]) / total_incidents * 100
        }
        
        return metrics
    
    # Helper methods
    
    def _create_default_playbooks(self):
        """Create default response playbooks"""
        
        # Malware Incident Response
        malware_playbook = {
            'playbook_id': 'PB_MALWARE_001',
            'name': 'Malware Incident Response',
            'description': 'Standard response for malware detection',
            'trigger_conditions': {
                'alert_types': ['malware', 'trojan', 'ransomware'],
                'severity': ['high', 'critical']
            },
            'steps': [
                {
                    'step': 1,
                    'name': 'Isolate Infected Systems',
                    'type': 'isolation',
                    'automation_level': 'automated',
                    'estimated_duration': 5,
                    'required': True
                },
                {
                    'step': 2,
                    'name': 'Collect Evidence',
                    'type': 'evidence_collection',
                    'automation_level': 'automated',
                    'estimated_duration': 15,
                    'required': True
                },
                {
                    'step': 3,
                    'name': 'Analyze Malware Sample',
                    'type': 'analysis',
                    'automation_level': 'manual',
                    'estimated_duration': 60,
                    'required': False
                },
                {
                    'step': 4,
                    'name': 'Remediate Systems',
                    'type': 'remediation',
                    'automation_level': 'semi-automated',
                    'estimated_duration': 30,
                    'required': True
                }
            ],
            'estimated_duration': 110,
            'required_roles': ['incident_responder', 'malware_analyst'],
            'automation_level': 'semi-automated',
            'success_criteria': [
                'All infected systems isolated',
                'Malware samples collected',
                'Systems successfully remediated'
            ]
        }
        
        # Create playbook
        self._create_playbook_from_dict(malware_playbook)
        
        # Data Breach Response
        breach_playbook = {
            'playbook_id': 'PB_BREACH_001',
            'name': 'Data Breach Response',
            'description': 'Response for potential data breach incidents',
            'trigger_conditions': {
                'alert_types': ['data_exfiltration', 'unauthorized_access'],
                'severity': ['medium', 'high', 'critical']
            },
            'steps': [
                {
                    'step': 1,
                    'name': 'Assess Scope of Breach',
                    'type': 'assessment',
                    'automation_level': 'manual',
                    'estimated_duration': 30,
                    'required': True
                },
                {
                    'step': 2,
                    'name': 'Preserve Evidence',
                    'type': 'evidence_collection',
                    'automation_level': 'automated',
                    'estimated_duration': 20,
                    'required': True
                },
                {
                    'step': 3,
                    'name': 'Notify Legal and Compliance',
                    'type': 'notification',
                    'automation_level': 'automated',
                    'estimated_duration': 10,
                    'required': True
                },
                {
                    'step': 4,
                    'name': 'Implement Containment',
                    'type': 'containment',
                    'automation_level': 'semi-automated',
                    'estimated_duration': 45,
                    'required': True
                }
            ],
            'estimated_duration': 105,
            'required_roles': ['incident_responder', 'legal_counsel', 'compliance_officer'],
            'automation_level': 'semi-automated',
            'success_criteria': [
                'Breach scope documented',
                'Evidence preserved',
                'Legal team notified',
                'Breach contained'
            ]
        }
        
        # Create playbook
        self._create_playbook_from_dict(breach_playbook)
    
    def _create_playbook_from_dict(self, playbook_data: Dict[str, Any]):
        """Create playbook from dictionary"""
        playbook = ResponsePlaybook(
            playbook_id=playbook_data['playbook_id'],
            name=playbook_data['name'],
            description=playbook_data['description'],
            trigger_conditions=playbook_data['trigger_conditions'],
            steps=playbook_data['steps'],
            estimated_duration=playbook_data['estimated_duration'],
            required_roles=playbook_data['required_roles'],
            automation_level=playbook_data['automation_level'],
            success_criteria=playbook_data['success_criteria'],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            usage_count=0,
            success_rate=0.0
        )
        
        self.playbooks[playbook_data['playbook_id']] = playbook
        self._cache_playbook(playbook)
    
    def _calculate_incident_priority(self, alert_data: Dict[str, Any]) -> Priority:
        """Calculate incident priority from alert data"""
        severity = alert_data.get('severity', '').lower()
        confidence = alert_data.get('confidence', 0.5)
        
        if severity == 'critical' and confidence > 0.8:
            return Priority.CRITICAL
        elif severity in ['critical', 'high'] and confidence > 0.6:
            return Priority.HIGH
        elif severity in ['medium', 'high'] and confidence > 0.4:
            return Priority.MEDIUM
        else:
            return Priority.LOW
    
    def _auto_assign_incident(self, incident_id: str):
        """Auto-assign incident based on priority and availability"""
        incident = self.incidents[incident_id]
        
        # Simple assignment logic - would integrate with team management system
        if incident.priority == Priority.CRITICAL:
            incident.assigned_to = "senior_responder_001"
        elif incident.priority == Priority.HIGH:
            incident.assigned_to = "responder_001"
        else:
            incident.assigned_to = "junior_responder_001"
        
        self._add_timeline_entry(
            incident_id,
            'incident_assigned',
            f'Incident assigned to {incident.assigned_to}'
        )
    
    def _trigger_initial_response(self, incident_id: str):
        """Trigger initial automated response actions"""
        incident = self.incidents[incident_id]
        
        # Auto-isolate for critical incidents
        if (incident.priority == Priority.CRITICAL and 
            self.config['automation_settings']['auto_isolate_critical']):
            
            for asset in incident.affected_assets:
                self._execute_isolation_action(asset)
        
        # Auto-block IOCs
        if self.config['automation_settings']['auto_block_iocs']:
            for ioc in incident.iocs:
                self._execute_block_action(ioc)
        
        # Auto-collect evidence
        if self.config['automation_settings']['auto_collect_evidence']:
            for asset in incident.affected_assets:
                self.collect_evidence(incident_id, 'logs', asset, 'automated')
    
    def _select_playbook_for_incident(self, incident: Incident) -> str:
        """Select appropriate playbook for incident"""
        
        # Check each playbook's trigger conditions
        for playbook_id, playbook in self.playbooks.items():
            conditions = playbook.trigger_conditions
            
            # Check alert types
            if 'alert_types' in conditions:
                # Simple keyword matching in incident title/description
                text = f"{incident.title} {incident.description}".lower()
                if not any(alert_type in text for alert_type in conditions['alert_types']):
                    continue
            
            # Check severity
            if 'severity' in conditions:
                if incident.severity.lower() not in conditions['severity']:
                    continue
            
            # Check MITRE tactics
            if 'mitre_tactics' in conditions:
                if not any(tactic in incident.mitre_tactics for tactic in conditions['mitre_tactics']):
                    continue
            
            # Playbook matches all conditions
            return playbook_id
        
        # Default fallback playbook
        return 'PB_GENERIC_001'
    
    def _execute_playbook_step(self, incident_id: str, step: Dict[str, Any], step_number: int) -> bool:
        """Execute individual playbook step"""
        
        step_type = step.get('type', 'manual')
        automation_level = step.get('automation_level', 'manual')
        
        try:
            if automation_level == 'automated':
                return self._execute_automated_step(incident_id, step)
            elif automation_level == 'semi-automated':
                return self._execute_semi_automated_step(incident_id, step)
            else:
                return self._execute_manual_step(incident_id, step)
                
        except Exception as e:
            logger.error(f"Error executing step {step_number}: {e}")
            return False
    
    def _execute_automated_step(self, incident_id: str, step: Dict[str, Any]) -> bool:
        """Execute automated step"""
        step_type = step.get('type')
        
        if step_type == 'isolation':
            incident = self.incidents[incident_id]
            for asset in incident.affected_assets:
                self._execute_isolation_action(asset)
                
        elif step_type == 'evidence_collection':
            incident = self.incidents[incident_id]
            for asset in incident.affected_assets:
                self.collect_evidence(incident_id, 'logs', asset, 'automated')
                
        elif step_type == 'notification':
            self._notify_stakeholders(incident_id, 'playbook_step')
            
        else:
            logger.warning(f"Unknown automated step type: {step_type}")
            return False
        
        return True
    
    def _execute_semi_automated_step(self, incident_id: str, step: Dict[str, Any]) -> bool:
        """Execute semi-automated step (requires approval)"""
        # In real implementation, would request approval and execute upon confirmation
        logger.info(f"Semi-automated step requires approval: {step.get('name')}")
        return True
    
    def _execute_manual_step(self, incident_id: str, step: Dict[str, Any]) -> bool:
        """Execute manual step (creates task for human)"""
        # Create task for manual execution
        logger.info(f"Manual step created: {step.get('name')}")
        
        # Add to incident timeline
        self._add_timeline_entry(
            incident_id,
            'manual_step_created',
            f"Manual step created: {step.get('name')}"
        )
        
        return True
    
    def _execute_isolation_action(self, asset: str):
        """Execute isolation action for asset"""
        # This would integrate with network/endpoint isolation tools
        logger.info(f"Isolating asset: {asset}")
        
        # Simulate isolation action
        # In real implementation, would call network isolation APIs
        
    def _execute_block_action(self, ioc: str):
        """Execute blocking action for IOC"""
        # This would integrate with firewalls, DNS filters, etc.
        logger.info(f"Blocking IOC: {ioc}")
    
    def _perform_evidence_collection(self, evidence_type: str, source_system: str, 
                                   collection_method: str) -> Dict[str, Any]:
        """Perform evidence collection"""
        
        # Simulate evidence collection
        # In real implementation, would integrate with forensics tools
        
        result = {
            'file_path': f"/evidence/{evidence_type}_{source_system}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            'file_hash': f"sha256_{uuid.uuid4().hex}",
            'file_size': 1024 * 1024,  # 1MB
            'collected_by': 'system'
        }
        
        return result
    
    def _add_timeline_entry(self, incident_id: str, event: str, description: str, user: str = 'system'):
        """Add entry to incident timeline"""
        if incident_id not in self.incidents:
            return
        
        incident = self.incidents[incident_id]
        incident.timeline.append({
            'timestamp': datetime.now().isoformat(),
            'event': event,
            'description': description,
            'user': user
        })
        
        incident.updated_at = datetime.now()
        self._cache_incident(incident)
    
    def _notify_stakeholders(self, incident_id: str, notification_type: str):
        """Send notifications to relevant stakeholders"""
        incident = self.incidents[incident_id]
        
        # Determine stakeholders to notify based on priority and type
        stakeholders_to_notify = []
        
        for stakeholder in self.stakeholders.values():
            should_notify = False
            
            # Check escalation threshold
            if notification_type == 'incident_created':
                if incident.priority.value in ['critical', 'high']:
                    should_notify = True
                elif stakeholder.escalation_threshold == 'all':
                    should_notify = True
            elif notification_type == 'incident_resolved':
                should_notify = True
            
            if should_notify:
                stakeholders_to_notify.append(stakeholder)
        
        # Send notifications
        for stakeholder in stakeholders_to_notify:
            self._send_notification(stakeholder, incident, notification_type)
    
    def _notify_escalation_stakeholders(self, incident_id: str, escalation_reason: str):
        """Notify stakeholders of incident escalation"""
        # Would identify and notify appropriate escalation contacts
        logger.info(f"Notifying escalation stakeholders for incident {incident_id}")
    
    def _send_notification(self, stakeholder: Stakeholder, incident: Incident, notification_type: str):
        """Send notification to stakeholder"""
        
        if self.config['notification_settings']['email_enabled']:
            self._send_email_notification(stakeholder, incident, notification_type)
        
        if self.config['notification_settings']['webhook_enabled']:
            self._send_webhook_notification(stakeholder, incident, notification_type)
    
    def _send_email_notification(self, stakeholder: Stakeholder, incident: Incident, notification_type: str):
        """Send email notification"""
        # Email implementation would go here
        logger.info(f"Email notification sent to {stakeholder.email} for incident {incident.incident_id}")
    
    def _send_webhook_notification(self, stakeholder: Stakeholder, incident: Incident, notification_type: str):
        """Send webhook notification"""
        # Webhook implementation would go here
        logger.info(f"Webhook notification sent for incident {incident.incident_id}")
    
    def _generate_incident_report(self, incident_id: str):
        """Generate comprehensive incident report"""
        incident = self.incidents[incident_id]
        
        report = {
            'incident_id': incident_id,
            'title': incident.title,
            'created_at': incident.created_at.isoformat(),
            'resolved_at': datetime.now().isoformat(),
            'severity': incident.severity,
            'priority': incident.priority.value,
            'affected_assets': incident.affected_assets,
            'timeline': incident.timeline,
            'evidence_collected': len(incident.evidence),
            'response_actions': len(incident.response_actions),
            'resolution_summary': incident.resolution_summary,
            'lessons_learned': incident.lessons_learned
        }
        
        # Save report
        report_path = self.data_dir / "reports" / f"incident_report_{incident_id}.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Generated incident report: {report_path}")
    
    # Database caching methods
    
    def _cache_incident(self, incident: Incident):
        """Cache incident in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO incidents
            (incident_id, title, description, severity, priority, status, created_at, updated_at,
             assigned_to, alert_ids_json, affected_assets_json, iocs_json, mitre_tactics_json,
             mitre_techniques_json, timeline_json, evidence_json, response_actions_json,
             stakeholders_notified_json, estimated_impact, containment_status, 
             resolution_summary, lessons_learned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            incident.incident_id, incident.title, incident.description, incident.severity,
            incident.priority.value, incident.status.value, incident.created_at.isoformat(),
            incident.updated_at.isoformat(), incident.assigned_to, json.dumps(incident.alert_ids),
            json.dumps(incident.affected_assets), json.dumps(incident.iocs),
            json.dumps(incident.mitre_tactics), json.dumps(incident.mitre_techniques),
            json.dumps(incident.timeline), json.dumps(incident.evidence),
            json.dumps(incident.response_actions), json.dumps(incident.stakeholders_notified),
            incident.estimated_impact, incident.containment_status,
            incident.resolution_summary, incident.lessons_learned
        ))
        
        conn.commit()
        conn.close()
    
    def _cache_playbook(self, playbook: ResponsePlaybook):
        """Cache playbook in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO playbooks
            (playbook_id, name, description, trigger_conditions_json, steps_json,
             estimated_duration, required_roles_json, automation_level, success_criteria_json,
             created_at, updated_at, usage_count, success_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            playbook.playbook_id, playbook.name, playbook.description,
            json.dumps(playbook.trigger_conditions), json.dumps(playbook.steps),
            playbook.estimated_duration, json.dumps(playbook.required_roles),
            playbook.automation_level, json.dumps(playbook.success_criteria),
            playbook.created_at.isoformat(), playbook.updated_at.isoformat(),
            playbook.usage_count, playbook.success_rate
        ))
        
        conn.commit()
        conn.close()
    
    def _cache_evidence(self, evidence: Evidence):
        """Cache evidence in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO evidence
            (evidence_id, incident_id, evidence_type, source_system, collection_method,
             file_path, file_hash, file_size, collected_at, collected_by,
             chain_of_custody_json, analysis_results_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            evidence.evidence_id, evidence.incident_id, evidence.evidence_type,
            evidence.source_system, evidence.collection_method, evidence.file_path,
            evidence.file_hash, evidence.file_size, evidence.collected_at.isoformat(),
            evidence.collected_by, json.dumps(evidence.chain_of_custody),
            json.dumps(evidence.analysis_results) if evidence.analysis_results else None
        ))
        
        conn.commit()
        conn.close()


# Example usage
if __name__ == "__main__":
    # Initialize response engine
    engine = ThreatResponseEngine(data_dir="../../../")
    
    try:
        # Create incident from alert
        sample_alert = {
            'alert_id': 'ALT_001',
            'title': 'Malware Detection',
            'description': 'Suspicious file detected on workstation',
            'severity': 'High',
            'confidence': 0.9,
            'affected_assets': ['workstation_001'],
            'indicators': ['192.168.1.100', 'malware.exe'],
            'mitre_tactics': ['Initial Access'],
            'mitre_techniques': ['T1566.001']
        }
        
        incident_id = engine.create_incident_from_alert(sample_alert)
        print(f"Created incident: {incident_id}")
        
        # Execute response playbook
        success = engine.execute_response_playbook(incident_id, 'PB_MALWARE_001')
        print(f"Playbook execution: {'Success' if success else 'Failed'}")
        
        # Collect evidence
        evidence_id = engine.collect_evidence(incident_id, 'logs', 'workstation_001')
        print(f"Collected evidence: {evidence_id}")
        
        # Resolve incident
        engine.resolve_incident(
            incident_id,
            "Malware removed, system cleaned and patched",
            "Update endpoint protection signatures more frequently"
        )
        
        # Get metrics
        metrics = engine.get_incident_metrics(30)
        print(f"Response metrics: {metrics}")
        
    except Exception as e:
        logger.error(f"Error in response engine: {e}")
        raise