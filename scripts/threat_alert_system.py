"""
Real-Time Threat Alert System
Sends notifications via Email, SMS, Slack, and other channels
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from collections import deque
import requests

class ThreatAlertSystem:
    """Multi-channel threat alert notification system"""
    
    def __init__(self, workspace_root, config_file=None):
        self.workspace_root = Path(workspace_root)
        self.config_file = config_file or self.workspace_root / 'data' / 'config' / 'alerts_config.json'
        
        # Alert history
        self.alert_history = deque(maxlen=1000)
        self.alert_stats = {
            'total_sent': 0,
            'by_severity': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
            'by_channel': {'email': 0, 'sms': 0, 'slack': 0, 'webhook': 0},
            'failed': 0
        }
        
        # Load configuration
        self.config = self._load_config()
        
        print("🔔 Threat Alert System initialized")
        print(f"   Email: {'✅' if self.config.get('email', {}).get('enabled') else '❌'}")
        print(f"   SMS: {'✅' if self.config.get('sms', {}).get('enabled') else '❌'}")
        print(f"   Slack: {'✅' if self.config.get('slack', {}).get('enabled') else '❌'}")
        print(f"   Webhook: {'✅' if self.config.get('webhook', {}).get('enabled') else '❌'}")
    
    
    def _load_config(self):
        """Load alert configuration"""
        default_config = {
            'email': {
                'enabled': False,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'from_addr': '',
                'to_addrs': [],
                'severity_threshold': 'MEDIUM'
            },
            'sms': {
                'enabled': False,
                'provider': 'twilio',  # twilio, aws_sns, etc.
                'account_sid': '',
                'auth_token': '',
                'from_number': '',
                'to_numbers': [],
                'severity_threshold': 'HIGH'
            },
            'slack': {
                'enabled': False,
                'webhook_url': '',
                'channel': '#security-alerts',
                'username': 'CyberGuard Bot',
                'severity_threshold': 'MEDIUM'
            },
            'webhook': {
                'enabled': False,
                'url': '',
                'method': 'POST',
                'headers': {},
                'severity_threshold': 'MEDIUM'
            },
            'general': {
                'rate_limit': 10,  # Max alerts per minute
                'quiet_hours': {
                    'enabled': False,
                    'start': '22:00',
                    'end': '07:00'
                }
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key in default_config:
                        if key in loaded_config:
                            default_config[key].update(loaded_config[key])
                    return default_config
            except Exception as e:
                print(f"⚠️  Config load error: {e}")
        
        # Save default config
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    
    def send_alert(self, threat_data):
        """Send alert through configured channels"""
        severity = threat_data.get('severity', 'MEDIUM')
        
        # Create alert message
        alert_message = self._format_alert_message(threat_data)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'threat': threat_data,
            'channels': {}
        }
        
        # Send through each enabled channel
        if self._should_send_alert('email', severity):
            results['channels']['email'] = self._send_email_alert(alert_message, threat_data)
        
        if self._should_send_alert('sms', severity):
            results['channels']['sms'] = self._send_sms_alert(alert_message, threat_data)
        
        if self._should_send_alert('slack', severity):
            results['channels']['slack'] = self._send_slack_alert(alert_message, threat_data)
        
        if self._should_send_alert('webhook', severity):
            results['channels']['webhook'] = self._send_webhook_alert(alert_message, threat_data)
        
        # Update statistics
        self._update_stats(results)
        
        # Add to history
        self.alert_history.append(results)
        
        return results
    
    
    def _should_send_alert(self, channel, severity):
        """Check if alert should be sent for this channel"""
        channel_config = self.config.get(channel, {})
        
        if not channel_config.get('enabled', False):
            return False
        
        # Check severity threshold
        threshold = channel_config.get('severity_threshold', 'MEDIUM')
        severity_levels = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        
        if severity_levels.get(severity, 0) < severity_levels.get(threshold, 0):
            return False
        
        # Check quiet hours
        if self._is_quiet_hours():
            if severity != 'CRITICAL':  # Always send CRITICAL
                return False
        
        return True
    
    
    def _is_quiet_hours(self):
        """Check if currently in quiet hours"""
        quiet_config = self.config.get('general', {}).get('quiet_hours', {})
        
        if not quiet_config.get('enabled', False):
            return False
        
        current_time = datetime.now().time()
        start_time = datetime.strptime(quiet_config.get('start', '22:00'), '%H:%M').time()
        end_time = datetime.strptime(quiet_config.get('end', '07:00'), '%H:%M').time()
        
        if start_time < end_time:
            return start_time <= current_time <= end_time
        else:  # Crosses midnight
            return current_time >= start_time or current_time <= end_time
    
    
    def _format_alert_message(self, threat_data):
        """Format threat alert message"""
        severity = threat_data.get('severity', 'MEDIUM')
        threat_type = threat_data.get('threat_type', 'Unknown')
        description = threat_data.get('description', 'No description')
        indicator = threat_data.get('indicator', 'N/A')
        action = threat_data.get('action', 'Logged')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Severity emoji
        severity_emoji = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }
        
        message = f"""
{severity_emoji.get(severity, '⚪')} SECURITY ALERT - {severity}

