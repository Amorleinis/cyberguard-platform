"""
Example: Using Individual Engines
Demonstrates using engines separately without the full platform
"""

import sys
from pathlib import Path
import os

# Add engine directories to path
base_dir = Path(__file__).parent
sys.path.insert(0, str(base_dir / "intelligence"))
sys.path.insert(0, str(base_dir / "prevention"))
sys.path.insert(0, str(base_dir / "detection"))
sys.path.insert(0, str(base_dir / "response"))
sys.path.insert(0, str(base_dir / "isolation"))
sys.path.insert(0, str(base_dir / "mitigation"))
sys.path.insert(0, str(base_dir / "recovery"))

def example_intelligence_engine():
    """Example: Using Intelligence Engine standalone"""
    print("\n" + "=" * 80)
    print("INTELLIGENCE ENGINE - Standalone Example")
    print("=" * 80)
    
    try:
        from threat_intelligence_engine import ThreatIntelligenceEngine
        
        engine = ThreatIntelligenceEngine(
            db_path="./data/individual/intelligence.db",
            neo4j_uri=None  # Skip Neo4j for demo
        )
        
        # Analyze a CVE
        cve_data = {
            "CVE_ID": "CVE-2024-12345",
            "description": "Remote code execution in Example Software",
            "severity": "CRITICAL",
            "cvss_score": 9.8,
            "published_date": "2024-01-15"
        }
        
        analysis = engine.analyze_cve(cve_data)
        print(f"✓ CVE Analyzed: {analysis.get('cve_id', 'Unknown')}")
        print(f"  Threat Score: {analysis.get('threat_score', 'N/A')}")
        print(f"  Severity: {analysis.get('severity', 'Unknown')}")
        
        engine.close()
        
    except Exception as e:
        print(f"⚠ Intelligence Engine (requires: pandas, neo4j): {e}")

def example_prevention_engine():
    """Example: Using Prevention Engine standalone"""
    print("\n" + "=" * 80)
    print("PREVENTION ENGINE - Standalone Example")
    print("=" * 80)
    
    try:
        from threat_prevention_engine import ThreatPreventionEngine
        
        engine = ThreatPreventionEngine(db_path="./data/individual/prevention.db")
        
        # Block a malicious IP
        result = engine.block_ioc(
            ioc_value="192.168.1.100",
            ioc_type="ip",
            source="threat_intel",
            severity="HIGH"
        )
        
        print(f"✓ IOC Blocked: {result}")
        print(f"  Type: IP Address")
        print(f"  Value: 192.168.1.100")
        
        engine.close()
        
    except Exception as e:
        print(f"⚠ Prevention Engine (requires: pandas): {e}")

def example_detection_engine():
    """Example: Using Detection Engine standalone"""
    print("\n" + "=" * 80)
    print("DETECTION ENGINE - Standalone Example")
    print("=" * 80)
    
    try:
        from threat_detection_engine import ThreatDetectionEngine
        
        engine = ThreatDetectionEngine(db_path="./data/individual/detection.db")
        
        # Detect an event
        event = {
            "timestamp": "2024-01-15T10:30:00",
            "source_ip": "10.0.0.50",
            "dest_ip": "192.168.1.100",
            "port": 4444,
            "event_type": "suspicious_connection"
        }
        
        detection = engine.analyze_event(event)
        print(f"✓ Event Analyzed")
        print(f"  Is Threat: {detection.get('is_threat', False)}")
        print(f"  Confidence: {detection.get('confidence', 0):.2f}")
        
        engine.close()
        
    except Exception as e:
        print(f"⚠ Detection Engine (requires: pandas, numpy, sklearn, torch): {e}")

def example_response_engine():
    """Example: Using Response Engine standalone"""
    print("\n" + "=" * 80)
    print("RESPONSE ENGINE - Standalone Example")
    print("=" * 80)
    
    try:
        from threat_response_engine import ThreatResponseEngine
        
        engine = ThreatResponseEngine(db_path="./data/individual/response.db")
        
        # Create an incident
        incident = engine.create_incident(
            title="Suspicious Network Activity",
            description="Detected unusual outbound connection",
            severity="MEDIUM",
            incident_type="network_intrusion",
            affected_assets=["workstation-123"]
        )
        
        print(f"✓ Incident Created: {incident.get('incident_id', 'Unknown')}")
        print(f"  Title: {incident.get('title', 'Unknown')}")
        print(f"  Severity: {incident.get('severity', 'Unknown')}")
        
        engine.close()
        
    except Exception as e:
        print(f"⚠ Response Engine (requires: requests): {e}")

def example_isolation_engine():
    """Example: Using Isolation Engine standalone"""
    print("\n" + "=" * 80)
    print("ISOLATION ENGINE - Standalone Example")
    print("=" * 80)
    
    try:
        from threat_isolation_engine import ThreatIsolationEngine
        
        engine = ThreatIsolationEngine()
        
        # Isolate a host
        result = engine.isolate_host(
            hostname="workstation-456",
            reason="Malware detected",
            severity="HIGH",
            duration_hours=24
        )
        
        print(f"✓ Host Isolated: {result}")
        print(f"  Hostname: workstation-456")
        print(f"  Duration: 24 hours")
        
        engine.close()
        
    except Exception as e:
        print(f"⚠ Isolation Engine: {e}")

def example_mitigation_engine():
    """Example: Using Mitigation Engine standalone"""
    print("\n" + "=" * 80)
    print("MITIGATION ENGINE - Standalone Example")
    print("=" * 80)
    
    try:
        from threat_mitigation_engine import ThreatMitigationEngine
        
        engine = ThreatMitigationEngine()
        
        # Remediate a vulnerability
        result = engine.remediate_vulnerability(
            vulnerability_id="CVE-2024-12345",
            affected_hosts=["server-001", "server-002"],
            remediation_type="patch",
            priority="HIGH"
        )
        
        print(f"✓ Vulnerability Remediated")
        print(f"  CVE: CVE-2024-12345")
        print(f"  Affected Hosts: 2")
        
        engine.close()
        
    except Exception as e:
        print(f"⚠ Mitigation Engine: {e}")

def example_recovery_engine():
    """Example: Using Recovery Engine standalone"""
    print("\n" + "=" * 80)
    print("RECOVERY ENGINE - Standalone Example")
    print("=" * 80)
    
    try:
        from threat_recovery_engine import ThreatRecoveryEngine
        
        engine = ThreatRecoveryEngine()
        
        # Create recovery plan
        plan = engine.create_recovery_plan(
            plan_name="Post-Incident Recovery",
            description="Recovery after malware incident",
            recovery_type="service_restoration",
            affected_systems=["web-server-01"]
        )
        
        print(f"✓ Recovery Plan Created")
        print(f"  Plan Name: Post-Incident Recovery")
        print(f"  Type: Service Restoration")
        
        engine.close()
        
    except Exception as e:
        print(f"⚠ Recovery Engine: {e}")

def main():
    print("=" * 80)
    print("INDIVIDUAL ENGINES EXAMPLES")
    print("=" * 80)
    print("\nDemonstrating each engine working independently...")
    
    # Create data directory
    os.makedirs("./data/individual", exist_ok=True)
    
    # Run each example
    example_intelligence_engine()
    example_prevention_engine()
    example_detection_engine()
    example_response_engine()
    example_isolation_engine()
    example_mitigation_engine()
    example_recovery_engine()
    
    print("\n" + "=" * 80)
    print("INDIVIDUAL ENGINES BENEFITS:")
    print("- Install only what you need")
    print("- Smaller dependencies")
    print("- Easier to integrate into existing systems")
    print("- Fine-grained control")
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
