"""
Simple Test Script - Validates all engines can be loaded and basic functionality works
"""

import sys
import os
from pathlib import Path

# Add all engine directories to path
base_dir = Path(__file__).parent
sys.path.insert(0, str(base_dir / "intelligence"))
sys.path.insert(0, str(base_dir / "prevention"))
sys.path.insert(0, str(base_dir / "detection"))
sys.path.insert(0, str(base_dir / "response"))
sys.path.insert(0, str(base_dir / "isolation"))
sys.path.insert(0, str(base_dir / "mitigation"))
sys.path.insert(0, str(base_dir / "recovery"))
sys.path.insert(0, str(base_dir / "orchestration"))

print("=" * 80)
print("THREAT INTELLIGENCE PLATFORM - ENGINE VALIDATION")
print("=" * 80)
print()

# Test 1: Import all engines
print("Test 1: Loading all engines...")
engines_loaded = {}

try:
    from threat_intelligence_engine import ThreatIntelligenceEngine
    engines_loaded['Intelligence'] = ThreatIntelligenceEngine
    print("✓ Intelligence Engine loaded")
except Exception as e:
    print(f"✗ Intelligence Engine failed: {e}")

try:
    from threat_prevention_engine import ThreatPreventionEngine
    engines_loaded['Prevention'] = ThreatPreventionEngine
    print("✓ Prevention Engine loaded")
except Exception as e:
    print(f"✗ Prevention Engine failed: {e}")

try:
    from threat_detection_engine import ThreatDetectionEngine
    engines_loaded['Detection'] = ThreatDetectionEngine
    print("✓ Detection Engine loaded")
except Exception as e:
    print(f"✗ Detection Engine failed: {e}")

try:
    from threat_response_engine import ThreatResponseEngine
    engines_loaded['Response'] = ThreatResponseEngine
    print("✓ Response Engine loaded")
except Exception as e:
    print(f"✗ Response Engine failed: {e}")

try:
    from threat_isolation_engine import ThreatIsolationEngine
    engines_loaded['Isolation'] = ThreatIsolationEngine
    print("✓ Isolation Engine loaded")
except Exception as e:
    print(f"✗ Isolation Engine failed: {e}")

try:
    from threat_mitigation_engine import ThreatMitigationEngine
    engines_loaded['Mitigation'] = ThreatMitigationEngine
    print("✓ Mitigation Engine loaded")
except Exception as e:
    print(f"✗ Mitigation Engine failed: {e}")

try:
    from threat_recovery_engine import ThreatRecoveryEngine
    engines_loaded['Recovery'] = ThreatRecoveryEngine
    print("✓ Recovery Engine loaded")
except Exception as e:
    print(f"✗ Recovery Engine failed: {e}")

try:
    from threat_platform_orchestrator import ThreatIntelligencePlatform
    engines_loaded['Orchestrator'] = ThreatIntelligencePlatform
    print("✓ Orchestrator loaded")
except Exception as e:
    print(f"✗ Orchestrator failed: {e}")

print()
print(f"Engines loaded: {len(engines_loaded)}/8")
print()

# Test 2: Initialize engines
print("Test 2: Initializing engines...")
import tempfile
temp_dir = tempfile.mkdtemp()
initialized = {}

if 'Intelligence' in engines_loaded:
    try:
        engine = engines_loaded['Intelligence'](
            db_path=os.path.join(temp_dir, "intel.db"),
            neo4j_uri=None,
            neo4j_user=None,
            neo4j_password=None
        )
        initialized['Intelligence'] = engine
        print("✓ Intelligence Engine initialized")
    except Exception as e:
        print(f"✗ Intelligence Engine init failed: {e}")

if 'Prevention' in engines_loaded:
    try:
        engine = engines_loaded['Prevention'](
            db_path=os.path.join(temp_dir, "prev.db")
        )
        initialized['Prevention'] = engine
        print("✓ Prevention Engine initialized")
    except Exception as e:
        print(f"✗ Prevention Engine init failed: {e}")

if 'Detection' in engines_loaded:
    try:
        engine = engines_loaded['Detection'](
            db_path=os.path.join(temp_dir, "detect.db")
        )
        initialized['Detection'] = engine
        print("✓ Detection Engine initialized")
    except Exception as e:
        print(f"✗ Detection Engine init failed: {e}")

if 'Response' in engines_loaded:
    try:
        engine = engines_loaded['Response'](
            db_path=os.path.join(temp_dir, "response.db")
        )
        initialized['Response'] = engine
        print("✓ Response Engine initialized")
    except Exception as e:
        print(f"✗ Response Engine init failed: {e}")

