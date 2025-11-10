# Threat Intelligence Platform - Complete README

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

**Complete threat lifecycle management platform with 7 integrated security engines**

## 🚀 Overview

The Threat Intelligence Platform is a comprehensive security solution that covers the entire threat lifecycle:

```
Intelligence → Prevention → Detection → Response → Isolation → Mitigation → Recovery
```

Each engine can be used **standalone** or as part of the **unified platform**.

## 📦 Installation Options

### Option 1: Unified Bundle (Recommended)

Install the complete platform with all engines:

```powershell
# Run the installer
.\install_unified.ps1

# Or install manually
pip install -e .
```

**Usage:**
```python
from orchestration.threat_platform_orchestrator import ThreatIntelligencePlatform

platform = ThreatIntelligencePlatform(base_dir="./data")
result = platform.process_threat_alert(alert_data)
platform.shutdown()
```

### Option 2: Individual Engines

Install only the engines you need:

```powershell
# Run the interactive installer
.\install_individual.ps1

# Or install manually
cd intelligence && pip install -e .
cd prevention && pip install -e .
# etc...
```

**Usage:**
```python
from intelligence import ThreatIntelligenceEngine
from prevention import ThreatPreventionEngine

intel = ThreatIntelligenceEngine(db_path="intel.db")
prev = ThreatPreventionEngine(db_path="prev.db")
```

## 🛡️ Engines

### 1. Intelligence Engine
- CVE analysis and threat scoring
- IOC extraction (IPs, domains, hashes)
- Threat actor profiling
- Neo4j graph integration

📖 [Intelligence README](intelligence/README.md)

### 2. Prevention Engine
- IOC blocking
- Patch management
- Attack surface monitoring
- Prevention rules

📖 [Prevention README](prevention/README.md)

### 3. Detection Engine
- ML-based anomaly detection
- Signature matching
- Behavioral analysis
- Real-time processing

📖 [Detection README](detection/README.md)

### 4. Response Engine
- Incident management
- Playbook execution
- Evidence collection
- Stakeholder notifications

📖 [Response README](response/README.md)

### 5. Isolation Engine
- Network segmentation
- Host quarantine
- User restrictions
- Container isolation

📖 [Isolation README](isolation/README.md)

### 6. Mitigation Engine
- Vulnerability remediation
- Malware removal
- System hardening
- Credential rotation

📖 [Mitigation README](mitigation/README.md)

### 7. Recovery Engine
- Backup/restore operations
- System rebuilds
- Business continuity
- Lessons learned

📖 [Recovery README](recovery/README.md)

## 🎯 Quick Start

### 1. Install the Platform

```powershell
.\install_unified.ps1
```

### 2. Run a Quick Test

```powershell
python validate_engines.py
```

### 3. Try the Examples

```powershell
# Unified platform example
python example_unified_bundle.py

# Individual engines example
python example_individual_engines.py
```

### 4. Use in Your Code

**Unified Platform:**
```python
from orchestration.threat_platform_orchestrator import ThreatIntelligencePlatform

platform = ThreatIntelligencePlatform(base_dir="./data")

# Process malware detection
alert = {
    "type": "malware_detection",
    "severity": "HIGH",
    "details": {"host": "workstation-123"}
}
result = platform.handle_malware_detection(alert)

# Get platform status
status = platform.get_platform_status()
print(f"Active engines: {status['active_engines']}")

platform.shutdown()
```

**Individual Engines:**
```python
from intelligence import ThreatIntelligenceEngine
from prevention import ThreatPreventionEngine

# Analyze CVE
intel = ThreatIntelligenceEngine(db_path="intel.db")
analysis = intel.analyze_cve({
    "CVE_ID": "CVE-2024-1234",
    "severity": "CRITICAL",
    "cvss_score": 9.8
})

# Block extracted IOCs
prev = ThreatPreventionEngine(db_path="prev.db")
for ip in analysis['iocs']['ip_addresses']:
    prev.block_ioc(ip, ioc_type="ip", severity="HIGH")

intel.close()
prev.close()
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [INSTALLATION.md](INSTALLATION.md) | Complete installation guide |
| [QUICKSTART.md](QUICKSTART.md) | 5-minute quick start |
| [architecture.md](architecture.md) | System architecture |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Quick reference card |
| [TEST_RESULTS.md](TEST_RESULTS.md) | Test results and packaging |

## 🧪 Testing

```powershell
# Quick validation
python validate_engines.py

