"""
Unit tests for Threat Intelligence Engine
"""

import unittest
import sys
import os
from pathlib import Path
from datetime import datetime
import json
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "intelligence"))

try:
    from threat_intelligence_engine import ThreatIntelligenceEngine
except ImportError as e:
    print(f"Import error: {e}")
    ThreatIntelligenceEngine = None


class TestThreatIntelligenceEngine(unittest.TestCase):
    """Test cases for Threat Intelligence Engine"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        if ThreatIntelligenceEngine is None:
            raise unittest.SkipTest("ThreatIntelligenceEngine not available")
        
        cls.temp_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.temp_dir, "test_intelligence.db")
        
        # Sample CVE data
        cls.sample_cve = {
            "CVE_ID": "CVE-2024-1234",
            "description": "Remote code execution vulnerability in test software",
            "severity": "CRITICAL",
            "cvss_score": 9.8,
            "published_date": "2024-01-15",
            "affected_products": ["Test Software 1.0"],
            "references": ["https://example.com/advisory"]
        }
    
    def setUp(self):
        """Set up test engine"""
        self.engine = ThreatIntelligenceEngine(
            db_path=self.db_path,
            neo4j_uri=None,  # Skip Neo4j for unit tests
            neo4j_user=None,
            neo4j_password=None
        )
    
    def test_01_engine_initialization(self):
        """Test engine initializes correctly"""
        self.assertIsNotNone(self.engine)
        self.assertTrue(os.path.exists(self.db_path))
    
    def test_02_analyze_cve(self):
        """Test CVE analysis"""
        analysis = self.engine.analyze_cve(self.sample_cve)
        
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis["cve_id"], "CVE-2024-1234")
        self.assertIn("threat_score", analysis)
        self.assertIn("severity", analysis)
        self.assertIn("iocs", analysis)
    
    def test_03_extract_iocs(self):
        """Test IOC extraction"""
        text = """
        Malicious IP: 192.168.1.100
        C2 Domain: evil.example.com
        File Hash: 5d41402abc4b2a76b9719d911017c592
        Suspicious URL: http://malware.example.org/payload.exe
        """
        
        iocs = self.engine.extract_iocs(text)
        
        self.assertIn("ip_addresses", iocs)
        self.assertIn("domains", iocs)
        self.assertIn("file_hashes", iocs)
        self.assertIn("urls", iocs)
    
    def test_04_threat_scoring(self):
        """Test threat scoring logic"""
        # High severity should have high score
        high_threat = {
            "severity": "CRITICAL",
            "cvss_score": 9.8,
            "exploit_available": True
        }
        
        analysis = self.engine.analyze_cve(high_threat)
        self.assertGreater(analysis.get("threat_score", 0), 7.0)
    
    def test_05_search_intelligence(self):
        """Test intelligence search"""
        # Add some test data
        self.engine.analyze_cve(self.sample_cve)
        
        # Search for it
        results = self.engine.search_intelligence(
            query="CVE-2024-1234",
            limit=10
        )
        
        self.assertIsInstance(results, list)
    
    def test_06_get_metrics(self):
        """Test metrics retrieval"""
        metrics = self.engine.get_metrics()
        
        self.assertIn("total_cves_analyzed", metrics)
        self.assertIn("total_threat_actors", metrics)
        self.assertIn("total_iocs_extracted", metrics)
    
    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'engine'):
            self.engine.close()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)


if __name__ == "__main__":
    unittest.main()
