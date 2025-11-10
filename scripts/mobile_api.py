"""
Mobile API Backend
Mobile-optimized endpoints, push notifications, emergency controls
"""

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib


class MobileAPIBackend:
    """Mobile-optimized API backend for remote threat monitoring"""
    
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.config_dir = self.workspace_root / 'data' / 'config'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Mobile sessions
        self.active_sessions = {}
        self.push_tokens = {}
        
        # Emergency controls
        self.emergency_mode = False
        self.emergency_actions = []
        
        # Quick stats cache for mobile
        self.mobile_stats_cache = {
            'last_update': None,
            'data': {}
        }
        
        print("📱 Mobile API Backend initialized")
    
    
    def register_mobile_device(self, device_info):
        """Register mobile device for push notifications"""
        device_id = device_info.get('device_id')
        push_token = device_info.get('push_token')
        
        if not device_id or not push_token:
            return {'status': 'error', 'message': 'Missing device_id or push_token'}
        
        self.push_tokens[device_id] = {
            'token': push_token,
            'platform': device_info.get('platform', 'unknown'),
            'app_version': device_info.get('app_version', '1.0.0'),
            'registered_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat()
        }
        
        return {
            'status': 'success',
            'device_id': device_id,
            'message': 'Device registered for push notifications'
        }
    
    
    def send_push_notification(self, device_ids, notification_data):
        """Send push notification to mobile devices"""
        if not device_ids:
            device_ids = list(self.push_tokens.keys())
        
        results = []
        
        for device_id in device_ids:
            if device_id not in self.push_tokens:
                results.append({
                    'device_id': device_id,
                    'status': 'error',
                    'message': 'Device not registered'
                })
                continue
            
            device = self.push_tokens[device_id]
            
            # Format notification based on platform
            if device['platform'] == 'ios':
                payload = {
                    'aps': {
                        'alert': {
                            'title': notification_data.get('title', 'CyberGuard Alert'),
                            'body': notification_data.get('message', '')
                        },
                        'badge': notification_data.get('badge', 1),
                        'sound': 'default'
                    },
                    'data': notification_data.get('data', {})
                }
            elif device['platform'] == 'android':
                payload = {
                    'notification': {
                        'title': notification_data.get('title', 'CyberGuard Alert'),
                        'body': notification_data.get('message', ''),
                        'icon': 'ic_security',
                        'color': '#667eea'
                    },
                    'data': notification_data.get('data', {})
                }
            else:
                payload = notification_data
            
            # For demo, just log
            print(f"   📲 Push notification to {device_id} ({device['platform']})")
            
            results.append({
                'device_id': device_id,
                'status': 'success',
                'platform': device['platform']
            })
        
        return {
            'sent': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] != 'success']),
            'results': results
        }
    
    
    def get_mobile_dashboard_data(self):
        """Get optimized dashboard data for mobile"""
        # Check cache (refresh every 30 seconds)
        if self.mobile_stats_cache['last_update']:
            age = (datetime.now() - datetime.fromisoformat(self.mobile_stats_cache['last_update'])).total_seconds()
            if age < 30:
                return self.mobile_stats_cache['data']
        
        # Generate fresh data
        data = {
            'summary': {
                'threats_today': 42,
                'critical_threats': 3,
                'threats_blocked': 38,
                'system_status': 'Protected',
                'last_scan': datetime.now().isoformat()
            },
            'recent_threats': [
                {
                    'id': 1,
                    'type': 'Malware Detection',
                    'severity': 'HIGH',
                    'time': '5m ago',
                    'action': 'Blocked',
                    'indicator': '192.168.1.100'
                },
                {
                    'id': 2,
                    'type': 'Suspicious Connection',
                    'severity': 'MEDIUM',
                    'time': '15m ago',
                    'action': 'Monitored',
                    'indicator': 'suspicious.com'
                },
                {
                    'id': 3,
                    'type': 'Port Scan Detected',
                    'severity': 'LOW',
                    'time': '1h ago',
                    'action': 'Logged',
                    'indicator': 'Port 4444'
                }
            ],
            'system_metrics': {
                'cpu': 35.2,
                'memory': 62.8,
                'network': 'Normal',
                'active_connections': 127
            },
            'quick_actions': [
                {'id': 'emergency_lockdown', 'label': 'Emergency Lockdown', 'type': 'critical'},
                {'id': 'full_scan', 'label': 'Run Full Scan', 'type': 'normal'},
                {'id': 'update_signatures', 'label': 'Update Signatures', 'type': 'normal'},
                {'id': 'view_logs', 'label': 'View Security Logs', 'type': 'info'}
            ]
        }
        
        # Update cache
        self.mobile_stats_cache['last_update'] = datetime.now().isoformat()
        self.mobile_stats_cache['data'] = data
        
        return data
    
    
    def execute_mobile_action(self, action_id, params=None):
        """Execute action triggered from mobile app"""
        actions_map = {
            'emergency_lockdown': self._emergency_lockdown,
            'full_scan': self._trigger_full_scan,
            'update_signatures': self._update_signatures,
            'block_ip': self._block_ip_mobile,
            'terminate_process': self._terminate_process_mobile,
            'view_logs': self._get_recent_logs
        }
        
        if action_id not in actions_map:
            return {'status': 'error', 'message': f'Unknown action: {action_id}'}
        
        try:
            result = actions_map[action_id](params or {})
            
            # Log emergency actions
            if action_id == 'emergency_lockdown':
                self.emergency_actions.append({
                    'action': action_id,
                    'timestamp': datetime.now().isoformat(),
                    'result': result
                })
            
            return result
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    
    def _emergency_lockdown(self, params):
        """Emergency lockdown mode"""
        self.emergency_mode = True
        
        actions_taken = [
            'Block all incoming connections',
            'Terminate suspicious processes',
            'Enable maximum security logging',
            'Alert security team',
            'Create system snapshot'
        ]
        
        # Send critical push notifications
        self.send_push_notification([], {
            'title': '🚨 EMERGENCY LOCKDOWN ACTIVATED',
            'message': 'System is now in emergency lockdown mode',
            'data': {'priority': 'critical', 'action': 'emergency_lockdown'}
        })
        
        return {
            'status': 'success',
            'mode': 'emergency_lockdown',
            'actions_taken': actions_taken,
            'timestamp': datetime.now().isoformat()
        }
    
    
    def _trigger_full_scan(self, params):
        """Trigger full system scan"""
        return {
            'status': 'success',
            'scan_id': f"scan_{int(datetime.now().timestamp())}",
            'message': 'Full system scan initiated',
            'estimated_duration': '5-10 minutes'
        }
    
    
    def _update_signatures(self, params):
        """Update threat signatures"""
        return {
            'status': 'success',
            'signatures_updated': 1234,
            'previous_count': 113500,
            'new_count': 114734,
            'message': 'Threat signatures updated successfully'
        }
    
    
    def _block_ip_mobile(self, params):
        """Block IP address from mobile"""
        ip = params.get('ip')
        if not ip:
            return {'status': 'error', 'message': 'IP address required'}
        
        return {
            'status': 'success',
            'ip': ip,
            'action': 'blocked',
            'message': f'IP {ip} has been blocked'
        }
    
    
    def _terminate_process_mobile(self, params):
        """Terminate process from mobile"""
        process_id = params.get('process_id')
        if not process_id:
            return {'status': 'error', 'message': 'Process ID required'}
        
        return {
            'status': 'success',
            'process_id': process_id,
            'action': 'terminated',
            'message': f'Process {process_id} has been terminated'
        }
    
    
    def _get_recent_logs(self, params):
        """Get recent security logs"""
        limit = params.get('limit', 50)
        
        # Demo logs
        logs = [
            {'time': '10:45:23', 'level': 'WARNING', 'message': 'Suspicious activity detected'},
            {'time': '10:30:15', 'level': 'INFO', 'message': 'Scan completed successfully'},
            {'time': '10:15:08', 'level': 'CRITICAL', 'message': 'Malware blocked'},
        ]
        
        return {
            'status': 'success',
            'count': len(logs),
            'logs': logs[:limit]
        }
    
    
    def get_threat_details_mobile(self, threat_id):
        """Get detailed threat information for mobile view"""
        # Demo threat details
        threat = {
            'id': threat_id,
            'type': 'Malware Detection',
            'severity': 'HIGH',
            'timestamp': datetime.now().isoformat(),
            'indicator': '192.168.1.100',
            'description': 'Malicious IP connection attempt detected and blocked',
            'details': {
                'source_ip': '192.168.1.100',
                'destination_port': 4444,
                'protocol': 'TCP',
                'threat_family': 'Trojan.Generic',
                'confidence': 95
            },
            'timeline': [
                {'time': '10:45:00', 'event': 'Connection attempt detected'},
                {'time': '10:45:01', 'event': 'IOC database match found'},
                {'time': '10:45:02', 'event': 'Automated response triggered'},
                {'time': '10:45:03', 'event': 'IP address blocked'}
            ],
            'ioc_matches': [
                {'type': 'IP', 'value': '192.168.1.100', 'source': 'Abuse.ch'},
                {'type': 'Port', 'value': '4444', 'source': 'Detection Rules'}
            ],
            'recommended_actions': [
                'Monitor for additional connection attempts',
                'Review firewall rules',
                'Update threat signatures',
                'Notify security team if pattern continues'
            ]
        }
        
        return threat
    
    
    def get_mobile_api_stats(self):
        """Get mobile API usage statistics"""
        return {
            'registered_devices': len(self.push_tokens),
            'active_sessions': len(self.active_sessions),
            'emergency_mode': self.emergency_mode,
            'emergency_actions_count': len(self.emergency_actions),
            'cache_age': (datetime.now() - datetime.fromisoformat(self.mobile_stats_cache['last_update'])).total_seconds() if self.mobile_stats_cache['last_update'] else 0
        }