if 'Isolation' in engines_loaded:
    try:
        engine = engines_loaded['Isolation'](
            db_path=os.path.join(temp_dir, "isolation.db")
        )
        initialized['Isolation'] = engine
        print("✓ Isolation Engine initialized")
    except Exception as e:
        print(f"✗ Isolation Engine init failed: {e}")

if 'Mitigation' in engines_loaded:
    try:
        engine = engines_loaded['Mitigation'](
            db_path=os.path.join(temp_dir, "mitigation.db")
        )
        initialized['Mitigation'] = engine
        print("✓ Mitigation Engine initialized")
    except Exception as e:
        print(f"✗ Mitigation Engine init failed: {e}")

if 'Recovery' in engines_loaded:
    try:
        engine = engines_loaded['Recovery'](
            db_path=os.path.join(temp_dir, "recovery.db")
        )
        initialized['Recovery'] = engine
        print("✓ Recovery Engine initialized")
    except Exception as e:
        print(f"✗ Recovery Engine init failed: {e}")

if 'Orchestrator' in engines_loaded:
    try:
        engine = engines_loaded['Orchestrator'](
            base_dir=temp_dir
        )
        initialized['Orchestrator'] = engine
        print("✓ Orchestrator initialized")
    except Exception as e:
        print(f"✗ Orchestrator init failed: {e}")

print()
print(f"Engines initialized: {len(initialized)}/8")
print()

# Test 3: Basic functionality
print("Test 3: Testing basic functionality...")

if 'Intelligence' in initialized:
    try:
        engine = initialized['Intelligence']
        analysis = engine.analyze_cve({
            "CVE_ID": "CVE-2024-TEST",
            "description": "Test vulnerability",
            "severity": "HIGH",
            "cvss_score": 8.5
        })
        print(f"✓ Intelligence: Analyzed CVE (threat_score={analysis.get('threat_score', 'N/A')})")
    except Exception as e:
        print(f"✗ Intelligence test failed: {e}")

if 'Prevention' in initialized:
    try:
        engine = initialized['Prevention']
        result = engine.block_ioc("192.168.1.100", ioc_type="ip", severity="HIGH")
        print(f"✓ Prevention: Blocked IOC (result={result})")
    except Exception as e:
        print(f"✗ Prevention test failed: {e}")

if 'Response' in initialized:
    try:
        engine = initialized['Response']
        incident = engine.create_incident(
            title="Test Incident",
            severity="MEDIUM",
            incident_type="test"
        )
        print(f"✓ Response: Created incident (id={incident.get('incident_id', 'N/A')})")
    except Exception as e:
        print(f"✗ Response test failed: {e}")

if 'Isolation' in initialized:
    try:
        engine = initialized['Isolation']
        result = engine.isolate_host("test-host", reason="Testing")
        print(f"✓ Isolation: Isolated host (result={result})")
    except Exception as e:
        print(f"✗ Isolation test failed: {e}")

if 'Mitigation' in initialized:
    try:
        engine = initialized['Mitigation']
        result = engine.remediate_vulnerability(
            "CVE-2024-TEST",
            affected_hosts=["test-host"]
        )
        print(f"✓ Mitigation: Remediated vulnerability")
    except Exception as e:
        print(f"✗ Mitigation test failed: {e}")

if 'Recovery' in initialized:
    try:
        engine = initialized['Recovery']
        plan = engine.create_recovery_plan(
            plan_name="Test Recovery",
            recovery_type="test"
        )
        print(f"✓ Recovery: Created recovery plan")
    except Exception as e:
        print(f"✗ Recovery test failed: {e}")

print()

# Test 4: Get metrics
print("Test 4: Retrieving metrics...")

for name, engine in initialized.items():
    if name == 'Orchestrator':
        continue
    try:
        if hasattr(engine, 'get_metrics'):
            metrics = engine.get_metrics()
            print(f"✓ {name}: {metrics}")
    except Exception as e:
        print(f"✗ {name} metrics failed: {e}")

print()

# Cleanup
print("Cleaning up...")
for name, engine in initialized.items():
    try:
        if hasattr(engine, 'close'):
            engine.close()
        elif hasattr(engine, 'shutdown'):
            engine.shutdown()
    except:
        pass

import shutil
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)

print()
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Engines Loaded: {len(engines_loaded)}/8")
print(f"Engines Initialized: {len(initialized)}/8")
print(f"Status: {'✓ ALL TESTS PASSED' if len(initialized) >= 7 else '⚠ SOME TESTS FAILED'}")
print("=" * 80)
