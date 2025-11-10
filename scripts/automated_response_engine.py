"""
Automated Threat Response Engine
Automatically responds to detected threats with blocking, termination, and isolation
"""

import json
import psutil
import subprocess
import platform
import os
import ctypes
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class AutomatedResponseEngine:
    """Executes automated responses to detected threats"""
    
    def __init__(self, workspace_root, auto_mode=False):
        self.workspace_root = Path(workspace_root)
        self.auto_mode = auto_mode  # If True, automatically execute responses
        self.actions_taken = []
        self.system = platform.system()
        self.is_admin = self.check_admin_privileges()
        
        # Load response playbooks
        self.load_playbooks()
        
    def check_admin_privileges(self):
        """Check if running with admin/root privileges"""
        try:
            if self.system == "Windows":
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except:
            return False
    
    def load_playbooks(self):
        """Load incident response playbooks"""
        playbook_file = self.workspace_root / "response" / "incident_playbooks.json"
        
        with open(playbook_file, 'r') as f:
            data = json.load(f)
        
        self.playbooks = {pb['id']: pb for pb in data['playbooks']}
        
    def block_ip_address(self, ip_address, reason="Malicious IP detected"):
        """Block an IP address using Windows Firewall"""
        action = {
            "timestamp": datetime.now().isoformat(),
            "action": "BLOCK_IP",
            "target": ip_address,
            "reason": reason,
            "status": "pending"
        }
        
        if not self.is_admin:
            action["status"] = "failed"
            action["error"] = "Administrator privileges required"
            print(f"  ⚠️  Cannot block IP {ip_address}: Admin privileges required")
            self.actions_taken.append(action)
            return False
        
        try:
            if self.system == "Windows":
                rule_name = f"CyberGuard_Block_{ip_address.replace('.', '_')}"
                
                # Create firewall rule to block IP
                cmd = [
                    "netsh", "advfirewall", "firewall", "add", "rule",
                    f"name={rule_name}",
                    "dir=out",
                    "action=block",
                    f"remoteip={ip_address}",
                    "enable=yes"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    action["status"] = "success"
                    action["rule_name"] = rule_name
                    print(f"  ✅ Blocked IP: {ip_address}")
                    print(f"     Firewall rule: {rule_name}")
                else:
                    action["status"] = "failed"
                    action["error"] = result.stderr
                    print(f"  ❌ Failed to block IP: {result.stderr}")
                    
            elif self.system == "Linux":
                # Use iptables
                cmd = ["iptables", "-A", "OUTPUT", "-d", ip_address, "-j", "DROP"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    action["status"] = "success"
                    print(f"  ✅ Blocked IP: {ip_address}")
                else:
                    action["status"] = "failed"
                    action["error"] = result.stderr
                    
            self.actions_taken.append(action)
            return action["status"] == "success"
            
        except Exception as e:
            action["status"] = "error"
            action["error"] = str(e)
            print(f"  ❌ Error blocking IP: {e}")
            self.actions_taken.append(action)
            return False
    
    def terminate_process(self, pid, process_name, reason="Malicious process detected"):
        """Terminate a malicious process"""
        action = {
            "timestamp": datetime.now().isoformat(),
            "action": "TERMINATE_PROCESS",
            "target": f"PID {pid} ({process_name})",
            "reason": reason,
            "status": "pending"
        }
        
        try:
            proc = psutil.Process(pid)
            
            # Get process info before termination
            action["process_info"] = {
                "name": proc.name(),
                "exe": proc.exe() if proc.exe() else "N/A",
                "cmdline": ' '.join(proc.cmdline()) if proc.cmdline() else "N/A"
            }
            
            # Terminate the process
            proc.terminate()
            
            # Wait for termination
            try:
                proc.wait(timeout=3)
                action["status"] = "success"
                print(f"  ✅ Terminated process: {process_name} (PID: {pid})")
            except psutil.TimeoutExpired:
                # Force kill if still running
                proc.kill()
                action["status"] = "success"
                action["force_killed"] = True
                print(f"  ✅ Force killed process: {process_name} (PID: {pid})")
                
        except psutil.NoSuchProcess:
            action["status"] = "already_terminated"
            print(f"  ℹ️  Process {pid} already terminated")
        except psutil.AccessDenied:
            action["status"] = "failed"
            action["error"] = "Access denied - requires admin privileges"
            print(f"  ⚠️  Cannot terminate process {pid}: Access denied")
        except Exception as e:
            action["status"] = "error"
            action["error"] = str(e)
            print(f"  ❌ Error terminating process: {e}")
        
        self.actions_taken.append(action)
        return action["status"] in ["success", "already_terminated"]
    
    def isolate_network(self, interface=None):
        """Isolate system from network"""
        action = {
            "timestamp": datetime.now().isoformat(),
            "action": "NETWORK_ISOLATION",
            "target": interface or "all",
            "reason": "Critical threat detected - isolating system",
            "status": "pending"
        }
        
        if not self.is_admin:
            action["status"] = "failed"
            action["error"] = "Administrator privileges required"
            print(f"  ⚠️  Cannot isolate network: Admin privileges required")
            self.actions_taken.append(action)
            return False
        
        try:
            if self.system == "Windows":
                # Disable all network adapters
                cmd = ["netsh", "interface", "set", "interface", "name=*", "admin=disabled"]
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                
                action["status"] = "success"
                print(f"  ✅ Network interfaces disabled - System isolated")
                
            elif self.system == "Linux":
                # Bring down all interfaces except loopback
                interfaces = psutil.net_if_addrs().keys()
                for iface in interfaces:
                    if iface != "lo":
                        cmd = ["ip", "link", "set", iface, "down"]
                        subprocess.run(cmd, capture_output=True)
                
                action["status"] = "success"
                print(f"  ✅ Network interfaces disabled - System isolated")
                
            self.actions_taken.append(action)
            return True
            
        except Exception as e:
            action["status"] = "error"
            action["error"] = str(e)
            print(f"  ❌ Error isolating network: {e}")
            self.actions_taken.append(action)
            return False
    
    def block_domain(self, domain, reason="Malicious domain detected"):
        """Block a domain by adding to hosts file"""
        action = {
            "timestamp": datetime.now().isoformat(),
            "action": "BLOCK_DOMAIN",
            "target": domain,
            "reason": reason,
            "status": "pending"
        }
        
        if not self.is_admin:
            action["status"] = "failed"
            action["error"] = "Administrator privileges required"
            print(f"  ⚠️  Cannot block domain {domain}: Admin privileges required")
            self.actions_taken.append(action)
            return False
        
        try:
            # Get hosts file path
            if self.system == "Windows":
                hosts_file = Path("C:/Windows/System32/drivers/etc/hosts")
            else:
                hosts_file = Path("/etc/hosts")
            
            # Add domain to hosts file (redirect to localhost)
            with open(hosts_file, 'a') as f:
                f.write(f"\n# CyberGuard Auto-block - {datetime.now().isoformat()}\n")
                f.write(f"127.0.0.1 {domain}\n")
                f.write(f"127.0.0.1 www.{domain}\n")
            
            action["status"] = "success"
            print(f"  ✅ Blocked domain: {domain}")
            
        except Exception as e:
            action["status"] = "error"
            action["error"] = str(e)
            print(f"  ❌ Error blocking domain: {e}")
        
        self.actions_taken.append(action)
        return action["status"] == "success"
    
    def quarantine_file(self, file_path, reason="Malicious file detected"):
        """Move suspicious file to quarantine"""
        action = {
            "timestamp": datetime.now().isoformat(),
            "action": "QUARANTINE_FILE",
            "target": str(file_path),
            "reason": reason,
            "status": "pending"
        }
        
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                action["status"] = "not_found"
                print(f"  ℹ️  File not found: {file_path}")
                self.actions_taken.append(action)
                return False
            
            # Create quarantine directory
            quarantine_dir = self.workspace_root / "data" / "quarantine"
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            
            # Move file to quarantine with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            quarantine_path = quarantine_dir / f"{timestamp}_{file_path.name}"
            
            file_path.rename(quarantine_path)
            
            action["status"] = "success"
            action["quarantine_path"] = str(quarantine_path)
            print(f"  ✅ Quarantined file: {file_path.name}")
            print(f"     Location: {quarantine_path}")
            
        except Exception as e:
            action["status"] = "error"
            action["error"] = str(e)
            print(f"  ❌ Error quarantining file: {e}")
        
        self.actions_taken.append(action)
        return action["status"] == "success"
    
    def execute_playbook(self, playbook_id, context={}):
        """Execute an incident response playbook"""
        action = {
            "timestamp": datetime.now().isoformat(),
            "action": "EXECUTE_PLAYBOOK",
            "target": playbook_id,
            "status": "pending"
        }
        
        if playbook_id not in self.playbooks:
            action["status"] = "not_found"
            print(f"  ❌ Playbook {playbook_id} not found")
            self.actions_taken.append(action)
            return False
        
        playbook = self.playbooks[playbook_id]
        
        print(f"\n  📋 Executing Playbook: {playbook['name']}")
        print(f"     Severity: {playbook['severity']}")
        print(f"     Category: {playbook['category']}")
        
        # Log playbook execution
        action["playbook_name"] = playbook['name']
        action["context"] = context
        action["status"] = "executed"
        
        print(f"  ✅ Playbook logged for manual review")
        
        self.actions_taken.append(action)
        return True
    
    def respond_to_threat(self, threat, auto_execute=None):
        """Automatically respond to a detected threat"""
        if auto_execute is None:
            auto_execute = self.auto_mode
        
        print(f"\n🔧 AUTOMATED RESPONSE ACTIVATED")
        print(f"   Threat: {threat['type']}")
        print(f"   Severity: {threat['severity']}")
        print(f"   Recommended Action: {threat['action']}")
        
        if not auto_execute:
            print(f"   ⚠️  Auto-execution disabled - Manual approval required")
            return False
        
        response_success = False
        
        # Execute appropriate response based on action type
        if threat['action'] == 'BLOCK_RECOMMENDED':
            if 'remote_ip' in threat['details']:
                response_success = self.block_ip_address(
                    threat['details']['remote_ip'],
                    reason=f"{threat['type']} detected"
                )
        
        elif threat['action'] == 'TERMINATE_RECOMMENDED':
            if 'pid' in threat['details']:
                response_success = self.terminate_process(
                    threat['details']['pid'],
                    threat['details'].get('name', 'unknown'),
                    reason=f"{threat['type']} detected"
                )
        
        elif threat['action'] == 'BLOCK_DNS':
            if 'hostname' in threat['details']:
                response_success = self.block_domain(
                    threat['details']['hostname'],
                    reason=f"{threat['type']} detected"
                )
        
        elif threat['action'] == 'ISOLATE_SYSTEM':
            response_success = self.isolate_network()
        
        elif threat['action'] == 'QUARANTINE_FILE':
            if 'file_path' in threat['details']:
                response_success = self.quarantine_file(
                    threat['details']['file_path'],
                    reason=f"{threat['type']} detected"
                )
        
        elif threat['action'] == 'INVESTIGATE':
            # Log for manual investigation
            print(f"   ℹ️  Threat logged for investigation")
            response_success = True
        
        # Execute relevant playbook based on threat type
        playbook_mapping = {
            "Malicious Network Connection": "PB-001",  # Ransomware Attack
            "Process Connected to Malicious IP": "PB-001",
            "Suspicious Process Behavior": "PB-002",  # Trojan Detection
            "Potential Data Exfiltration": "PB-003",  # Data Breach Response
        }
        
        if threat['type'] in playbook_mapping:
            self.execute_playbook(
                playbook_mapping[threat['type']],
                context=threat['details']
            )
        
        return response_success
    
    def generate_action_report(self):
        """Generate report of all automated actions taken"""
        print("\n" + "="*80)
        print("🤖 AUTOMATED RESPONSE REPORT")
        print("="*80)
        
        if not self.actions_taken:
            print("\n  No automated actions taken\n")
            return
        
        # Group by action type
        by_action = defaultdict(list)
        for action in self.actions_taken:
            by_action[action['action']].append(action)
        
        print(f"\n  Total Actions: {len(self.actions_taken)}\n")
        
        for action_type, actions in by_action.items():
            successful = sum(1 for a in actions if a['status'] == 'success')
            print(f"  {action_type}: {len(actions)} actions ({successful} successful)")
        
        print("\n" + "-"*80)
        print("Action Details:")
        print("-"*80)
        
        for i, action in enumerate(self.actions_taken, 1):
            status_icon = "✅" if action['status'] == 'success' else "❌" if action['status'] == 'failed' else "⚠️"
            print(f"\n  {i}. {status_icon} {action['action']}")
            print(f"     Target: {action['target']}")
            print(f"     Time: {action['timestamp']}")
            print(f"     Status: {action['status']}")
            if 'error' in action:
                print(f"     Error: {action['error']}")
        
        print("\n" + "="*80 + "\n")
        
        # Save action log
        log_file = self.workspace_root / "data" / "logs" / f"actions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_actions": len(self.actions_taken),
                "actions": self.actions_taken,
                "admin_privileges": self.is_admin
            }, f, indent=2)
        
        print(f"💾 Action log saved to: {log_file}\n")


