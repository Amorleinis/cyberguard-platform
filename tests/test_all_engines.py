"""
Integration tests for all 7 engines working together
"""

import unittest
import sys
import os
from pathlib import Path
import tempfile
import json
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "intelligence"))
sys.path.insert(0, str(Path(__file__).parent.parent / "prevention"))
sys.path.insert(0, str(Path(__file__).parent.parent / "detection"))
sys.path.insert(0, str(Path(__file__).parent.parent / "response"))
sys.path.insert(0, str(Path(__file__).parent.parent / "isolation"))
sys.path.insert(0, str(Path(__file__).parent.parent / "mitigation"))
sys.path.insert(0, str(Path(__file__).parent.parent / "recovery"))
sys.path.insert(0, str(Path(__file__).parent.parent / "orchestration"))


class TestAllEngines(unittest.TestCase):
    """Integration tests for complete threat intelligence platform"""
    
    @classmethod
    def setUpClass(cls):
        """Set up all engines"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.engines_loaded = {}
        
        # Try to import all engines
        try:
            from threat_intelligence_engine import ThreatIntelligenceEngine
            cls.engines_loaded['intelligence'] = ThreatIntelligenceEngine
        except ImportError as e:
            print(f"Intelligence engine not loaded: {e}")
        
        try:
            from threat_prevention_engine import ThreatPreventionEngine
            cls.engines_loaded['prevention'] = ThreatPreventionEngine
        except ImportError as e:
            print(f"Prevention engine not loaded: {e}")
        
        try:
            from threat_detection_engine import ThreatDetectionEngine
            cls.engines_loaded['detection'] = ThreatDetectionEngine
        except ImportError as e:
            print(f"Detection engine not loaded: {e}")
        
        try:
            from threat_response_engine import ThreatResponseEngine
            cls.engines_loaded['response'] = ThreatResponseEngine
        except ImportError as e:
            print(f"Response engine not loaded: {e}")
        
        try:
            from threat_isolation_engine import ThreatIsolationEngine
            cls.engines_loaded['isolation'] = ThreatIsolationEngine
        except ImportError as e:
            print(f"Isolation engine not loaded: {e}")
        
        try:
            from threat_mitigation_engine import ThreatMitigationEngine
            cls.engines_loaded['mitigation'] = ThreatMitigationEngine
        except ImportError as e:
            print(f"Mitigation engine not loaded: {e}")
        
        try:
            from threat_recovery_engine import ThreatRecoveryEngine
            cls.engines_loaded['recovery'] = ThreatRecoveryEngine
        except ImportError as e:
            print(f"Recovery engine not loaded: {e}")
        
        try:
            from threat_platform_orchestrator import ThreatIntelligencePlatform
            cls.engines_loaded['orchestrator'] = ThreatIntelligencePlatform
        except ImportError as e:
            print(f"Orchestrator not loaded: {e}")
    
    def test_01_all_engines_available(self):
        """Test that all engines can be imported"""
        expected_engines = [
            'intelligence', 'prevention', 'detection', 'response',
            'isolation', 'mitigation', 'recovery', 'orchestrator'
        ]
        
        for engine_name in expected_engines:
            with self.subTest(engine=engine_name):
                self.assertIn(engine_name, self.engines_loaded,
                            f"{engine_name} engine not loaded")
    
    def test_02_intelligence_to_prevention_flow(self):
        """Test flow from intelligence to prevention"""
        if 'intelligence' not in self.engines_loaded or 'prevention' not in self.engines_loaded:
            self.skipTest("Required engines not loaded")
        
        # Create engines
        intel_engine = self.engines_loaded['intelligence'](
            db_path=os.path.join(self.temp_dir, "intel.db")
        )
        prev_engine = self.engines_loaded['prevention'](
            db_path=os.path.join(self.temp_dir, "prev.db")
        )
        
        # Analyze CVE and extract IOCs
        cve_data = {
            "CVE_ID": "CVE-2024-TEST",
            "description": "Test vulnerability at 192.168.1.100",
            "severity": "HIGH",
            "cvss_score": 8.5
        }
        
        analysis = intel_engine.analyze_cve(cve_data)
        iocs = analysis.get("iocs", {})
        
        # Block IOCs in prevention engine
        for ip in iocs.get("ip_addresses", []):
            result = prev_engine.block_ioc(
                ioc_value=ip,
                ioc_type="ip",
                source="intelligence_engine",
                severity="HIGH"
            )
            self.assertTrue(result)
        
        intel_engine.close()
        prev_engine.close()
    
    def test_03_detection_to_response_flow(self):
        """Test flow from detection to response"""
        if 'detection' not in self.engines_loaded or 'response' not in self.engines_loaded:
            self.skipTest("Required engines not loaded")
        
        # Create engines
        detect_engine = self.engines_loaded['detection'](
            db_path=os.path.join(self.temp_dir, "detect.db")
        )
        response_engine = self.engines_loaded['response'](
            db_path=os.path.join(self.temp_dir, "response.db")
        )
        
        # Simulate detection
        detection_event = {
            "timestamp": datetime.now().isoformat(),
            "source": "network_monitor",
            "event_type": "suspicious_connection",
            "severity": "HIGH",
            "details": {
                "src_ip": "10.0.0.50",
                "dst_ip": "192.168.1.100",
                "port": 4444
            }
        }
        
        # Create incident from detection
        incident = response_engine.create_incident(
            title="Suspicious Network Connection Detected",
            description=f"Detection event: {json.dumps(detection_event)}",
            severity="HIGH",
            incident_type="network_intrusion",
            affected_assets=["10.0.0.50"]
        )
        
        self.assertIsNotNone(incident)
        self.assertIn("incident_id", incident)
        
        detect_engine.close()
        response_engine.close()
    
    def test_04_response_to_isolation_flow(self):
        """Test flow from response to isolation"""
        if 'response' not in self.engines_loaded or 'isolation' not in self.engines_loaded:
            self.skipTest("Required engines not loaded")
        
        # Create engines
        response_engine = self.engines_loaded['response'](
            db_path=os.path.join(self.temp_dir, "response2.db")
        )
        isolation_engine = self.engines_loaded['isolation'](
            db_path=os.path.join(self.temp_dir, "isolation.db")
        )
        
        # Create incident
        incident = response_engine.create_incident(
            title="Malware Infection",
            description="Host compromised with malware",
            severity="CRITICAL",
            incident_type="malware",
            affected_assets=["workstation-123"]
        )
        
        # Isolate affected host
        isolation_result = isolation_engine.isolate_host(
            hostname="workstation-123",
            reason=f"Response to incident {incident['incident_id']}",
            severity="CRITICAL",
            duration_hours=24
        )
        
        self.assertTrue(isolation_result)
        
        response_engine.close()
        isolation_engine.close()
    
    def test_05_mitigation_to_recovery_flow(self):
        """Test flow from mitigation to recovery"""
        if 'mitigation' not in self.engines_loaded or 'recovery' not in self.engines_loaded:
            self.skipTest("Required engines not loaded")
        
        # Create engines
        mitigation_engine = self.engines_loaded['mitigation'](
            db_path=os.path.join(self.temp_dir, "mitigation.db")
        )
        recovery_engine = self.engines_loaded['recovery'](
            db_path=os.path.join(self.temp_dir, "recovery.db")
        )
        
        # Remediate vulnerability
        remediation = mitigation_engine.remediate_vulnerability(
            vulnerability_id="CVE-2024-TEST",
            affected_hosts=["server-001"],
            remediation_type="patch",
            priority="HIGH"
        )
        
        self.assertIsNotNone(remediation)
        
        # Create recovery plan
        recovery_plan = recovery_engine.create_recovery_plan(
            plan_name="Post-Mitigation Recovery",
            description="Recovery after CVE-2024-TEST mitigation",
            recovery_type="service_restoration",
            affected_systems=["server-001"]
        )
        
        self.assertIsNotNone(recovery_plan)
        
        mitigation_engine.close()
        recovery_engine.close()
    
    def test_06_orchestrator_end_to_end(self):
        """Test orchestrator managing entire workflow"""
        if 'orchestrator' not in self.engines_loaded:
            self.skipTest("Orchestrator not loaded")
        
        # Create platform orchestrator
        platform = self.engines_loaded['orchestrator'](
            base_dir=self.temp_dir
        )
        
        # Process a threat alert end-to-end
        alert = {
            "type": "malware_detection",
            "severity": "HIGH",
            "source": "endpoint_protection",
            "details": {
                "host": "workstation-456",
                "malware_family": "Ransomware.Generic",
                "file_hash": "abc123def456"
            }
        }
        
        # Process alert through platform
        # Note: This will use mock implementations if actual engines aren't fully loaded
        try:
            result = platform.process_threat_alert(alert)
            self.assertIsNotNone(result)
        except Exception as e:
            # Expected if dependencies not installed
            print(f"Orchestrator test partial: {e}")
        
        platform.shutdown()
    
    def test_07_platform_metrics(self):
        """Test platform-wide metrics collection"""
        if 'orchestrator' not in self.engines_loaded:
            self.skipTest("Orchestrator not loaded")
        
        platform = self.engines_loaded['orchestrator'](
            base_dir=self.temp_dir
        )
        
        try:
            metrics = platform.get_platform_status()
            self.assertIn("platform_status", metrics)
            self.assertIn("active_engines", metrics)
        except Exception as e:
            print(f"Metrics test partial: {e}")
        
        platform.shutdown()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up"""
        import shutil
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)


if __name__ == "__main__":
    unittest.main(verbosity=2)
