"""
SIEM Integration Framework
Connectors for Splunk, Elastic Stack, Azure Sentinel, and SOAR platforms
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from collections import deque
import base64


class SIEMIntegrationHub:
    """Central hub for SIEM and SOAR platform integrations"""
    
    def __init__(self, workspace_root, config_file=None):
        self.workspace_root = Path(workspace_root)
        self.config_file = config_file or self.workspace_root / 'data' / 'config' / 'siem_config.json'
        
        # Integration connectors
        self.connectors = {
            'splunk': SplunkConnector(),
            'elastic': ElasticConnector(),
            'azure_sentinel': AzureSentinelConnector(),
            'soar': SOARConnector()
        }
        
        # Event queue
        self.event_queue = deque(maxlen=1000)
        
        # Statistics
        self.stats = {
            'events_sent': 0,
            'events_failed': 0,
            'by_platform': {},
            'last_sync': None
        }
        
        # Load configuration
        self.config = self._load_config()
        
        print("🔗 SIEM Integration Hub initialized")
        print(f"   Available connectors: {len(self.connectors)}")
        self._print_connector_status()
    
    
    def _load_config(self):
        """Load SIEM integration configuration"""
        default_config = {
            'splunk': {
                'enabled': False,
                'hec_url': 'https://splunk.example.com:8088/services/collector',
                'hec_token': '',
                'index': 'cyberguard',
                'source': 'threat_detection',
                'sourcetype': 'json'
            },
            'elastic': {
                'enabled': False,
                'hosts': ['https://elasticsearch.example.com:9200'],
                'api_key': '',
                'index_pattern': 'cyberguard-threats',
                'username': '',
                'password': ''
            },
            'azure_sentinel': {
                'enabled': False,
                'workspace_id': '',
                'shared_key': '',
                'log_type': 'CyberGuardThreats'
            },
            'soar': {
                'enabled': False,
                'platform': 'generic',  # generic, cortex_xsoar, splunk_phantom
                'api_url': '',
                'api_key': '',
                'playbook_triggers': {
                    'CRITICAL': 'incident_response_critical',
                    'HIGH': 'incident_response_high'
                }
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    for key in default_config:
                        if key in loaded_config:
                            default_config[key].update(loaded_config[key])
                    return default_config
            except Exception as e:
                print(f"   ⚠️  Config load error: {e}")
        
        # Save default config
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    
    def _print_connector_status(self):
        """Print status of all connectors"""
        for name, config in self.config.items():
            status = '✅' if config.get('enabled') else '❌'
            print(f"   {status} {name.replace('_', ' ').title()}")
    
    
    def send_threat_event(self, threat_data):
        """Send threat event to all enabled SIEM platforms"""
        results = {}
        
        # Normalize threat data
        event = self._normalize_threat_event(threat_data)
        
        # Add to queue
        self.event_queue.append(event)
        
        # Send to each enabled platform
        if self.config['splunk']['enabled']:
            results['splunk'] = self.connectors['splunk'].send_event(
                event, self.config['splunk']
            )
        
        if self.config['elastic']['enabled']:
            results['elastic'] = self.connectors['elastic'].send_event(
                event, self.config['elastic']
            )
        
        if self.config['azure_sentinel']['enabled']:
            results['azure_sentinel'] = self.connectors['azure_sentinel'].send_event(
                event, self.config['azure_sentinel']
            )
        
        # Update statistics
        self._update_stats(results)
        
        return results
    
    
    def _normalize_threat_event(self, threat_data):
        """Normalize threat data for SIEM ingestion"""
        return {
            'timestamp': threat_data.get('timestamp', datetime.now().isoformat()),
            'event_type': 'threat_detected',
            'severity': threat_data.get('severity', 'MEDIUM'),
            'threat_type': threat_data.get('threat_type', 'unknown'),
            'description': threat_data.get('description', ''),
            'indicator': threat_data.get('indicator', ''),
            'action_taken': threat_data.get('action', 'LOGGED'),
            'source': 'CyberGuard_Platform',
            'host': threat_data.get('host', 'localhost'),
            'user': threat_data.get('user', 'system'),
            'additional_data': {
                'matched_iocs': threat_data.get('matched_iocs', []),
                'matched_rules': threat_data.get('matched_rules', []),
                'risk_score': threat_data.get('risk_score', 0)
            }
        }
    
    
    def trigger_soar_playbook(self, incident_data, playbook_name=None):
        """Trigger SOAR playbook for incident response"""
        if not self.config['soar']['enabled']:
            return {'status': 'disabled', 'message': 'SOAR integration not enabled'}
        
        # Auto-select playbook based on severity if not specified
        if playbook_name is None:
            severity = incident_data.get('severity', 'MEDIUM')
            playbook_name = self.config['soar']['playbook_triggers'].get(severity)
        
        if not playbook_name:
            return {'status': 'error', 'message': 'No playbook configured for this severity'}
        
        result = self.connectors['soar'].trigger_playbook(
            playbook_name,
            incident_data,
            self.config['soar']
        )
        
        return result
    
    
    def query_siem(self, platform, query_params):
        """Query SIEM platform for threat intelligence"""
        if platform not in self.connectors:
            return {'status': 'error', 'message': f'Unknown platform: {platform}'}
        
        if not self.config[platform]['enabled']:
            return {'status': 'disabled', 'message': f'{platform} not enabled'}
        
        connector = self.connectors[platform]
        result = connector.query(query_params, self.config[platform])
        
        return result
    
    
    def sync_threat_intelligence(self, platforms=None):
        """Sync threat intelligence from SIEM platforms"""
        if platforms is None:
            platforms = [p for p in self.connectors if self.config[p]['enabled']]
        
        results = {}
        
        for platform in platforms:
            if platform in self.connectors and self.config[platform]['enabled']:
                connector = self.connectors[platform]
                results[platform] = connector.pull_threat_intel(self.config[platform])
        
        self.stats['last_sync'] = datetime.now().isoformat()
        
        return results
    
    
    def _update_stats(self, results):
        """Update integration statistics"""
        for platform, result in results.items():
            if result.get('status') == 'success':
                self.stats['events_sent'] += 1
                self.stats['by_platform'][platform] = self.stats['by_platform'].get(platform, 0) + 1
            else:
                self.stats['events_failed'] += 1
    
    
    def get_integration_stats(self):
        """Get integration statistics"""
        return {
            **self.stats,
            'queue_size': len(self.event_queue),
            'enabled_platforms': [p for p in self.config if self.config[p].get('enabled')]
        }


class SplunkConnector:
    """Splunk HTTP Event Collector (HEC) integration"""
    
    def send_event(self, event, config):
        """Send event to Splunk HEC"""
        try:
            payload = {
                'time': datetime.now().timestamp(),
                'host': event.get('host', 'cyberguard'),
                'source': config['source'],
                'sourcetype': config['sourcetype'],
                'index': config['index'],
                'event': event
            }
            
            headers = {
                'Authorization': f"Splunk {config['hec_token']}",
                'Content-Type': 'application/json'
            }
            
            # For demo, don't actually send
            print(f"   📤 Would send to Splunk: {event['event_type']}")
            
            return {
                'status': 'success',
                'platform': 'splunk',
                'event_id': 'demo_' + str(datetime.now().timestamp()),
                'method': 'hec'
            }
            
        except Exception as e:
            return {'status': 'error', 'platform': 'splunk', 'error': str(e)}
    
    
    def query(self, query_params, config):
        """Query Splunk for threat data"""
        # Demo implementation
        return {
            'status': 'success',
            'results': [],
            'count': 0,
            'method': 'rest_api'
        }
    
    
    def pull_threat_intel(self, config):
        """Pull threat intelligence from Splunk"""
        return {
            'status': 'success',
            'threats_pulled': 0,
            'method': 'rest_api'
        }


class ElasticConnector:
    """Elasticsearch integration"""
    
    def send_event(self, event, config):
        """Send event to Elasticsearch"""
        try:
            index_name = f"{config['index_pattern']}-{datetime.now().strftime('%Y.%m.%d')}"
            
            # For demo
            print(f"   📤 Would send to Elastic: {event['event_type']}")
            
            return {
                'status': 'success',
                'platform': 'elastic',
                'index': index_name,
                'event_id': 'demo_' + str(datetime.now().timestamp())
            }
            
        except Exception as e:
            return {'status': 'error', 'platform': 'elastic', 'error': str(e)}
    
    
    def query(self, query_params, config):
        """Query Elasticsearch"""
        return {
            'status': 'success',
            'hits': [],
            'total': 0
        }
    
    
    def pull_threat_intel(self, config):
        """Pull threat intelligence from Elasticsearch"""
        return {
            'status': 'success',
            'threats_pulled': 0
        }


class AzureSentinelConnector:
    """Azure Sentinel integration"""
    
    def send_event(self, event, config):
        """Send event to Azure Sentinel"""
        try:
            # For demo
            print(f"   📤 Would send to Azure Sentinel: {event['event_type']}")
            
            return {
                'status': 'success',
                'platform': 'azure_sentinel',
                'workspace': config['workspace_id'],
                'event_id': 'demo_' + str(datetime.now().timestamp())
            }
            
        except Exception as e:
            return {'status': 'error', 'platform': 'azure_sentinel', 'error': str(e)}
    
    
    def query(self, query_params, config):
        """Query Azure Sentinel"""
        return {
            'status': 'success',
            'results': [],
            'count': 0
        }
    
    
    def pull_threat_intel(self, config):
        """Pull threat intelligence from Azure Sentinel"""
        return {
            'status': 'success',
            'threats_pulled': 0
        }


class SOARConnector:
    """SOAR platform integration (Cortex XSOAR, Phantom, etc.)"""
    
    def trigger_playbook(self, playbook_name, incident_data, config):
        """Trigger SOAR playbook"""
        try:
            # For demo
            print(f"   🎭 Would trigger SOAR playbook: {playbook_name}")
            
            return {
                'status': 'success',
                'playbook': playbook_name,
                'incident_id': 'INC-' + datetime.now().strftime('%Y%m%d%H%M%S'),
                'platform': config['platform']
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    
    def query(self, query_params, config):
        """Query SOAR platform"""
        return {
            'status': 'success',
            'incidents': [],
            'count': 0
        }
    
    
    def pull_threat_intel(self, config):
        """Pull threat intelligence from SOAR"""
        return {
            'status': 'success',
            'indicators_pulled': 0
        }


if __name__ == '__main__':
    import sys
    from pathlib import Path
    
    workspace = Path(__file__).parent.parent
    
    print("=" * 70)
    print("🔗 SIEM INTEGRATION HUB - DEMO")
    print("=" * 70)
    print()
    
    siem_hub = SIEMIntegrationHub(workspace)
    
    # Test threat event
    print("\n📡 Sending Test Threat Event...")
    threat = {
        'timestamp': datetime.now().isoformat(),
        'severity': 'HIGH',
        'threat_type': 'malware_detection',
        'description': 'Malicious file detected',
        'indicator': 'malware.exe',
        'action': 'QUARANTINED',
        'matched_iocs': ['hash123'],
        'risk_score': 85
    }
    
    results = siem_hub.send_threat_event(threat)
    for platform, result in results.items():
        status = '✅' if result['status'] == 'success' else '❌'
        print(f"   {status} {platform}: {result.get('event_id', 'N/A')}")
    
    # Test SOAR playbook trigger
    print("\n🎭 Triggering SOAR Playbook...")
    incident = {
        'severity': 'CRITICAL',
        'threat_type': 'ransomware',
        'description': 'Ransomware activity detected',
        'affected_hosts': ['server-01', 'workstation-15']
    }
    
    soar_result = siem_hub.trigger_soar_playbook(incident)
    print(f"   Status: {soar_result['status']}")
    if soar_result['status'] == 'success':
        print(f"   Incident ID: {soar_result['incident_id']}")
        print(f"   Playbook: {soar_result['playbook']}")
    
    # Display statistics
    print("\n📊 Integration Statistics:")
    stats = siem_hub.get_integration_stats()
    print(f"   Events sent: {stats['events_sent']}")
    print(f"   Events failed: {stats['events_failed']}")
    print(f"   Queue size: {stats['queue_size']}")
    print(f"   Enabled platforms: {', '.join(stats['enabled_platforms']) if stats['enabled_platforms'] else 'None'}")
    
    print("\n✅ SIEM Integration Demo complete!")
    print("\n💡 To enable integrations, edit:")
    print(f"   {siem_hub.config_file}")
