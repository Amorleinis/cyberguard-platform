# Quick Start Guide - Threat Intelligence Platform

## 5-Minute Setup

### 1. Install Dependencies

```powershell
cd c:\Users\allue\OneDrive\Desktop\datasets
pip install -r requirements.txt
```

### 2. Quick Test

```powershell
# Run tests to verify everything works
python tests/run_all_tests.py
```

### 3. Use the Platform

#### Option A: Unified Platform (All Engines)

```python
from orchestration.threat_platform_orchestrator import ThreatIntelligencePlatform

# Initialize platform
platform = ThreatIntelligencePlatform(base_dir="./data")

# Process a threat alert
alert = {
    "type": "malware_detection",
    "severity": "HIGH",
    "source": "endpoint",
    "details": {
        "host": "workstation-001",
        "malware": "Trojan.Generic"
    }
}

result = platform.process_threat_alert(alert)
print(f"Alert processed: {result}")

# Get platform status
status = platform.get_platform_status()
print(f"Active engines: {status['active_engines']}")

# Shutdown
platform.shutdown()
```

#### Option B: Individual Engines

```python
# Intelligence Engine
from intelligence.threat_intelligence_engine import ThreatIntelligenceEngine

intel = ThreatIntelligenceEngine(db_path="data/intel.db")
analysis = intel.analyze_cve({
    "CVE_ID": "CVE-2024-1234",
    "severity": "CRITICAL",
    "cvss_score": 9.8
})
print(f"Threat score: {analysis['threat_score']}")
intel.close()
```

```python
# Detection Engine
from detection.threat_detection_engine import ThreatDetectionEngine

detector = ThreatDetectionEngine(db_path="data/detection.db")
event = {
    "timestamp": "2024-01-15T10:30:00",
    "source_ip": "192.168.1.100",
    "event_type": "port_scan"
}
detection = detector.analyze_event(event)
print(f"Threat detected: {detection['is_threat']}")
detector.close()
```

```python
# Response Engine
from response.threat_response_engine import ThreatResponseEngine

responder = ThreatResponseEngine(db_path="data/response.db")
incident = responder.create_incident(
    title="Malware Infection",
    severity="HIGH",
    incident_type="malware",
    affected_assets=["workstation-001"]
)
print(f"Incident created: {incident['incident_id']}")
responder.close()
```

## Common Use Cases

### Use Case 1: Analyze CVE and Block IOCs

```python
from intelligence.threat_intelligence_engine import ThreatIntelligenceEngine
from prevention.threat_prevention_engine import ThreatPreventionEngine

# Analyze CVE
intel = ThreatIntelligenceEngine(db_path="data/intel.db")
cve_analysis = intel.analyze_cve({
    "CVE_ID": "CVE-2024-1234",
    "description": "RCE vulnerability allowing execution via 192.168.1.100",
    "severity": "CRITICAL"
})

# Extract and block IOCs
prevention = ThreatPreventionEngine(db_path="data/prevention.db")
for ip in cve_analysis['iocs'].get('ip_addresses', []):
    prevention.block_ioc(ip, ioc_type="ip", severity="HIGH")
    print(f"Blocked IP: {ip}")

intel.close()
prevention.close()
```

### Use Case 2: Detect, Respond, and Isolate

```python
from detection.threat_detection_engine import ThreatDetectionEngine
from response.threat_response_engine import ThreatResponseEngine
from isolation.threat_isolation_engine import ThreatIsolationEngine

# Detect threat
detector = ThreatDetectionEngine(db_path="data/detection.db")
event = {"source_ip": "10.0.0.50", "event_type": "malware"}
detection = detector.analyze_event(event)

if detection['is_threat']:
    # Create incident
    responder = ThreatResponseEngine(db_path="data/response.db")
    incident = responder.create_incident(
        title="Malware Detected",
        severity="HIGH",
        incident_type="malware"
    )
    
    # Isolate affected host
    isolator = ThreatIsolationEngine(db_path="data/isolation.db")
    isolator.isolate_host("workstation-123", reason="Malware detected")
    
    print(f"Incident {incident['incident_id']}: Host isolated")
    
    responder.close()
    isolator.close()

detector.close()
```

### Use Case 3: Mitigate and Recover

```python
from mitigation.threat_mitigation_engine import ThreatMitigationEngine
from recovery.threat_recovery_engine import ThreatRecoveryEngine

# Remediate vulnerability
mitigator = ThreatMitigationEngine(db_path="data/mitigation.db")
remediation = mitigator.remediate_vulnerability(
    vulnerability_id="CVE-2024-1234",
    affected_hosts=["server-001"],
    remediation_type="patch"
)

# Create recovery plan
recovery = ThreatRecoveryEngine(db_path="data/recovery.db")
plan = recovery.create_recovery_plan(
    plan_name="Post-Patch Recovery",
    recovery_type="service_restoration",
    affected_systems=["server-001"]
)

print(f"Remediation {remediation['remediation_id']} completed")
print(f"Recovery plan {plan['plan_id']} created")

mitigator.close()
recovery.close()
```

## Next Steps

1. **Configure Neo4j** (optional): For advanced threat intelligence features
   - Install Neo4j Desktop
   - Create a new database
   - Update connection details in your code

2. **Load Your Data**:
   ```python
   intel = ThreatIntelligenceEngine(db_path="data/intel.db")
   
   # Load CVE data
   import json
   with open('cve_data_2020_2024_merged.json') as f:
       cves = json.load(f)
       for cve in cves[:100]:  # Process first 100
           intel.analyze_cve(cve)
   ```

3. **Set Up Monitoring**:
   ```python
   from orchestration.threat_platform_orchestrator import ThreatIntelligencePlatform
   
   platform = ThreatIntelligencePlatform(base_dir="./data")
   platform.start_monitoring()  # Runs continuous monitoring
   ```

4. **Review Documentation**:
   - `INSTALLATION.md` - Full installation guide
   - `README.md` - Complete API documentation
   - `architecture.md` - System architecture

## Getting Help

- Run tests: `python tests/run_all_tests.py`
- Check logs: Look in `data/*.db` and console output
- Review examples: See `tests/test_all_engines.py`
