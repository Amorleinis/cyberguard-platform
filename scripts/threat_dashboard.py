"""
CyberGuard Industries - Real-Time Threat Monitoring Dashboard
Enterprise-grade web-based security monitoring and visualization platform
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import threading
import time
from datetime import datetime, timedelta
import psutil
import os
from collections import defaultdict, deque
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from active_threat_monitor import ActiveThreatMonitor
from automated_response_engine import AutomatedResponseEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cyberguard-industries-2024-secure-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global monitoring state
monitoring_active = False
monitor_thread = None
threat_monitor = None
response_engine = None

# Dashboard statistics
dashboard_stats = {
    'total_scans': 0,
    'threats_detected': 0,
    'threats_blocked': 0,
    'active_connections': 0,
    'running_processes': 0,
    'cpu_usage': 0.0,
    'memory_usage': 0.0,
    'network_throughput': 0,
    'uptime': 0,
    'iocs_loaded': 0,
    'rules_loaded': 0,
    'last_scan_time': None,
    'scan_duration': 0
}

# Real-time threat feed (last 100 threats)
threat_feed = deque(maxlen=100)

# Threat statistics by type
threat_stats = {
    'malicious_ip': 0,
    'malicious_domain': 0,
    'malicious_hash': 0,
    'suspicious_process': 0,
    'suspicious_port': 0,
    'behavioral_anomaly': 0
}

# Timeline data for charts (last 60 data points)
timeline_data = {
    'timestamps': deque(maxlen=60),
    'cpu': deque(maxlen=60),
    'memory': deque(maxlen=60),
    'threats': deque(maxlen=60),
    'connections': deque(maxlen=60)
}

# Response actions log
response_log = deque(maxlen=50)

# System start time
start_time = datetime.now()


def initialize_monitoring_engines():
    """Initialize threat monitoring and response engines"""
    global threat_monitor, response_engine
    
    print("🔧 Initializing monitoring engines...")
    
    # Get workspace root (parent of scripts directory)
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Initialize response engine
    response_engine = AutomatedResponseEngine(workspace_root, auto_mode=True)
    
    # Initialize threat monitor with auto-response
    threat_monitor = ActiveThreatMonitor(workspace_root, auto_respond=True)
    
    # Update stats with loaded data
    dashboard_stats['iocs_loaded'] = threat_monitor.iocs_loaded
    dashboard_stats['rules_loaded'] = len(threat_monitor.detection_rules)
    
    print(f"✅ Loaded {dashboard_stats['iocs_loaded']:,} IOCs")
    print(f"✅ Loaded {dashboard_stats['rules_loaded']:,} detection rules")


def run_monitoring_loop():
    """Background thread for continuous monitoring"""
    global monitoring_active, dashboard_stats, threat_feed, timeline_data
    
    print("🚀 Starting continuous monitoring loop...")
    
    while monitoring_active:
        try:
            scan_start = time.time()
            
            # Perform comprehensive scan
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running security scan...")
            
            # Scan network connections
            conn_threats = threat_monitor.scan_network_connections()
            
            # Scan running processes
            proc_threats = threat_monitor.scan_running_processes()
            
            # Scan DNS queries
            dns_threats = threat_monitor.scan_dns_queries()
            
            # Scan open ports
            port_threats = threat_monitor.scan_open_ports()
            
            # Behavioral analysis
            behavioral_threats = threat_monitor.behavioral_analysis()
            
            # Combine all threats
            all_threats = (conn_threats + proc_threats + dns_threats + 
                          port_threats + behavioral_threats)
            
            # Update statistics
            scan_duration = time.time() - scan_start
            dashboard_stats['total_scans'] += 1
            dashboard_stats['scan_duration'] = round(scan_duration, 2)
            dashboard_stats['last_scan_time'] = datetime.now().isoformat()
            
            # Get system metrics
            dashboard_stats['cpu_usage'] = psutil.cpu_percent(interval=0.1)
            dashboard_stats['memory_usage'] = psutil.virtual_memory().percent
            dashboard_stats['active_connections'] = len(psutil.net_connections())
            dashboard_stats['running_processes'] = len(list(psutil.process_iter()))
            dashboard_stats['uptime'] = int((datetime.now() - start_time).total_seconds())
            
            # Get network throughput
            net_io = psutil.net_io_counters()
            dashboard_stats['network_throughput'] = net_io.bytes_sent + net_io.bytes_recv
            
            # Process detected threats
            if all_threats:
                dashboard_stats['threats_detected'] += len(all_threats)
                
                for threat in all_threats:
                    # Add to threat feed
                    threat_entry = {
                        'timestamp': datetime.now().isoformat(),
                        'severity': threat.get('severity', 'MEDIUM'),
                        'type': threat.get('threat_type', 'Unknown'),
                        'description': threat.get('description', 'No description'),
                        'indicator': threat.get('indicator', 'N/A'),
                        'action': threat.get('action', 'Logged')
                    }
                    threat_feed.append(threat_entry)
                    
                    # Update threat statistics
                    threat_type = threat.get('threat_type', 'unknown')
                    if threat_type in threat_stats:
                        threat_stats[threat_type] += 1
                    
                    # Log automated response
                    if threat.get('action') and threat.get('action') != 'LOGGED':
                        response_entry = {
                            'timestamp': datetime.now().isoformat(),
                            'action': threat.get('action'),
                            'target': threat.get('indicator', 'Unknown'),
                            'status': 'Success',
                            'threat_type': threat_type
                        }
                        response_log.append(response_entry)
                        dashboard_stats['threats_blocked'] += 1
                
                # Emit real-time update to connected clients
                socketio.emit('threat_detected', {
                    'threats': [t for t in threat_feed][-10:],  # Last 10 threats
                    'count': len(all_threats)
                })
            
            # Update timeline data
            current_time = datetime.now().strftime('%H:%M:%S')
            timeline_data['timestamps'].append(current_time)
            timeline_data['cpu'].append(dashboard_stats['cpu_usage'])
            timeline_data['memory'].append(dashboard_stats['memory_usage'])
            timeline_data['threats'].append(len(all_threats))
            timeline_data['connections'].append(dashboard_stats['active_connections'])
            
            # Emit stats update
            socketio.emit('stats_update', dashboard_stats)
            
            # Emit timeline update
            socketio.emit('timeline_update', {
                'timestamps': list(timeline_data['timestamps']),
                'cpu': list(timeline_data['cpu']),
                'memory': list(timeline_data['memory']),
                'threats': list(timeline_data['threats']),
                'connections': list(timeline_data['connections'])
            })
            
            print(f"✅ Scan complete: {len(all_threats)} threats | "
                  f"CPU: {dashboard_stats['cpu_usage']:.1f}% | "
                  f"Memory: {dashboard_stats['memory_usage']:.1f}%")
            
            # Wait before next scan (configurable interval)
            time.sleep(30)  # Scan every 30 seconds
            
        except Exception as e:
            print(f"❌ Error in monitoring loop: {e}")
            time.sleep(5)
    
    print("🛑 Monitoring loop stopped")


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/stats')
def get_stats():
    """Get current dashboard statistics"""
    return jsonify(dashboard_stats)


@app.route('/api/threats')
def get_threats():
    """Get recent threat feed"""
    return jsonify({
        'threats': list(threat_feed),
        'total': len(threat_feed)
    })


@app.route('/api/threat-stats')
def get_threat_stats():
    """Get threat statistics by type"""
    return jsonify(threat_stats)


@app.route('/api/responses')
def get_responses():
    """Get automated response log"""
    return jsonify({
        'responses': list(response_log),
        'total': len(response_log)
    })


@app.route('/api/timeline')
def get_timeline():
    """Get timeline data for charts"""
    return jsonify({
        'timestamps': list(timeline_data['timestamps']),
        'cpu': list(timeline_data['cpu']),
        'memory': list(timeline_data['memory']),
        'threats': list(timeline_data['threats']),
        'connections': list(timeline_data['connections'])
    })


@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    """Start continuous monitoring"""
    global monitoring_active, monitor_thread
    
    if not monitoring_active:
        monitoring_active = True
        monitor_thread = threading.Thread(target=run_monitoring_loop, daemon=True)
        monitor_thread.start()
        return jsonify({'status': 'success', 'message': 'Monitoring started'})
    else:
        return jsonify({'status': 'warning', 'message': 'Monitoring already active'})


@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """Stop continuous monitoring"""
    global monitoring_active
    
    monitoring_active = False
    return jsonify({'status': 'success', 'message': 'Monitoring stopped'})


@app.route('/api/monitoring/status')
def monitoring_status():
    """Get monitoring status"""
    return jsonify({
        'active': monitoring_active,
        'uptime': dashboard_stats['uptime'],
        'total_scans': dashboard_stats['total_scans']
    })


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'🔌 Client connected: {request.sid}')
    emit('connection_response', {'status': 'connected'})
    
    # Send initial data
    emit('stats_update', dashboard_stats)
    emit('threat_feed', {'threats': list(threat_feed)})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'🔌 Client disconnected: {request.sid}')


@socketio.on('request_stats')
def handle_stats_request():
    """Handle stats request from client"""
    emit('stats_update', dashboard_stats)


def create_dashboard_template():
    """Create HTML template for dashboard"""
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    template_path = os.path.join(template_dir, 'dashboard.html')
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CyberGuard Industries - Threat Monitoring Dashboard</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            overflow-x: hidden;
        }
        
        .header {
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 5px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .container {
            max-width: 1600px;
            margin: 20px auto;
            padding: 0 20px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        
        .stat-card h3 {
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.85em;
            margin-top: 5px;
        }
        
        .threat-critical { color: #dc3545; }
        .threat-high { color: #fd7e14; }
        .threat-medium { color: #ffc107; }
        .threat-low { color: #28a745; }
        
        .main-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .panel {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .panel h2 {
            color: #667eea;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
        }
        
        .threat-feed {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .threat-item {
            padding: 12px;
            border-left: 4px solid;
            margin-bottom: 10px;
            background: #f8f9fa;
            border-radius: 0 5px 5px 0;
        }
        
        .threat-item.CRITICAL { border-left-color: #dc3545; }
        .threat-item.HIGH { border-left-color: #fd7e14; }
        .threat-item.MEDIUM { border-left-color: #ffc107; }
        .threat-item.LOW { border-left-color: #28a745; }
        
        .threat-time {
            font-size: 0.8em;
            color: #666;
        }
        
        .threat-desc {
            margin: 5px 0;
            font-weight: 500;
        }
        
        .threat-indicator {
            font-size: 0.85em;
            color: #666;
            font-family: monospace;
        }
        
        .controls {
            text-align: center;
            margin: 20px 0;
        }
        
        .btn {
            padding: 12px 30px;
            margin: 0 10px;
            border: none;
            border-radius: 5px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: bold;
        }
        
        .btn-start {
            background: #28a745;
            color: white;
        }
        
        .btn-start:hover {
            background: #218838;
        }
        
        .btn-stop {
            background: #dc3545;
            color: white;
        }
        
        .btn-stop:hover {
            background: #c82333;
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin-left: 10px;
        }
        
        .status-active {
            background: #28a745;
            color: white;
        }
        
        .status-inactive {
            background: #6c757d;
            color: white;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ CyberGuard Industries</h1>
        <p>Real-Time Threat Monitoring Dashboard</p>
        <span id="status-badge" class="status-badge status-inactive">⚫ INACTIVE</span>
    </div>
    
    <div class="container">
        <div class="controls">
            <button class="btn btn-start" onclick="startMonitoring()">▶️ Start Monitoring</button>
            <button class="btn btn-stop" onclick="stopMonitoring()">⏹️ Stop Monitoring</button>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Scans</h3>
                <div class="stat-value" id="total-scans">0</div>
                <div class="stat-label">Security scans performed</div>
            </div>
            <div class="stat-card">
                <h3>Threats Detected</h3>
                <div class="stat-value threat-critical" id="threats-detected">0</div>
                <div class="stat-label">Security threats identified</div>
            </div>
            <div class="stat-card">
                <h3>Threats Blocked</h3>
                <div class="stat-value threat-high" id="threats-blocked">0</div>
                <div class="stat-label">Automated responses executed</div>
            </div>
            <div class="stat-card">
                <h3>Active Connections</h3>
                <div class="stat-value" id="active-connections">0</div>
                <div class="stat-label">Network connections monitored</div>
            </div>
            <div class="stat-card">
                <h3>CPU Usage</h3>
                <div class="stat-value" id="cpu-usage">0%</div>
                <div class="stat-label">System processor load</div>
            </div>
            <div class="stat-card">
                <h3>Memory Usage</h3>
                <div class="stat-value" id="memory-usage">0%</div>
                <div class="stat-label">System memory load</div>
            </div>
            <div class="stat-card">
                <h3>IOCs Loaded</h3>
                <div class="stat-value" id="iocs-loaded">0</div>
                <div class="stat-label">Threat indicators</div>
            </div>
            <div class="stat-card">
                <h3>Detection Rules</h3>
                <div class="stat-value" id="rules-loaded">0</div>
                <div class="stat-label">Active security rules</div>
            </div>
        </div>
        
        <div class="main-grid">
            <div class="panel">
                <h2>📊 System Metrics Timeline</h2>
                <div class="chart-container">
                    <canvas id="metricsChart"></canvas>
                </div>
            </div>
            
            <div class="panel">
                <h2>🎯 Threat Distribution</h2>
                <div class="chart-container">
                    <canvas id="threatChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="panel">
            <h2>🚨 Live Threat Feed</h2>
            <div class="threat-feed" id="threat-feed">
                <p style="text-align: center; color: #666; padding: 20px;">
                    No threats detected. System is secure.
                </p>
            </div>
        </div>
    </div>
    
    <script>
        const socket = io();
        let metricsChart, threatChart;
        let monitoringActive = false;
        
        // Initialize charts
        function initCharts() {
            const ctxMetrics = document.getElementById('metricsChart').getContext('2d');
            metricsChart = new Chart(ctxMetrics, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'CPU Usage (%)',
                            data: [],
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Memory Usage (%)',
                            data: [],
                            borderColor: '#764ba2',
                            backgroundColor: 'rgba(118, 75, 162, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Threats Detected',
                            data: [],
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
            
            const ctxThreat = document.getElementById('threatChart').getContext('2d');
            threatChart = new Chart(ctxThreat, {
                type: 'doughnut',
                data: {
                    labels: ['Malicious IP', 'Malicious Domain', 'Malicious Hash', 
                             'Suspicious Process', 'Suspicious Port', 'Behavioral Anomaly'],
                    datasets: [{
                        data: [0, 0, 0, 0, 0, 0],
                        backgroundColor: [
                            '#dc3545', '#fd7e14', '#ffc107', 
                            '#28a745', '#17a2b8', '#6f42c1'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
        
        // Socket.IO event handlers
        socket.on('connect', () => {
            console.log('Connected to dashboard server');
        });
        
        socket.on('stats_update', (stats) => {
            document.getElementById('total-scans').textContent = stats.total_scans.toLocaleString();
            document.getElementById('threats-detected').textContent = stats.threats_detected.toLocaleString();
            document.getElementById('threats-blocked').textContent = stats.threats_blocked.toLocaleString();
            document.getElementById('active-connections').textContent = stats.active_connections.toLocaleString();
            document.getElementById('cpu-usage').textContent = stats.cpu_usage.toFixed(1) + '%';
            document.getElementById('memory-usage').textContent = stats.memory_usage.toFixed(1) + '%';
            document.getElementById('iocs-loaded').textContent = stats.iocs_loaded.toLocaleString();
            document.getElementById('rules-loaded').textContent = stats.rules_loaded.toLocaleString();
        });
        
        socket.on('timeline_update', (data) => {
            if (metricsChart) {
                metricsChart.data.labels = data.timestamps;
                metricsChart.data.datasets[0].data = data.cpu;
                metricsChart.data.datasets[1].data = data.memory;
                metricsChart.data.datasets[2].data = data.threats;
                metricsChart.update('none');
            }
        });
        
        socket.on('threat_detected', (data) => {
            updateThreatFeed(data.threats);
        });
        
        function updateThreatFeed(threats) {
            const feed = document.getElementById('threat-feed');
            if (threats.length === 0) {
                feed.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">No threats detected. System is secure.</p>';
                return;
            }
            
            feed.innerHTML = '';
            threats.reverse().forEach(threat => {
                const item = document.createElement('div');
                item.className = `threat-item ${threat.severity}`;
                item.innerHTML = `
                    <div class="threat-time">${new Date(threat.timestamp).toLocaleTimeString()}</div>
                    <div class="threat-desc">${threat.description}</div>
                    <div class="threat-indicator">Indicator: ${threat.indicator} | Action: ${threat.action}</div>
                `;
                feed.appendChild(item);
            });
        }
        
        async function startMonitoring() {
            const response = await fetch('/api/monitoring/start', { method: 'POST' });
            const data = await response.json();
            if (data.status === 'success') {
                monitoringActive = true;
                updateStatusBadge();
            }
            alert(data.message);
        }
        
        async function stopMonitoring() {
            const response = await fetch('/api/monitoring/stop', { method: 'POST' });
            const data = await response.json();
            if (data.status === 'success') {
                monitoringActive = false;
                updateStatusBadge();
            }
            alert(data.message);
        }
        
        function updateStatusBadge() {
            const badge = document.getElementById('status-badge');
            if (monitoringActive) {
                badge.textContent = '🟢 ACTIVE';
                badge.className = 'status-badge status-active pulse';
            } else {
                badge.textContent = '⚫ INACTIVE';
                badge.className = 'status-badge status-inactive';
            }
        }
        
        // Initialize on page load
        window.onload = () => {
            initCharts();
            // Request initial stats
            socket.emit('request_stats');
        };
    </script>
</body>
</html>
"""
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard template created: {template_path}")


if __name__ == '__main__':
    print("=" * 70)
    print("🛡️  CYBERGUARD INDUSTRIES - THREAT MONITORING DASHBOARD")
    print("=" * 70)
    print()
    
    # Create dashboard template
    create_dashboard_template()
    
    # Initialize monitoring engines
    initialize_monitoring_engines()
    
    print()
    print("🌐 Starting web dashboard server...")
    print("📍 Dashboard URL: http://localhost:5000")
    print("=" * 70)
    print()
    print("🎯 Features:")
    print("   ✅ Real-time threat monitoring")
    print("   ✅ Live system metrics")
    print("   ✅ Interactive charts and visualizations")
    print("   ✅ Automated response tracking")
    print("   ✅ WebSocket-powered updates")
    print()
    print("⌨️  Press Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    # Run Flask app with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