def demo_automated_response():
    """Demonstrate automated response capabilities"""
    workspace = Path(__file__).parent.parent
    engine = AutomatedResponseEngine(workspace, auto_mode=False)
    
    print("="*80)
    print("🤖 AUTOMATED RESPONSE ENGINE - DEMONSTRATION")
    print("="*80)
    print(f"\nSystem: {engine.system}")
    print(f"Admin Privileges: {'✅ Yes' if engine.is_admin else '❌ No (some actions will be limited)'}")
    print(f"Auto-execution Mode: {'✅ Enabled' if engine.auto_mode else '❌ Disabled (manual approval required)'}")
    
    # Simulate threat scenarios
    print("\n" + "="*80)
    print("SIMULATED THREAT SCENARIOS")
    print("="*80)
    
    # Scenario 1: Malicious IP connection
    print("\n📍 Scenario 1: Malicious IP Connection Detected")
    threat1 = {
        "type": "Malicious Network Connection",
        "severity": "CRITICAL",
        "action": "BLOCK_RECOMMENDED",
        "details": {
            "remote_ip": "192.0.2.100",  # TEST-NET IP (safe to use)
            "remote_port": 4444,
            "status": "ESTABLISHED"
        }
    }
    
    print(f"   Would block IP: {threat1['details']['remote_ip']}")
    print(f"   ⚠️  Auto-execution disabled - Manual approval required")
    
    # Scenario 2: Malicious process
    print("\n📍 Scenario 2: Suspicious Process Detected")
    threat2 = {
        "type": "Suspicious Process Behavior",
        "severity": "HIGH",
        "action": "TERMINATE_RECOMMENDED",
        "details": {
            "pid": 99999,  # Non-existent PID
            "name": "suspicious.exe",
            "detection": "Encoded PowerShell Command"
        }
    }
    
    print(f"   Would terminate process: {threat2['details']['name']} (PID: {threat2['details']['pid']})")
    print(f"   ⚠️  Auto-execution disabled - Manual approval required")
    
    # Scenario 3: Malicious domain
    print("\n📍 Scenario 3: Malicious Domain Resolution")
    threat3 = {
        "type": "Malicious Domain Resolution",
        "severity": "HIGH",
        "action": "BLOCK_DNS",
        "details": {
            "hostname": "evil-test-domain.example.com",
            "ip": "192.0.2.101"
        }
    }
    
    print(f"   Would block domain: {threat3['details']['hostname']}")
    print(f"   ⚠️  Auto-execution disabled - Manual approval required")
    
    print("\n" + "="*80)
    print("CAPABILITIES")
    print("="*80)
    print("\n✅ IP Address Blocking (Windows Firewall / iptables)")
    print("✅ Process Termination (immediate threat stopping)")
    print("✅ Domain Blocking (hosts file modification)")
    print("✅ Network Isolation (full system quarantine)")
    print("✅ File Quarantine (malware containment)")
    print("✅ Playbook Execution (automated incident response)")
    print("✅ Action Logging (audit trail)")
    
    print("\n" + "="*80)
    print("TO ENABLE AUTO-EXECUTION:")
    print("="*80)
    print("\n1. Run Python as Administrator")
    print("2. Set auto_mode=True when initializing engine")
    print("3. System will automatically respond to threats")
    print("\nWARNING: Only enable in controlled environments!")
    print("="*80 + "\n")


if __name__ == "__main__":
    demo_automated_response()
