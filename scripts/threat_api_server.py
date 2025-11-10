"""
CyberGuard Industries - REST API
Comprehensive API for external tool integration and automation
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import jwt
import json
import io
import csv
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps
import sys

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))

from active_threat_monitor import ActiveThreatMonitor
from automated_response_engine import AutomatedResponseEngine
from threat_intelligence_feeds import ThreatIntelligenceFeedManager
from threat_alert_system import ThreatAlertSystem

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['SECRET_KEY'] = 'cyberguard-api-secret-key-2024'
app.config['JWT_EXPIRATION_HOURS'] = 24

# Global instances
workspace_root = Path(__file__).parent.parent
threat_monitor = None
response_engine = None
feed_manager = None
alert_system = None

# API statistics
api_stats = {
    'total_requests': 0,
    'by_endpoint': {},
    'by_method': {},
    'errors': 0,
    'start_time': datetime.now().isoformat()
}


def initialize_engines():
    """Initialize security engines"""
    global threat_monitor, response_engine, feed_manager, alert_system
    
    print("🔧 Initializing security engines...")
    
    response_engine = AutomatedResponseEngine(workspace_root, auto_mode=False)
    threat_monitor = ActiveThreatMonitor(workspace_root, auto_respond=False)
    feed_manager = ThreatIntelligenceFeedManager(workspace_root)
    alert_system = ThreatAlertSystem(workspace_root)
    
    print("✅ All engines initialized")


def require_auth(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Missing authentication token'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user = data['user']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def track_request(f):
    """Decorator to track API requests"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_stats['total_requests'] += 1
        
        endpoint = request.endpoint or 'unknown'
        method = request.method
        
        api_stats['by_endpoint'][endpoint] = api_stats['by_endpoint'].get(endpoint, 0) + 1
        api_stats['by_method'][method] = api_stats['by_method'].get(method, 0) + 1
        
        try:
            return f(*args, **kwargs)
        except Exception as e:
            api_stats['errors'] += 1
            raise
    
    return decorated


# ==================== AUTHENTICATION ====================

