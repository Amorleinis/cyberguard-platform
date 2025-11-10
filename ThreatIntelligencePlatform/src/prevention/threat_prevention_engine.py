"""
Threat Prevention Module

This module provides proactive threat prevention capabilities including:
- IOC-based blocking and filtering
- Vulnerability management and patching
- Attack surface reduction
- Threat hunting and proactive detection
- Security configuration management
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import sqlite3
import ipaddress
import requests
from collections import defaultdict
import yaml
import hashlib
import re
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PreventionAction(Enum):
    BLOCK = "block"
    ALERT = "alert" 
    MONITOR = "monitor"
    QUARANTINE = "quarantine"
    PATCH = "patch"
    CONFIGURE = "configure"

@dataclass
class PreventionRule:
    """Threat prevention rule"""
    rule_id: str
    name: str
    description: str
    rule_type: str  # ioc, vulnerability, configuration, behavior
    action: PreventionAction
    severity: str
    confidence: float
    conditions: Dict[str, Any]
    mitigations: List[str]
    enabled: bool
    created_at: datetime
    updated_at: datetime
    expiry_date: Optional[datetime]

@dataclass  
class IOCBlocklist:
    """Indicator of Compromise blocklist entry"""
    ioc_id: str
    ioc_type: str  # ip, domain, hash, url, email
    ioc_value: str
    threat_id: str
    severity: str
    confidence: float
    source: str
    first_seen: datetime
    last_seen: datetime
    block_action: str
    notes: str

@dataclass
class VulnerabilityPatch:
    """Vulnerability patch information"""
    patch_id: str
    cve_id: str
    affected_systems: List[str]
    patch_available: bool
    patch_url: str
    patch_priority: str
    patch_complexity: str
    estimated_downtime: int  # minutes
    deployment_method: str
    rollback_plan: str
    testing_required: bool
    scheduled_deployment: Optional[datetime]

@dataclass
class AttackSurfaceAsset:
    """Attack surface asset tracking"""
    asset_id: str
    asset_type: str
    asset_name: str
    ip_addresses: List[str]
    open_ports: List[int]
    services: List[str]
    vulnerabilities: List[str]
    security_score: float
    exposure_level: str
    last_scanned: datetime
    recommended_actions: List[str]

class ThreatPreventionEngine:
    """
    Threat Prevention Engine
    
    Provides comprehensive proactive threat prevention including:
    - IOC blocking and filtering
    - Vulnerability patching management  
    - Attack surface monitoring
    - Proactive threat hunting
    - Security hardening automation
    """
    
    def __init__(self, data_dir: str = "../../../", config_path: str = None):
        self.data_dir = Path(data_dir)
        self.config_path = config_path
        
        # Initialize local storage
        self.db_path = self.data_dir / "threat_prevention.db"
        self._init_local_db()
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize blocklists and rules
        self.ioc_blocklist = {}
        self.prevention_rules = {}
        self.vulnerability_patches = {}
        self.attack_surface = {}
        
        # Load existing data
        self._load_prevention_data()
        
        logger.info("Threat Prevention Engine initialized")
    
    def _init_local_db(self):
        """Initialize local SQLite database for prevention data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # IOC blocklist table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ioc_blocklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ioc_id TEXT UNIQUE NOT NULL,
                ioc_type TEXT,
                ioc_value TEXT,
                threat_id TEXT,
                severity TEXT,
                confidence REAL,
                source TEXT,
                first_seen TEXT,
                last_seen TEXT,
                block_action TEXT,
                notes TEXT
            )
        ''')
        
        # Prevention rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prevention_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT UNIQUE NOT NULL,
                name TEXT,
                description TEXT,
                rule_type TEXT,
                action TEXT,
                severity TEXT,
                confidence REAL,
                conditions_json TEXT,
                mitigations_json TEXT,
                enabled INTEGER,
                created_at TEXT,
                updated_at TEXT,
                expiry_date TEXT
            )
        ''')
        
        # Vulnerability patches table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vulnerability_patches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patch_id TEXT UNIQUE NOT NULL,
                cve_id TEXT,
                affected_systems_json TEXT,
                patch_available INTEGER,
                patch_url TEXT,
                patch_priority TEXT,
                patch_complexity TEXT,
                estimated_downtime INTEGER,
                deployment_method TEXT,
                rollback_plan TEXT,
                testing_required INTEGER,
                scheduled_deployment TEXT
            )
        ''')
        
        # Attack surface assets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attack_surface_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id TEXT UNIQUE NOT NULL,
                asset_type TEXT,
                asset_name TEXT,
                ip_addresses_json TEXT,
                open_ports_json TEXT,
                services_json TEXT,
                vulnerabilities_json TEXT,
                security_score REAL,
                exposure_level TEXT,
                last_scanned TEXT,
                recommended_actions_json TEXT
            )
        ''')
        
        # Prevention actions log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prevention_actions_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_id TEXT,
                action_type TEXT,
                target TEXT,
                action_taken TEXT,
                result TEXT,
                timestamp TEXT,
                details_json TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load prevention configuration"""
        default_config = {
            'ioc_sources': ['local', 'misp', 'otx', 'virustotal'],
            'block_thresholds': {
                'ip': 0.7,
                'domain': 0.8, 
                'hash': 0.9,
                'url': 0.7,
                'email': 0.6
            },
            'patch_priorities': {
                'Critical': 24,  # hours
                'High': 72,
                'Medium': 168,  # 1 week
                'Low': 720  # 1 month
            },
            'scan_intervals': {
                'vulnerability': 24,  # hours
                'attack_surface': 12,
                'threat_hunting': 6
            },
            'notification_settings': {
                'email': True,
                'sms': False,
                'webhook': True
            }
        }
        
        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config file: {e}")
        
        return default_config
    
    def _load_prevention_data(self):
        """Load existing prevention data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Load IOC blocklist
            blocklist_df = pd.read_sql_query("SELECT * FROM ioc_blocklist", conn)
            for _, row in blocklist_df.iterrows():
                ioc = IOCBlocklist(
                    ioc_id=row['ioc_id'],
                    ioc_type=row['ioc_type'],
                    ioc_value=row['ioc_value'],
                    threat_id=row['threat_id'],
                    severity=row['severity'],
                    confidence=row['confidence'],
                    source=row['source'],
                    first_seen=datetime.fromisoformat(row['first_seen']),
                    last_seen=datetime.fromisoformat(row['last_seen']),
                    block_action=row['block_action'],
                    notes=row['notes']
                )
                self.ioc_blocklist[row['ioc_id']] = ioc
            
            # Load prevention rules
            rules_df = pd.read_sql_query("SELECT * FROM prevention_rules", conn)
            for _, row in rules_df.iterrows():
                rule = PreventionRule(
                    rule_id=row['rule_id'],
                    name=row['name'],
                    description=row['description'],
                    rule_type=row['rule_type'],
                    action=PreventionAction(row['action']),
                    severity=row['severity'],
                    confidence=row['confidence'],
                    conditions=json.loads(row['conditions_json']),
                    mitigations=json.loads(row['mitigations_json']),
                    enabled=bool(row['enabled']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    expiry_date=datetime.fromisoformat(row['expiry_date']) if row['expiry_date'] else None
                )
                self.prevention_rules[row['rule_id']] = rule
            
            conn.close()
            logger.info(f"Loaded {len(self.ioc_blocklist)} IOCs and {len(self.prevention_rules)} rules")
            
        except Exception as e:
            logger.error(f"Error loading prevention data: {e}")
    
    def add_ioc_to_blocklist(self, ioc_type: str, ioc_value: str, threat_id: str, 
                           severity: str = "Medium", confidence: float = 0.8,
                           source: str = "manual", notes: str = "") -> str:
        """
        Add IOC to blocklist for prevention
        
        Args:
            ioc_type: Type of IOC (ip, domain, hash, url, email)
            ioc_value: The actual IOC value
            threat_id: Associated threat ID
            severity: Severity level
            confidence: Confidence score
            source: Source of the IOC
            notes: Additional notes
            
        Returns:
            IOC ID
        """
        # Generate IOC ID
        ioc_id = f"IOC_{hashlib.md5(f'{ioc_type}_{ioc_value}'.encode()).hexdigest()[:8]}"
        
        # Validate IOC format
        if not self._validate_ioc(ioc_type, ioc_value):
            raise ValueError(f"Invalid IOC format: {ioc_type}:{ioc_value}")
        
        # Determine block action based on confidence and severity
        block_action = self._determine_block_action(ioc_type, severity, confidence)
        
        # Create IOC entry
        ioc_entry = IOCBlocklist(
            ioc_id=ioc_id,
            ioc_type=ioc_type,
            ioc_value=ioc_value,
            threat_id=threat_id,
            severity=severity,
            confidence=confidence,
            source=source,
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            block_action=block_action,
            notes=notes
        )
        
        # Add to memory and database
        self.ioc_blocklist[ioc_id] = ioc_entry
        self._cache_ioc_blocklist_entry(ioc_entry)
        
        # Deploy blocking rule
        self._deploy_ioc_block(ioc_entry)
        
        logger.info(f"Added IOC {ioc_id} ({ioc_type}:{ioc_value}) to blocklist with action {block_action}")
        return ioc_id
    
    def create_prevention_rule(self, name: str, description: str, rule_type: str,
                             action: PreventionAction, conditions: Dict[str, Any],
                             severity: str = "Medium", confidence: float = 0.8,
                             mitigations: List[str] = None,
                             expiry_hours: Optional[int] = None) -> str:
        """
        Create a new prevention rule
        
        Args:
            name: Rule name
            description: Rule description
            rule_type: Type of rule (ioc, vulnerability, configuration, behavior)
            action: Action to take when rule matches
            conditions: Rule conditions
            severity: Severity level
            confidence: Confidence score
            mitigations: List of mitigation steps
            expiry_hours: Hours until rule expires (None for no expiry)
            
        Returns:
            Rule ID
        """
        # Generate rule ID
        rule_id = f"RULE_{hashlib.md5(f'{name}_{rule_type}'.encode()).hexdigest()[:8]}"
        
        # Set expiry date
        expiry_date = None
        if expiry_hours:
            expiry_date = datetime.now() + timedelta(hours=expiry_hours)
        
        # Create rule
        rule = PreventionRule(
            rule_id=rule_id,
            name=name,
            description=description,
            rule_type=rule_type,
            action=action,
            severity=severity,
            confidence=confidence,
            conditions=conditions,
            mitigations=mitigations or [],
            enabled=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            expiry_date=expiry_date
        )
        
        # Add to memory and database
        self.prevention_rules[rule_id] = rule
        self._cache_prevention_rule(rule)
        
        # Deploy rule
        self._deploy_prevention_rule(rule)
        
        logger.info(f"Created prevention rule {rule_id}: {name}")
        return rule_id
    
    def manage_vulnerability_patches(self) -> List[VulnerabilityPatch]:
        """
        Manage vulnerability patches based on threat intelligence
        
        Returns:
            List of vulnerability patches to deploy
        """
        patches = []
        
        # Load CVE data from threat intelligence
        cve_data = self._load_cve_data()
        
        for cve in cve_data:
            cve_id = cve.get('cve_id')
            if not cve_id:
                continue
            
            # Check if patch is needed
            if self._requires_patching(cve):
                patch = self._create_patch_plan(cve)
                patches.append(patch)
                self.vulnerability_patches[patch.patch_id] = patch
                self._cache_vulnerability_patch(patch)
        
        # Prioritize patches
        patches = self._prioritize_patches(patches)
        
        # Schedule deployments
        for patch in patches[:10]:  # Limit to top 10 for safety
            self._schedule_patch_deployment(patch)
        
        logger.info(f"Managed {len(patches)} vulnerability patches")
        return patches
    
    def monitor_attack_surface(self) -> Dict[str, AttackSurfaceAsset]:
        """
        Monitor and analyze attack surface
        
        Returns:
            Dictionary of attack surface assets
        """
        assets = {}
        
        # Load asset data (simplified - would integrate with asset discovery)
        asset_data = self._discover_assets()
        
        for asset_info in asset_data:
            asset_id = asset_info['id']
            
            # Scan asset for vulnerabilities and exposure
            scan_results = self._scan_asset(asset_info)
            
            # Calculate security score
            security_score = self._calculate_security_score(scan_results)
            
            # Determine exposure level
            exposure_level = self._determine_exposure_level(scan_results, security_score)
            
            # Generate recommendations
            recommendations = self._generate_asset_recommendations(scan_results)
            
            asset = AttackSurfaceAsset(
                asset_id=asset_id,
                asset_type=asset_info.get('type', 'unknown'),
                asset_name=asset_info.get('name', ''),
                ip_addresses=asset_info.get('ip_addresses', []),
                open_ports=scan_results.get('open_ports', []),
                services=scan_results.get('services', []),
                vulnerabilities=scan_results.get('vulnerabilities', []),
                security_score=security_score,
                exposure_level=exposure_level,
                last_scanned=datetime.now(),
                recommended_actions=recommendations
            )
            
            assets[asset_id] = asset
            self.attack_surface[asset_id] = asset
            self._cache_attack_surface_asset(asset)
        
        logger.info(f"Monitored {len(assets)} attack surface assets")
        return assets
    
    def conduct_threat_hunting(self, hunt_type: str = "proactive") -> Dict[str, Any]:
        """
        Conduct proactive threat hunting
        
        Args:
            hunt_type: Type of hunt (proactive, reactive, intelligence_driven)
            
        Returns:
            Threat hunting results
        """
        results = {
            'hunt_id': f"HUNT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'hunt_type': hunt_type,
            'start_time': datetime.now(),
            'hypotheses': [],
            'findings': [],
            'iocs_discovered': [],
            'recommendations': []
        }
        
        # Generate hunting hypotheses based on threat intelligence
        hypotheses = self._generate_hunting_hypotheses()
        results['hypotheses'] = hypotheses
        
        # Execute hunting queries for each hypothesis
        for hypothesis in hypotheses:
            findings = self._execute_hunting_query(hypothesis)
            results['findings'].extend(findings)
        
        # Analyze findings for new IOCs
        new_iocs = self._extract_iocs_from_findings(results['findings'])
        results['iocs_discovered'] = new_iocs
        
        # Add new IOCs to blocklist
        for ioc in new_iocs:
            self.add_ioc_to_blocklist(
                ioc_type=ioc['type'],
                ioc_value=ioc['value'],
                threat_id=f"HUNT_{results['hunt_id']}",
                severity="Medium",
                confidence=0.6,
                source="threat_hunting",
                notes=f"Discovered during hunt {results['hunt_id']}"
            )
        
        # Generate recommendations
        results['recommendations'] = self._generate_hunting_recommendations(results)
        results['end_time'] = datetime.now()
        
        # Log hunting session
        self._log_hunting_session(results)
        
        logger.info(f"Completed threat hunt {results['hunt_id']}, found {len(new_iocs)} new IOCs")
        return results
    
    def evaluate_ioc_blocking_effectiveness(self) -> Dict[str, Any]:
        """
        Evaluate effectiveness of IOC blocking
        
        Returns:
            Effectiveness metrics and recommendations
        """
        metrics = {
            'total_iocs': len(self.ioc_blocklist),
            'blocked_attempts': 0,
            'false_positives': 0,
            'coverage_by_type': defaultdict(int),
            'effectiveness_score': 0.0,
            'recommendations': []
        }
        
        # Analyze IOC coverage
        for ioc in self.ioc_blocklist.values():
            metrics['coverage_by_type'][ioc.ioc_type] += 1
        
        # Calculate blocking effectiveness (simplified)
        # In real implementation, would analyze actual blocking logs
        total_weight = sum(self.config['block_thresholds'].values())
        weighted_score = 0.0
        
        for ioc_type, count in metrics['coverage_by_type'].items():
            if ioc_type in self.config['block_thresholds']:
                weight = self.config['block_thresholds'][ioc_type]
                # Assume effectiveness based on IOC count and confidence
                type_effectiveness = min(1.0, count / 100.0)  # Normalize to reasonable scale
                weighted_score += weight * type_effectiveness
        
        metrics['effectiveness_score'] = weighted_score / total_weight if total_weight > 0 else 0.0
        
        # Generate recommendations
        if metrics['effectiveness_score'] < 0.6:
            metrics['recommendations'].append("Increase IOC collection and blocking rules")
        
        for ioc_type, threshold in self.config['block_thresholds'].items():
            if metrics['coverage_by_type'][ioc_type] < 10:
                metrics['recommendations'].append(f"Improve {ioc_type} IOC coverage")
        
        return metrics
    
    def update_prevention_rules(self) -> int:
        """
        Update prevention rules based on new threat intelligence
        
        Returns:
            Number of rules updated
        """
        updated_count = 0
        
        # Check for expired rules
        current_time = datetime.now()
        for rule_id, rule in list(self.prevention_rules.items()):
            if rule.expiry_date and current_time > rule.expiry_date:
                self._disable_prevention_rule(rule_id)
                updated_count += 1
        
        # Update rules based on new threat intelligence
        # (This would integrate with the threat intelligence engine)
        
        # Update IOC blocklist from external sources
        new_iocs = self._fetch_external_iocs()
        for ioc_data in new_iocs:
            try:
                self.add_ioc_to_blocklist(**ioc_data)
                updated_count += 1
            except Exception as e:
                logger.warning(f"Failed to add IOC: {e}")
        
        logger.info(f"Updated {updated_count} prevention rules")
        return updated_count
    
    # Helper methods
    
    def _validate_ioc(self, ioc_type: str, ioc_value: str) -> bool:
        """Validate IOC format"""
        validators = {
            'ip': self._validate_ip,
            'domain': self._validate_domain,
            'hash': self._validate_hash,
            'url': self._validate_url,
            'email': self._validate_email
        }
        
        validator = validators.get(ioc_type)
        if validator:
            return validator(ioc_value)
        
        return False
    
    def _validate_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def _validate_domain(self, domain: str) -> bool:
        """Validate domain format"""
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return re.match(domain_pattern, domain) is not None
    
    def _validate_hash(self, hash_value: str) -> bool:
        """Validate hash format (MD5, SHA1, SHA256)"""
        hash_patterns = [
            r'^[a-f0-9]{32}$',  # MD5
            r'^[a-f0-9]{40}$',  # SHA1
            r'^[a-f0-9]{64}$'   # SHA256
        ]
        
        return any(re.match(pattern, hash_value, re.IGNORECASE) for pattern in hash_patterns)
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format"""
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return re.match(url_pattern, url) is not None
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    def _determine_block_action(self, ioc_type: str, severity: str, confidence: float) -> str:
        """Determine what blocking action to take"""
        threshold = self.config['block_thresholds'].get(ioc_type, 0.7)
        
        if confidence >= threshold:
            if severity in ['Critical', 'High']:
                return 'block'
            else:
                return 'alert'
        else:
            return 'monitor'
    
    def _deploy_ioc_block(self, ioc_entry: IOCBlocklist):
        """Deploy IOC blocking rule to security infrastructure"""
        # This would integrate with firewalls, DNS filters, proxies, etc.
        logger.info(f"Deploying {ioc_entry.block_action} for {ioc_entry.ioc_type}:{ioc_entry.ioc_value}")
        
        # Log the action
        self._log_prevention_action(
            action_type="ioc_block",
            target=f"{ioc_entry.ioc_type}:{ioc_entry.ioc_value}",
            action_taken=ioc_entry.block_action,
            result="deployed",
            details={'ioc_id': ioc_entry.ioc_id, 'confidence': ioc_entry.confidence}
        )
    
    def _deploy_prevention_rule(self, rule: PreventionRule):
        """Deploy prevention rule to security infrastructure"""
        # This would integrate with SIEM, EDR, network security tools
        logger.info(f"Deploying prevention rule {rule.rule_id}: {rule.name}")
        
        # Log the action
        self._log_prevention_action(
            action_type="rule_deploy",
            target=rule.rule_id,
            action_taken=rule.action.value,
            result="deployed",
            details={'rule_type': rule.rule_type, 'severity': rule.severity}
        )
    
    def _load_cve_data(self) -> List[Dict[str, Any]]:
        """Load CVE data for patch management"""
        # This would integrate with the threat intelligence engine
        try:
            cve_file = self.data_dir / "cve_data_with_use_cases.json"
            if cve_file.exists():
                with open(cve_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading CVE data: {e}")
        
        return []
    
    def _requires_patching(self, cve: Dict[str, Any]) -> bool:
        """Determine if CVE requires immediate patching"""
        severity = cve.get('severity', '').lower()
        
        # High priority conditions
        if 'critical' in severity or 'high' in severity:
            return True
        
        # Check for exploit availability
        description = cve.get('description', '').lower()
        if 'exploit' in description or 'poc' in description:
            return True
        
        # Check CVSS score
        cvss_score = cve.get('cvss_score', 0)
        if cvss_score >= 7.0:
            return True
        
        return False
    
    def _create_patch_plan(self, cve: Dict[str, Any]) -> VulnerabilityPatch:
        """Create patch deployment plan for CVE"""
        patch_id = f"PATCH_{cve.get('cve_id', 'unknown')}"
        
        # Determine affected systems (simplified)
        affected_systems = self._find_affected_systems(cve)
        
        # Calculate patch priority and complexity
        severity = cve.get('severity', 'Medium')
        priority_hours = self.config['patch_priorities'].get(severity, 168)
        
        patch = VulnerabilityPatch(
            patch_id=patch_id,
            cve_id=cve.get('cve_id', ''),
            affected_systems=affected_systems,
            patch_available=True,  # Assume available for now
            patch_url=cve.get('patch_url', ''),
            patch_priority=severity,
            patch_complexity='Medium',  # Would be determined by analysis
            estimated_downtime=30,  # minutes
            deployment_method='automated',
            rollback_plan='snapshot_restore',
            testing_required=len(affected_systems) > 5,
            scheduled_deployment=datetime.now() + timedelta(hours=priority_hours)
        )
        
        return patch
    
    def _find_affected_systems(self, cve: Dict[str, Any]) -> List[str]:
        """Find systems affected by CVE"""
        # This would integrate with asset management and vulnerability scanning
        # For now, return sample systems
        return ['server01', 'server02', 'workstation01']
    
    def _prioritize_patches(self, patches: List[VulnerabilityPatch]) -> List[VulnerabilityPatch]:
        """Prioritize patches by risk and impact"""
        priority_order = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
        
        return sorted(patches, 
                     key=lambda p: (priority_order.get(p.patch_priority, 0), 
                                  len(p.affected_systems)), 
                     reverse=True)
    
    def _schedule_patch_deployment(self, patch: VulnerabilityPatch):
        """Schedule patch deployment"""
        logger.info(f"Scheduled patch {patch.patch_id} for {patch.scheduled_deployment}")
        
        # This would integrate with deployment automation tools
        self._log_prevention_action(
            action_type="patch_schedule",
            target=patch.cve_id,
            action_taken="schedule",
            result="scheduled",
            details={'patch_id': patch.patch_id, 'deployment_time': patch.scheduled_deployment.isoformat()}
        )
    
    def _discover_assets(self) -> List[Dict[str, Any]]:
        """Discover network assets"""
        # This would integrate with network discovery tools
        # For now, return sample assets
        return [
            {
                'id': 'asset_001',
                'name': 'Web Server',
                'type': 'server',
                'ip_addresses': ['192.168.1.100']
            },
            {
                'id': 'asset_002', 
                'name': 'Database Server',
                'type': 'database',
                'ip_addresses': ['192.168.1.101']
            }
        ]
    
    def _scan_asset(self, asset_info: Dict[str, Any]) -> Dict[str, Any]:
        """Scan asset for vulnerabilities and configuration"""
        # This would integrate with vulnerability scanners
        # For now, return sample scan results
        return {
            'open_ports': [22, 80, 443],
            'services': ['ssh', 'nginx', 'mysql'],
            'vulnerabilities': ['CVE-2024-1234', 'CVE-2024-5678'],
            'configuration_issues': ['weak_password_policy', 'missing_encryption']
        }
    
    def _calculate_security_score(self, scan_results: Dict[str, Any]) -> float:
        """Calculate security score for asset"""
        base_score = 1.0
        
        # Deduct for vulnerabilities
        vuln_count = len(scan_results.get('vulnerabilities', []))
        base_score -= min(0.5, vuln_count * 0.1)
        
        # Deduct for configuration issues
        config_issues = len(scan_results.get('configuration_issues', []))
        base_score -= min(0.3, config_issues * 0.05)
        
        # Deduct for unnecessary open ports
        open_ports = len(scan_results.get('open_ports', []))
        if open_ports > 5:
            base_score -= min(0.2, (open_ports - 5) * 0.02)
        
        return max(0.0, base_score)
    
    def _determine_exposure_level(self, scan_results: Dict[str, Any], security_score: float) -> str:
        """Determine asset exposure level"""
        if security_score >= 0.8:
            return 'Low'
        elif security_score >= 0.6:
            return 'Medium'
        elif security_score >= 0.4:
            return 'High'
        else:
            return 'Critical'
    
    def _generate_asset_recommendations(self, scan_results: Dict[str, Any]) -> List[str]:
        """Generate security recommendations for asset"""
        recommendations = []
        
        vulnerabilities = scan_results.get('vulnerabilities', [])
        if vulnerabilities:
            recommendations.append(f"Patch {len(vulnerabilities)} vulnerabilities")
        
        config_issues = scan_results.get('configuration_issues', [])
        if 'weak_password_policy' in config_issues:
            recommendations.append("Strengthen password policy")
        if 'missing_encryption' in config_issues:
            recommendations.append("Enable encryption")
        
        open_ports = scan_results.get('open_ports', [])
        if len(open_ports) > 5:
            recommendations.append("Close unnecessary ports")
        
        return recommendations
    
    def _generate_hunting_hypotheses(self) -> List[Dict[str, Any]]:
        """Generate threat hunting hypotheses"""
        hypotheses = [
            {
                'id': 'H001',
                'name': 'Lateral Movement Detection',
                'description': 'Detect unusual network connections between internal systems',
                'query_type': 'network_analysis',
                'confidence': 0.7
            },
            {
                'id': 'H002', 
                'name': 'Privilege Escalation Attempts',
                'description': 'Look for unusual privilege changes or admin account usage',
                'query_type': 'account_analysis',
                'confidence': 0.8
            },
            {
                'id': 'H003',
                'name': 'Data Exfiltration Patterns',
                'description': 'Identify unusual data transfer patterns',
                'query_type': 'data_flow_analysis',
                'confidence': 0.6
            }
        ]
        
        return hypotheses
    
    def _execute_hunting_query(self, hypothesis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute hunting query for hypothesis"""
        # This would integrate with SIEM/log analysis tools
        # For now, return sample findings
        findings = []
        
        if hypothesis['query_type'] == 'network_analysis':
            findings = [
                {
                    'type': 'network_anomaly',
                    'description': 'Unusual connection from server01 to server02',
                    'severity': 'Medium',
                    'indicators': ['192.168.1.100', '192.168.1.101'],
                    'timestamp': datetime.now().isoformat()
                }
            ]
        
        return findings
    
    def _extract_iocs_from_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract IOCs from hunting findings"""
        iocs = []
        
        for finding in findings:
            indicators = finding.get('indicators', [])
            for indicator in indicators:
                # Determine IOC type
                ioc_type = 'unknown'
                if self._validate_ip(indicator):
                    ioc_type = 'ip'
                elif self._validate_domain(indicator):
                    ioc_type = 'domain'
                elif self._validate_hash(indicator):
                    ioc_type = 'hash'
                
                if ioc_type != 'unknown':
                    iocs.append({
                        'type': ioc_type,
                        'value': indicator,
                        'source_finding': finding.get('type', 'unknown')
                    })
        
        return iocs
    
    def _generate_hunting_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on hunting results"""
        recommendations = []
        
        findings_count = len(results['findings'])
        iocs_count = len(results['iocs_discovered'])
        
        if findings_count > 0:
            recommendations.append(f"Investigate {findings_count} suspicious findings")
        
        if iocs_count > 0:
            recommendations.append(f"Monitor {iocs_count} new IOCs discovered")
        
        if findings_count == 0:
            recommendations.append("Expand hunting scope or update hypotheses")
        
        return recommendations
    
    def _fetch_external_iocs(self) -> List[Dict[str, Any]]:
        """Fetch IOCs from external threat intelligence sources"""
        # This would integrate with threat intel feeds
        # For now, return empty list
        return []
    
    def _disable_prevention_rule(self, rule_id: str):
        """Disable expired prevention rule"""
        if rule_id in self.prevention_rules:
            self.prevention_rules[rule_id].enabled = False
            self.prevention_rules[rule_id].updated_at = datetime.now()
            
            # Update in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE prevention_rules SET enabled = 0, updated_at = ? WHERE rule_id = ?",
                (datetime.now().isoformat(), rule_id)
            )
            conn.commit()
            conn.close()
            
            logger.info(f"Disabled expired rule {rule_id}")
    
    def _log_prevention_action(self, action_type: str, target: str, action_taken: str, 
                             result: str, details: Dict[str, Any] = None):
        """Log prevention action"""
        action_id = f"ACT_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO prevention_actions_log
            (action_id, action_type, target, action_taken, result, timestamp, details_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            action_id,
            action_type,
            target,
            action_taken,
            result,
            datetime.now().isoformat(),
            json.dumps(details or {})
        ))
        
        conn.commit()
        conn.close()
    
    def _log_hunting_session(self, results: Dict[str, Any]):
        """Log threat hunting session"""
        self._log_prevention_action(
            action_type="threat_hunting",
            target=results['hunt_type'],
            action_taken="hunt",
            result="completed",
            details={
                'hunt_id': results['hunt_id'],
                'hypotheses_count': len(results['hypotheses']),
                'findings_count': len(results['findings']),
                'iocs_found': len(results['iocs_discovered'])
            }
        )
    
    # Database caching methods
    
    def _cache_ioc_blocklist_entry(self, ioc: IOCBlocklist):
        """Cache IOC in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO ioc_blocklist
            (ioc_id, ioc_type, ioc_value, threat_id, severity, confidence, source,
             first_seen, last_seen, block_action, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ioc.ioc_id, ioc.ioc_type, ioc.ioc_value, ioc.threat_id,
            ioc.severity, ioc.confidence, ioc.source,
            ioc.first_seen.isoformat(), ioc.last_seen.isoformat(),
            ioc.block_action, ioc.notes
        ))
        
        conn.commit()
        conn.close()
    
    def _cache_prevention_rule(self, rule: PreventionRule):
        """Cache prevention rule in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO prevention_rules
            (rule_id, name, description, rule_type, action, severity, confidence,
             conditions_json, mitigations_json, enabled, created_at, updated_at, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rule.rule_id, rule.name, rule.description, rule.rule_type,
            rule.action.value, rule.severity, rule.confidence,
            json.dumps(rule.conditions), json.dumps(rule.mitigations),
            int(rule.enabled), rule.created_at.isoformat(),
            rule.updated_at.isoformat(),
            rule.expiry_date.isoformat() if rule.expiry_date else None
        ))
        
        conn.commit()
        conn.close()
    
    def _cache_vulnerability_patch(self, patch: VulnerabilityPatch):
        """Cache vulnerability patch in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO vulnerability_patches
            (patch_id, cve_id, affected_systems_json, patch_available, patch_url,
             patch_priority, patch_complexity, estimated_downtime, deployment_method,
             rollback_plan, testing_required, scheduled_deployment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            patch.patch_id, patch.cve_id, json.dumps(patch.affected_systems),
            int(patch.patch_available), patch.patch_url, patch.patch_priority,
            patch.patch_complexity, patch.estimated_downtime, patch.deployment_method,
            patch.rollback_plan, int(patch.testing_required),
            patch.scheduled_deployment.isoformat() if patch.scheduled_deployment else None
        ))
        
        conn.commit()
        conn.close()
    
    def _cache_attack_surface_asset(self, asset: AttackSurfaceAsset):
        """Cache attack surface asset in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO attack_surface_assets
            (asset_id, asset_type, asset_name, ip_addresses_json, open_ports_json,
             services_json, vulnerabilities_json, security_score, exposure_level,
             last_scanned, recommended_actions_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            asset.asset_id, asset.asset_type, asset.asset_name,
            json.dumps(asset.ip_addresses), json.dumps(asset.open_ports),
            json.dumps(asset.services), json.dumps(asset.vulnerabilities),
            asset.security_score, asset.exposure_level,
            asset.last_scanned.isoformat(), json.dumps(asset.recommended_actions)
        ))
        
        conn.commit()
        conn.close()