# Full test suite
python tests\run_all_tests.py

# Run examples
python example_unified_bundle.py
python example_individual_engines.py
```

## 📋 Requirements

### Core Dependencies
- Python 3.8+
- pandas, numpy
- requests
- python-dateutil

### ML Dependencies (for Detection Engine)
- scikit-learn
- torch
- networkx

### Graph Database (for Intelligence Engine)
- neo4j

**Install all dependencies:**
```powershell
pip install -r requirements.txt
```

## 🏗️ Architecture

```
Threat Intelligence Platform
│
├── Intelligence Engine ──┐
├── Prevention Engine ────┤
├── Detection Engine ─────┤
├── Response Engine ──────┼──► Orchestrator ──► Unified Platform
├── Isolation Engine ─────┤
├── Mitigation Engine ────┤
└── Recovery Engine ──────┘
```

**Each engine:**
- ✅ Works standalone
- ✅ Has its own database
- ✅ Can integrate with others
- ✅ Provides full API
- ✅ Includes documentation

## 🔧 Configuration

Create `config.json`:

```json
{
  "neo4j": {
    "uri": "bolt://localhost:7687",
    "user": "neo4j",
    "password": "password"
  },
  "databases": {
    "intelligence": "data/intelligence.db",
    "prevention": "data/prevention.db",
    "detection": "data/detection.db",
    "response": "data/response.db",
    "isolation": "data/isolation.db",
    "mitigation": "data/mitigation.db",
    "recovery": "data/recovery.db"
  }
}
```

## 🚢 Deployment

### Docker
```powershell
docker build -t threat-intelligence-platform .
docker run -d -v ./data:/app/data threat-intelligence-platform
```

### Kubernetes
```powershell
kubectl apply -f k8s-deployment.yaml
```

See [INSTALLATION.md](INSTALLATION.md) for detailed deployment instructions.

## 📦 Building Packages

### Build Individual Engine
```powershell
cd intelligence
python setup.py sdist bdist_wheel
pip install dist/threat-intelligence-engine-1.0.0.tar.gz
```

### Build Unified Bundle
```powershell
python setup.py sdist bdist_wheel
pip install dist/threat_intelligence_platform-1.0.0-py3-none-any.whl
```

## 🤝 Integration Examples

### Intelligence → Prevention
```python
analysis = intel_engine.analyze_cve(cve_data)
for ioc in analysis['iocs']['ip_addresses']:
    prevention_engine.block_ioc(ioc, ioc_type="ip")
```

### Detection → Response → Isolation
```python
detection = detect_engine.analyze_event(event)
if detection['is_threat']:
    incident = response_engine.create_incident(...)
    isolation_engine.isolate_host(affected_host)
```

### Mitigation → Recovery
```python
mitigation_engine.remediate_vulnerability(cve_id, hosts)
recovery_engine.create_recovery_plan(plan_name, affected_systems)
```

## 📊 Metrics & Monitoring

```python
# Get platform-wide metrics
metrics = platform.get_platform_status()

# Get individual engine metrics
intel_metrics = intel_engine.get_metrics()
detect_metrics = detect_engine.get_metrics()
```

## 🆘 Support

- **Documentation**: See docs/ directory
- **Examples**: See example_*.py files
- **Tests**: Run `python validate_engines.py`
- **Issues**: Check TEST_RESULTS.md

## 📄 License

MIT License - See LICENSE file

## 🎯 Use Cases

- **Enterprise Security**: Complete threat management
- **SOC Operations**: Automated threat response
- **Incident Response**: Coordinated response workflows
- **Threat Intelligence**: CVE analysis and IOC extraction
- **Compliance**: Security control implementation

## ⚡ Performance

- Real-time event processing
- Scalable architecture
- Parallel engine execution
- Optimized database queries
- Caching and indexing

## 🔒 Security

- Secure evidence chain of custody
- Encrypted credentials storage
- Audit logging
- Role-based access control (RBAC ready)
- Compliance frameworks (NIST, CIS, PCI-DSS)

---

**Made with ❤️ for the security community**
