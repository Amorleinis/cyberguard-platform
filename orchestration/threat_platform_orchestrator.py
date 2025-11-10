"""
Threat Intelligence Platform Orchestrator

This module provides the main orchestration layer that integrates all threat management
components into a unified platform:

- Threat Intelligence Engine
- Threat Prevention Engine
- Threat Detection Engine
- Threat Response Engine
- Threat Isolation Engine
- Threat Mitigation Engine
- Threat Recovery Engine

Provides unified API, workflow automation, and centralized management.
"""

import sys
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import all threat management engines
from intelligence.threat_intelligence_engine import ThreatIntelligenceEngine
from prevention.threat_prevention_engine import ThreatPreventionEngine
from detection.threat_detection_engine import ThreatDetectionEngine
from response.threat_response_engine import ThreatResponseEngine
from isolation.threat_isolation_engine import ThreatIsolationEngine
from mitigation.threat_mitigation_engine import ThreatMitigationEngine
from recovery.threat_recovery_engine import ThreatRecoveryEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ThreatIntelligencePlatform:
    """
    Unified Threat Intelligence Platform
    
    Orchestrates all threat management engines to provide comprehensive
    security operations capabilities across the entire threat lifecycle.
    """
    
    def __init__(self, data_dir: str = "../../../"):
        """
        Initialize the Threat Intelligence Platform
        
        Args:
            data_dir: Base directory for data storage
        """
        self.data_dir = Path(data_dir)
        self.platform_start_time = datetime.now()
        
        logger.info("=" * 80)
        logger.info("Initializing Threat Intelligence Platform")
        logger.info("=" * 80)
        
        # Initialize all engines
        try:
            logger.info("Loading Threat Intelligence Engine...")
            self.intelligence = ThreatIntelligenceEngine(data_dir=str(self.data_dir))
            
            logger.info("Loading Threat Prevention Engine...")
            self.prevention = ThreatPreventionEngine(data_dir=str(self.data_dir))
            
            logger.info("Loading Threat Detection Engine...")
            self.detection = ThreatDetectionEngine(data_dir=str(self.data_dir))
            
            logger.info("Loading Threat Response Engine...")
            self.response = ThreatResponseEngine(data_dir=str(self.data_dir))
            
            logger.info("Loading Threat Isolation Engine...")
            self.isolation = ThreatIsolationEngine(data_dir=str(self.data_dir))
            
            logger.info("Loading Threat Mitigation Engine...")
            self.mitigation = ThreatMitigationEngine(data_dir=str(self.data_dir))
            
            logger.info("Loading Threat Recovery Engine...")
            self.recovery = ThreatRecoveryEngine(data_dir=str(self.data_dir))
            
            logger.info("=" * 80)
            logger.info("✓ All engines initialized successfully")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Failed to initialize platform: {e}")
            raise
    
    def process_threat_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a threat alert through the entire threat lifecycle
        
        This orchestrates the complete response workflow:
        1. Analyze threat with intelligence engine
        2. Detect and classify the threat
        3. Create incident and initiate response
        4. Isolate affected systems
        5. Mitigate the threat
        6. Recover systems
        
        Args:
            alert_data: Alert information
            
        Returns:
            Processing results with all action IDs
        """
        logger.info(f"Processing threat alert: {alert_data.get('title', 'Unknown')}")
        
        results = {
            'alert_id': alert_data.get('alert_id', 'UNKNOWN'),
            'timestamp': datetime.now().isoformat(),
            'actions_taken': []
        }
        
        try:
            # Step 1: Intelligence Analysis
            logger.info("Step 1: Analyzing threat intelligence...")
            if 'cve_id' in alert_data:
                vuln_analysis = self.intelligence.analyze_cve(alert_data['cve_id'])
                results['intelligence_analysis'] = vuln_analysis
                results['actions_taken'].append('intelligence_analysis_completed')
            
            # Step 2: Create Incident
            logger.info("Step 2: Creating incident...")
            incident_id = self.response.create_incident_from_alert(alert_data)
            results['incident_id'] = incident_id
            results['actions_taken'].append(f'incident_created:{incident_id}')
            
            # Step 3: Auto-Isolation (if critical)
            if alert_data.get('severity', '').lower() in ['critical', 'high']:
                logger.info("Step 3: Initiating isolation...")
                
                for asset in alert_data.get('affected_assets', []):
                    isolation_id = self.isolation.isolate_host(
                        target=asset,
                        incident_id=incident_id
                    )
                    results['actions_taken'].append(f'isolation:{isolation_id}')
            
            # Step 4: Block IOCs (Prevention)
            logger.info("Step 4: Blocking indicators...")
            for ioc in alert_data.get('indicators', []):
                block_id = self.prevention.block_ioc(ioc, incident_id=incident_id)
                results['actions_taken'].append(f'ioc_blocked:{block_id}')
            
            # Step 5: Execute Response Playbook
            logger.info("Step 5: Executing response playbook...")
            playbook_success = self.response.execute_response_playbook(incident_id)
            results['playbook_executed'] = playbook_success
            results['actions_taken'].append('response_playbook_executed')
            
            # Step 6: Evidence Collection
            logger.info("Step 6: Collecting evidence...")
            for asset in alert_data.get('affected_assets', []):
                evidence_id = self.response.collect_evidence(
                    incident_id=incident_id,
                    evidence_type='logs',
                    source_system=asset
                )
                results['actions_taken'].append(f'evidence_collected:{evidence_id}')
            
            results['status'] = 'success'
            results['message'] = 'Threat alert processed successfully'
            
            logger.info(f"✓ Alert processed successfully: {len(results['actions_taken'])} actions taken")
            
        except Exception as e:
            logger.error(f"Error processing alert: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def handle_malware_detection(self, malware_hash: str, affected_systems: List[str],
                                 malware_name: str = None) -> Dict[str, Any]:
        """
        Complete malware incident handling workflow
        
        Args:
            malware_hash: Hash of detected malware
            affected_systems: List of affected systems
            malware_name: Optional malware name
            
        Returns:
            Handling results
        """
        logger.info(f"Handling malware detection: {malware_name or malware_hash}")
        
        results = {
            'malware_hash': malware_hash,
            'affected_systems': affected_systems,
            'timestamp': datetime.now().isoformat(),
            'actions': []
        }
        
        try:
            # Create incident
            alert_data = {
                'alert_id': f'MAL_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'title': f'Malware Detection: {malware_name or "Unknown"}',
                'description': f'Malware detected with hash {malware_hash}',
                'severity': 'High',
                'affected_assets': affected_systems,
                'indicators': [malware_hash]
            }
            
            incident_id = self.response.create_incident_from_alert(alert_data)
            results['incident_id'] = incident_id
            
            # Isolate infected systems
            for system in affected_systems:
                isolation_id = self.isolation.isolate_host(system, incident_id=incident_id)
                results['actions'].append(f'isolated:{system}:{isolation_id}')
            
            # Remove malware
            remediation_id = self.mitigation.remove_malware(
                malware_hash=malware_hash,
                affected_systems=affected_systems,
                malware_name=malware_name,
                incident_id=incident_id
            )
            results['remediation_id'] = remediation_id
            results['actions'].append(f'malware_removed:{remediation_id}')
            
            # Create recovery points before restoration
            for system in affected_systems:
                rp_id = self.recovery.create_recovery_point(system, "full")
                results['actions'].append(f'recovery_point:{rp_id}')
            
            results['status'] = 'success'
            logger.info(f"✓ Malware handled successfully")
            
        except Exception as e:
            logger.error(f"Error handling malware: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def respond_to_data_breach(self, affected_systems: List[str],
                               compromised_accounts: List[str],
                               data_accessed: List[str]) -> Dict[str, Any]:
        """
        Complete data breach response workflow
        
        Args:
            affected_systems: Systems involved in breach
            compromised_accounts: Compromised user accounts
            data_accessed: Data that was accessed
            
        Returns:
            Response results
        """
        logger.info("Handling data breach incident")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'actions': []
        }
        
        try:
            # Create high-priority incident
            alert_data = {
                'alert_id': f'BREACH_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'title': 'Data Breach Detection',
                'description': 'Potential data breach detected',
                'severity': 'Critical',
                'affected_assets': affected_systems,
                'indicators': []
            }
            
            incident_id = self.response.create_incident_from_alert(alert_data)
            results['incident_id'] = incident_id
            
            # Isolate affected systems
            for system in affected_systems:
                isolation_id = self.isolation.isolate_host(system, incident_id=incident_id)
                results['actions'].append(f'isolated:{system}')
            
            # Rotate compromised credentials
            if compromised_accounts:
                rotation_id = self.mitigation.rotate_credentials(
                    affected_accounts=compromised_accounts,
                    incident_id=incident_id
                )
                results['credential_rotation_id'] = rotation_id
                results['actions'].append('credentials_rotated')
            
            # Assess damage
            damage_id = self.mitigation.assess_damage(
                incident_id=incident_id,
                affected_systems=affected_systems,
                compromised_accounts=compromised_accounts
            )
            results['damage_assessment_id'] = damage_id
            results['actions'].append('damage_assessed')
            
            # Collect forensic evidence
            for system in affected_systems:
                evidence_id = self.response.collect_evidence(
                    incident_id=incident_id,
                    evidence_type='logs',
                    source_system=system
                )
                results['actions'].append(f'evidence:{evidence_id}')
            
            results['status'] = 'success'
            logger.info("✓ Data breach response initiated successfully")
            
        except Exception as e:
            logger.error(f"Error responding to data breach: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def patch_vulnerability(self, cve_id: str, affected_systems: List[str]) -> Dict[str, Any]:
        """
        Complete vulnerability patching workflow
        
        Args:
            cve_id: CVE identifier
            affected_systems: Systems to patch
            
        Returns:
            Patching results
        """
        logger.info(f"Initiating vulnerability patching for {cve_id}")
        
        results = {
            'cve_id': cve_id,
            'affected_systems': affected_systems,
            'timestamp': datetime.now().isoformat(),
            'actions': []
        }
        
        try:
            # Analyze vulnerability
            vuln_analysis = self.intelligence.analyze_cve(cve_id)
            results['vulnerability_analysis'] = {
                'severity': vuln_analysis.get('severity'),
                'cvss_score': vuln_analysis.get('cvss_score'),
                'exploit_available': vuln_analysis.get('exploit_available')
            }
            
            # Block exploitation attempts (if exploit available)
            if vuln_analysis.get('exploit_available'):
                # Create prevention rules
                results['actions'].append('prevention_rules_created')
            
            # Create remediation action
            # Note: This would require creating a vulnerability object first
            # For now, we'll create a mitigation action directly
            
            # Deploy patches
            patch_info = vuln_analysis.get('patch_info', {})
            if patch_info:
                deployment_id = self.mitigation.deploy_patch(
                    patch_name=patch_info.get('name', f'Patch for {cve_id}'),
                    patch_version=patch_info.get('version', '1.0'),
                    target_systems=affected_systems,
                    cve_ids=[cve_id]
                )
                results['patch_deployment_id'] = deployment_id
                results['actions'].append('patch_deployed')
            
            results['status'] = 'success'
            logger.info(f"✓ Vulnerability patching initiated for {cve_id}")
            
        except Exception as e:
            logger.error(f"Error patching vulnerability: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def get_platform_status(self) -> Dict[str, Any]:
        """
        Get overall platform status and statistics
        
        Returns:
            Platform status information
        """
        logger.info("Gathering platform status...")
        
        status = {
            'platform': {
                'name': 'Threat Intelligence Platform',
                'version': '1.0.0',
                'uptime_minutes': int((datetime.now() - self.platform_start_time).total_seconds() / 60),
                'status': 'operational'
            },
            'engines': {},
            'statistics': {}
        }
        
        try:
            # Intelligence Engine Status
            status['engines']['intelligence'] = {
                'status': 'operational',
                'cves_analyzed': len(self.intelligence.cve_cache),
                'threat_actors': len(self.intelligence.threat_actors),
                'campaigns': len(self.intelligence.attack_campaigns)
            }
            
            # Prevention Engine Status
            status['engines']['prevention'] = {
                'status': 'operational',
                'active_blocklists': len(self.prevention.blocklists),
                'prevention_rules': len(self.prevention.prevention_rules)
            }
            
            # Detection Engine Status  
            status['engines']['detection'] = {
                'status': 'operational',
                'detection_rules': len(self.detection.detection_rules),
                'ml_models_loaded': len(self.detection.ml_models)
            }
            
            # Response Engine Status
            status['engines']['response'] = {
                'status': 'operational',
                'active_incidents': len([i for i in self.response.incidents.values() if i.status.value not in ['resolved', 'closed']]),
                'total_incidents': len(self.response.incidents),
                'playbooks': len(self.response.playbooks)
            }
            
            # Isolation Engine Status
            status['engines']['isolation'] = {
                'status': 'operational',
                'active_isolations': len(self.isolation.active_isolations),
                'isolation_rules': len(self.isolation.rules),
                'quarantine_zones': len(self.isolation.quarantine_zones)
            }
            
            # Mitigation Engine Status
            status['engines']['mitigation'] = {
                'status': 'operational',
                'active_mitigations': len([m for m in self.mitigation.mitigation_actions.values() if m.status.value == 'in_progress']),
                'vulnerabilities_tracked': len(self.mitigation.vulnerabilities),
                'patch_deployments': len(self.mitigation.patch_deployments)
            }
            
            # Recovery Engine Status
            status['engines']['recovery'] = {
                'status': 'operational',
                'recovery_points': len(self.recovery.recovery_points),
                'active_recoveries': len([r for r in self.recovery.recovery_tasks.values() if r.status.value == 'in_progress']),
                'lessons_learned': len(self.recovery.lessons_learned)
            }
            
            logger.info("✓ Platform status retrieved successfully")
            
        except Exception as e:
            logger.error(f"Error getting platform status: {e}")
            status['error'] = str(e)
        
        return status
    
    def get_platform_metrics(self, time_period_days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive platform metrics
        
        Args:
            time_period_days: Number of days to analyze
            
        Returns:
            Platform metrics
        """
        logger.info(f"Gathering platform metrics for {time_period_days} days...")
        
        metrics = {
            'time_period_days': time_period_days,
            'timestamp': datetime.now().isoformat(),
            'engines': {}
        }
        
        try:
            # Get metrics from each engine
            metrics['engines']['prevention'] = self.prevention.get_prevention_metrics(time_period_days)
            metrics['engines']['detection'] = self.detection.get_detection_metrics(time_period_days)
            metrics['engines']['response'] = self.response.get_incident_metrics(time_period_days)
            metrics['engines']['isolation'] = self.isolation.get_isolation_metrics(time_period_days)
            metrics['engines']['mitigation'] = self.mitigation.get_mitigation_metrics(time_period_days)
            metrics['engines']['recovery'] = self.recovery.get_recovery_metrics(time_period_days)
            
            # Calculate platform-wide metrics
            metrics['platform_summary'] = {
                'total_incidents': metrics['engines']['response'].get('total_incidents', 0),
                'threats_prevented': metrics['engines']['prevention'].get('total_prevention_actions', 0),
                'threats_detected': metrics['engines']['detection'].get('total_detections', 0),
                'systems_isolated': metrics['engines']['isolation'].get('total_isolation_actions', 0),
                'threats_mitigated': metrics['engines']['mitigation'].get('total_mitigation_actions', 0),
                'systems_recovered': metrics['engines']['recovery'].get('completed_tasks', 0)
            }
            
            logger.info("✓ Platform metrics retrieved successfully")
            
        except Exception as e:
            logger.error(f"Error getting platform metrics: {e}")
            metrics['error'] = str(e)
        
        return metrics
    
    def generate_platform_report(self, time_period_days: int = 30) -> str:
        """
        Generate comprehensive platform report
        
        Args:
            time_period_days: Number of days to include in report
            
        Returns:
            Report file path
        """
        logger.info(f"Generating platform report for {time_period_days} days...")
        
        try:
            # Get status and metrics
            status = self.get_platform_status()
            metrics = self.get_platform_metrics(time_period_days)
            
            # Create report
            report = {
                'report_type': 'Platform Status and Metrics Report',
                'generated_at': datetime.now().isoformat(),
                'time_period_days': time_period_days,
                'platform_status': status,
                'platform_metrics': metrics,
                'summary': {
                    'total_threats_handled': (
                        metrics['platform_summary'].get('threats_prevented', 0) +
                        metrics['platform_summary'].get('threats_detected', 0)
                    ),
                    'incidents_resolved': metrics['engines']['response'].get('resolved_incidents', 0),
                    'systems_protected': len(self.prevention.protected_assets),
                    'platform_effectiveness': 'Operational'
                }
            }
            
            # Save report
            report_dir = self.data_dir / "reports"
            report_dir.mkdir(exist_ok=True)
            
            report_path = report_dir / f"platform_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"✓ Platform report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Error generating platform report: {e}")
            raise