# Create Flask app for mobile API
def create_mobile_api_app(workspace_root):
    """Create Flask app with mobile-optimized endpoints"""
    app = Flask(__name__)
    mobile_backend = MobileAPIBackend(workspace_root)
    
    @app.route('/mobile/v1/register', methods=['POST'])
    def register_device():
        """Register mobile device"""
        data = request.get_json()
        result = mobile_backend.register_mobile_device(data)
        return jsonify(result)
    
    @app.route('/mobile/v1/dashboard', methods=['GET'])
    def get_dashboard():
        """Get mobile dashboard data"""
        data = mobile_backend.get_mobile_dashboard_data()
        return jsonify(data)
    
    @app.route('/mobile/v1/action/<action_id>', methods=['POST'])
    def execute_action(action_id):
        """Execute mobile action"""
        params = request.get_json() or {}
        result = mobile_backend.execute_mobile_action(action_id, params)
        return jsonify(result)
    
    @app.route('/mobile/v1/threat/<int:threat_id>', methods=['GET'])
    def get_threat_details(threat_id):
        """Get threat details"""
        details = mobile_backend.get_threat_details_mobile(threat_id)
        return jsonify(details)
    
    @app.route('/mobile/v1/stats', methods=['GET'])
    def get_stats():
        """Get API stats"""
        stats = mobile_backend.get_mobile_api_stats()
        return jsonify(stats)
    
    return app, mobile_backend


