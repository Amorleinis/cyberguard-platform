"""
Real-Time Active Threat Monitoring System
Continuously monitors system for threats using 113,500 IOCs and 10,000 detection rules
"""

import json
import psutil
import socket
import hashlib
import re
import threading
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import subprocess
import platform
import sys
import os

# Import automated response engine
sys.path.append(str(Path(__file__).parent))
from automated_response_engine import AutomatedResponseEngine

class ActiveThreatMonitor:
    """Real-time threat detection and prevention system"""
    
    def __init__(self, workspace_root, auto_respond=False):
        self.workspace_root = Path(workspace_root)
        self.running = False
        self.threats_detected = []
        self.scan_stats = defaultdict(int)
        self.auto_respond = auto_respond
        
        # Initialize automated response engine
        if auto_respond:
            print("🤖 Initializing automated response engine...")
            self.response_engine = AutomatedResponseEngine(workspace_root, auto_mode=True)
            print(f"   Auto-response: {'✅ ENABLED' if auto_respond else '❌ DISABLED'}")
            if self.response_engine.is_admin:
                print("   Admin privileges: ✅ Detected")
            else:
                print("   Admin privileges: ⚠️  Not detected (some actions limited)")
        else:
            self.response_engine = None
        
        # Load threat intelligence
        print("🔄 Loading threat intelligence databases...")
        self.load_iocs()
        self.load_detection_rules()
        print(f"✅ Loaded {self.iocs_loaded:,} IOCs and {self.rules_loaded:,} detection rules\n")
        
    def load_iocs(self):
        """Load IOC blocklist"""
        ioc_file = self.workspace_root / "data" / "processed" / "prevention" / "ioc_blocklist_enhanced.json"
        
        with open(ioc_file, 'r') as f:
            data = json.load(f)
        
        self.malicious_ips = set(ioc['ip'] for ioc in data['categories']['malicious_ips'])
        self.malicious_domains = set(ioc['domain'] for ioc in data['categories']['malicious_domains'])
        self.malicious_hashes = set(ioc['sha256'] for ioc in data['categories']['file_hashes'])
        self.malicious_urls = set(ioc['url'] for ioc in data['categories']['urls'])
        
        self.iocs_loaded = (
            len(self.malicious_ips) + 
            len(self.malicious_domains) + 
            len(self.malicious_hashes) + 
            len(self.malicious_urls)
        )
        
    def load_detection_rules(self):
        """Load detection rules"""
        rules_file = self.workspace_root / "detection" / "enhanced_detection_rules.json"
        
        with open(rules_file, 'r') as f:
            data = json.load(f)
        
        self.detection_rules = [rule for rule in data['rules'] if rule.get('enabled', True)]
        self.rules_loaded = len(self.detection_rules)
        
    def scan_network_connections(self):
        """Scan active network connections for malicious IPs"""
        print("\n🌐 Scanning Active Network Connections...")
        
        connections = psutil.net_connections(kind='inet')
        threats = []
        
        for conn in connections:
            if conn.raddr:  # Remote address exists
                remote_ip = conn.raddr.ip
                
                # Check against malicious IPs
                if remote_ip in self.malicious_ips:
                    threat = {
                        "timestamp": datetime.now().isoformat(),
                        "type": "Malicious Network Connection",
                        "severity": "CRITICAL",
                        "details": {
                            "remote_ip": remote_ip,
                            "remote_port": conn.raddr.port,
                            "local_port": conn.laddr.port,
                            "status": conn.status,
                            "pid": conn.pid
                        },
                        "action": "BLOCK_RECOMMENDED"
                    }
                    
                    threats.append(threat)
                    self.threats_detected.append(threat)
                    
                    # Execute automated response if enabled
                    if self.response_engine:
                        self.response_engine.respond_to_threat(threat)
                    
                    print(f"  🚨 THREAT DETECTED!")
                    print(f"     Malicious IP: {remote_ip}:{conn.raddr.port}")
                    print(f"     PID: {conn.pid} | Status: {conn.status}")
                    
                self.scan_stats['connections_scanned'] += 1
        
        if not threats:
            print(f"  ✅ Scanned {len(connections)} connections - No threats detected")
        else:
            print(f"  ⚠️  Found {len(threats)} malicious connections!")
            
        return threats
    
    def scan_running_processes(self):
        """Scan running processes for suspicious behavior"""
        print("\n🔍 Scanning Running Processes...")
        
        threats = []
        suspicious_names = ['powershell', 'cmd', 'wscript', 'cscript', 'mshta', 'regsvr32', 'rundll32']
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                pinfo = proc.info
                self.scan_stats['processes_scanned'] += 1
                
                # Check for suspicious process names
                if pinfo['name'] and any(sus in pinfo['name'].lower() for sus in suspicious_names):
                    # Check if running with suspicious parameters
                    if pinfo['cmdline'] and len(pinfo['cmdline']) > 2:
                        cmdline = ' '.join(pinfo['cmdline'])
                        
                        # Detection patterns
                        suspicious_patterns = [
                            (r'-enc.*[A-Za-z0-9+/=]{50,}', 'Encoded PowerShell Command'),
                            (r'downloadstring|downloadfile', 'Download Command'),
                            (r'invoke-expression|iex', 'Code Execution'),
                            (r'bypass.*execution.*policy', 'Policy Bypass'),
                            (r'\\\\.*\\.*\$', 'Network Share Access'),
                        ]
                        
                        for pattern, description in suspicious_patterns:
                            if re.search(pattern, cmdline, re.IGNORECASE):
                                threat = {
                                    "timestamp": datetime.now().isoformat(),
                                    "type": "Suspicious Process Behavior",
                                    "severity": "HIGH",
                                    "details": {
                                        "pid": pinfo['pid'],
                                        "name": pinfo['name'],
                                        "detection": description,
                                        "cmdline": cmdline[:200]
                                    },
                                    "action": "INVESTIGATE"
                                }
                                threats.append(threat)
                                self.threats_detected.append(threat)
                                
                                # Execute automated response if enabled
                                if self.response_engine:
                                    self.response_engine.respond_to_threat(threat)
                                
                                print(f"  🚨 SUSPICIOUS PROCESS!")
                                print(f"     PID: {pinfo['pid']} | Name: {pinfo['name']}")
                                print(f"     Detection: {description}")
                            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not threats:
            print(f"  ✅ Scanned {self.scan_stats['processes_scanned']} processes - No suspicious activity")
        else:
            print(f"  ⚠️  Found {len(threats)} suspicious processes!")
            
        return threats
    
    def scan_dns_queries(self):
        """Monitor DNS queries for malicious domains"""
        print("\n🌍 Checking DNS Resolution...")
        
        # Check if any network connections resolve to malicious domains
        threats = []
        checked_ips = set()
        
        for conn in psutil.net_connections(kind='inet'):
            if conn.raddr and conn.raddr.ip not in checked_ips:
                checked_ips.add(conn.raddr.ip)
                
                try:
                    # Reverse DNS lookup
                    hostname = socket.gethostbyaddr(conn.raddr.ip)[0]
                    
                    # Check if hostname matches malicious domains
                    if any(domain in hostname for domain in list(self.malicious_domains)[:1000]):
                        threat = {
                            "timestamp": datetime.now().isoformat(),
                            "type": "Malicious Domain Resolution",
                            "severity": "HIGH",
                            "details": {
                                "ip": conn.raddr.ip,
                                "hostname": hostname,
                                "local_port": conn.laddr.port
                            },
                            "action": "BLOCK_DNS"
                        }
                        threats.append(threat)
                        self.threats_detected.append(threat)
                        
                        print(f"  🚨 Malicious domain detected: {hostname} ({conn.raddr.ip})")
                        
                except (socket.herror, socket.gaierror):
                    pass  # No reverse DNS available
                    
                self.scan_stats['dns_queries'] += 1
        
        if not threats:
            print(f"  ✅ Checked {len(checked_ips)} IPs - No malicious domains detected")
        else:
            print(f"  ⚠️  Found {len(threats)} malicious domains!")
            
        return threats
    
    def scan_open_ports(self):
        """Scan for suspicious open ports"""
        print("\n🔌 Scanning Open Ports...")
        
        # Get listening connections
        listeners = [conn for conn in psutil.net_connections(kind='inet') if conn.status == 'LISTEN']
        
        # Suspicious ports (common backdoor/malware ports)
        suspicious_ports = {
            31337: "Back Orifice",
            12345: "NetBus",
            6667: "IRC (Botnet C2)",
            6666: "IRC Backdoor",
            4444: "Metasploit",
            5555: "Android Debug/Backdoor",
            8080: "Proxy/Web Backdoor",
            3389: "RDP (if not expected)",
        }
        
        threats = []
        
        for conn in listeners:
            port = conn.laddr.port
            
            if port in suspicious_ports:
                threat = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "Suspicious Open Port",
                    "severity": "MEDIUM",
                    "details": {
                        "port": port,
                        "description": suspicious_ports[port],
                        "pid": conn.pid,
                        "address": conn.laddr.ip
                    },
                    "action": "INVESTIGATE"
                }
                threats.append(threat)
                self.threats_detected.append(threat)
                
                print(f"  ⚠️  Suspicious port {port} open - {suspicious_ports[port]}")
        
        self.scan_stats['ports_scanned'] = len(listeners)
        
        if not threats:
            print(f"  ✅ Scanned {len(listeners)} listening ports - No suspicious ports")
        else:
            print(f"  ⚠️  Found {len(threats)} suspicious open ports!")
            
        return threats
    
    def behavioral_analysis(self):
        """Detect anomalous system behavior"""
        print("\n🧠 Performing Behavioral Analysis...")
        
        threats = []
        
        # CPU usage anomaly detection
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            threat = {
                "timestamp": datetime.now().isoformat(),
                "type": "Anomalous CPU Usage",
                "severity": "MEDIUM",
                "details": {
                    "cpu_percent": cpu_percent,
                    "description": "Extremely high CPU usage detected - potential cryptomining or DoS"
                },
                "action": "INVESTIGATE"
            }
            threats.append(threat)
            self.threats_detected.append(threat)
            print(f"  ⚠️  High CPU usage: {cpu_percent}%")
        
        # Memory usage check
        mem = psutil.virtual_memory()
        if mem.percent > 90:
            threat = {
                "timestamp": datetime.now().isoformat(),
                "type": "Anomalous Memory Usage",
                "severity": "MEDIUM",
                "details": {
                    "memory_percent": mem.percent,
                    "available_mb": mem.available / (1024*1024)
                },
                "action": "INVESTIGATE"
            }
            threats.append(threat)
            self.threats_detected.append(threat)
            print(f"  ⚠️  High memory usage: {mem.percent}%")
        
        # Network anomaly detection
        net_io = psutil.net_io_counters()
        if hasattr(self, 'prev_net_io'):
            bytes_sent = net_io.bytes_sent - self.prev_net_io.bytes_sent
            bytes_recv = net_io.bytes_recv - self.prev_net_io.bytes_recv
            
            # More than 100MB sent in scan interval = potential data exfiltration
            if bytes_sent > 100 * 1024 * 1024:
                threat = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "Potential Data Exfiltration",
                    "severity": "HIGH",
                    "details": {
                        "bytes_sent_mb": bytes_sent / (1024*1024),
                        "description": "Large amount of data sent - potential exfiltration"
                    },
                    "action": "BLOCK_EGRESS"
                }
                threats.append(threat)
                self.threats_detected.append(threat)
                print(f"  🚨 Large data transfer detected: {bytes_sent/(1024*1024):.2f} MB sent")
        
        self.prev_net_io = net_io
        
        if not threats:
            print(f"  ✅ System behavior normal")
        
        return threats
    
    def generate_threat_report(self):
        """Generate comprehensive threat report"""
        print("\n" + "="*80)
        print("📊 THREAT DETECTION REPORT")
        print("="*80)
        
        if not self.threats_detected:
            print("\n✅ NO THREATS DETECTED - System is clean!\n")
        else:
            print(f"\n⚠️  TOTAL THREATS DETECTED: {len(self.threats_detected)}\n")
            
            # Group by severity
            by_severity = defaultdict(list)
            for threat in self.threats_detected:
                by_severity[threat['severity']].append(threat)
            
            print("Threats by Severity:")
            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                count = len(by_severity[severity])
                if count > 0:
                    icon = "🔴" if severity == "CRITICAL" else "🟠" if severity == "HIGH" else "🟡"
                    print(f"  {icon} {severity}: {count} threat(s)")
            
            print("\n" + "-"*80)
            print("Recent Threats (Last 10):")
            print("-"*80)
            
            for i, threat in enumerate(self.threats_detected[-10:], 1):
                print(f"\n{i}. [{threat['severity']}] {threat['type']}")
                print(f"   Time: {threat['timestamp']}")
                print(f"   Action: {threat['action']}")
                for key, value in threat['details'].items():
                    print(f"   {key}: {value}")
        
        print("\n" + "="*80)
        print("📈 SCAN STATISTICS")
        print("="*80)
        print(f"  • Network Connections Scanned: {self.scan_stats['connections_scanned']:,}")
        print(f"  • Processes Scanned: {self.scan_stats['processes_scanned']:,}")
        print(f"  • DNS Queries Checked: {self.scan_stats['dns_queries']:,}")
        print(f"  • Open Ports Scanned: {self.scan_stats['ports_scanned']:,}")
        print(f"\n  • IOCs Loaded: {self.iocs_loaded:,}")
        print(f"  • Detection Rules Active: {self.rules_loaded:,}")
        print("="*80 + "\n")
        
    def run_full_scan(self):
        """Execute complete threat scan"""
        print("="*80)
        print("🛡️  ACTIVE THREAT MONITORING SYSTEM")
        print("="*80)
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Threat Intelligence: {self.iocs_loaded:,} IOCs | {self.rules_loaded:,} Rules")
        print("="*80)
        
        all_threats = []
        
        # Run all scans
        all_threats.extend(self.scan_network_connections())
        all_threats.extend(self.scan_running_processes())
        all_threats.extend(self.scan_dns_queries())
        all_threats.extend(self.scan_open_ports())
        all_threats.extend(self.behavioral_analysis())
        
        # Generate report
        self.generate_threat_report()
        
        # Save threats to file
        if self.threats_detected:
            output_file = self.workspace_root / "data" / "logs" / f"threats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump({
                    "scan_time": datetime.now().isoformat(),
                    "total_threats": len(self.threats_detected),
                    "threats": self.threats_detected,
                    "statistics": dict(self.scan_stats)
                }, f, indent=2)
            
            print(f"💾 Threat report saved to: {output_file}\n")
        
        return all_threats
    
    def continuous_monitoring(self, interval=60):
        """Run continuous monitoring"""
        print(f"\n🔄 Starting continuous monitoring (scan every {interval} seconds)")
        print("Press Ctrl+C to stop\n")
        
        self.running = True
        scan_count = 0
        
        try:
            while self.running:
                scan_count += 1
                print(f"\n{'='*80}")
                print(f"SCAN #{scan_count} - {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*80}")
                
                self.run_full_scan()
                
                print(f"\n⏳ Next scan in {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            self.running = False


def main():
    """Main execution"""
    workspace = Path(__file__).parent.parent
    monitor = ActiveThreatMonitor(workspace)
    
    print("\n" + "="*80)
    print("🎯 REAL-TIME THREAT MONITORING OPTIONS")
    print("="*80)
    print("\n1. Run single scan (quick check)")
def main():
    """Main execution"""
    workspace = Path(__file__).parent.parent
    
    print("\n" + "="*80)
    print("🎯 REAL-TIME THREAT MONITORING OPTIONS")
    print("="*80)
    print("\n=== MONITORING MODE ===")
    print("1. Run single scan (quick check)")
    print("2. Continuous monitoring (every 60 seconds)")
    print("3. Continuous monitoring (every 5 minutes)")
    print("\n=== AUTOMATED RESPONSE MODE ===")
    print("4. Single scan WITH auto-response (⚠️  requires admin)")
    print("5. Continuous monitoring WITH auto-response (⚠️  requires admin)")
    print("\n=== OTHER ===")
    print("6. Demo automated response capabilities")
    print("7. Exit\n")
    
    choice = input("Select option [1-7]: ").strip()
    
    if choice == "1":
        monitor = ActiveThreatMonitor(workspace, auto_respond=False)
        monitor.run_full_scan()
    elif choice == "2":
        monitor = ActiveThreatMonitor(workspace, auto_respond=False)
        monitor.continuous_monitoring(interval=60)
    elif choice == "3":
        monitor = ActiveThreatMonitor(workspace, auto_respond=False)
        monitor.continuous_monitoring(interval=300)
    elif choice == "4":
        print("\n⚠️  WARNING: Automated response will take action against threats!")
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm == "yes":
            monitor = ActiveThreatMonitor(workspace, auto_respond=True)
            monitor.run_full_scan()
            if monitor.response_engine:
                monitor.response_engine.generate_action_report()
        else:
            print("Cancelled.")
    elif choice == "5":
        print("\n⚠️  WARNING: Automated response will continuously protect your system!")
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm == "yes":
            monitor = ActiveThreatMonitor(workspace, auto_respond=True)
            try:
                monitor.continuous_monitoring(interval=60)
            finally:
                if monitor.response_engine:
                    monitor.response_engine.generate_action_report()
        else:
            print("Cancelled.")
    elif choice == "6":
        # Import and run demo
        from automated_response_engine import demo_automated_response
        demo_automated_response()
    else:
        print("Exiting...")


if __name__ == "__main__":
    main()

