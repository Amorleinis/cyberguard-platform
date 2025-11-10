# Threat Intelligence Platform - Installation & Deployment Guide

## Table of Contents
1. [Installation Options](#installation-options)
2. [Unified Bundle Installation](#unified-bundle-installation)
3. [Individual Engine Installation](#individual-engine-installation)
4. [Configuration](#configuration)
5. [Testing](#testing)
6. [Deployment](#deployment)

---

## Installation Options

The Threat Intelligence Platform can be installed in two ways:

### Option 1: Unified Bundle (Recommended)
Install all 7 engines together as a complete platform.

### Option 2: Individual Engines
Install only the specific engines you need.

---

## Unified Bundle Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- (Optional) Neo4j database for advanced threat intelligence features

### Step 1: Install from Source

```powershell
# Navigate to the platform directory
cd c:\Users\allue\OneDrive\Desktop\datasets

# Install in development mode
pip install -e .

# Or install with all dependencies
pip install -e ".[dev,docs]"
```

### Step 2: Install from Package

```powershell
# Build the package
python setup.py sdist bdist_wheel

# Install the built package
pip install dist/threat-intelligence-platform-1.0.0.tar.gz
```

### Step 3: Verify Installation

```python
# Test imports
from threat_intelligence_platform import (
    ThreatIntelligenceEngine,
    ThreatPreventionEngine,
    ThreatDetectionEngine,
    ThreatResponseEngine,
    ThreatIsolationEngine,
    ThreatMitigationEngine,
    ThreatRecoveryEngine,
    ThreatIntelligencePlatform
)

print("All engines imported successfully!")
```

---

## Individual Engine Installation

### Intelligence Engine Only

```powershell
cd intelligence
pip install -e .
```

**Usage:**
```python
from intelligence import ThreatIntelligenceEngine

engine = ThreatIntelligenceEngine(db_path="intel.db")
analysis = engine.analyze_cve({
    "CVE_ID": "CVE-2024-1234",
    "severity": "HIGH",
    "cvss_score": 8.5
})
```

### Prevention Engine Only

```powershell
cd prevention
pip install -e .
```

**Usage:**
```python
from prevention import ThreatPreventionEngine

engine = ThreatPreventionEngine(db_path="prevention.db")
engine.block_ioc("192.168.1.100", ioc_type="ip", severity="HIGH")
```

### Detection Engine Only

```powershell
cd detection
pip install -e .
```

**Usage:**
```python
from detection import ThreatDetectionEngine

engine = ThreatDetectionEngine(db_path="detection.db")
result = engine.detect_anomaly(event_data)
```

### Response Engine Only

```powershell
cd response
pip install -e .
```

**Usage:**
```python
from response import ThreatResponseEngine

engine = ThreatResponseEngine(db_path="response.db")
incident = engine.create_incident(
    title="Security Breach",
    severity="CRITICAL",
    incident_type="data_breach"
)
```

### Isolation Engine Only

```powershell
cd isolation
pip install -e .
```

**Usage:**
```python
from isolation import ThreatIsolationEngine

engine = ThreatIsolationEngine(db_path="isolation.db")
engine.isolate_host("workstation-123", reason="Malware detected")
```

### Mitigation Engine Only

```powershell
cd mitigation
pip install -e .
```

**Usage:**
```python
from mitigation import ThreatMitigationEngine

engine = ThreatMitigationEngine(db_path="mitigation.db")
engine.remediate_vulnerability("CVE-2024-1234", affected_hosts=["server-01"])
```

### Recovery Engine Only

```powershell
cd recovery
pip install -e .
```

**Usage:**
```python
from recovery import ThreatRecoveryEngine

engine = ThreatRecoveryEngine(db_path="recovery.db")
plan = engine.create_recovery_plan(
    plan_name="Disaster Recovery",
    recovery_type="full_restore"
)
```

---

## Configuration

### Environment Setup

Create a configuration file `config.json`:

```json
{
  "neo4j": {
    "uri": "bolt://localhost:7687",
    "user": "neo4j",
    "password": "your_password"
  },
  "databases": {
    "intelligence": "data/intelligence.db",
    "prevention": "data/prevention.db",
    "detection": "data/detection.db",
    "response": "data/response.db",
    "isolation": "data/isolation.db",
    "mitigation": "data/mitigation.db",
    "recovery": "data/recovery.db"
  },
  "logging": {
    "level": "INFO",
    "file": "logs/platform.log"
  },
  "alerts": {
    "email": "security@example.com",
    "slack_webhook": "https://hooks.slack.com/..."
  }
}
```

### Using Configuration in Code

```python
import json
from orchestration import ThreatIntelligencePlatform

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

# Initialize platform with config
platform = ThreatIntelligencePlatform(
    base_dir="./data",
    neo4j_uri=config['neo4j']['uri'],
    neo4j_user=config['neo4j']['user'],
    neo4j_password=config['neo4j']['password']
)
```

---

## Testing

### Run All Tests

```powershell
# Using the test runner
python tests/run_all_tests.py

# Or using pytest (if installed)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Run Specific Test Suites

```powershell
# Test intelligence engine only
python -m unittest tests.test_intelligence_engine

# Test all engines integration
python -m unittest tests.test_all_engines
```

### Quick Smoke Test

```python
# quick_test.py
from orchestration import ThreatIntelligencePlatform

platform = ThreatIntelligencePlatform(base_dir="./test_data")

# Test threat alert processing
alert = {
    "type": "suspicious_activity",
    "severity": "MEDIUM",
    "source": "ids",
    "details": {"ip": "192.168.1.100"}
}

result = platform.process_threat_alert(alert)
print(f"Alert processed: {result}")

# Get platform status
status = platform.get_platform_status()
print(f"Platform status: {status}")

platform.shutdown()
```

---

## Deployment

### Development Environment

```powershell
# Install with development dependencies
pip install -e ".[dev]"

# Run in development mode
python -c "from orchestration import ThreatIntelligencePlatform; p = ThreatIntelligencePlatform('./dev_data'); p.start_monitoring()"
```

### Production Environment

#### 1. System Service (Windows)

Create `threat-platform-service.ps1`:

```powershell
# threat-platform-service.ps1
$pythonPath = "C:\Python38\python.exe"
$scriptPath = "C:\ThreatPlatform\run_platform.py"

while ($true) {
    & $pythonPath $scriptPath
    Start-Sleep -Seconds 5
}
```

#### 2. Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install -e .

CMD ["python", "-m", "orchestration.threat_platform_orchestrator"]
```

Build and run:

```powershell
docker build -t threat-intelligence-platform .
docker run -d -p 8080:8080 -v ./data:/app/data threat-intelligence-platform
```

#### 3. Kubernetes Deployment

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: threat-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: threat-platform
  template:
    metadata:
      labels:
        app: threat-platform
    spec:
      containers:
      - name: platform
        image: threat-intelligence-platform:1.0.0
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: threat-platform-data
```

---

## Package Distribution

### Build Individual Packages

```powershell
# Build intelligence engine package
cd intelligence
python setup.py sdist bdist_wheel

# Build prevention engine package
cd ../prevention
python setup.py sdist bdist_wheel

# Repeat for all engines...
```

### Build Unified Bundle

```powershell
# Build complete platform
cd c:\Users\allue\OneDrive\Desktop\datasets
python setup.py sdist bdist_wheel

# Package will be in dist/
# threat-intelligence-platform-1.0.0.tar.gz
# threat_intelligence_platform-1.0.0-py3-none-any.whl
```

### Install from Built Package

```powershell
# Install wheel package
pip install threat_intelligence_platform-1.0.0-py3-none-any.whl

# Or install tar.gz
pip install threat-intelligence-platform-1.0.0.tar.gz
```

---

## Troubleshooting

### Import Errors

If you encounter import errors:

```powershell
# Ensure Python can find the modules
$env:PYTHONPATH = "C:\Users\allue\OneDrive\Desktop\datasets"

# Or add to path permanently in code
import sys
sys.path.insert(0, r'C:\Users\allue\OneDrive\Desktop\datasets')
```

### Database Permissions

```powershell
# Ensure data directory exists and is writable
New-Item -ItemType Directory -Force -Path ".\data"
```

### Neo4j Connection Issues

```python
# Test Neo4j connection
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password")
)

with driver.session() as session:
    result = session.run("RETURN 1 as test")
    print(result.single()['test'])

driver.close()
```

---

## Support & Documentation

- Full API documentation: See `README.md`
- Architecture guide: See `architecture.md`
- Test examples: See `tests/` directory
- Issue tracking: GitHub Issues
- Security advisories: security@example.com

---

## License

MIT License - See LICENSE file for details
