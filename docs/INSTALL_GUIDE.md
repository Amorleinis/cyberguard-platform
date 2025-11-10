# 🚀 MASTER INSTALLATION GUIDE
## Threat Intelligence Platform - Complete Setup Instructions

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Unified Bundle Installation](#unified-bundle-installation)
4. [Individual Engine Installation](#individual-engine-installation)
5. [Verification](#verification)
6. [Quick Start](#quick-start)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- ✅ **Python 3.8 or higher**
- ✅ **pip** (Python package manager)
- ✅ **Git** (optional, for version control)

### Optional
- **Neo4j Database** (for advanced Intelligence Engine features)
- **Docker** (for containerized deployment)

### Check Your Setup

```powershell
# Check Python version
python --version
# Should show: Python 3.8.x or higher

# Check pip
pip --version
# Should show: pip 20.x or higher

# Upgrade pip if needed
python -m pip install --upgrade pip
```

---

## Installation Methods

### 🎯 Which Option Should You Choose?

| Use Case | Recommended Option | Install Script |
|----------|-------------------|----------------|
| **Complete security platform** | Unified Bundle | `install_unified.ps1` |
| **Specific threat lifecycle stages** | Individual Engines | `install_individual.ps1` |
| **CVE analysis only** | Intelligence Engine only | Manual install |
| **Development/Testing** | Unified Bundle | `install_unified.ps1` |
| **Production SOC** | Unified Bundle | `install_unified.ps1` |
| **Integration with existing tools** | Individual Engines | `install_individual.ps1` |

---

## Unified Bundle Installation

### Method 1: Automated Installer (Recommended)

```powershell
# Navigate to platform directory
cd c:\Users\allue\OneDrive\Desktop\datasets

# Run the unified installer
.\install_unified.ps1
```

**What it does:**
1. ✅ Checks dependencies
2. ✅ Installs all required Python packages
3. ✅ Installs all 7 engines + orchestrator
4. ✅ Verifies installation
5. ✅ Shows next steps

### Method 2: Manual Installation

```powershell
# Navigate to platform directory
cd c:\Users\allue\OneDrive\Desktop\datasets

# Install dependencies
pip install -r requirements.txt

# Install the platform
pip install -e .
```

### Method 3: From Wheel Package

```powershell
# Build the package first
python setup.py sdist bdist_wheel

# Install from wheel
pip install dist/threat_intelligence_platform-1.0.0-py3-none-any.whl
```

### Verify Unified Installation

```python
python -c "from orchestration.threat_platform_orchestrator import ThreatIntelligencePlatform; print('✓ Unified platform installed successfully!')"
```

---

## Individual Engine Installation

### Method 1: Interactive Installer (Recommended)

```powershell
# Navigate to platform directory
cd c:\Users\allue\OneDrive\Desktop\datasets

# Run the individual installer
.\install_individual.ps1
```

**You'll see a menu:**
```
1. Intelligence Engine (CVE analysis, IOC extraction)
2. Prevention Engine (IOC blocking, patch management)
3. Detection Engine (ML-based threat detection)
4. Response Engine (Incident management)
5. Isolation Engine (Network segmentation, quarantine)
6. Mitigation Engine (Vulnerability remediation)
7. Recovery Engine (Backup/restore, business continuity)
8. Install ALL engines separately
```

### Method 2: Manual Installation (Single Engine)

```powershell
# Example: Install Intelligence Engine only
cd c:\Users\allue\OneDrive\Desktop\datasets\intelligence
pip install -e .

# Example: Install Prevention Engine only
cd c:\Users\allue\OneDrive\Desktop\datasets\prevention
pip install -e .

# Repeat for other engines as needed
```

### Method 3: Install Multiple Specific Engines

```powershell
# Install Intelligence + Prevention + Detection
cd intelligence && pip install -e . && cd ..
cd prevention && pip install -e . && cd ..
cd detection && pip install -e . && cd ..
```

### Verify Individual Installation

```python
# Test Intelligence Engine
python -c "from intelligence import ThreatIntelligenceEngine; print('✓ Intelligence Engine ready!')"

# Test Prevention Engine
python -c "from prevention import ThreatPreventionEngine; print('✓ Prevention Engine ready!')"

# Test Detection Engine
python -c "from detection import ThreatDetectionEngine; print('✓ Detection Engine ready!')"
```

---

## Verification

### Quick Validation Test

```powershell
# Run the validation script
python validate_engines.py
```

**Expected output:**
```
Test 1: Loading all engines...
✓ Intelligence Engine loaded
✓ Prevention Engine loaded
✓ Detection Engine loaded
✓ Response Engine loaded
✓ Isolation Engine loaded
✓ Mitigation Engine loaded
✓ Recovery Engine loaded
✓ Orchestrator loaded

Engines loaded: 8/8
```

### Run Examples

```powershell
# Test unified bundle
python example_unified_bundle.py

# Test individual engines
python example_individual_engines.py
```

### Run Full Test Suite

```powershell
python tests\run_all_tests.py
```

---

## Quick Start

### Unified Platform

```python
from orchestration.threat_platform_orchestrator import ThreatIntelligencePlatform

# Initialize platform
platform = ThreatIntelligencePlatform(base_dir="./data")

# Process a threat alert
alert = {
    "type": "malware_detection",
    "severity": "HIGH",
    "source": "endpoint",
    "details": {"host": "workstation-123"}
}

result = platform.process_threat_alert(alert)
print(f"Alert processed: {result}")

# Get platform status
status = platform.get_platform_status()
print(f"Active engines: {status['active_engines']}")

# Shutdown
platform.shutdown()
```

### Individual Engines

```python
# Intelligence Engine
from intelligence import ThreatIntelligenceEngine

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
# Prevention Engine
from prevention import ThreatPreventionEngine

prev = ThreatPreventionEngine(db_path="data/prev.db")
result = prev.block_ioc("192.168.1.100", ioc_type="ip", severity="HIGH")
print(f"IOC blocked: {result}")
prev.close()
```

---

## Troubleshooting

### Issue: Import errors

**Symptom:**
```
ImportError: No module named 'threat_intelligence_engine'
```

**Solutions:**
```powershell
# Option 1: Ensure you're in the right directory
cd c:\Users\allue\OneDrive\Desktop\datasets

# Option 2: Add to Python path
$env:PYTHONPATH = "c:\Users\allue\OneDrive\Desktop\datasets"

# Option 3: Reinstall
pip install -e . --force-reinstall
```

### Issue: Missing dependencies

**Symptom:**
```
ModuleNotFoundError: No module named 'pandas'
```

**Solution:**
```powershell
# Install dependencies
pip install -r requirements.txt

# Or install specific packages
pip install pandas numpy requests python-dateutil

# For ML features
pip install scikit-learn torch networkx

# For Neo4j
pip install neo4j
```

### Issue: Permission errors

**Symptom:**
```
PermissionError: [WinError 5] Access is denied
```

**Solution:**
```powershell
# Run PowerShell as Administrator
# Or install in user directory
pip install -e . --user
```

### Issue: Engines not loading

**Symptom:**
```
Engines loaded: 0/8
```

**Solution:**
```powershell
# Check Python version
python --version  # Must be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for syntax errors
python -m py_compile intelligence/threat_intelligence_engine.py
```

### Issue: Neo4j connection errors

**Symptom:**
```
neo4j.exceptions.ServiceUnavailable
```

**Solution:**
```python
# Skip Neo4j for testing
engine = ThreatIntelligenceEngine(
    db_path="intel.db",
    neo4j_uri=None  # Disable Neo4j
)

# Or install and configure Neo4j
# Download from: https://neo4j.com/download/
```

### Issue: Slow installation

**Symptom:**
Installation takes very long or hangs

**Solution:**
```powershell
# Use faster mirror
pip install -r requirements.txt -i https://pypi.org/simple

# Install without dependencies first
pip install -e . --no-deps

# Then install dependencies separately
pip install -r requirements.txt
```

---

## Next Steps

### After Installation

1. **Read Documentation**
   - `PLATFORM_README.md` - Complete overview
   - `QUICKSTART.md` - 5-minute tutorial
   - Individual engine READMEs in each directory

2. **Run Examples**
   ```powershell
   python example_unified_bundle.py
   python example_individual_engines.py
   ```

3. **Load Your Data**
   ```python
   import json
   from intelligence import ThreatIntelligenceEngine
   
   engine = ThreatIntelligenceEngine(db_path="intel.db")
   
   with open('cve_data_2020_2024_merged.json') as f:
       cves = json.load(f)
       for cve in cves[:100]:
           engine.analyze_cve(cve)
   ```

4. **Configure Neo4j** (optional)
   - Install Neo4j Desktop
   - Create database
   - Update connection details in code

5. **Set Up Monitoring**
   ```python
   from orchestration.threat_platform_orchestrator import ThreatIntelligencePlatform
   
   platform = ThreatIntelligencePlatform(base_dir="./data")
   platform.start_monitoring()  # Continuous monitoring
   ```

---

## Support & Resources

### Documentation Files
- `PLATFORM_README.md` - Main platform overview
- `INSTALLATION.md` - Detailed installation guide
- `QUICKSTART.md` - Quick start tutorial
- `QUICK_REFERENCE.md` - Quick reference card
- `TEST_RESULTS.md` - Test results and packaging info
- `architecture.md` - System architecture

### Individual Engine Docs
- `intelligence/README.md` - Intelligence Engine
- `prevention/README.md` - Prevention Engine
- `detection/README.md` - Detection Engine
- `response/README.md` - Response Engine
- `isolation/README.md` - Isolation Engine
- `mitigation/README.md` - Mitigation Engine
- `recovery/README.md` - Recovery Engine

### Test Files
- `validate_engines.py` - Quick validation
- `example_unified_bundle.py` - Unified examples
- `example_individual_engines.py` - Individual examples
- `tests/run_all_tests.py` - Full test suite

---

## Installation Checklist

### Pre-Installation
- [ ] Python 3.8+ installed
- [ ] pip updated
- [ ] Downloaded/cloned platform code

### Unified Bundle
- [ ] Ran `install_unified.ps1` or manual install
- [ ] Dependencies installed
- [ ] Verification test passed
- [ ] Example ran successfully

### Individual Engines
- [ ] Ran `install_individual.ps1` or manual install
- [ ] Selected engines installed
- [ ] Engine-specific tests passed
- [ ] Ready to use

### Post-Installation
- [ ] Read QUICKSTART.md
- [ ] Ran validation tests
- [ ] Configured databases
- [ ] Set up Neo4j (if needed)
- [ ] Ready for production use

---

**✅ Installation Complete!**

You're now ready to use the Threat Intelligence Platform. See `QUICKSTART.md` for next steps.
