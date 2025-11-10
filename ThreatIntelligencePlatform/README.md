# Threat Intelligence Platform

A comprehensive, modular threat intelligence and security operations platform that covers the complete threat lifecycle from intelligence gathering to recovery.

## 🎯 Overview

This platform provides **7 integrated threat management engines** that work together to provide end-to-end threat handling capabilities:

1. **Threat Intelligence Engine** - CVE analysis, threat actor profiling, IOC extraction
2. **Threat Prevention Engine** - IOC blocking, vulnerability patching, attack surface monitoring
3. **Threat Detection Engine** - Multi-method detection (ML, signatures, behavioral, graph analysis)
4. **Threat Response Engine** - Incident management, playbook execution, evidence collection
5. **Threat Isolation Engine** - Network segmentation, system quarantine, access control
6. **Threat Mitigation Engine** - Vulnerability remediation, malware removal, system hardening
7. **Threat Recovery Engine** - System restoration, data recovery, lessons learned

## 📁 Project Structure

```
ThreatIntelligencePlatform/
├── architecture.md                    # System architecture documentation
├── src/
│   ├── intelligence/
│   │   └── threat_intelligence_engine.py    # CVE analysis, threat intel
│   ├── prevention/
│   │   └── threat_prevention_engine.py      # IOC blocking, prevention
│   ├── detection/
│   │   └── threat_detection_engine.py       # Multi-method detection
│   ├── response/
│   │   └── threat_response_engine.py        # Incident response
│   ├── isolation/
│   │   └── threat_isolation_engine.py       # Network/host isolation
│   ├── mitigation/
│   │   └── threat_mitigation_engine.py      # Remediation workflows
│   ├── recovery/
│   │   └── threat_recovery_engine.py        # System recovery
│   └── orchestration/
│       └── threat_platform_orchestrator.py  # Main orchestrator
├── data/                              # Data storage (auto-created)
│   ├── threat_intelligence.db
│   ├── threat_prevention.db
│   ├── threat_detection.db
│   ├── threat_response.db
│   ├── threat_isolation.db
│   ├── threat_mitigation.db
│   └── threat_recovery.db
└── README.md                          # This file
```

## 🚀 Features

### Intelligence Engine
- CVE vulnerability analysis from NVD data
- Threat actor profiling and tracking
- Attack campaign correlation
- IOC (Indicators of Compromise) extraction
- MITRE ATT&CK mapping
- Threat scoring and prioritization

### Prevention Engine
- Automated IOC blocking (IP, domain, hash, URL)
- Vulnerability patch management
- Attack surface monitoring
- Configuration compliance checking
- Threat hunting capabilities
- Prevention rule management

### Detection Engine
- Machine learning-based anomaly detection
- Signature-based threat detection
- Behavioral analysis
- Graph-based attack pattern detection
- Network traffic analysis
- Real-time event correlation

### Response Engine
- Automated incident creation and tracking
- Response playbook execution
- Digital evidence collection and chain of custody
- Stakeholder notification and communication
- SLA monitoring and escalation
- Incident timeline tracking

### Isolation Engine
- Network segmentation and VLAN isolation
- Host-based quarantine
- User account isolation
- Container and VM isolation
- Quarantine zone management
- Automated rollback capabilities

### Mitigation Engine
- Vulnerability remediation workflows
- Malware removal and cleanup
- System hardening (CIS benchmarks)
- Credential rotation
- Damage assessment
- Patch deployment automation

### Recovery Engine
- Backup and snapshot management
- System restoration workflows
- Data recovery operations
- Business continuity execution
- Lessons learned documentation
- Recovery metrics (RTO/RPO tracking)

## 📊 Data Sources

The platform integrates with multiple data sources:

- **CVE Data**: `cve_data_*.json` - Vulnerability intelligence from NVD
- **Neo4j**: Threat actor relationships and attack patterns
- **Enhanced Scenarios**: Blue team scenario data
- **DATAX Models**: Hybrid neuro-symbolic threat models

## 🔧 Usage

### Basic Platform Initialization

```python
from src.orchestration.threat_platform_orchestrator import ThreatIntelligencePlatform

# Initialize the platform
platform = ThreatIntelligencePlatform(data_dir="./")

# Get platform status
status = platform.get_platform_status()
print(status)
```

### Processing a Threat Alert

```python
# Create a threat alert
alert = {
    'alert_id': 'ALT_001',
    'title': 'Malware Detection',
    'description': 'Suspicious file detected',
    'severity': 'High',
    'confidence': 0.9,
    'affected_assets': ['workstation_001'],
    'indicators': ['192.168.1.100', 'malware.exe'],
    'mitre_tactics': ['Initial Access'],
    'mitre_techniques': ['T1566.001']
}

# Process through full threat lifecycle
result = platform.process_threat_alert(alert)

# Result includes:
# - Incident ID
# - Isolation actions
# - IOC blocking
# - Evidence collection
# - Response playbook execution
```

### Handling a Malware Incident

