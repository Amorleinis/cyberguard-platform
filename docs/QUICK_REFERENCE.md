# Quick Reference Card - Threat Intelligence Platform

## Installation Options

### Option 1: Install Everything (Unified Bundle)
```powershell
cd c:\Users\allue\OneDrive\Desktop\datasets
pip install -e .
```

### Option 2: Install Individual Engines
```powershell
# Pick the engines you need:
cd intelligence && pip install -e .  # Intelligence Engine
cd prevention && pip install -e .    # Prevention Engine
cd detection && pip install -e .     # Detection Engine
cd response && pip install -e .      # Response Engine
cd isolation && pip install -e .     # Isolation Engine
cd mitigation && pip install -e .    # Mitigation Engine
cd recovery && pip install -e .      # Recovery Engine
```

---

## Quick Start - Unified Platform

```python
from orchestration.threat_platform_orchestrator import ThreatIntelligencePlatform

platform = ThreatIntelligencePlatform(base_dir="./data")

# Process alert through all 7 engines
alert = {"type": "malware", "severity": "HIGH"}
result = platform.process_threat_alert(alert)

platform.shutdown()
```

---

## Quick Start - Individual Engines

```python
# Intelligence - Analyze CVE
from intelligence.threat_intelligence_engine import ThreatIntelligenceEngine
intel = ThreatIntelligenceEngine(db_path="intel.db")
analysis = intel.analyze_cve({"CVE_ID": "CVE-2024-1234"})

# Prevention - Block IOC
from prevention.threat_prevention_engine import ThreatPreventionEngine
prev = ThreatPreventionEngine(db_path="prev.db")
prev.block_ioc("192.168.1.100", ioc_type="ip", severity="HIGH")

# Response - Create Incident
from response.threat_response_engine import ThreatResponseEngine
resp = ThreatResponseEngine(db_path="response.db")
incident = resp.create_incident(title="Breach", severity="CRITICAL")
```

---

## Testing

```powershell
# Quick validation
python validate_engines.py

# Full test suite
python tests/run_all_tests.py

# Examples
python example_unified_bundle.py
python example_individual_engines.py
```

---

## Build Distribution Packages

```powershell
# Build unified bundle
python setup.py sdist bdist_wheel

# Build individual engine (example)
cd intelligence
python setup.py sdist bdist_wheel
```

---

## Package Structure

```
📦 Unified Bundle: threat-intelligence-platform
   ├── Intelligence Engine
   ├── Prevention Engine
   ├── Detection Engine
   ├── Response Engine
   ├── Isolation Engine
   ├── Mitigation Engine
   ├── Recovery Engine
   └── Orchestrator

📦 Individual Packages (7):
   - threat-intelligence-engine
   - threat-prevention-engine
   - threat-detection-engine
   - threat-response-engine
   - threat-isolation-engine
   - threat-mitigation-engine
   - threat-recovery-engine
```

---

## Dependencies

**Core (All Engines):**
- pandas, numpy, requests, python-dateutil

**ML (Detection Engine):**
- scikit-learn, torch, networkx

**Graph DB (Intelligence Engine):**
- neo4j

**Install All:**
```powershell
pip install -r requirements.txt
```

---

## Documentation Files

| File | Purpose |
|------|---------|
| `INSTALLATION.md` | Full installation guide |
| `QUICKSTART.md` | 5-minute quick start |
| `README.md` | Complete API docs |
| `TEST_RESULTS.md` | Test results & packaging summary |
| `PACKAGING_SUMMARY.md` | Package structure details |
| `architecture.md` | System architecture |

---

## Test Files

| File | Purpose |
|------|---------|
| `validate_engines.py` | Quick engine validation |
| `example_unified_bundle.py` | Unified platform example |
| `example_individual_engines.py` | Individual engines example |
| `tests/run_all_tests.py` | Full test suite runner |
| `tests/test_all_engines.py` | Integration tests |

---

## Support

📚 Full docs: See `INSTALLATION.md` and `QUICKSTART.md`
🧪 Examples: Run `python example_*.py`
✅ Tests: Run `python validate_engines.py`