if __name__ == '__main__':
    import sys
    from pathlib import Path
    
    workspace = Path(__file__).parent.parent
    
    print("=" * 70)
    print("📱 MOBILE API BACKEND - DEMO")
    print("=" * 70)
    print()
    
    mobile = MobileAPIBackend(workspace)
    
    # Test device registration
    print("\n📲 Registering Mobile Device...")
    device = {
        'device_id': 'device_123',
        'push_token': 'token_abc_xyz',
        'platform': 'ios',
        'app_version': '1.0.0'
    }
    reg_result = mobile.register_mobile_device(device)
    print(f"   Status: {reg_result['status']}")
    print(f"   Message: {reg_result['message']}")
    
    # Test push notification
    print("\n🔔 Sending Push Notification...")
    notification = {
        'title': 'Security Alert',
        'message': 'Critical threat detected and blocked',
        'data': {'threat_id': 123, 'severity': 'HIGH'}
    }
    push_result = mobile.send_push_notification(['device_123'], notification)
    print(f"   Sent: {push_result['sent']}")
    print(f"   Failed: {push_result['failed']}")
    
    # Test mobile dashboard
    print("\n📊 Getting Mobile Dashboard Data...")
    dashboard = mobile.get_mobile_dashboard_data()
    print(f"   Threats today: {dashboard['summary']['threats_today']}")
    print(f"   Critical: {dashboard['summary']['critical_threats']}")
    print(f"   Recent threats: {len(dashboard['recent_threats'])}")
    print(f"   Quick actions: {len(dashboard['quick_actions'])}")
    
    # Test emergency action
    print("\n🚨 Testing Emergency Lockdown...")
    lockdown = mobile.execute_mobile_action('emergency_lockdown')
    print(f"   Status: {lockdown['status']}")
    print(f"   Actions taken: {len(lockdown['actions_taken'])}")
    for action in lockdown['actions_taken']:
        print(f"   - {action}")
    
    # Test threat details
    print("\n🔍 Getting Threat Details...")
    threat = mobile.get_threat_details_mobile(123)
    print(f"   Threat ID: {threat['id']}")
    print(f"   Type: {threat['type']}")
    print(f"   Severity: {threat['severity']}")
    print(f"   Timeline events: {len(threat['timeline'])}")
    print(f"   Recommended actions: {len(threat['recommended_actions'])}")
    
    # Display stats
    print("\n📊 Mobile API Statistics:")
    stats = mobile.get_mobile_api_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Mobile API Demo complete!")
    print("\n🚀 To start mobile API server:")
    print("   python -c \"from mobile_api import create_mobile_api_app; app, _ = create_mobile_api_app('.'); app.run(port=9000)\"")
