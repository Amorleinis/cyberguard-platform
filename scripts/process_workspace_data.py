"""
CyberGuard Industries - Engine Data Processor
Lance Brady & AI Collaboration

This script enhances all engines with workspace data processing capabilities
and creates practical, ready-to-use implementations.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkspaceDataProcessor:
    """Process real workspace data for all engines"""
    
    def __init__(self, workspace_root: str):
        self.root = Path(workspace_root)
        self.data_inventory = {
            'cve_files': [],
            'mitre_files': [],
            'malware_files': [],
            'neo4j_files': [],
            'csv_files': [],
            'json_files': []
        }
        self.scan_workspace()
    
    def scan_workspace(self):
        """Scan workspace for available data files"""
        logger.info("Scanning workspace for data files...")
        
        # CVE data files
        cve_patterns = ['cve_data*.json', '*cve*.json']
        for pattern in cve_patterns:
            self.data_inventory['cve_files'].extend(self.root.glob(pattern))
        
        # MITRE ATT&CK data
        mitre_dirs = ['neo4j_data', 'neo4j', 'NVD']
        for dir_name in mitre_dirs:
            mitre_dir = self.root / dir_name
            if mitre_dir.exists():
                self.data_inventory['mitre_files'].extend(mitre_dir.glob('*.json'))
                self.data_inventory['csv_files'].extend(mitre_dir.glob('*.csv'))
        
        # Malware/threat data
        nvd_dir = self.root / 'NVD'
        if nvd_dir.exists():
            self.data_inventory['malware_files'].extend(nvd_dir.glob('*malware*.csv'))
            self.data_inventory['malware_files'].extend(nvd_dir.glob('*hash*.csv'))
        
        # All JSON files for comprehensive analysis
        self.data_inventory['json_files'] = list(self.root.glob('**/*.json'))[:50]  # Limit for performance
        
        logger.info(f"Found {len(self.data_inventory['cve_files'])} CVE files")
        logger.info(f"Found {len(self.data_inventory['mitre_files'])} MITRE files")
        logger.info(f"Found {len(self.data_inventory['malware_files'])} malware files")
        logger.info(f"Found {len(self.data_inventory['csv_files'])} CSV files")
    
    def process_cve_data_for_intelligence(self):
        """Process CVE data for intelligence engine"""
        logger.info("Processing CVE data for Intelligence Engine...")
        
        all_cves = []
        iocs_extracted = {'ips': set(), 'domains': set(), 'hashes': set()}
        
        for cve_file in self.data_inventory['cve_files'][:3]:  # Process first 3 files
            try:
                with open(cve_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if isinstance(data, list):
                        all_cves.extend(data)
                    elif isinstance(data, dict) and 'CVE_Items' in data:
                        all_cves.extend(data['CVE_Items'])
                    
                    logger.info(f"Loaded {len(data) if isinstance(data, list) else 1} CVEs from {cve_file.name}")
            except Exception as e:
                logger.error(f"Error processing {cve_file}: {e}")
        
        # Extract IOCs from CVE descriptions
        import re
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        domain_pattern = r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b'
        hash_pattern = r'\b[a-f0-9]{32,64}\b'
        
        for cve in all_cves[:100]:  # Sample first 100
            description = str(cve.get('description', '')) + str(cve.get('summary', ''))
            
            iocs_extracted['ips'].update(re.findall(ip_pattern, description))
            iocs_extracted['domains'].update(re.findall(domain_pattern, description.lower()))
            iocs_extracted['hashes'].update(re.findall(hash_pattern, description.lower()))
        
        results = {
            'total_cves': len(all_cves),
            'iocs': {
                'ip_addresses': list(iocs_extracted['ips'])[:50],
                'domains': list(iocs_extracted['domains'])[:50],
                'file_hashes': list(iocs_extracted['hashes'])[:50]
            },
            'severity_distribution': self._analyze_severity_distribution(all_cves),
            'top_vendors': self._extract_top_vendors(all_cves)
        }
        
        # Save processed intelligence
        output_file = self.root / 'intelligence' / 'processed_intelligence_data.json'
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Saved processed intelligence to {output_file}")
        return results
    
    def process_malware_data_for_prevention(self):
        """Process malware data for prevention engine"""
        logger.info("Processing malware data for Prevention Engine...")
        
        blocklist = {
            'malicious_ips': [],
            'malicious_domains': [],
            'malicious_hashes': []
        }
        
        for malware_file in self.data_inventory['malware_files']:
            try:
                df = pd.read_csv(malware_file, nrows=100)  # Sample 100 rows
                
                # Extract hashes
                hash_columns = [col for col in df.columns if 'hash' in col.lower() or 'md5' in col.lower() or 'sha' in col.lower()]
                for col in hash_columns:
                    blocklist['malicious_hashes'].extend(df[col].dropna().astype(str).tolist())
                
                logger.info(f"Processed {len(df)} malware samples from {malware_file.name}")
            except Exception as e:
                logger.error(f"Error processing {malware_file}: {e}")
        
        # Add sample malicious IOCs (for demo purposes)
        blocklist['malicious_ips'].extend([
            '192.168.100.50', '10.0.0.100', '172.16.0.200'
        ])
        blocklist['malicious_domains'].extend([
            'malicious-c2.example', 'phishing-site.fake', 'malware-dl.bad'
        ])
        
        # Save blocklist
        output_file = self.root / 'prevention' / 'ioc_blocklist_enhanced.json'
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(blocklist, f, indent=2)
        
        logger.info(f"Saved enhanced blocklist to {output_file}")
        return blocklist
    
    def process_attack_patterns_for_detection(self):
        """Process MITRE ATT&CK patterns for detection engine"""
        logger.info("Processing attack patterns for Detection Engine...")
        
        attack_patterns = []
        
        for mitre_file in self.data_inventory['mitre_files']:
            if 'attack-pattern' in mitre_file.name.lower():
                try:
                    with open(mitre_file, 'r') as f:
                        data = json.load(f)
                        
                        if isinstance(data, list):
                            attack_patterns.extend(data)
                        elif isinstance(data, dict) and 'objects' in data:
                            attack_patterns.extend(data['objects'])
                    
                    logger.info(f"Loaded {len(data) if isinstance(data, list) else 'N/A'} patterns from {mitre_file.name}")
                except Exception as e:
                    logger.error(f"Error processing {mitre_file}: {e}")
        
        # Create detection signatures
        detection_rules = []
        for pattern in attack_patterns[:50]:  # First 50 patterns
            if isinstance(pattern, dict):
                rule = {
                    'id': pattern.get('id', f"rule-{len(detection_rules)}"),
                    'name': pattern.get('name', 'Unknown Pattern'),
                    'description': pattern.get('description', '')[:200],
                    'tactics': pattern.get('kill_chain_phases', []),
                    'severity': 'HIGH',
                    'enabled': True
                }
                detection_rules.append(rule)
        
        # Save detection rules
        output_file = self.root / 'detection' / 'enhanced_detection_rules.json'
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(detection_rules, f, indent=2)
        
        logger.info(f"Saved {len(detection_rules)} detection rules to {output_file}")
        return detection_rules
    
    def create_incident_playbooks_for_response(self):
        """Create incident response playbooks"""
        logger.info("Creating incident response playbooks...")
        
        playbooks = {
            'ransomware_response': {
                'name': 'Ransomware Incident Response',
                'severity': 'CRITICAL',
                'steps': [
                    {'order': 1, 'action': 'Isolate affected systems', 'automation': True},
                    {'order': 2, 'action': 'Collect forensic evidence', 'automation': True},
                    {'order': 3, 'action': 'Notify security team and management', 'automation': True},
                    {'order': 4, 'action': 'Assess impact and data loss', 'automation': False},
                    {'order': 5, 'action': 'Determine if backups are available', 'automation': True},
                    {'order': 6, 'action': 'Initiate recovery procedures', 'automation': False}
                ],
                'sla_hours': 4
            },
            'data_breach_response': {
                'name': 'Data Breach Response',
                'severity': 'HIGH',
                'steps': [
                    {'order': 1, 'action': 'Contain the breach', 'automation': True},
                    {'order': 2, 'action': 'Identify affected data', 'automation': False},
                    {'order': 3, 'action': 'Notify legal and compliance teams', 'automation': True},
                    {'order': 4, 'action': 'Begin forensic investigation', 'automation': True},
                    {'order': 5, 'action': 'Prepare breach notifications', 'automation': False}
                ],
                'sla_hours': 8
            },
            'malware_infection': {
                'name': 'Malware Infection Response',
                'severity': 'HIGH',
                'steps': [
                    {'order': 1, 'action': 'Quarantine infected systems', 'automation': True},
                    {'order': 2, 'action': 'Run malware analysis', 'automation': True},
                    {'order': 3, 'action': 'Identify propagation vectors', 'automation': False},
                    {'order': 4, 'action': 'Deploy remediation', 'automation': True},
                    {'order': 5, 'action': 'Verify system integrity', 'automation': True}
                ],
                'sla_hours': 2
            }
        }
        
        # Save playbooks
        output_file = self.root / 'response' / 'incident_playbooks.json'
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(playbooks, f, indent=2)
        
        logger.info(f"Saved {len(playbooks)} playbooks to {output_file}")
        return playbooks
    
    def create_isolation_policies(self):
        """Create network isolation policies"""
        logger.info("Creating isolation policies...")
        
        policies = {
            'quarantine_vlan': {
                'name': 'Quarantine VLAN Policy',
                'vlan_id': 999,
                'description': 'Isolated VLAN for compromised assets',
                'rules': [
                    {'action': 'deny', 'direction': 'outbound', 'protocol': 'all'},
                    {'action': 'allow', 'direction': 'inbound', 'protocol': 'icmp', 'source': 'monitoring'},
                    {'action': 'allow', 'direction': 'inbound', 'protocol': 'ssh', 'source': 'admin'}
                ]
            },
            'dmz_isolation': {
                'name': 'DMZ Isolation Policy',
                'description': 'Isolate DMZ from internal network',
                'rules': [
                    {'action': 'deny', 'direction': 'inbound', 'destination': 'internal', 'protocol': 'all'},
                    {'action': 'allow', 'direction': 'outbound', 'protocol': 'http/https'},
                    {'action': 'allow', 'direction': 'inbound', 'protocol': 'http/https', 'port': [80, 443]}
                ]
            }
        }
        
        # Save policies
        output_file = self.root / 'isolation' / 'isolation_policies.json'
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(policies, f, indent=2)
        
        logger.info(f"Saved isolation policies to {output_file}")
        return policies
    
    def create_mitigation_strategies(self):
        """Create mitigation strategies and patch schedules"""
        logger.info("Creating mitigation strategies...")
        
        strategies = {
            'critical_patch_deployment': {
                'name': 'Critical Patch Deployment',
                'priority': 'P0',
                'schedule': 'Immediate',
                'testing_required': True,
                'rollback_plan': True,
                'steps': [
                    'Download and verify patch integrity',
                    'Deploy to test environment',
                    'Validate functionality',
                    'Schedule production deployment',
                    'Monitor post-deployment'
                ]
            },
            'system_hardening': {
                'name': 'System Hardening',
                'priority': 'P1',
                'schedule': 'Weekly',
                'actions': [
                    'Disable unnecessary services',
                    'Update firewall rules',
                    'Review and rotate credentials',
                    'Update antivirus signatures',
                    'Scan for misconfigurations'
                ]
            },
            'vulnerability_remediation': {
                'name': 'Vulnerability Remediation',
                'priority': 'P2',
                'schedule': 'Monthly',
                'workflow': [
                    'Run vulnerability scans',
                    'Prioritize findings by risk',
                    'Assign remediation tasks',
                    'Verify fixes',
                    'Update CMDB'
                ]
            }
        }
        
        # Save strategies
        output_file = self.root / 'mitigation' / 'mitigation_strategies.json'
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(strategies, f, indent=2)
        
        logger.info(f"Saved mitigation strategies to {output_file}")
        return strategies
    
    def create_recovery_plans(self):
        """Create disaster recovery and business continuity plans"""
        logger.info("Creating recovery plans...")
        
        plans = {
            'database_recovery': {
                'name': 'Database Recovery Plan',
                'rto_hours': 4,
                'rpo_hours': 1,
                'backup_schedule': 'Hourly incremental, Daily full',
                'steps': [
                    'Verify backup integrity',
                    'Prepare recovery environment',
                    'Restore from latest backup',
                    'Apply transaction logs',
                    'Verify data consistency',
                    'Bring services online',
                    'Monitor for issues'
                ]
            },
            'web_application_recovery': {
                'name': 'Web Application Recovery',
                'rto_hours': 2,
                'rpo_hours': 0.5,
                'backup_schedule': 'Continuous replication',
                'steps': [
                    'Activate standby environment',
                    'Update DNS records',
                    'Verify application functionality',
                    'Monitor traffic',
                    'Investigate root cause'
                ]
            },
            'full_datacenter_recovery': {
                'name': 'Full Datacenter Recovery',
                'rto_hours': 24,
                'rpo_hours': 4,
                'prerequisites': [
                    'Secondary datacenter available',
                    'Current backups replicated',
                    'Network connectivity established'
                ],
                'steps': [
                    'Activate disaster recovery site',
                    'Restore critical infrastructure',
                    'Restore business-critical applications',
                    'Restore remaining systems',
                    'Verify all services operational',
                    'Begin normal operations'
                ]
            }
        }
        
        # Save plans
        output_file = self.root / 'recovery' / 'recovery_plans.json'
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(plans, f, indent=2)
        
        logger.info(f"Saved recovery plans to {output_file}")
        return plans
    
    def _analyze_severity_distribution(self, cves):
        """Analyze CVE severity distribution"""
        severity_count = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'UNKNOWN': 0}
        
        for cve in cves[:500]:  # Sample
            severity = str(cve.get('severity', cve.get('impact', {}))).upper()
            
            if 'CRITICAL' in severity:
                severity_count['CRITICAL'] += 1
            elif 'HIGH' in severity:
                severity_count['HIGH'] += 1
            elif 'MEDIUM' in severity:
                severity_count['MEDIUM'] += 1
            elif 'LOW' in severity:
                severity_count['LOW'] += 1
            else:
                severity_count['UNKNOWN'] += 1
        
        return severity_count
    
    def _extract_top_vendors(self, cves):
        """Extract top affected vendors"""
        from collections import Counter
        vendors = []
        
        for cve in cves[:200]:  # Sample
            # Try to extract vendor from description or affected products
            description = str(cve.get('description', '')) + str(cve.get('summary', ''))
            
            # Common vendor names
            common_vendors = ['Microsoft', 'Oracle', 'Adobe', 'Google', 'Apple', 'Linux', 
                            'Cisco', 'IBM', 'SAP', 'VMware', 'Apache', 'PHP']
            
            for vendor in common_vendors:
                if vendor.lower() in description.lower():
                    vendors.append(vendor)
        
        return [vendor for vendor, count in Counter(vendors).most_common(10)]
    
    def process_all(self):
        """Process data for all engines"""
        logger.info("\n" + "="*60)
        logger.info("Processing workspace data for all engines...")
        logger.info("="*60 + "\n")
        
        results = {}
        
        try:
            results['intelligence'] = self.process_cve_data_for_intelligence()
        except Exception as e:
            logger.error(f"Intelligence processing failed: {e}")
        
        try:
            results['prevention'] = self.process_malware_data_for_prevention()
        except Exception as e:
            logger.error(f"Prevention processing failed: {e}")
        
        try:
            results['detection'] = self.process_attack_patterns_for_detection()
        except Exception as e:
            logger.error(f"Detection processing failed: {e}")
        
        try:
            results['response'] = self.create_incident_playbooks_for_response()
        except Exception as e:
            logger.error(f"Response processing failed: {e}")
        
        try:
            results['isolation'] = self.create_isolation_policies()
        except Exception as e:
            logger.error(f"Isolation processing failed: {e}")
        
        try:
            results['mitigation'] = self.create_mitigation_strategies()
        except Exception as e:
            logger.error(f"Mitigation processing failed: {e}")
        
        try:
            results['recovery'] = self.create_recovery_plans()
        except Exception as e:
            logger.error(f"Recovery processing failed: {e}")
        
        logger.info("\n" + "="*60)
        logger.info("Data processing complete!")
        logger.info("="*60 + "\n")
        
        return results

def main():
    """Main execution"""
    import sys
    
    workspace_root = Path(__file__).parent.parent
    
    print("\n" + "="*80)
    print("  CyberGuard Industries - Engine Data Processor")
    print("  Lance Brady & AI Collaboration")
    print("="*80 + "\n")
    
    processor = WorkspaceDataProcessor(workspace_root)
    results = processor.process_all()
    
    print("\n✅ Data processing complete!")
    print(f"   • Intelligence data: {results.get('intelligence', {}).get('total_cves', 0)} CVEs processed")
    print(f"   • Prevention blocklist: {len(results.get('prevention', {}).get('malicious_hashes', []))} hashes")
    print(f"   • Detection rules: {len(results.get('detection', []))} rules created")
    print(f"   • Response playbooks: {len(results.get('response', {}))} playbooks")
    print(f"   • Isolation policies: {len(results.get('isolation', {}))} policies")
    print(f"   • Mitigation strategies: {len(results.get('mitigation', {}))} strategies")
    print(f"   • Recovery plans: {len(results.get('recovery', {}))} plans")
    print()

if __name__ == "__main__":
    main()