Threat Type: {threat_type}
Severity: {severity}
Time: {timestamp}

Description:
{description}

Indicator: {indicator}
Action Taken: {action}

---
CyberGuard Industries - Automated Threat Detection
        """.strip()
        
        return message
    
    
    def _send_email_alert(self, message, threat_data):
        """Send email alert"""
        try:
            email_config = self.config['email']
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{threat_data.get('severity')}] Security Alert: {threat_data.get('threat_type')}"
            msg['From'] = email_config['from_addr']
            msg['To'] = ', '.join(email_config['to_addrs'])
            
            # Plain text and HTML versions
            text_part = MIMEText(message, 'plain')
            html_part = MIMEText(self._format_html_email(message, threat_data), 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['username'], email_config['password'])
                server.send_message(msg)
            
            self.alert_stats['by_channel']['email'] += 1
            return {'status': 'success', 'message': 'Email sent'}
            
        except Exception as e:
            self.alert_stats['failed'] += 1
            return {'status': 'error', 'message': str(e)}
    
    
    def _send_sms_alert(self, message, threat_data):
        """Send SMS alert (Twilio)"""
        try:
            sms_config = self.config['sms']
            
            # Shorten message for SMS
            short_message = f"{threat_data.get('severity')}: {threat_data.get('description', '')[:100]}"
            
            # Example with Twilio (requires twilio library)
            # from twilio.rest import Client
            # client = Client(sms_config['account_sid'], sms_config['auth_token'])
            # for to_number in sms_config['to_numbers']:
            #     client.messages.create(
            #         body=short_message,
            #         from_=sms_config['from_number'],
            #         to=to_number
            #     )
            
            # For demo, just log
            print(f"📱 SMS Alert: {short_message}")
            
            self.alert_stats['by_channel']['sms'] += 1
            return {'status': 'success', 'message': 'SMS sent (demo mode)'}
            
        except Exception as e:
            self.alert_stats['failed'] += 1
            return {'status': 'error', 'message': str(e)}
    
    
    def _send_slack_alert(self, message, threat_data):
        """Send Slack alert"""
        try:
            slack_config = self.config['slack']
            
            # Format Slack message
            severity_color = {
                'CRITICAL': '#dc3545',
                'HIGH': '#fd7e14',
                'MEDIUM': '#ffc107',
                'LOW': '#28a745'
            }
            
            payload = {
                'username': slack_config['username'],
                'channel': slack_config['channel'],
                'attachments': [{
                    'color': severity_color.get(threat_data.get('severity'), '#6c757d'),
                    'title': f"{threat_data.get('severity')} Threat Detected",
                    'text': threat_data.get('description', ''),
                    'fields': [
                        {'title': 'Type', 'value': threat_data.get('threat_type', 'Unknown'), 'short': True},
                        {'title': 'Indicator', 'value': threat_data.get('indicator', 'N/A'), 'short': True},
                        {'title': 'Action', 'value': threat_data.get('action', 'Logged'), 'short': True},
                        {'title': 'Time', 'value': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'short': True}
                    ],
                    'footer': 'CyberGuard Industries',
                    'ts': int(datetime.now().timestamp())
                }]
            }
            
            response = requests.post(slack_config['webhook_url'], json=payload, timeout=10)
            
            if response.status_code == 200:
                self.alert_stats['by_channel']['slack'] += 1
                return {'status': 'success', 'message': 'Slack alert sent'}
            else:
                self.alert_stats['failed'] += 1
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
                
        except Exception as e:
            self.alert_stats['failed'] += 1
            return {'status': 'error', 'message': str(e)}
    
    
    def _send_webhook_alert(self, message, threat_data):
        """Send webhook alert"""
        try:
            webhook_config = self.config['webhook']
            
            payload = {
                'timestamp': datetime.now().isoformat(),
                'severity': threat_data.get('severity'),
                'threat_type': threat_data.get('threat_type'),
                'description': threat_data.get('description'),
                'indicator': threat_data.get('indicator'),
                'action': threat_data.get('action'),
                'source': 'CyberGuard Industries'
            }
            
            headers = webhook_config.get('headers', {})
            headers['Content-Type'] = 'application/json'
            
            method = webhook_config.get('method', 'POST').upper()
            
            if method == 'POST':
                response = requests.post(webhook_config['url'], json=payload, 
                                       headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(webhook_config['url'], json=payload, 
                                      headers=headers, timeout=10)
            
            if response.status_code < 400:
                self.alert_stats['by_channel']['webhook'] += 1
                return {'status': 'success', 'message': 'Webhook called'}
            else:
                self.alert_stats['failed'] += 1
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
                
        except Exception as e:
            self.alert_stats['failed'] += 1
            return {'status': 'error', 'message': str(e)}
    
    
    def _format_html_email(self, message, threat_data):
        """Format HTML email"""
        severity = threat_data.get('severity', 'MEDIUM')
        severity_colors = {
            'CRITICAL': '#dc3545',
            'HIGH': '#fd7e14',
            'MEDIUM': '#ffc107',
            'LOW': '#28a745'
        }
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="border-left: 4px solid {severity_colors.get(severity, '#6c757d')}; padding-left: 15px;">
                <h2 style="color: {severity_colors.get(severity)};">🛡️ Security Alert - {severity}</h2>
                <p><strong>Threat Type:</strong> {threat_data.get('threat_type', 'Unknown')}</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Description:</strong> {threat_data.get('description', 'No description')}</p>
                <p><strong>Indicator:</strong> <code>{threat_data.get('indicator', 'N/A')}</code></p>
                <p><strong>Action Taken:</strong> {threat_data.get('action', 'Logged')}</p>
            </div>
            <hr>
            <p style="color: #666; font-size: 0.9em;">CyberGuard Industries - Automated Threat Detection</p>
        </body>
        </html>
        """
        
        return html
    
    
    def _update_stats(self, results):
        """Update alert statistics"""
        self.alert_stats['total_sent'] += 1
        
        severity = results['threat'].get('severity', 'MEDIUM')
        if severity in self.alert_stats['by_severity']:
            self.alert_stats['by_severity'][severity] += 1
    
    
    def get_stats(self):
        """Get alert statistics"""
        return self.alert_stats
    
    
    def get_recent_alerts(self, limit=50):
        """Get recent alert history"""
        return list(self.alert_history)[-limit:]


if __name__ == '__main__':
    # Demo
    import sys
    from pathlib import Path
    
    workspace = Path(__file__).parent.parent
    
    print("=" * 70)
    print("🔔 THREAT ALERT SYSTEM - DEMO")
    print("=" * 70)
    print()
    
    alert_system = ThreatAlertSystem(workspace)
    
    # Test alert
    test_threat = {
        'severity': 'CRITICAL',
        'threat_type': 'Malicious IP Connection',
        'description': 'Connection attempt from known malicious IP address 192.168.1.100',
        'indicator': '192.168.1.100',
        'action': 'BLOCKED'
    }
    
    print("\n📤 Sending test alert...")
    result = alert_system.send_alert(test_threat)
    
    print("\n📊 Alert Statistics:")
    stats = alert_system.get_stats()
    print(f"   Total sent: {stats['total_sent']}")
    print(f"   By severity: {stats['by_severity']}")
    print(f"   By channel: {stats['by_channel']}")
    print(f"   Failed: {stats['failed']}")
    
    print("\n✅ Demo complete!")