```python
# Complete malware response workflow
result = platform.handle_malware_detection(
    malware_hash="abc123def456",
    affected_systems=["workstation_001", "workstation_002"],
    malware_name="TrickBot"
)

# Automatically performs:
# 1. Creates incident
# 2. Isolates infected systems
# 3. Removes malware
# 4. Creates recovery points
```

### Responding to a Data Breach

```python
# Data breach response workflow
result = platform.respond_to_data_breach(
    affected_systems=["server_001"],
    compromised_accounts=["user001", "admin001"],
    data_accessed=["customer_database", "financial_records"]
)

# Automatically performs:
# 1. Creates critical incident
# 2. Isolates affected systems
# 3. Rotates compromised credentials
# 4. Assesses damage
# 5. Collects forensic evidence
```

### Vulnerability Patching

```python
# Patch vulnerability workflow
result = platform.patch_vulnerability(
    cve_id="CVE-2021-44228",
    affected_systems=["server_001", "server_002", "server_003"]
)

# Automatically performs:
# 1. Analyzes vulnerability
# 2. Creates prevention rules
# 3. Deploys patches
# 4. Validates remediation
```

### Platform Metrics and Reporting

```python
# Get comprehensive metrics
metrics = platform.get_platform_metrics(time_period_days=30)

# Metrics include:
# - Incidents handled
# - Threats prevented
# - Threats detected
# - Systems isolated
# - Threats mitigated
# - Systems recovered

# Generate platform report
report_path = platform.generate_platform_report(time_period_days=30)
```

## 🎨 Individual Engine Usage

Each engine can also be used independently:

### Intelligence Engine

```python
from src.intelligence.threat_intelligence_engine import ThreatIntelligenceEngine

intel = ThreatIntelligenceEngine(
    data_dir="./",
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)

# Analyze CVE
analysis = intel.get_cve_details("CVE-2021-44228")

# Profile threat actor
actor_profile = intel.get_threat_actor_profile("APT28")

# Extract IOCs
iocs = intel.extract_iocs_from_text("Sample threat report...")
```

### Detection Engine

```python
from src.detection.threat_detection_engine import ThreatDetectionEngine

detector = ThreatDetectionEngine(data_dir="./")

# Detect threats in network event
event = {
    'timestamp': '2025-11-09T12:00:00',
    'source_ip': '192.168.1.100',
    'destination_ip': '10.0.0.50',
    'port': 443,
    'protocol': 'tcp',
    'bytes': 1500
}

detections = detector.detect_threats([event])
```

### Response Engine

```python
from src.response.threat_response_engine import ThreatResponseEngine

responder = ThreatResponseEngine(data_dir="./")

# Create incident
incident_id = responder.create_incident_from_alert(alert_data)

# Execute playbook
success = responder.execute_response_playbook(incident_id)

# Collect evidence
evidence_id = responder.collect_evidence(
    incident_id=incident_id,
    evidence_type='logs',
    source_system='server_001'
)
```

### Isolation Engine

```python
from src.isolation.threat_isolation_engine import ThreatIsolationEngine

isolator = ThreatIsolationEngine(data_dir="./")

# Isolate compromised host
action_id = isolator.isolate_host(
    target="192.168.1.100",
    isolation_method="auto",
    incident_id=incident_id,
    duration_hours=2
)

# Move to quarantine
quarantine_id = isolator.move_to_quarantine(
    target="192.168.1.101",
    quarantine_zone="QUAR_DEFAULT"
)
```

### Mitigation Engine

```python
from src.mitigation.threat_mitigation_engine import ThreatMitigationEngine

mitigator = ThreatMitigationEngine(data_dir="./")

# Remove malware
remediation_id = mitigator.remove_malware(
    malware_hash="abc123def456",
    affected_systems=["workstation_001"],
    malware_name="TrickBot"
)

# Harden system
hardening_id = mitigator.harden_system(
    target_system="server_001",
    hardening_profile="server",
    compliance_framework="cis"
)
```

### Recovery Engine

```python
from src.recovery.threat_recovery_engine import ThreatRecoveryEngine

recovery = ThreatRecoveryEngine(data_dir="./")

# Create recovery point (backup)
rp_id = recovery.create_recovery_point(
    source_system="server_001",
    backup_type="full"
)

# Restore from backup
task_id = recovery.restore_from_backup(
    target_system="server_001",
    recovery_point_id=rp_id,
    incident_id=incident_id
)

# Document lessons learned
lessons_id = recovery.document_lessons_learned(
    incident_id=incident_id,
    incident_summary="Ransomware attack",
    timeline=[...],
    what_worked=["Quick detection", "Effective isolation"],
    what_needs_improvement=["Faster restoration"],
    root_causes=["Unpatched vulnerability"],
    recommendations=[...]
)
```

## 🔐 Security Features

- **Evidence Chain of Custody**: Cryptographic tracking of forensic evidence
- **Audit Logging**: All actions logged with timestamps and user attribution
- **Rollback Capabilities**: Automated rollback for failed operations
- **Encrypted Backups**: All recovery points encrypted by default
- **RBAC Ready**: Role-based access control integration points
- **Compliance**: CIS, NIST, PCI-DSS framework support

