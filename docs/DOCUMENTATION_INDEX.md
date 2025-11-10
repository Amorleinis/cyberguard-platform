# 📚 Documentation Index - Threat Intelligence Platform

**Quick navigation to all documentation, READMEs, and installation resources**

---

## 🚀 START HERE

### New to the Platform?
1. 📖 Read [PLATFORM_README.md](PLATFORM_README.md) - Complete overview
2. 📋 Read [INSTALL_GUIDE.md](INSTALL_GUIDE.md) - Installation instructions
3. 🔧 Run `install_unified.ps1` - Automated installer
4. ✅ Run `python validate_engines.py` - Verify installation

### Want Individual Engines?
1. 📋 Read [INSTALL_GUIDE.md](INSTALL_GUIDE.md) - See "Individual Engine Installation"
2. 🔧 Run `install_individual.ps1` - Interactive engine selector
3. 📖 Read specific engine READMEs (see below)

---

## 📄 Main Documentation

| File | Description | When to Read |
|------|-------------|--------------|
| [PLATFORM_README.md](PLATFORM_README.md) | Complete platform overview | Start here |
| [INSTALL_GUIDE.md](INSTALL_GUIDE.md) | Master installation guide | Before installing |
| [QUICKSTART.md](QUICKSTART.md) | 5-minute quick start | After installing |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Quick reference card | Daily use |
| [architecture.md](architecture.md) | System architecture | Understanding design |
| [INSTALLATION.md](INSTALLATION.md) | Detailed installation | Advanced setup |
| [TEST_RESULTS.md](TEST_RESULTS.md) | Test results & packaging | Development |
| [PACKAGING_SUMMARY.md](PACKAGING_SUMMARY.md) | Package structure | Building packages |

---

## 🔧 Installation Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `install_unified.ps1` | Install complete platform | `.\install_unified.ps1` |
| `install_individual.ps1` | Install specific engines | `.\install_individual.ps1` |

---

## 📦 Individual Engine Documentation

### Intelligence Engine
- 📖 [intelligence/README.md](intelligence/README.md)
- 🔧 [intelligence/setup.py](intelligence/setup.py)
- **Features:** CVE analysis, IOC extraction, threat actor profiling
- **Install:** `cd intelligence && pip install -e .`

### Prevention Engine
- 📖 [prevention/README.md](prevention/README.md)
- 🔧 [prevention/setup.py](prevention/setup.py)
- **Features:** IOC blocking, patch management, attack surface monitoring
- **Install:** `cd prevention && pip install -e .`

### Detection Engine
- 📖 [detection/README.md](detection/README.md)
- 🔧 [detection/setup.py](detection/setup.py)
- **Features:** ML detection, signature matching, behavioral analysis
- **Install:** `cd detection && pip install -e .`

### Response Engine
- 📖 [response/README.md](response/README.md)
- 🔧 [response/setup.py](response/setup.py)
- **Features:** Incident management, playbook execution, evidence collection
- **Install:** `cd response && pip install -e .`

### Isolation Engine
- 📖 [isolation/README.md](isolation/README.md)
- 🔧 [isolation/setup.py](isolation/setup.py)
- **Features:** Network segmentation, host quarantine, user restrictions
- **Install:** `cd isolation && pip install -e .`

### Mitigation Engine
- 📖 [mitigation/README.md](mitigation/README.md)
- 🔧 [mitigation/setup.py](mitigation/setup.py)
- **Features:** Vulnerability remediation, malware removal, system hardening
- **Install:** `cd mitigation && pip install -e .`

### Recovery Engine
- 📖 [recovery/README.md](recovery/README.md)
- 🔧 [recovery/setup.py](recovery/setup.py)
- **Features:** Backup/restore, business continuity, lessons learned
- **Install:** `cd recovery && pip install -e .`

---

## 🧪 Testing & Examples

| File | Purpose | Usage |
|------|---------|-------|
| `validate_engines.py` | Quick validation test | `python validate_engines.py` |
| `example_unified_bundle.py` | Unified platform example | `python example_unified_bundle.py` |
| `example_individual_engines.py` | Individual engines example | `python example_individual_engines.py` |
| `tests/run_all_tests.py` | Full test suite | `python tests/run_all_tests.py` |
| `tests/test_all_engines.py` | Integration tests | See run_all_tests.py |
| `tests/test_intelligence_engine.py` | Unit tests | See run_all_tests.py |

---

## 🗂️ Configuration Files

