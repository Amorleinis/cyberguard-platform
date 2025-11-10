"""
Threat Isolation Module

This module provides comprehensive threat isolation capabilities including:
- Network segmentation and traffic control
- System quarantine and containment
- Access control restrictions
- Asset isolation orchestration
- Communication blocking
- Automated and manual isolation workflows
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
import ipaddress
import subprocess
import socket
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IsolationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ISOLATED = "isolated"
    PARTIAL = "partial"
    FAILED = "failed"
    RELEASED = "released"

class IsolationType(Enum):
    NETWORK = "network"
    HOST = "host"
    USER = "user"
    APPLICATION = "application"
    CONTAINER = "container"
    VIRTUAL_MACHINE = "virtual_machine"

class IsolationMethod(Enum):
    FIREWALL_RULE = "firewall_rule"
    VLAN_ISOLATION = "vlan_isolation"
    ENDPOINT_QUARANTINE = "endpoint_quarantine"
    DNS_SINKHOLE = "dns_sinkhole"
    PROXY_BLOCK = "proxy_block"
    AD_DISABLE = "ad_disable"
    VPN_REVOKE = "vpn_revoke"
    CONTAINER_STOP = "container_stop"

@dataclass
class IsolationTarget:
    """Target for isolation"""
    target_id: str
    target_type: str  # ip, hostname, user, container, vm
    target_value: str
    description: str
    criticality: str  # low, medium, high, critical
    network_segments: List[str]
    dependencies: List[str]
    isolation_methods: List[str]
    created_at: datetime

@dataclass
class IsolationRule:
    """Network isolation rule"""
    rule_id: str
    name: str
    description: str
    rule_type: str  # allow, deny, redirect
    source: str
    destination: str
    port: Optional[str]
    protocol: str
    action: str
    priority: int
    created_at: datetime
    expires_at: Optional[datetime]
    applied: bool
    device_applied: List[str]

@dataclass
class IsolationAction:
    """Individual isolation action"""
    action_id: str
    incident_id: str
    target_id: str
    isolation_type: IsolationType
    isolation_method: IsolationMethod
    status: IsolationStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_minutes: Optional[int]
    success: bool
    error_message: Optional[str]
    rollback_data: Dict[str, Any]
    executed_by: str

@dataclass
class NetworkSegment:
    """Network segment definition"""
    segment_id: str
    name: str
    description: str
    cidr_blocks: List[str]
    vlan_id: Optional[int]
    isolation_level: str  # none, monitor, restrict, quarantine
    allowed_outbound: List[str]
    allowed_inbound: List[str]
    gateway: str
    dns_servers: List[str]

@dataclass
class QuarantineZone:
    """Quarantine network zone"""
    zone_id: str
    name: str
    description: str
    network_range: str
    vlan_id: int
    gateway_ip: str
    dns_server: str
    allowed_services: List[str]  # minimal services like DNS, NTP
    monitoring_enabled: bool
    max_capacity: int
    current_hosts: int

class ThreatIsolationEngine:
    """
    Threat Isolation Engine
    
    Provides comprehensive threat isolation capabilities including:
    - Network segmentation and quarantine
    - Host-based isolation
    - User access restriction
    - Container and VM isolation
    - Automated rollback capabilities
    """
    
    def __init__(self, data_dir: str = "../../../", config_path: str = None):
        self.data_dir = Path(data_dir)
        self.config_path = config_path
        
        # Initialize local storage
        self.db_path = self.data_dir / "threat_isolation.db"
        self._init_local_db()
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize isolation components
        self.targets = {}
        self.rules = {}
        self.actions = {}
        self.network_segments = {}
        self.quarantine_zones = {}
        self.active_isolations = {}
        
        # Load existing data
        self._load_isolation_data()
        
        # Initialize default network segments and quarantine zones
        self._create_default_segments()
        self._create_quarantine_zones()
        
        # Start monitoring thread
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_isolation_status)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info("Threat Isolation Engine initialized")
    
    def _init_local_db(self):
        """Initialize local SQLite database for isolation data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Targets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS isolation_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id TEXT UNIQUE NOT NULL,
                target_type TEXT,
                target_value TEXT,
                description TEXT,
                criticality TEXT,
                network_segments_json TEXT,
                dependencies_json TEXT,
                isolation_methods_json TEXT,
                created_at TEXT
            )
        ''')
        
        # Rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS isolation_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT UNIQUE NOT NULL,
                name TEXT,
                description TEXT,
                rule_type TEXT,
                source TEXT,
                destination TEXT,
                port TEXT,
                protocol TEXT,
                action TEXT,
                priority INTEGER,
                created_at TEXT,
                expires_at TEXT,
                applied BOOLEAN,
                device_applied_json TEXT
            )
        ''')
        
        # Actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS isolation_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_id TEXT UNIQUE NOT NULL,
                incident_id TEXT,
                target_id TEXT,
                isolation_type TEXT,
                isolation_method TEXT,
                status TEXT,
                created_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                duration_minutes INTEGER,
                success BOOLEAN,
                error_message TEXT,
                rollback_data_json TEXT,
                executed_by TEXT
            )
        ''')
        
        # Network segments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                segment_id TEXT UNIQUE NOT NULL,
                name TEXT,
                description TEXT,
                cidr_blocks_json TEXT,
                vlan_id INTEGER,
                isolation_level TEXT,
                allowed_outbound_json TEXT,
                allowed_inbound_json TEXT,
                gateway TEXT,
                dns_servers_json TEXT
            )
        ''')
        
        # Quarantine zones table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quarantine_zones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zone_id TEXT UNIQUE NOT NULL,
                name TEXT,
                description TEXT,
                network_range TEXT,
                vlan_id INTEGER,
                gateway_ip TEXT,
                dns_server TEXT,
                allowed_services_json TEXT,
                monitoring_enabled BOOLEAN,
                max_capacity INTEGER,
                current_hosts INTEGER
            )
        ''')
        
        # Isolation history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS isolation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id TEXT,
                action_type TEXT,
                timestamp TEXT,
                status TEXT,
                details TEXT,
                executed_by TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load isolation configuration"""
        default_config = {
            'network_isolation': {
                'default_quarantine_vlan': 999,
                'quarantine_subnet': '192.168.99.0/24',
                'isolation_gateway': '192.168.99.1',
                'quarantine_dns': '192.168.99.2',
                'max_isolation_duration': 7200  # 2 hours
            },
            'firewall_integration': {
                'enabled': True,
                'type': 'generic',  # pfsense, cisco, fortinet, etc.
                'api_endpoint': None,
                'credentials': None
            },
            'endpoint_integration': {
                'enabled': True,
                'type': 'generic',  # crowdstrike, sentinelone, defender, etc.
                'api_endpoint': None,
                'credentials': None
            },
            'switch_integration': {
                'enabled': False,
                'type': 'generic',  # cisco, hp, aruba, etc.
                'snmp_community': 'public',
                'devices': []
            },
            'isolation_policies': {
                'auto_isolate_critical': True,
                'auto_isolate_malware': True,
                'require_approval_for': ['domain_controller', 'server'],
                'max_simultaneous_isolations': 50,
                'quarantine_timeout_hours': 24
            },
            'monitoring': {
                'ping_interval_seconds': 60,
                'log_isolation_events': True,
                'alert_on_isolation_failure': True,
                'track_network_changes': True
            }
        }
        
        return default_config
    
    def _load_isolation_data(self):
        """Load existing isolation data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load targets
            cursor.execute("SELECT * FROM isolation_targets")
            for row in cursor.fetchall():
                target = IsolationTarget(
                    target_id=row[1],
                    target_type=row[2],
                    target_value=row[3],
                    description=row[4],
                    criticality=row[5],
                    network_segments=json.loads(row[6] or '[]'),
                    dependencies=json.loads(row[7] or '[]'),
                    isolation_methods=json.loads(row[8] or '[]'),
                    created_at=datetime.fromisoformat(row[9])
                )
                self.targets[row[1]] = target
            
            # Load rules
            cursor.execute("SELECT * FROM isolation_rules")
            for row in cursor.fetchall():
                rule = IsolationRule(
                    rule_id=row[1],
                    name=row[2],
                    description=row[3],
                    rule_type=row[4],
                    source=row[5],
                    destination=row[6],
                    port=row[7],
                    protocol=row[8],
                    action=row[9],
                    priority=row[10],
                    created_at=datetime.fromisoformat(row[11]),
                    expires_at=datetime.fromisoformat(row[12]) if row[12] else None,
                    applied=bool(row[13]),
                    device_applied=json.loads(row[14] or '[]')
                )
                self.rules[row[1]] = rule
            
            # Load network segments
            cursor.execute("SELECT * FROM network_segments")
            for row in cursor.fetchall():
                segment = NetworkSegment(
                    segment_id=row[1],
                    name=row[2],
                    description=row[3],
                    cidr_blocks=json.loads(row[4] or '[]'),
                    vlan_id=row[5],
                    isolation_level=row[6],
                    allowed_outbound=json.loads(row[7] or '[]'),
                    allowed_inbound=json.loads(row[8] or '[]'),
                    gateway=row[9],
                    dns_servers=json.loads(row[10] or '[]')
                )
                self.network_segments[row[1]] = segment
            
            # Load quarantine zones
            cursor.execute("SELECT * FROM quarantine_zones")
            for row in cursor.fetchall():
                zone = QuarantineZone(
                    zone_id=row[1],
                    name=row[2],
                    description=row[3],
                    network_range=row[4],
                    vlan_id=row[5],
                    gateway_ip=row[6],
                    dns_server=row[7],
                    allowed_services=json.loads(row[8] or '[]'),
                    monitoring_enabled=bool(row[9]),
                    max_capacity=row[10],
                    current_hosts=row[11]
                )
                self.quarantine_zones[row[1]] = zone
            
            conn.close()
            logger.info(f"Loaded {len(self.targets)} targets and {len(self.rules)} isolation rules")
            
        except Exception as e:
            logger.error(f"Error loading isolation data: {e}")
    
    def isolate_host(self, target: str, isolation_method: str = "auto", 
                    incident_id: str = None, duration_hours: int = None) -> str:
        """
        Isolate host using specified method
        
        Args:
            target: IP address, hostname, or MAC address to isolate
            isolation_method: Method to use for isolation
            incident_id: Associated incident ID
            duration_hours: Isolation duration (None for indefinite)
            
        Returns:
            Action ID
        """
        action_id = f"ISO_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Determine target type and validate
        target_type = self._identify_target_type(target)
        if not target_type:
            logger.error(f"Could not identify target type for: {target}")
            return None
        
        # Auto-select isolation method if needed
        if isolation_method == "auto":
            isolation_method = self._select_isolation_method(target, target_type)
        
        # Create isolation action
        action = IsolationAction(
            action_id=action_id,
            incident_id=incident_id,
            target_id=target,
            isolation_type=IsolationType.HOST,
            isolation_method=IsolationMethod(isolation_method),
            status=IsolationStatus.PENDING,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            duration_minutes=duration_hours * 60 if duration_hours else None,
            success=False,
            error_message=None,
            rollback_data={},
            executed_by='system'
        )
        
        self.actions[action_id] = action
        
        # Execute isolation
        success = self._execute_host_isolation(action)
        
        if success:
            action.status = IsolationStatus.ISOLATED
            action.success = True
            action.started_at = datetime.now()
            action.completed_at = datetime.now()
            
            # Schedule auto-release if duration specified
            if duration_hours:
                self._schedule_auto_release(action_id, duration_hours)
            
            # Add to active isolations
            self.active_isolations[action_id] = action
            
        else:
            action.status = IsolationStatus.FAILED
            action.error_message = "Isolation execution failed"
        
        # Cache action
        self._cache_action(action)
        
        # Log to history
        self._log_isolation_event(
            target, 
            'isolate_host', 
            action.status.value,
            f"Method: {isolation_method}"
        )
        
        logger.info(f"Host isolation {'successful' if success else 'failed'}: {target}")
        return action_id
    
    def isolate_network_segment(self, network: str, isolation_level: str = "quarantine",
                               incident_id: str = None) -> str:
        """
        Isolate entire network segment
        
        Args:
            network: Network CIDR to isolate
            isolation_level: Level of isolation (monitor, restrict, quarantine)
            incident_id: Associated incident ID
            
        Returns:
            Action ID
        """
        action_id = f"ISO_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Validate network CIDR
        try:
            network_obj = ipaddress.ip_network(network)
        except ValueError as e:
            logger.error(f"Invalid network CIDR: {network}")
            return None
        
        # Create isolation action
        action = IsolationAction(
            action_id=action_id,
            incident_id=incident_id,
            target_id=network,
            isolation_type=IsolationType.NETWORK,
            isolation_method=IsolationMethod.VLAN_ISOLATION,
            status=IsolationStatus.PENDING,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            duration_minutes=None,
            success=False,
            error_message=None,
            rollback_data={},
            executed_by='system'
        )
        
        self.actions[action_id] = action
        
        # Execute network isolation
        success = self._execute_network_isolation(action, isolation_level)
        
        if success:
            action.status = IsolationStatus.ISOLATED
            action.success = True
            action.started_at = datetime.now()
            action.completed_at = datetime.now()
            
            self.active_isolations[action_id] = action
        else:
            action.status = IsolationStatus.FAILED
            action.error_message = "Network isolation execution failed"
        
        # Cache action
        self._cache_action(action)
        
        # Log event
        self._log_isolation_event(
            network,
            'isolate_network',
            action.status.value,
            f"Level: {isolation_level}"
        )
        
        logger.info(f"Network isolation {'successful' if success else 'failed'}: {network}")
        return action_id
    
    def isolate_user(self, username: str, isolation_methods: List[str] = None,
                    incident_id: str = None) -> str:
        """
        Isolate user account and access
        
        Args:
            username: Username to isolate
            isolation_methods: Methods to use (ad_disable, vpn_revoke, etc.)
            incident_id: Associated incident ID
            
        Returns:
            Action ID
        """
        action_id = f"ISO_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Default isolation methods for users
        if not isolation_methods:
            isolation_methods = ['ad_disable', 'vpn_revoke']
        
        # Create isolation action
        action = IsolationAction(
            action_id=action_id,
            incident_id=incident_id,
            target_id=username,
            isolation_type=IsolationType.USER,
            isolation_method=IsolationMethod.AD_DISABLE,
            status=IsolationStatus.PENDING,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            duration_minutes=None,
            success=False,
            error_message=None,
            rollback_data={},
            executed_by='system'
        )
        
        self.actions[action_id] = action
        
        # Execute user isolation
        success = self._execute_user_isolation(action, isolation_methods)
        
        if success:
            action.status = IsolationStatus.ISOLATED
            action.success = True
            action.started_at = datetime.now()
            action.completed_at = datetime.now()
            
            self.active_isolations[action_id] = action
        else:
            action.status = IsolationStatus.FAILED
            action.error_message = "User isolation execution failed"
        
        # Cache action
        self._cache_action(action)
        
        # Log event
        self._log_isolation_event(
            username,
            'isolate_user',
            action.status.value,
            f"Methods: {', '.join(isolation_methods)}"
        )
        
        logger.info(f"User isolation {'successful' if success else 'failed'}: {username}")
        return action_id
    
    def move_to_quarantine(self, target: str, quarantine_zone: str = "default",
                          incident_id: str = None) -> str:
        """
        Move host to quarantine network zone
        
        Args:
            target: Host to quarantine
            quarantine_zone: Quarantine zone to use
            incident_id: Associated incident ID
            
        Returns:
            Action ID
        """
        action_id = f"ISO_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Validate quarantine zone
        if quarantine_zone not in self.quarantine_zones:
            logger.error(f"Quarantine zone not found: {quarantine_zone}")
            return None
        
        zone = self.quarantine_zones[quarantine_zone]
        
        # Check zone capacity
        if zone.current_hosts >= zone.max_capacity:
            logger.error(f"Quarantine zone {quarantine_zone} at capacity")
            return None
        
        # Create isolation action
        action = IsolationAction(
            action_id=action_id,
            incident_id=incident_id,
            target_id=target,
            isolation_type=IsolationType.NETWORK,
            isolation_method=IsolationMethod.VLAN_ISOLATION,
            status=IsolationStatus.PENDING,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            duration_minutes=None,
            success=False,
            error_message=None,
            rollback_data={},
            executed_by='system'
        )
        
        self.actions[action_id] = action
        
        # Execute quarantine
        success = self._execute_quarantine(action, zone)
        
        if success:
            action.status = IsolationStatus.ISOLATED
            action.success = True
            action.started_at = datetime.now()
            action.completed_at = datetime.now()
            
            # Update zone capacity
            zone.current_hosts += 1
            self._cache_quarantine_zone(zone)
            
            self.active_isolations[action_id] = action
        else:
            action.status = IsolationStatus.FAILED
            action.error_message = "Quarantine execution failed"
        
        # Cache action
        self._cache_action(action)
        
        # Log event
        self._log_isolation_event(
            target,
            'move_to_quarantine',
            action.status.value,
            f"Zone: {quarantine_zone}"
        )
        
        logger.info(f"Quarantine {'successful' if success else 'failed'}: {target}")
        return action_id
    
    def release_isolation(self, action_id: str, release_reason: str = "manual") -> bool:
        """
        Release host from isolation
        
        Args:
            action_id: Isolation action to release
            release_reason: Reason for release
            
        Returns:
            Success status
        """
        if action_id not in self.actions:
            logger.error(f"Isolation action not found: {action_id}")
            return False
        
        action = self.actions[action_id]
        
        if action.status != IsolationStatus.ISOLATED:
            logger.warning(f"Action {action_id} is not in isolated state")
            return False
        
        # Execute release based on isolation method
        success = self._execute_isolation_release(action)
        
        if success:
            action.status = IsolationStatus.RELEASED
            
            # Remove from active isolations
            if action_id in self.active_isolations:
                del self.active_isolations[action_id]
            
            # Update quarantine zone capacity if applicable
            if action.isolation_method == IsolationMethod.VLAN_ISOLATION:
                for zone in self.quarantine_zones.values():
                    if zone.current_hosts > 0:
                        zone.current_hosts -= 1
                        self._cache_quarantine_zone(zone)
                        break
            
            # Log event
            self._log_isolation_event(
                action.target_id,
                'release_isolation',
                'released',
                f"Reason: {release_reason}"
            )
            
            logger.info(f"Released isolation for {action.target_id}")
        else:
            logger.error(f"Failed to release isolation for {action.target_id}")
        
        # Update action
        self._cache_action(action)
        
        return success
    
    def create_firewall_rule(self, name: str, source: str, destination: str,
                           action: str = "deny", protocol: str = "any",
                           port: str = "any", priority: int = 100,
                           duration_hours: int = None) -> str:
        """
        Create firewall rule for traffic blocking
        
        Args:
            name: Rule name
            source: Source IP/network
            destination: Destination IP/network
            action: Rule action (allow/deny/redirect)
            protocol: Protocol (tcp/udp/icmp/any)
            port: Port or port range
            priority: Rule priority
            duration_hours: Rule expiration
            
        Returns:
            Rule ID
        """
        rule_id = f"FW_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Calculate expiration time
        expires_at = None
        if duration_hours:
            expires_at = datetime.now() + timedelta(hours=duration_hours)
        
        # Create rule
        rule = IsolationRule(
            rule_id=rule_id,
            name=name,
            description=f"Isolation rule: {source} -> {destination}",
            rule_type="firewall",
            source=source,
            destination=destination,
            port=port,
            protocol=protocol,
            action=action,
            priority=priority,
            created_at=datetime.now(),
            expires_at=expires_at,
            applied=False,
            device_applied=[]
        )
        
        self.rules[rule_id] = rule
        
        # Apply rule to firewall devices
        success = self._apply_firewall_rule(rule)
        
        if success:
            rule.applied = True
            
        # Cache rule
        self._cache_rule(rule)
        
        logger.info(f"Firewall rule {'created and applied' if success else 'created but not applied'}: {rule_id}")
        return rule_id
    
    def get_isolation_status(self, target: str = None) -> Dict[str, Any]:
        """
        Get isolation status for target or all active isolations
        
        Args:
            target: Specific target to check, or None for all
            
        Returns:
            Isolation status information
        """
        if target:
            # Get status for specific target
            target_actions = [
                action for action in self.actions.values()
                if action.target_id == target
            ]
            
            if not target_actions:
                return {'target': target, 'status': 'not_isolated'}
            
            # Get most recent action
            latest_action = max(target_actions, key=lambda x: x.created_at)
            
            return {
                'target': target,
                'status': latest_action.status.value,
                'isolation_type': latest_action.isolation_type.value,
                'isolation_method': latest_action.isolation_method.value,
                'isolated_since': latest_action.started_at.isoformat() if latest_action.started_at else None,
                'incident_id': latest_action.incident_id,
                'action_id': latest_action.action_id
            }
        else:
            # Get all active isolations
            active_status = {}
            
            for action_id, action in self.active_isolations.items():
                active_status[action.target_id] = {
                    'action_id': action_id,
                    'status': action.status.value,
                    'isolation_type': action.isolation_type.value,
                    'isolation_method': action.isolation_method.value,
                    'isolated_since': action.started_at.isoformat() if action.started_at else None,
                    'incident_id': action.incident_id
                }
            
            return {
                'active_isolations': len(self.active_isolations),
                'targets': active_status,
                'quarantine_zones': {
                    zone_id: {
                        'current_hosts': zone.current_hosts,
                        'max_capacity': zone.max_capacity,
                        'utilization': (zone.current_hosts / zone.max_capacity * 100) if zone.max_capacity > 0 else 0
                    }
                    for zone_id, zone in self.quarantine_zones.items()
                }
            }
    
    def get_isolation_metrics(self, time_period: int = 30) -> Dict[str, Any]:
        """
        Get isolation metrics for specified time period
        
        Args:
            time_period: Number of days to analyze
            
        Returns:
            Metrics dictionary
        """
        start_date = datetime.now() - timedelta(days=time_period)
        
        # Filter actions by time period
        recent_actions = [
            action for action in self.actions.values()
            if action.created_at >= start_date
        ]
        
        if not recent_actions:
            return {'message': 'No isolation actions in time period'}
        
        # Calculate metrics
        total_actions = len(recent_actions)
        successful_actions = len([a for a in recent_actions if a.success])
        failed_actions = total_actions - successful_actions
        
        # Success rate by isolation type
        type_stats = defaultdict(lambda: {'total': 0, 'successful': 0})
        
        for action in recent_actions:
            type_stats[action.isolation_type.value]['total'] += 1
            if action.success:
                type_stats[action.isolation_type.value]['successful'] += 1
        
        # Calculate success rates
        for stats in type_stats.values():
            stats['success_rate'] = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        # Average isolation duration
        completed_actions = [
            a for a in recent_actions 
            if a.completed_at and a.started_at
        ]
        
        avg_duration = 0
        if completed_actions:
            durations = [
                (a.completed_at - a.started_at).total_seconds() / 60
                for a in completed_actions
            ]
            avg_duration = sum(durations) / len(durations)
        
        # Currently active isolations
        current_active = len(self.active_isolations)
        
        # Quarantine zone utilization
        zone_utilization = {}
        for zone_id, zone in self.quarantine_zones.items():
            utilization = (zone.current_hosts / zone.max_capacity * 100) if zone.max_capacity > 0 else 0
            zone_utilization[zone_id] = {
                'current_hosts': zone.current_hosts,
                'max_capacity': zone.max_capacity,
                'utilization_percent': round(utilization, 2)
            }
        
        metrics = {
            'time_period_days': time_period,
            'total_isolation_actions': total_actions,
            'successful_actions': successful_actions,
            'failed_actions': failed_actions,
            'overall_success_rate': (successful_actions / total_actions * 100) if total_actions > 0 else 0,
            'success_rate_by_type': dict(type_stats),
            'average_isolation_duration_minutes': round(avg_duration, 2),
            'currently_active_isolations': current_active,
            'quarantine_zone_utilization': zone_utilization
        }
        
        return metrics
    
    # Helper methods for isolation execution
    
    def _create_default_segments(self):
        """Create default network segments"""
        
        # Production segment
        production_segment = NetworkSegment(
            segment_id="PROD_001",
            name="Production Network",
            description="Main production network segment",
            cidr_blocks=["10.0.0.0/16"],
            vlan_id=100,
            isolation_level="none",
            allowed_outbound=["any"],
            allowed_inbound=["management"],
            gateway="10.0.0.1",
            dns_servers=["10.0.0.10", "10.0.0.11"]
        )
        
        # Management segment
        management_segment = NetworkSegment(
            segment_id="MGMT_001",
            name="Management Network",
            description="Network management and monitoring",
            cidr_blocks=["192.168.1.0/24"],
            vlan_id=200,
            isolation_level="restrict",
            allowed_outbound=["production", "dmz"],
            allowed_inbound=["production"],
            gateway="192.168.1.1",
            dns_servers=["192.168.1.10"]
        )
        
        # DMZ segment
        dmz_segment = NetworkSegment(
            segment_id="DMZ_001",
            name="DMZ Network",
            description="Demilitarized zone for public services",
            cidr_blocks=["172.16.0.0/24"],
            vlan_id=300,
            isolation_level="monitor",
            allowed_outbound=["internet"],
            allowed_inbound=["internet", "production"],
            gateway="172.16.0.1",
            dns_servers=["8.8.8.8", "8.8.4.4"]
        )
        
        # Store segments
        for segment in [production_segment, management_segment, dmz_segment]:
            self.network_segments[segment.segment_id] = segment
            self._cache_network_segment(segment)
    
    def _create_quarantine_zones(self):
        """Create default quarantine zones"""
        
        # Default quarantine zone
        default_zone = QuarantineZone(
            zone_id="QUAR_DEFAULT",
            name="Default Quarantine",
            description="Default isolation zone for infected hosts",
            network_range="192.168.99.0/24",
            vlan_id=999,
            gateway_ip="192.168.99.1",
            dns_server="192.168.99.2",
            allowed_services=["dns", "ntp", "http_remediation"],
            monitoring_enabled=True,
            max_capacity=50,
            current_hosts=0
        )
        
        # High security quarantine
        high_security_zone = QuarantineZone(
            zone_id="QUAR_HIGH_SEC",
            name="High Security Quarantine",
            description="High security isolation for critical threats",
            network_range="192.168.98.0/24",
            vlan_id=998,
            gateway_ip="192.168.98.1",
            dns_server="192.168.98.2",
            allowed_services=["dns"],
            monitoring_enabled=True,
            max_capacity=20,
            current_hosts=0
        )
        
        # Store zones
        for zone in [default_zone, high_security_zone]:
            self.quarantine_zones[zone.zone_id] = zone
            self._cache_quarantine_zone(zone)
    
    def _identify_target_type(self, target: str) -> str:
        """Identify the type of target (IP, hostname, MAC, etc.)"""
        
        # Check if IP address
        try:
            ipaddress.ip_address(target)
            return "ip"
        except ValueError:
            pass
        
        # Check if MAC address
        if len(target) == 17 and target.count(':') == 5:
            return "mac"
        
        # Check if hostname/FQDN
        if '.' in target or target.isalpha():
            return "hostname"
        
        return None
    
    def _select_isolation_method(self, target: str, target_type: str) -> str:
        """Select appropriate isolation method for target"""
        
        if target_type == "ip":
            return "firewall_rule"
        elif target_type == "hostname":
            return "endpoint_quarantine"
        elif target_type == "mac":
            return "vlan_isolation"
        else:
            return "firewall_rule"
    
    def _execute_host_isolation(self, action: IsolationAction) -> bool:
        """Execute host isolation based on method"""
        
        method = action.isolation_method
        target = action.target_id
        
        try:
            if method == IsolationMethod.FIREWALL_RULE:
                return self._isolate_via_firewall(target, action)
            elif method == IsolationMethod.ENDPOINT_QUARANTINE:
                return self._isolate_via_endpoint(target, action)
            elif method == IsolationMethod.VLAN_ISOLATION:
                return self._isolate_via_vlan(target, action)
            elif method == IsolationMethod.DNS_SINKHOLE:
                return self._isolate_via_dns(target, action)
            else:
                logger.warning(f"Unsupported isolation method: {method}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing host isolation: {e}")
            action.error_message = str(e)
            return False
    
    def _execute_network_isolation(self, action: IsolationAction, isolation_level: str) -> bool:
        """Execute network segment isolation"""
        
        network = action.target_id
        
        try:
            # Create network isolation rules
            rule_id = self.create_firewall_rule(
                name=f"Isolate Network {network}",
                source=network,
                destination="any",
                action="deny",
                priority=10
            )
            
            if rule_id:
                action.rollback_data['firewall_rule_id'] = rule_id
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error executing network isolation: {e}")
            action.error_message = str(e)
            return False
    
    def _execute_user_isolation(self, action: IsolationAction, methods: List[str]) -> bool:
        """Execute user account isolation"""
        
        username = action.target_id
        
        try:
            success_count = 0
            
            for method in methods:
                if method == "ad_disable":
                    if self._disable_ad_account(username, action):
                        success_count += 1
                elif method == "vpn_revoke":
                    if self._revoke_vpn_access(username, action):
                        success_count += 1
                elif method == "proxy_block":
                    if self._block_proxy_access(username, action):
                        success_count += 1
            
            # Consider success if at least half of methods succeed
            return success_count >= len(methods) / 2
            
        except Exception as e:
            logger.error(f"Error executing user isolation: {e}")
            action.error_message = str(e)
            return False
    
    def _execute_quarantine(self, action: IsolationAction, zone: QuarantineZone) -> bool:
        """Execute host quarantine to specified zone"""
        
        target = action.target_id
        
        try:
            # Move host to quarantine VLAN
            success = self._move_to_quarantine_vlan(target, zone, action)
            
            if success:
                action.rollback_data['quarantine_zone'] = zone.zone_id
                action.rollback_data['original_network'] = "unknown"  # Would be determined dynamically
                
            return success
            
        except Exception as e:
            logger.error(f"Error executing quarantine: {e}")
            action.error_message = str(e)
            return False
    
    def _execute_isolation_release(self, action: IsolationAction) -> bool:
        """Execute isolation release/rollback"""
        
        method = action.isolation_method
        
        try:
            if method == IsolationMethod.FIREWALL_RULE:
                return self._release_firewall_isolation(action)
            elif method == IsolationMethod.ENDPOINT_QUARANTINE:
                return self._release_endpoint_isolation(action)
            elif method == IsolationMethod.VLAN_ISOLATION:
                return self._release_vlan_isolation(action)
            elif method == IsolationMethod.AD_DISABLE:
                return self._release_user_isolation(action)
            else:
                logger.warning(f"Unsupported release method: {method}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing isolation release: {e}")
            return False
    
    # Isolation method implementations (these would integrate with actual systems)
    
    def _isolate_via_firewall(self, target: str, action: IsolationAction) -> bool:
        """Isolate host via firewall rules"""
        
        # Create deny rule for target
        rule_id = self.create_firewall_rule(
            name=f"Isolate Host {target}",
            source=target,
            destination="any",
            action="deny",
            priority=1
        )
        
        if rule_id:
            action.rollback_data['firewall_rule_id'] = rule_id
            return True
        
        return False
    
    def _isolate_via_endpoint(self, target: str, action: IsolationAction) -> bool:
        """Isolate host via endpoint protection"""
        
        # This would integrate with endpoint protection platforms
        # Simulate endpoint isolation
        logger.info(f"Simulating endpoint isolation for {target}")
        
        # Store rollback information
        action.rollback_data['endpoint_isolation'] = True
        action.rollback_data['target'] = target
        
        return True
    
    def _isolate_via_vlan(self, target: str, action: IsolationAction) -> bool:
        """Isolate host via VLAN change"""
        
        # This would integrate with network switches
        # Simulate VLAN isolation
        logger.info(f"Simulating VLAN isolation for {target}")
        
        # Store original VLAN for rollback
        action.rollback_data['original_vlan'] = 100  # Would be detected dynamically
        action.rollback_data['quarantine_vlan'] = 999
        
        return True
    
    def _isolate_via_dns(self, target: str, action: IsolationAction) -> bool:
        """Isolate host via DNS sinkhole"""
        
        # This would configure DNS to redirect target's queries
        logger.info(f"Simulating DNS sinkhole for {target}")
        
        action.rollback_data['dns_sinkhole'] = True
        
        return True
    
    def _disable_ad_account(self, username: str, action: IsolationAction) -> bool:
        """Disable Active Directory account"""
        
        # This would integrate with Active Directory
        logger.info(f"Simulating AD account disable for {username}")
        
        action.rollback_data['ad_disabled'] = True
        action.rollback_data['username'] = username
        
        return True
    
    def _revoke_vpn_access(self, username: str, action: IsolationAction) -> bool:
        """Revoke VPN access for user"""
        
        # This would integrate with VPN system
        logger.info(f"Simulating VPN access revocation for {username}")
        
        action.rollback_data['vpn_revoked'] = True
        
        return True
    
    def _block_proxy_access(self, username: str, action: IsolationAction) -> bool:
        """Block proxy access for user"""
        
        # This would integrate with proxy server
        logger.info(f"Simulating proxy access block for {username}")
        
        action.rollback_data['proxy_blocked'] = True
        
        return True
    
    def _move_to_quarantine_vlan(self, target: str, zone: QuarantineZone, action: IsolationAction) -> bool:
        """Move host to quarantine VLAN"""
        
        # This would integrate with network infrastructure
        logger.info(f"Simulating quarantine VLAN move for {target} to zone {zone.zone_id}")
        
        return True
    
    def _apply_firewall_rule(self, rule: IsolationRule) -> bool:
        """Apply rule to firewall devices"""
        
        # This would integrate with firewall management systems
        logger.info(f"Simulating firewall rule application: {rule.rule_id}")
        
        # Simulate successful application
        rule.device_applied.append("firewall_001")
        
        return True
    
    # Release/rollback implementations
    
    def _release_firewall_isolation(self, action: IsolationAction) -> bool:
        """Release firewall-based isolation"""
        
        if 'firewall_rule_id' in action.rollback_data:
            rule_id = action.rollback_data['firewall_rule_id']
            
            # Remove firewall rule
            if rule_id in self.rules:
                del self.rules[rule_id]
                logger.info(f"Removed firewall rule: {rule_id}")
                return True
        
        return False
    
    def _release_endpoint_isolation(self, action: IsolationAction) -> bool:
        """Release endpoint-based isolation"""
        
        if action.rollback_data.get('endpoint_isolation'):
            target = action.rollback_data.get('target')
            logger.info(f"Simulating endpoint isolation release for {target}")
            return True
        
        return False
    
    def _release_vlan_isolation(self, action: IsolationAction) -> bool:
        """Release VLAN-based isolation"""
        
        if 'original_vlan' in action.rollback_data:
            original_vlan = action.rollback_data['original_vlan']
            logger.info(f"Simulating VLAN restoration to {original_vlan}")
            return True
        
        return False
    
    def _release_user_isolation(self, action: IsolationAction) -> bool:
        """Release user account isolation"""
        
        success_count = 0
        
        if action.rollback_data.get('ad_disabled'):
            logger.info("Simulating AD account re-enable")
            success_count += 1
        
        if action.rollback_data.get('vpn_revoked'):
            logger.info("Simulating VPN access restoration")
            success_count += 1
        
        if action.rollback_data.get('proxy_blocked'):
            logger.info("Simulating proxy access restoration")
            success_count += 1
        
        return success_count > 0
    
    def _schedule_auto_release(self, action_id: str, duration_hours: int):
        """Schedule automatic isolation release"""
        
        def auto_release():
            time.sleep(duration_hours * 3600)  # Convert to seconds
            
            if action_id in self.active_isolations:
                success = self.release_isolation(action_id, "auto_timeout")
                if success:
                    logger.info(f"Auto-released isolation: {action_id}")
                else:
                    logger.error(f"Failed to auto-release isolation: {action_id}")
        
        # Start auto-release thread
        release_thread = threading.Thread(target=auto_release)
        release_thread.daemon = True
        release_thread.start()
    
    def _monitor_isolation_status(self):
        """Monitor isolation status and health"""
        
        while self.monitoring_active:
            try:
                # Check for expired rules
                current_time = datetime.now()
                expired_rules = [
                    rule for rule in self.rules.values()
                    if rule.expires_at and rule.expires_at <= current_time and rule.applied
                ]
                
                for rule in expired_rules:
                    logger.info(f"Removing expired rule: {rule.rule_id}")
                    rule.applied = False
                    self._cache_rule(rule)
                
                # Monitor quarantine zone health
                for zone_id, zone in self.quarantine_zones.items():
                    if zone.monitoring_enabled:
                        self._check_quarantine_zone_health(zone)
                
                # Sleep for monitoring interval
                time.sleep(self.config['monitoring']['ping_interval_seconds'])
                
            except Exception as e:
                logger.error(f"Error in isolation monitoring: {e}")
                time.sleep(60)  # Sleep longer on error
    
    def _check_quarantine_zone_health(self, zone: QuarantineZone):
        """Check health of quarantine zone"""
        
        # This would perform actual health checks
        # For now, just log zone status
        if zone.current_hosts > 0:
            utilization = (zone.current_hosts / zone.max_capacity) * 100
            if utilization > 90:
                logger.warning(f"Quarantine zone {zone.zone_id} near capacity: {utilization:.1f}%")
    
    def _log_isolation_event(self, target: str, action_type: str, status: str, details: str):
        """Log isolation event to history"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO isolation_history
            (target_id, action_type, timestamp, status, details, executed_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (target, action_type, datetime.now().isoformat(), status, details, 'system'))
        
        conn.commit()
        conn.close()
    
    # Database caching methods
    
    def _cache_action(self, action: IsolationAction):
        """Cache isolation action in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO isolation_actions
            (action_id, incident_id, target_id, isolation_type, isolation_method,
             status, created_at, started_at, completed_at, duration_minutes,
             success, error_message, rollback_data_json, executed_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            action.action_id, action.incident_id, action.target_id,
            action.isolation_type.value, action.isolation_method.value,
            action.status.value, action.created_at.isoformat(),
            action.started_at.isoformat() if action.started_at else None,
            action.completed_at.isoformat() if action.completed_at else None,
            action.duration_minutes, action.success, action.error_message,
            json.dumps(action.rollback_data), action.executed_by
        ))
        
        conn.commit()
        conn.close()
    
    def _cache_rule(self, rule: IsolationRule):
        """Cache isolation rule in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO isolation_rules
            (rule_id, name, description, rule_type, source, destination,
             port, protocol, action, priority, created_at, expires_at,
             applied, device_applied_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rule.rule_id, rule.name, rule.description, rule.rule_type,
            rule.source, rule.destination, rule.port, rule.protocol,
            rule.action, rule.priority, rule.created_at.isoformat(),
            rule.expires_at.isoformat() if rule.expires_at else None,
            rule.applied, json.dumps(rule.device_applied)
        ))
        
        conn.commit()
        conn.close()
    
    def _cache_network_segment(self, segment: NetworkSegment):
        """Cache network segment in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO network_segments
            (segment_id, name, description, cidr_blocks_json, vlan_id,
             isolation_level, allowed_outbound_json, allowed_inbound_json,
             gateway, dns_servers_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            segment.segment_id, segment.name, segment.description,
            json.dumps(segment.cidr_blocks), segment.vlan_id,
            segment.isolation_level, json.dumps(segment.allowed_outbound),
            json.dumps(segment.allowed_inbound), segment.gateway,
            json.dumps(segment.dns_servers)
        ))
        
        conn.commit()
        conn.close()
    
    def _cache_quarantine_zone(self, zone: QuarantineZone):
        """Cache quarantine zone in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO quarantine_zones
            (zone_id, name, description, network_range, vlan_id,
             gateway_ip, dns_server, allowed_services_json,
             monitoring_enabled, max_capacity, current_hosts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            zone.zone_id, zone.name, zone.description, zone.network_range,
            zone.vlan_id, zone.gateway_ip, zone.dns_server,
            json.dumps(zone.allowed_services), zone.monitoring_enabled,
            zone.max_capacity, zone.current_hosts
        ))
        
        conn.commit()
        conn.close()


# Example usage
if __name__ == "__main__":
    # Initialize isolation engine
    engine = ThreatIsolationEngine(data_dir="../../../")
    
    try:
        # Isolate a compromised host
        action_id = engine.isolate_host(
            target="192.168.1.100",
            isolation_method="auto",
            incident_id="INC_001",
            duration_hours=2
        )
        print(f"Host isolation action: {action_id}")
        
        # Move host to quarantine
        quarantine_id = engine.move_to_quarantine(
            target="192.168.1.101",
            quarantine_zone="QUAR_DEFAULT",
            incident_id="INC_002"
        )
        print(f"Quarantine action: {quarantine_id}")
        
        # Isolate user account
        user_id = engine.isolate_user(
            username="compromised_user",
            isolation_methods=["ad_disable", "vpn_revoke"],
            incident_id="INC_003"
        )
        print(f"User isolation action: {user_id}")
        
        # Create firewall rule
        rule_id = engine.create_firewall_rule(
            name="Block Malicious IP",
            source="1.2.3.4",
            destination="any",
            action="deny",
            duration_hours=24
        )
        print(f"Firewall rule: {rule_id}")
        
        # Get isolation status
        status = engine.get_isolation_status()
        print(f"Isolation status: {status}")
        
        # Get metrics
        metrics = engine.get_isolation_metrics(30)
        print(f"Isolation metrics: {metrics}")
        
    except Exception as e:
        logger.error(f"Error in isolation engine: {e}")
        raise