## 📈 Metrics and KPIs

The platform tracks comprehensive metrics:

- **Prevention Metrics**: IOCs blocked, vulnerabilities patched, attack surface reduction
- **Detection Metrics**: True/false positives, MTTD (Mean Time to Detect)
- **Response Metrics**: SLA compliance, incident resolution time, escalation rate
- **Isolation Metrics**: Isolation success rate, quarantine zone utilization
- **Mitigation Metrics**: Vulnerability remediation rate, patch deployment success
- **Recovery Metrics**: RTO/RPO compliance, recovery success rate, data loss

## 🎯 Use Cases

1. **Automated Threat Response**
   - Real-time threat detection and automatic isolation
   - Playbook-driven incident response
   - Evidence collection for forensics

2. **Vulnerability Management**
   - CVE analysis and prioritization
   - Automated patch deployment
   - Vulnerability remediation tracking

3. **Malware Incident Handling**
   - Malware detection and isolation
   - Automated removal and cleanup
   - System recovery and validation

4. **Data Breach Response**
   - Rapid containment and isolation
   - Credential rotation
   - Damage assessment and forensics

5. **Business Continuity**
   - Automated backup management
   - System restoration workflows
   - RTO/RPO tracking

## 🔄 Integration Points

The platform is designed to integrate with:

- **SIEM**: Splunk, QRadar, ArcSight
- **EDR/XDR**: CrowdStrike, SentinelOne, Microsoft Defender
- **Firewall**: Palo Alto, Fortinet, Cisco
- **Network**: Cisco, Aruba, HP switches
- **Ticketing**: Jira, ServiceNow
- **SOAR**: Phantom, Demisto, Cortex XSOAR
- **Threat Intel**: MISP, ThreatConnect, Anomali

## 📝 Database Schema

Each engine maintains its own SQLite database:

- `threat_intelligence.db` - CVE cache, threat actors, campaigns, IOCs
- `threat_prevention.db` - Blocklists, prevention rules, protected assets
- `threat_detection.db` - Detection rules, alerts, ML models
- `threat_response.db` - Incidents, playbooks, evidence, stakeholders
- `threat_isolation.db` - Isolation actions, rules, quarantine zones
- `threat_mitigation.db` - Vulnerabilities, remediations, patches
- `threat_recovery.db` - Recovery points, tasks, lessons learned

## 🛠️ Configuration

Each engine can be configured via YAML configuration files or programmatically:

```python
# Example configuration
config = {
    'automation_settings': {
        'auto_isolate_critical': True,
        'auto_block_iocs': True,
        'auto_collect_evidence': True
    },
    'notification_settings': {
        'email_enabled': True,
        'webhook_enabled': True
    },
    'sla_times': {
        'critical': 15,  # minutes
        'high': 60,
        'medium': 240,
        'low': 1440
    }
}
```

## 📊 Reporting

Generate comprehensive reports:

- **Platform Status Report**: Overall health and statistics
- **Incident Reports**: Complete incident documentation
- **Metrics Dashboard**: Performance metrics and KPIs
- **Lessons Learned**: Post-incident analysis and recommendations
- **Compliance Reports**: Framework compliance status

## 🚦 Status Codes

All operations return standardized status codes:

- `pending` - Operation queued
- `in_progress` - Currently executing
- `completed` - Successfully finished
- `failed` - Operation failed
- `verified` - Completed and validated
- `rollback_required` - Needs rollback

## 🎓 Best Practices

1. **Regular Testing**: Test response playbooks and recovery procedures
2. **Backup Verification**: Regularly verify backup integrity
3. **Metric Review**: Review platform metrics weekly
4. **Lessons Learned**: Document and review all major incidents
5. **Tuning**: Continuously tune detection rules to reduce false positives
6. **Updates**: Keep threat intelligence feeds updated
7. **Training**: Regular team training on platform capabilities

## 📚 Documentation

- `architecture.md` - Detailed system architecture
- API documentation - Available in each engine module
- Integration guides - See individual engine READMEs
- Playbook templates - In `response/playbooks/`

## 🤝 Contributing

This platform is designed to be modular and extensible. To add new capabilities:

1. Create new detection rules in `detection/`
2. Add response playbooks in `response/`
3. Implement custom integrations in `orchestration/`
4. Extend mitigation workflows in `mitigation/`

## 📄 License

See LICENSE file for details.

## 🔮 Future Enhancements

- Machine learning model training pipeline
- Advanced threat hunting capabilities
- Real-time dashboard and visualization
- Cloud-native deployment (Kubernetes)
- Advanced automation and orchestration
- Threat intelligence sharing (STIX/TAXII)
- Integration with additional security tools

## 📞 Support

For issues, questions, or contributions, please refer to the project documentation and issue tracker.

---

**Built with**: Python 3.8+, SQLite, Neo4j, PyTorch, scikit-learn

**Version**: 1.0.0

**Last Updated**: November 9, 2025