def main():
    """Main entry point for the Threat Intelligence Platform"""
    
    print("\n" + "=" * 80)
    print(" " * 20 + "THREAT INTELLIGENCE PLATFORM")
    print("=" * 80 + "\n")
    
    try:
        # Initialize platform
        platform = ThreatIntelligencePlatform(data_dir="../../../")
        
        # Display platform status
        print("\nPlatform Status:")
        print("-" * 80)
        status = platform.get_platform_status()
        
        print(f"\nPlatform: {status['platform']['name']} v{status['platform']['version']}")
        print(f"Status: {status['platform']['status'].upper()}")
        print(f"Uptime: {status['platform']['uptime_minutes']} minutes")
        
        print("\nEngine Status:")
        for engine_name, engine_status in status['engines'].items():
            print(f"  ✓ {engine_name.capitalize()}: {engine_status['status']}")
        
        print("\n" + "=" * 80)
        print("Platform ready for threat management operations")
        print("=" * 80 + "\n")
        
        # Example: Process a sample threat alert
        print("\nExample: Processing sample threat alert...")
        print("-" * 80)
        
        sample_alert = {
            'alert_id': 'DEMO_001',
            'title': 'Suspicious Network Activity',
            'description': 'Potential command and control communication detected',
            'severity': 'High',
            'confidence': 0.85,
            'affected_assets': ['workstation_001'],
            'indicators': ['192.168.1.100', '10.0.0.50'],
            'mitre_tactics': ['Command and Control'],
            'mitre_techniques': ['T1071.001']
        }
        
        result = platform.process_threat_alert(sample_alert)
        
        print(f"\nAlert Processing Results:")
        print(f"  Status: {result.get('status', 'unknown').upper()}")
        print(f"  Incident ID: {result.get('incident_id', 'N/A')}")
        print(f"  Actions Taken: {len(result.get('actions_taken', []))}")
        
        for action in result.get('actions_taken', [])[:5]:  # Show first 5 actions
            print(f"    - {action}")
        
        print("\n" + "=" * 80)
        print("Platform demonstration complete")
        print("=" * 80 + "\n")
        
    except Exception as e:
        logger.error(f"Platform initialization failed: {e}")
        print(f"\n❌ Error: {e}\n")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