@app.route('/api/v1/auth/login', methods=['POST'])
@track_request
def login():
    """Authenticate and get JWT token"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    # Simple auth (in production, use proper authentication)
    if username == 'admin' and password == 'cyberguard2024':
        token = jwt.encode({
            'user': username,
            'exp': datetime.utcnow() + timedelta(hours=app.config['JWT_EXPIRATION_HOURS'])
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'token': token,
            'expires_in': app.config['JWT_EXPIRATION_HOURS'] * 3600,
            'user': username
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401


# ==================== THREAT SCANNING ====================

@app.route('/api/v1/scan/connections', methods=['POST'])
@track_request
@require_auth
def scan_connections():
    """Scan network connections for threats"""
    threats = threat_monitor.scan_network_connections()
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'scan_type': 'network_connections',
        'threats_found': len(threats),
        'threats': threats
    })


@app.route('/api/v1/scan/processes', methods=['POST'])
@track_request
@require_auth
def scan_processes():
    """Scan running processes for threats"""
    threats = threat_monitor.scan_running_processes()
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'scan_type': 'running_processes',
        'threats_found': len(threats),
        'threats': threats
    })


@app.route('/api/v1/scan/dns', methods=['POST'])
@track_request
@require_auth
def scan_dns():
    """Scan DNS queries for threats"""
    threats = threat_monitor.scan_dns_queries()
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'scan_type': 'dns_queries',
        'threats_found': len(threats),
        'threats': threats
    })


@app.route('/api/v1/scan/ports', methods=['POST'])
@track_request
@require_auth
def scan_ports():
    """Scan open ports for threats"""
    threats = threat_monitor.scan_open_ports()
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'scan_type': 'open_ports',
        'threats_found': len(threats),
        'threats': threats
    })


@app.route('/api/v1/scan/full', methods=['POST'])
@track_request
@require_auth
def scan_full():
    """Perform full system scan"""
    all_threats = []
    
    all_threats.extend(threat_monitor.scan_network_connections())
    all_threats.extend(threat_monitor.scan_running_processes())
    all_threats.extend(threat_monitor.scan_dns_queries())
    all_threats.extend(threat_monitor.scan_open_ports())
    all_threats.extend(threat_monitor.behavioral_analysis())
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'scan_type': 'full_system',
        'threats_found': len(all_threats),
        'threats': all_threats,
        'by_type': {
            'network': len([t for t in all_threats if 'connection' in t.get('threat_type', '').lower()]),
            'process': len([t for t in all_threats if 'process' in t.get('threat_type', '').lower()]),
            'dns': len([t for t in all_threats if 'domain' in t.get('threat_type', '').lower()]),
            'port': len([t for t in all_threats if 'port' in t.get('threat_type', '').lower()]),
            'behavioral': len([t for t in all_threats if 'anomaly' in t.get('threat_type', '').lower()])
        }
    })


# ==================== IOC MANAGEMENT ====================

@app.route('/api/v1/iocs/search', methods=['GET'])
@track_request
@require_auth
def search_iocs():
    """Search IOC database"""
    query = request.args.get('q', '')
    ioc_type = request.args.get('type', 'all')
    
    results = []
    
    if ioc_type in ['ip', 'all'] and query in threat_monitor.malicious_ips:
        results.append({'type': 'ip', 'indicator': query, 'status': 'malicious'})
    
    if ioc_type in ['domain', 'all'] and query in threat_monitor.malicious_domains:
        results.append({'type': 'domain', 'indicator': query, 'status': 'malicious'})
    
    if ioc_type in ['hash', 'all'] and query in threat_monitor.malicious_hashes:
        results.append({'type': 'hash', 'indicator': query, 'status': 'malicious'})
    
    return jsonify({
        'query': query,
        'type': ioc_type,
        'results': results,
        'found': len(results) > 0
    })


@app.route('/api/v1/iocs/stats', methods=['GET'])
@track_request
@require_auth
def ioc_stats():
    """Get IOC statistics"""
    return jsonify({
        'total_iocs': threat_monitor.iocs_loaded,
        'by_type': {
            'ips': len(threat_monitor.malicious_ips),
            'domains': len(threat_monitor.malicious_domains),
            'hashes': len(threat_monitor.malicious_hashes),
            'urls': len(threat_monitor.malicious_urls),
            'emails': len(threat_monitor.malicious_emails)
        },
        'detection_rules': len(threat_monitor.detection_rules)
    })


@app.route('/api/v1/iocs/add', methods=['POST'])
@track_request
@require_auth
def add_ioc():
    """Add new IOC"""
    data = request.get_json()
    
    ioc_type = data.get('type')
    indicator = data.get('indicator')
    
    if not ioc_type or not indicator:
        return jsonify({'error': 'Missing type or indicator'}), 400
    
    # Add to appropriate set
    if ioc_type == 'ip':
        threat_monitor.malicious_ips.add(indicator)
    elif ioc_type == 'domain':
        threat_monitor.malicious_domains.add(indicator)
    elif ioc_type == 'hash':
        threat_monitor.malicious_hashes.add(indicator)
    elif ioc_type == 'url':
        threat_monitor.malicious_urls.add(indicator)
    else:
        return jsonify({'error': 'Invalid IOC type'}), 400
    
    threat_monitor.iocs_loaded += 1
    
    return jsonify({
        'status': 'success',
        'type': ioc_type,
        'indicator': indicator,
        'total_iocs': threat_monitor.iocs_loaded
    })


# ==================== AUTOMATED RESPONSE ====================

@app.route('/api/v1/response/block-ip', methods=['POST'])
@track_request
@require_auth
def block_ip():
    """Block an IP address"""
    data = request.get_json()
    ip = data.get('ip')
    
    if not ip:
        return jsonify({'error': 'Missing IP address'}), 400
    
    result = response_engine.block_ip_address(ip)
    
    return jsonify({
        'action': 'block_ip',
        'ip': ip,
        'result': result
    })


@app.route('/api/v1/response/terminate-process', methods=['POST'])
@track_request
@require_auth
def terminate_process():
    """Terminate a process"""
    data = request.get_json()
    pid = data.get('pid')
    
    if not pid:
        return jsonify({'error': 'Missing process ID'}), 400
    
    result = response_engine.terminate_process(pid)
    
    return jsonify({
        'action': 'terminate_process',
        'pid': pid,
        'result': result
    })


@app.route('/api/v1/response/block-domain', methods=['POST'])
@track_request
@require_auth
def block_domain():
    """Block a domain"""
    data = request.get_json()
    domain = data.get('domain')
    
    if not domain:
        return jsonify({'error': 'Missing domain'}), 400
    
    result = response_engine.block_domain(domain)
    
    return jsonify({
        'action': 'block_domain',
        'domain': domain,
        'result': result
    })


# ==================== THREAT INTELLIGENCE FEEDS ====================

@app.route('/api/v1/feeds/update', methods=['POST'])
@track_request
@require_auth
def update_feeds():
    """Update threat intelligence feeds"""
    feed_id = request.args.get('feed')
    
    if feed_id:
        indicators = feed_manager.fetch_feed(feed_id)
        count = len(indicators) if indicators else 0
    else:
        count = feed_manager.fetch_all_feeds()
    
    return jsonify({
        'status': 'success',
        'feed': feed_id or 'all',
        'new_indicators': count
    })


@app.route('/api/v1/feeds/stats', methods=['GET'])
@track_request
@require_auth
def feed_stats():
    """Get feed statistics"""
    stats = feed_manager.get_feed_stats()
    
    return jsonify(stats)


# ==================== ALERTS ====================

@app.route('/api/v1/alerts/send', methods=['POST'])
@track_request
@require_auth
def send_alert():
    """Send threat alert"""
    data = request.get_json()
    
    result = alert_system.send_alert(data)
    
    return jsonify(result)


@app.route('/api/v1/alerts/stats', methods=['GET'])
@track_request
@require_auth
def alert_stats():
    """Get alert statistics"""
    stats = alert_system.get_stats()
    
    return jsonify(stats)


@app.route('/api/v1/alerts/history', methods=['GET'])
@track_request
@require_auth
def alert_history():
    """Get alert history"""
    limit = int(request.args.get('limit', 50))
    
    alerts = alert_system.get_recent_alerts(limit)
    
    return jsonify({
        'count': len(alerts),
        'alerts': alerts
    })


# ==================== REPORTS ====================

@app.route('/api/v1/reports/threats', methods=['GET'])
@track_request
@require_auth
def threat_report():
    """Generate threat report"""
    format_type = request.args.get('format', 'json')
    days = int(request.args.get('days', 7))
    
    # Get recent threats
    threats = threat_monitor.threats_detected[-100:]
    
    if format_type == 'csv':
        # Generate CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['timestamp', 'severity', 'type', 'description', 'indicator'])
        writer.writeheader()
        
        for threat in threats:
            writer.writerow({
                'timestamp': threat.get('timestamp', ''),
                'severity': threat.get('severity', ''),
                'type': threat.get('threat_type', ''),
                'description': threat.get('description', ''),
                'indicator': threat.get('indicator', '')
            })
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'threat_report_{datetime.now().strftime("%Y%m%d")}.csv'
        )
    
    # JSON format
    return jsonify({
        'report_date': datetime.now().isoformat(),
        'period_days': days,
        'total_threats': len(threats),
        'threats': threats
    })


# ==================== SYSTEM INFO ====================

@app.route('/api/v1/system/status', methods=['GET'])
@track_request
def system_status():
    """Get system status"""
    return jsonify({
        'status': 'operational',
        'version': '1.0.0',
        'uptime': (datetime.now() - datetime.fromisoformat(api_stats['start_time'])).total_seconds(),
        'engines': {
            'threat_monitor': threat_monitor is not None,
            'response_engine': response_engine is not None,
            'feed_manager': feed_manager is not None,
            'alert_system': alert_system is not None
        }
    })


@app.route('/api/v1/system/stats', methods=['GET'])
@track_request
def system_stats():
    """Get API statistics"""
    return jsonify(api_stats)


# ==================== DOCUMENTATION ====================

@app.route('/api/v1/docs', methods=['GET'])
@track_request
def api_docs():
    """API documentation"""
    return jsonify({
        'name': 'CyberGuard Industries API',
        'version': '1.0.0',
        'description': 'Comprehensive threat detection and response API',
        'endpoints': {
            'authentication': {
                'POST /api/v1/auth/login': 'Get JWT authentication token'
            },
            'scanning': {
                'POST /api/v1/scan/connections': 'Scan network connections',
                'POST /api/v1/scan/processes': 'Scan running processes',
                'POST /api/v1/scan/dns': 'Scan DNS queries',
                'POST /api/v1/scan/ports': 'Scan open ports',
                'POST /api/v1/scan/full': 'Full system scan'
            },
            'iocs': {
                'GET /api/v1/iocs/search': 'Search IOC database',
                'GET /api/v1/iocs/stats': 'Get IOC statistics',
                'POST /api/v1/iocs/add': 'Add new IOC'
            },
            'response': {
                'POST /api/v1/response/block-ip': 'Block IP address',
                'POST /api/v1/response/terminate-process': 'Terminate process',
                'POST /api/v1/response/block-domain': 'Block domain'
            },
            'feeds': {
                'POST /api/v1/feeds/update': 'Update threat feeds',
                'GET /api/v1/feeds/stats': 'Get feed statistics'
            },
            'alerts': {
                'POST /api/v1/alerts/send': 'Send threat alert',
                'GET /api/v1/alerts/stats': 'Get alert statistics',
                'GET /api/v1/alerts/history': 'Get alert history'
            },
            'reports': {
                'GET /api/v1/reports/threats': 'Generate threat report'
            },
            'system': {
                'GET /api/v1/system/status': 'Get system status',
                'GET /api/v1/system/stats': 'Get API statistics'
            }
        }
    })


if __name__ == '__main__':
    print("=" * 70)
    print("🔌 CYBERGUARD INDUSTRIES - REST API SERVER")
    print("=" * 70)
    print()
    
    # Initialize engines
    initialize_engines()
    
    print()
    print("🌐 Starting API server...")
    print("📍 API URL: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/api/v1/docs")
    print("=" * 70)
    print()
    print("🔐 Default credentials:")
    print("   Username: admin")
    print("   Password: cyberguard2024")
    print()
    print("⌨️  Press Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=8000, debug=False)
