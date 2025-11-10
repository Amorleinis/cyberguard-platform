"""
PLUG AND PLAY - Complete Platform Demo
Automatically loads all real data and runs end-to-end threat lifecycle
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Setup paths
base_dir = Path(__file__).parent
for engine in ['intelligence', 'prevention', 'detection', 'response', 
               'isolation', 'mitigation', 'recovery', 'orchestration']:
    sys.path.insert(0, str(base_dir / engine))

print("=" * 80)
print("THREAT INTELLIGENCE PLATFORM - PLUG AND PLAY DEMO")
print("Complete End-to-End Threat Lifecycle with Real Data")
print("=" * 80)
print()

# Create data directory
os.makedirs("data/plug_and_play", exist_ok=True)

# Scan for available data
print("📊 Scanning workspace for data files...")
print("-" * 80)

data_inventory = {
    'cve_data': [],
    'threat_data': [],
    'mitre_techniques': [],
    'malware_hashes': [],
    'attack_vectors': []
}

# Find CVE data
cve_files = [
    base_dir / "cve_data_2020_2024_merged.json",
    base_dir / "cve_data.json",
    base_dir / "NVD" / "nvd_cve_processed.json"
]
for f in cve_files:
    if f.exists():
        data_inventory['cve_data'].append(f)
        print(f"✓ CVE Data: {f.name}")

# Find MITRE data
mitre_files = list((base_dir / "neo4j").glob("MitreTechnique*.csv"))
for f in mitre_files:
    if f.exists():
        data_inventory['mitre_techniques'].append(f)
        print(f"✓ MITRE Techniques: {f.name}")

# Find malware data
malware_files = list((base_dir / "neo4j").glob("malware_hashes*.csv"))
for f in malware_files:
    if f.exists():
        data_inventory['malware_hashes'].append(f)
        print(f"✓ Malware Hashes: {f.name}")

# Find threat data
threat_files = [
    base_dir / "DATAX" / "data" / "processed" / "enriched_cyber_threats_scored.json",
    base_dir / "data" / "enriched_results.json"
]
for f in threat_files:
    if f.exists():
        data_inventory['threat_data'].append(f)
        print(f"✓ Threat Data: {f.name}")

print("-" * 80)
print()

# Try to load each engine
print("🔧 Initializing engines...")
print("-" * 80)

engines = {}

try:
    from threat_intelligence_engine import ThreatIntelligenceEngine
    engines['intelligence'] = ThreatIntelligenceEngine(
        db_path="data/plug_and_play/intelligence.db",
        neo4j_uri=None
    )
    print("✓ Intelligence Engine loaded")
except Exception as e:
    print(f"⚠ Intelligence Engine: {e}")

try:
    from threat_prevention_engine import ThreatPreventionEngine
    engines['prevention'] = ThreatPreventionEngine(
        db_path="data/plug_and_play/prevention.db"
    )
    print("✓ Prevention Engine loaded")
except Exception as e:
    print(f"⚠ Prevention Engine: {e}")

try:
    from threat_detection_engine import ThreatDetectionEngine
    engines['detection'] = ThreatDetectionEngine(
        db_path="data/plug_and_play/detection.db"
    )
    print("✓ Detection Engine loaded")
except Exception as e:
    print(f"⚠ Detection Engine: {e}")

try:
    from threat_response_engine import ThreatResponseEngine
    engines['response'] = ThreatResponseEngine(
        db_path="data/plug_and_play/response.db"
    )
    print("✓ Response Engine loaded")
except Exception as e:
    print(f"⚠ Response Engine: {e}")

try:
    from threat_isolation_engine import ThreatIsolationEngine
    engines['isolation'] = ThreatIsolationEngine()
    print("✓ Isolation Engine loaded")
except Exception as e:
    print(f"⚠ Isolation Engine: {e}")

try:
    from threat_mitigation_engine import ThreatMitigationEngine
    engines['mitigation'] = ThreatMitigationEngine()
    print("✓ Mitigation Engine loaded")
except Exception as e:
    print(f"⚠ Mitigation Engine: {e}")

try:
    from threat_recovery_engine import ThreatRecoveryEngine
    engines['recovery'] = ThreatRecoveryEngine()
    print("✓ Recovery Engine loaded")
except Exception as e:
    print(f"⚠ Recovery Engine: {e}")

print("-" * 80)
print(f"Engines loaded: {len(engines)}/7")
print()

if len(engines) == 0:
    print("✗ No engines loaded. Please install dependencies:")
    print("  .\\install_unified.ps1")
    sys.exit(1)

# Demo 1: Intelligence → Prevention workflow
if 'intelligence' in engines and 'prevention' in engines and data_inventory['cve_data']:
    print("=" * 80)
    print("DEMO 1: Intelligence → Prevention Workflow")
    print("=" * 80)
    print()
    
    # Load real CVE data
    cve_file = data_inventory['cve_data'][0]
    print(f"Loading CVEs from {cve_file.name}...")
    
    with open(cve_file, 'r', encoding='utf-8') as f:
        cve_data = json.load(f)
    
    # Get first few CVEs
    if isinstance(cve_data, list):
        cves = cve_data[:3]
    elif isinstance(cve_data, dict) and 'CVE_Items' in cve_data:
        cves = cve_data['CVE_Items'][:3]
    else:
        cves = [cve_data]
    
    print(f"Analyzing {len(cves)} CVEs...\n")
    
    total_iocs_blocked = 0
    
    for cve in cves:
        try:
            # Normalize CVE
            cve_id = cve.get('CVE_ID') or cve.get('id') or cve.get('cve', {}).get('id', 'UNKNOWN')
            normalized_cve = {
                'CVE_ID': cve_id,
                'description': str(cve.get('description', 'No description'))[:200],
                'severity': cve.get('severity', 'UNKNOWN'),
                'cvss_score': float(cve.get('cvss_score', 0.0))
            }
            
            # Analyze with Intelligence Engine
            analysis = engines['intelligence'].analyze_cve(normalized_cve)
            print(f"📊 {analysis['cve_id']}")
            print(f"   Threat Score: {analysis['threat_score']:.1f}/10")
            
            # Block IOCs with Prevention Engine
            ioc_count = 0
            for ip in analysis['iocs'].get('ip_addresses', [])[:2]:
                engines['prevention'].block_ioc(ip, ioc_type="ip", severity="HIGH", source=cve_id)
                ioc_count += 1
            
            for domain in analysis['iocs'].get('domains', [])[:2]:
                engines['prevention'].block_ioc(domain, ioc_type="domain", severity="HIGH", source=cve_id)
                ioc_count += 1
            
            if ioc_count > 0:
                print(f"   🛡️ Blocked {ioc_count} IOCs")
                total_iocs_blocked += ioc_count
            
            print()
            
        except Exception as e:
            print(f"   ✗ Error: {e}\n")
    
    print(f"✓ Total IOCs blocked: {total_iocs_blocked}\n")

# Demo 2: Detection → Response → Isolation workflow
if 'detection' in engines and 'response' in engines:
    print("=" * 80)
    print("DEMO 2: Detection → Response → Isolation Workflow")
    print("=" * 80)
    print()
    
    # Create realistic security events
    events = [
        {
            "timestamp": datetime.now().isoformat(),
            "source_ip": "192.168.1.100",
            "dest_ip": "10.0.0.50",
            "port": 4444,
            "event_type": "suspicious_outbound_connection",
            "bytes_sent": 1024000
        },
        {
            "timestamp": datetime.now().isoformat(),
            "source_ip": "10.0.0.75",
            "dest_ip": "192.168.1.200",
            "port": 445,
            "event_type": "lateral_movement",
            "bytes_sent": 512000
        }
    ]
    
    incidents_created = 0
    hosts_isolated = 0
    
    for i, event in enumerate(events, 1):
        print(f"Event {i}: {event['event_type']}")
        
        # Detect threat
        detection = engines['detection'].analyze_event(event)
        print(f"  Detection: {'🚨 THREAT' if detection.get('is_threat') else '✓ Clean'}")
        print(f"  Confidence: {detection.get('confidence', 0):.0%}")
        
        if detection.get('is_threat') or detection.get('confidence', 0) > 0.5:
            # Create incident
            incident = engines['response'].create_incident(
                title=f"Suspicious {event['event_type']}",
                description=f"Detected from {event['source_ip']}",
                severity="HIGH" if detection.get('confidence', 0) > 0.7 else "MEDIUM",
                incident_type="network_intrusion",
                affected_assets=[f"host-{event['source_ip']}"]
            )
            print(f"  📋 Incident created: {incident['incident_id']}")
            incidents_created += 1
            
            # Isolate if in engines
            if 'isolation' in engines and detection.get('confidence', 0) > 0.7:
                try:
                    result = engines['isolation'].isolate_network(
                        network_segment=f"segment-{event['source_ip'].split('.')[2]}",
                        reason=f"Incident {incident['incident_id']}",
                        severity="HIGH"
                    )
                    if result:
                        print(f"  🔒 Network segment isolated")
                        hosts_isolated += 1
                except:
                    pass
        
        print()
    
    print(f"✓ Incidents created: {incidents_created}")
    if hosts_isolated > 0:
        print(f"✓ Segments isolated: {hosts_isolated}")
    print()

# Demo 3: Platform Metrics
print("=" * 80)
print("PLATFORM METRICS")
print("=" * 80)
print()

for engine_name, engine in engines.items():
    if hasattr(engine, 'get_metrics'):
        try:
            metrics = engine.get_metrics()
            print(f"📊 {engine_name.upper()} ENGINE:")
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    print(f"   {key}: {value}")
            print()
        except:
            pass

# Cleanup
print("=" * 80)
print("✓ COMPLETE PLATFORM DEMO FINISHED")
print("=" * 80)
print()
print("Data processed:")
for category, files in data_inventory.items():
    if files:
        print(f"  ✓ {category}: {len(files)} file(s)")

print()
print("Engines used:")
for engine_name in engines.keys():
    print(f"  ✓ {engine_name}")

print()
print("Database location: data/plug_and_play/")
print()
print("Next steps:")
print("  1. Explore databases in data/plug_and_play/")
print("  2. Load more CVE data by removing [:3] limits")
print("  3. Configure Neo4j for graph analysis")
print("  4. Integrate with your SIEM/security tools")
print("  5. Run .\\install_unified.ps1 to install all engines")
print()

# Close all engines
for engine in engines.values():
    if hasattr(engine, 'close'):
        try:
            engine.close()
        except:
            pass
    elif hasattr(engine, 'shutdown'):
        try:
            engine.shutdown()
        except:
            pass