| File | Purpose |
|------|---------|
| `setup.py` | Unified bundle installer config |
| `requirements.txt` | Python dependencies |
| `MANIFEST.in` | Package manifest |
| `*/setup.py` | Individual engine installers (7 files) |

---

## 📋 Quick Command Reference

### Installation
```powershell
# Unified bundle
.\install_unified.ps1

# Individual engines
.\install_individual.ps1

# Manual unified
pip install -e .

# Manual individual
cd intelligence && pip install -e .
```

### Testing
```powershell
# Quick validation
python validate_engines.py

# Full tests
python tests\run_all_tests.py

# Examples
python example_unified_bundle.py
python example_individual_engines.py
```

### Building Packages
```powershell
# Build unified bundle
python setup.py sdist bdist_wheel

# Build individual engine
cd intelligence
python setup.py sdist bdist_wheel
```

---

## 🎯 Common Tasks

### I want to...

**Install everything quickly**
→ Run `install_unified.ps1`

**Install only specific engines**
→ Run `install_individual.ps1`

**Understand the platform**
→ Read `PLATFORM_README.md`

**Get started in 5 minutes**
→ Read `QUICKSTART.md`

**Troubleshoot installation**
→ See `INSTALL_GUIDE.md` → Troubleshooting section

**Learn about one specific engine**
→ Read `[engine]/README.md`

**See code examples**
→ Run `example_unified_bundle.py` or `example_individual_engines.py`

**Check if everything works**
→ Run `python validate_engines.py`

**Build distribution packages**
→ See `PACKAGING_SUMMARY.md`

**Deploy to production**
→ See `INSTALLATION.md` → Deployment section

**Integrate with existing tools**
→ Read individual engine READMEs for API details

---

## 📊 Documentation Statistics

- **Total documentation files:** 20+
- **Installation guides:** 2 main guides
- **Installation scripts:** 2 PowerShell scripts
- **Engine READMEs:** 7 individual guides
- **Test files:** 4 test scripts
- **Example files:** 2 example scripts
- **Configuration files:** 10+ config files

**Total lines of documentation:** ~2,500+ lines

---

## 🆘 Getting Help

### Documentation Flow

```
New User
  ↓
PLATFORM_README.md (Overview)
  ↓
INSTALL_GUIDE.md (Installation)
  ↓
install_unified.ps1 (Automated install)
  ↓
QUICKSTART.md (First steps)
  ↓
example_*.py (Try examples)
  ↓
Individual READMEs (Deep dive)
```

### Troubleshooting Flow

```
Issue?
  ↓
INSTALL_GUIDE.md → Troubleshooting section
  ↓
Still stuck?
  ↓
TEST_RESULTS.md → Known issues
  ↓
Still stuck?
  ↓
validate_engines.py → Check what's working
```

---

## 📦 Package Structure Reference

```
datasets/
│
├── 📚 MAIN DOCS
│   ├── PLATFORM_README.md           ⭐ Start here
│   ├── INSTALL_GUIDE.md             ⭐ Installation guide
│   ├── QUICKSTART.md                 Quick start
│   ├── QUICK_REFERENCE.md            Reference card
│   ├── architecture.md               Architecture
│   └── DOCUMENTATION_INDEX.md        This file
│
├── 🔧 INSTALLATION
│   ├── install_unified.ps1          ⭐ Unified installer
│   ├── install_individual.ps1       ⭐ Individual installer
│   ├── setup.py                      Unified setup
│   └── requirements.txt              Dependencies
│
├── 🧪 TESTING
│   ├── validate_engines.py           Quick test
│   ├── example_unified_bundle.py     Unified example
│   ├── example_individual_engines.py Individual example
│   └── tests/                        Full test suite
│
└── 📦 ENGINES (7 directories)
    ├── intelligence/
    │   ├── README.md                ⭐ Engine docs
    │   ├── setup.py                  Engine installer
    │   └── threat_intelligence_engine.py
    ├── prevention/
    ├── detection/
    ├── response/
    ├── isolation/
    ├── mitigation/
    └── recovery/
```

---

## ✅ Next Steps

1. **Read** `PLATFORM_README.md` for overview
2. **Follow** `INSTALL_GUIDE.md` for installation
3. **Run** installation script (unified or individual)
4. **Test** with `validate_engines.py`
5. **Try** examples in `example_*.py` files
6. **Explore** individual engine READMEs
7. **Deploy** to your environment

---

**All documentation is ready! Choose your path and get started! 🚀**
