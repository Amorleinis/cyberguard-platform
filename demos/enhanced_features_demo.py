"""
CyberGuard Industries - Enhanced Features Demo
Demonstrates all new capabilities
"""

import os
import sys
import time
from pathlib import Path

# Add scripts to path
sys.path.append(str(Path(__file__).parent.parent / 'scripts'))

from threat_intelligence_feeds import ThreatIntelligenceFeedManager
from threat_alert_system import ThreatAlertSystem

def print_header(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_threat_feeds():
    """Demo threat intelligence feeds"""
    print_header("📡 THREAT INTELLIGENCE FEEDS DEMO")
    
    workspace = Path(__file__).parent.parent
    feed_manager = ThreatIntelligenceFeedManager(workspace)
    
    print("🔍 Available Feeds:")
    for feed_id, feed_data in feed_manager.feed_sources.items():
        status = "✅ Enabled" if feed_data['enabled'] else "❌ Disabled"
        print(f"   {status} - {feed_data['name']}")
        print(f"      Type: {feed_data['type']}")
        print(f"      Update interval: {feed_data['interval']/3600:.1f} hours")
    
    print("\n📥 Fetching latest threat intelligence...")
    print("   (This may take 30-60 seconds for all feeds)")
    
    total_new = feed_manager.fetch_all_feeds()
    
    print(f"\n✅ Fetch complete!")
    print(f"   Total new indicators: {total_new}")
    
    # Get statistics
    stats = feed_manager.get_feed_stats()
    
    print("\n📊 Feed Statistics:")
    print(f"   Total feeds: {stats['total_feeds']}")
    print(f"   Active feeds: {stats['active_feeds']}")
    print(f"   Total indicators collected: {stats['total_indicators']}")
    
    print("\n🆕 New IOCs discovered:")
    print(f"   Malicious IPs: {stats['new_iocs']['ips']}")
    print(f"   Malicious Domains: {stats['new_iocs']['domains']}")
    print(f"   Malware Hashes: {stats['new_iocs']['hashes']}")
    print(f"   Phishing URLs: {stats['new_iocs']['urls']}")
    
    # Show sample IOCs
    new_iocs = feed_manager.get_new_iocs()
    if new_iocs['ips']:
        print("\n📌 Sample malicious IPs:")
        for ip in list(new_iocs['ips'])[:5]:
            print(f"   • {ip}")
    
    if new_iocs['domains']:
        print("\n📌 Sample malicious domains:")
        for domain in list(new_iocs['domains'])[:5]:
            print(f"   • {domain}")


def demo_alert_system():
    """Demo alert system"""
    print_header("🔔 MULTI-CHANNEL ALERT SYSTEM DEMO")
    
    workspace = Path(__file__).parent.parent
    alert_system = ThreatAlertSystem(workspace)
    
    print("📋 Alert Channels Configuration:")
    print(f"   Email: {'✅ Enabled' if alert_system.config['email']['enabled'] else '❌ Disabled'}")
    print(f"   SMS: {'✅ Enabled' if alert_system.config['sms']['enabled'] else '❌ Disabled'}")
    print(f"   Slack: {'✅ Enabled' if alert_system.config['slack']['enabled'] else '❌ Disabled'}")
    print(f"   Webhook: {'✅ Enabled' if alert_system.config['webhook']['enabled'] else '❌ Disabled'}")
    
    print("\n⚙️  Configuration File:")
    print(f"   Location: {alert_system.config_file}")
    print(f"   Edit this file to enable email/SMS/Slack alerts")
    
    print("\n📤 Sending test alerts...")
    
    # Test different severity levels
    test_threats = [
        {
            'severity': 'CRITICAL',
            'threat_type': 'Ransomware Detection',
            'description': 'Suspicious file encryption activity detected',
            'indicator': 'process: ransomware.exe',
            'action': 'TERMINATED'
        },
        {
            'severity': 'HIGH',
            'threat_type': 'C2 Communication',
            'description': 'Connection to known command & control server',
            'indicator': '203.0.113.42',
            'action': 'BLOCKED'
        },
        {
            'severity': 'MEDIUM',
            'threat_type': 'Suspicious Port Scan',
            'description': 'Port scanning activity detected from internal IP',
            'indicator': '192.168.1.105',
            'action': 'LOGGED'
        }
    ]
    
    for threat in test_threats:
        print(f"\n   Sending {threat['severity']} alert...")
        result = alert_system.send_alert(threat)
        
        channels_sent = [ch for ch, res in result['channels'].items() if res.get('status') == 'success']
        if channels_sent:
            print(f"   ✅ Alert sent via: {', '.join(channels_sent)}")
        else:
            print(f"   ℹ️  No channels configured (demo mode)")
    
    print("\n📊 Alert Statistics:")
    stats = alert_system.get_stats()
    print(f"   Total alerts sent: {stats['total_sent']}")
    print(f"   By severity: {stats['by_severity']}")
    print(f"   By channel: {stats['by_channel']}")
    print(f"   Failed: {stats['failed']}")


def demo_api_features():
    """Demo API features"""
    print_header("🔌 REST API DEMO")
    
    print("📚 API Documentation:")
    print("   Base URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/api/v1/docs")
    
    print("\n🔐 Authentication:")
    print("   Username: admin")
    print("   Password: cyberguard2024")
    
    print("\n📋 Available Endpoints:")
    
    endpoints = {
        'Scanning': [
            'POST /api/v1/scan/full - Full system scan',
            'POST /api/v1/scan/connections - Network connections',
            'POST /api/v1/scan/processes - Running processes',
            'POST /api/v1/scan/dns - DNS queries',
            'POST /api/v1/scan/ports - Open ports'
        ],
        'IOC Management': [
            'GET /api/v1/iocs/search - Search IOCs',
            'GET /api/v1/iocs/stats - Get statistics',
            'POST /api/v1/iocs/add - Add new IOC'
        ],
        'Response Actions': [
            'POST /api/v1/response/block-ip - Block IP',
            'POST /api/v1/response/terminate-process - Kill process',
            'POST /api/v1/response/block-domain - Block domain'
        ],
        'Threat Feeds': [
            'POST /api/v1/feeds/update - Update feeds',
            'GET /api/v1/feeds/stats - Feed statistics'
        ],
        'Alerts': [
            'POST /api/v1/alerts/send - Send alert',
            'GET /api/v1/alerts/stats - Alert statistics',
            'GET /api/v1/alerts/history - Alert history'
        ],
        'Reports': [
            'GET /api/v1/reports/threats - Generate report',
            'GET /api/v1/reports/threats?format=csv - CSV export'
        ]
    }
    
    for category, eps in endpoints.items():
        print(f"\n   {category}:")
        for ep in eps:
            print(f"      • {ep}")
    
    print("\n💡 Example API Usage:")
    print("""
    # 1. Get authentication token
    curl -X POST http://localhost:8000/api/v1/auth/login \\
      -H "Content-Type: application/json" \\
      -d '{"username": "admin", "password": "cyberguard2024"}'
    
    # 2. Perform full scan
    curl -X POST http://localhost:8000/api/v1/scan/full \\
      -H "Authorization: Bearer YOUR_TOKEN"
    
    # 3. Block malicious IP
    curl -X POST http://localhost:8000/api/v1/response/block-ip \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"ip": "192.168.1.100"}'
    
    # 4. Generate CSV report
    curl -X GET "http://localhost:8000/api/v1/reports/threats?format=csv" \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      --output threat_report.csv
    """)
    
    print("\n🚀 Starting API Server:")
    print("   Run: python scripts/threat_api_server.py")
    print("   Then access API at http://localhost:8000")


def demo_dashboard():
    """Demo dashboard features"""
    print_header("📊 ENHANCED WEB DASHBOARD DEMO")
    
    print("🌐 Dashboard Features:")
    print("   URL: http://localhost:5000")
    
    print("\n📈 Real-Time Monitoring:")
    print("   ✅ Live threat feed with WebSocket updates")
    print("   ✅ System metrics (CPU, Memory, Network)")
    print("   ✅ Active connections tracking")
    print("   ✅ Process monitoring")
    print("   ✅ Threat statistics by type")
    
    print("\n📊 Interactive Charts:")
    print("   ✅ CPU/Memory timeline chart")
    print("   ✅ Threat detection trend line")
    print("   ✅ Threat distribution pie chart")
    print("   ✅ Network connections graph")
    
    print("\n🎛️  Control Panel:")
    print("   ✅ Start/Stop monitoring")
    print("   ✅ Real-time status indicator")
    print("   ✅ Scan statistics")
    print("   ✅ Response action log")
    
    print("\n🔔 Alert Integration:")
    print("   ✅ Visual threat notifications")
    print("   ✅ Severity color coding")
    print("   ✅ Action taken display")
    print("   ✅ Timestamp tracking")
    
    print("\n🚀 Starting Dashboard:")
    print("   Run: python scripts/threat_dashboard.py")
    print("   Then open http://localhost:5000 in your browser")


def print_summary():
    """Print feature summary"""
    print_header("✨ CYBERGUARD INDUSTRIES - FEATURE SUMMARY")
    
    print("🎯 Core Platform:")
    print("   ✅ 113,500+ IOC Database")
    print("   ✅ 10,000+ Detection Rules")
    print("   ✅ Real-time Threat Monitoring")
    print("   ✅ Automated Response Engine")
    print("   ✅ 7 Security Engines")
    
    print("\n🆕 New Enhancements:")
    print("   ✅ Threat Intelligence Feeds (4 sources)")
    print("   ✅ Multi-Channel Alerts (Email, SMS, Slack, Webhook)")
    print("   ✅ REST API (20+ endpoints)")
    print("   ✅ Enhanced Web Dashboard")
    print("   ✅ Report Generation (CSV, JSON)")
    print("   ✅ Historical Analytics")
    
    print("\n📦 Integration Capabilities:")
    print("   ✅ SIEM Integration")
    print("   ✅ SOAR Platform Integration")
    print("   ✅ Ticketing Systems")
    print("   ✅ Custom Webhooks")
    print("   ✅ Python/PowerShell APIs")
    
    print("\n🔐 Security Features:")
    print("   ✅ JWT Authentication")
    print("   ✅ Encrypted Communications")
    print("   ✅ Audit Logging")
    print("   ✅ Rate Limiting")
    print("   ✅ Access Control")
    
    print("\n📚 Documentation:")
    print("   📄 PLATFORM_ENHANCEMENTS.md - Complete feature guide")
    print("   📄 ACTIVE_PROTECTION_GUIDE.md - Usage instructions")
    print("   📄 API Docs - http://localhost:8000/api/v1/docs")
    print("   📄 GitHub - https://github.com/Amorleinis/cyberguard-platform")
    
    print("\n🚀 Quick Start Commands:")
    print("   Dashboard:  python scripts/threat_dashboard.py")
    print("   API Server: python scripts/threat_api_server.py")
    print("   Feed Test:  python scripts/threat_intelligence_feeds.py")
    print("   Alert Test: python scripts/threat_alert_system.py")


def main():
    """Main demo function"""
    print("\n" + "=" * 70)
    print("  🛡️  CYBERGUARD INDUSTRIES - ENHANCED FEATURES DEMO")
    print("=" * 70)
    print()
    print("This demo showcases all new platform enhancements:")
    print("   1. Threat Intelligence Feeds")
    print("   2. Multi-Channel Alert System")
    print("   3. REST API")
    print("   4. Enhanced Dashboard")
    print()
    input("Press Enter to begin demo...")
    
    try:
        # Demo each feature
        demo_threat_feeds()
        input("\nPress Enter to continue to Alert System demo...")
        
        demo_alert_system()
        input("\nPress Enter to continue to API demo...")
        
        demo_api_features()
        input("\nPress Enter to continue to Dashboard demo...")
        
        demo_dashboard()
        input("\nPress Enter to view summary...")
        
        print_summary()
        
        print("\n" + "=" * 70)
        print("  ✅ DEMO COMPLETE!")
        print("=" * 70)
        print()
        print("Your Fortune 500-scale cybersecurity platform is ready!")
        print()
        print("Next Steps:")
        print("   1. Configure alerts in data/config/alerts_config.json")
        print("   2. Start the dashboard: python scripts/threat_dashboard.py")
        print("   3. Start the API: python scripts/threat_api_server.py")
        print("   4. Read docs/PLATFORM_ENHANCEMENTS.md for details")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo error: {e}")


if __name__ == '__main__':
    main()