# Example usage and testing
if __name__ == "__main__":
    # Initialize the engine
    engine = ThreatPreventionEngine(data_dir="../../../")
    
    try:
        # Add IOCs to blocklist
        ioc1 = engine.add_ioc_to_blocklist(
            ioc_type="ip",
            ioc_value="192.168.1.100",
            threat_id="THREAT_001",
            severity="High",
            confidence=0.9,
            source="threat_intel",
            notes="Known malicious IP"
        )
        print(f"Added IOC: {ioc1}")
        
        # Create prevention rule
        rule1 = engine.create_prevention_rule(
            name="Block Suspicious Network Traffic",
            description="Block traffic from known malicious IPs",
            rule_type="ioc",
            action=PreventionAction.BLOCK,
            conditions={'ioc_type': 'ip', 'confidence_threshold': 0.8},
            severity="High",
            confidence=0.9,
            expiry_hours=168  # 1 week
        )
        print(f"Created rule: {rule1}")
        
        # Manage vulnerability patches
        patches = engine.manage_vulnerability_patches()
        print(f"Managed {len(patches)} patches")
        
        # Monitor attack surface
        assets = engine.monitor_attack_surface()
        print(f"Monitored {len(assets)} assets")
        
        # Conduct threat hunting
        hunt_results = engine.conduct_threat_hunting("proactive")
        print(f"Hunt completed: {hunt_results['hunt_id']}")
        
        # Evaluate effectiveness
        effectiveness = engine.evaluate_ioc_blocking_effectiveness()
        print(f"IOC blocking effectiveness: {effectiveness['effectiveness_score']:.2f}")
        
        # Update prevention rules
        updates = engine.update_prevention_rules()
        print(f"Updated {updates} prevention rules")
        
    except Exception as e:
        logger.error(f"Error in prevention engine: {e}")
        raise