"""
Threat Intelligence Engine Core Module

This module provides the core threat intelligence capabilities including:
- CVE analysis and risk scoring
- Threat actor profiling and attribution
- Attack campaign analysis and correlation
- IOC extraction and enrichment
- Predictive threat modeling
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from neo4j import GraphDatabase
import sqlite3
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
import networkx as nx
import pickle
import re
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ThreatIntelligence:
    """Core threat intelligence data structure"""
    threat_id: str
    threat_type: str
    severity: str
    confidence: float
    indicators: List[str]
    actors: List[str]
    techniques: List[str]
    timestamp: datetime
    source: str
    description: str
    raw_data: Dict[str, Any]

@dataclass
class ThreatActor:
    """Threat actor profile"""
    actor_id: str
    name: str
    type: str
    origin: str
    sophistication: str
    techniques: List[str]
    campaigns: List[str]
    targets: List[str]
    confidence: float

@dataclass
class VulnerabilityIntelligence:
    """CVE intelligence with enrichment"""
    cve_id: str
    published_date: datetime
    severity: str
    cvss_score: float
    exploit_available: bool
    exploitation_likelihood: float
    affected_products: List[str]
    attack_vectors: List[str]
    mitigations: List[str]
    related_threats: List[str]

@dataclass
class AttackCampaign:
    """Attack campaign analysis"""
    campaign_id: str
    name: str
    actors: List[str]
    start_date: datetime
    end_date: Optional[datetime]
    techniques: List[str]
    indicators: List[str]
    targets: List[str]
    success_rate: float
    impact_score: float

class ThreatIntelligenceEngine:
    """
    Core Threat Intelligence Engine
    
    Provides comprehensive threat intelligence capabilities including:
    - Data ingestion from multiple sources
    - Threat correlation and analysis
    - Risk scoring and prioritization
    - Predictive modeling
    - Intelligence sharing and export
    """
    
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str,
                 data_dir: str = "../../../"):
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.data_dir = Path(data_dir)
        
        # Initialize connections
        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri, auth=(neo4j_user, neo4j_password)
        )
        
        # Initialize local storage
        self.db_path = self.data_dir / "threat_intelligence.db"
        self._init_local_db()
        
        # Load ML models
        self.models = {}
        self._init_ml_models()
        
        # Load data
        self.cve_data = None
        self.actor_data = None
        self.threat_actions = None
        self._load_datasets()
        
        logger.info("Threat Intelligence Engine initialized")
    
    def _init_local_db(self):
        """Initialize local SQLite database for caching and fast queries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threat_intelligence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                threat_id TEXT UNIQUE NOT NULL,
                threat_type TEXT,
                severity TEXT,
                confidence REAL,
                timestamp TEXT,
                source TEXT,
                data_json TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threat_actors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_id TEXT UNIQUE NOT NULL,
                name TEXT,
                type TEXT,
                origin TEXT,
                sophistication TEXT,
                confidence REAL,
                data_json TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vulnerability_intel (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cve_id TEXT UNIQUE NOT NULL,
                severity TEXT,
                cvss_score REAL,
                exploit_available INTEGER,
                exploitation_likelihood REAL,
                published_date TEXT,
                data_json TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attack_campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT UNIQUE NOT NULL,
                name TEXT,
                start_date TEXT,
                end_date TEXT,
                success_rate REAL,
                impact_score REAL,
                data_json TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _init_ml_models(self):
        """Initialize machine learning models"""
        # Threat severity classifier
        self.models['severity_classifier'] = RandomForestClassifier(
            n_estimators=100, random_state=42
        )
        
        # Anomaly detection for threat behavior
        self.models['anomaly_detector'] = IsolationForest(
            contamination=0.1, random_state=42
        )
        
        # Threat actor clustering
        self.models['actor_clusterer'] = DBSCAN(eps=0.5, min_samples=5)
        
        # Feature scaler
        self.models['scaler'] = StandardScaler()
        
        # PCA for dimensionality reduction
        self.models['pca'] = PCA(n_components=10)
    
    def _load_datasets(self):
        """Load existing datasets from the workspace"""
        try:
            # Load CVE data
            cve_files = [
                "cve_data_with_use_cases.json",
                "cve_data.json"
            ]
            
            for file in cve_files:
                file_path = self.data_dir / file
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        self.cve_data = json.load(f)
                    logger.info(f"Loaded CVE data from {file}")
                    break
            
            # Load threat actor data
            actor_file = self.data_dir / "neo4j" / "Actor (1).csv"
            if actor_file.exists():
                self.actor_data = pd.read_csv(actor_file)
                logger.info(f"Loaded actor data: {len(self.actor_data)} actors")
            
            # Load threat actions
            actions_file = self.data_dir / "neo4j" / "ThreatAction_nextgen.csv"
            if actions_file.exists():
                self.threat_actions = pd.read_csv(actions_file)
                logger.info(f"Loaded threat actions: {len(self.threat_actions)} actions")
                
        except Exception as e:
            logger.error(f"Error loading datasets: {e}")
    
    def analyze_cve_intelligence(self, cve_id: str = None) -> List[VulnerabilityIntelligence]:
        """
        Analyze CVE data to extract intelligence
        
        Args:
            cve_id: Specific CVE to analyze, or None for all
            
        Returns:
            List of vulnerability intelligence objects
        """
        if not self.cve_data:
            logger.warning("No CVE data available")
            return []
        
        intelligence = []
        
        for cve in self.cve_data:
            if cve_id and cve.get('cve_id') != cve_id:
                continue
                
            # Extract basic information
            vuln_intel = VulnerabilityIntelligence(
                cve_id=cve.get('cve_id', 'Unknown'),
                published_date=datetime.fromisoformat(
                    cve.get('published', '2024-01-01').replace('Z', '+00:00')
                ),
                severity=self._determine_severity(cve),
                cvss_score=self._extract_cvss_score(cve),
                exploit_available=self._check_exploit_availability(cve),
                exploitation_likelihood=self._calculate_exploitation_likelihood(cve),
                affected_products=self._extract_affected_products(cve),
                attack_vectors=self._extract_attack_vectors(cve),
                mitigations=self._extract_mitigations(cve),
                related_threats=self._find_related_threats(cve)
            )
            
            intelligence.append(vuln_intel)
            
            # Cache in local database
            self._cache_vulnerability_intelligence(vuln_intel)
        
        logger.info(f"Analyzed {len(intelligence)} CVE intelligence items")
        return intelligence
    
    def profile_threat_actors(self) -> List[ThreatActor]:
        """
        Create detailed threat actor profiles
        
        Returns:
            List of threat actor profiles
        """
        if self.actor_data is None:
            logger.warning("No actor data available")
            return []
        
        profiles = []
        
        for _, actor_row in self.actor_data.iterrows():
            # Get related techniques from threat actions
            techniques = self._get_actor_techniques(actor_row['id'])
            campaigns = self._get_actor_campaigns(actor_row['id'])
            targets = self._get_actor_targets(actor_row['id'])
            
            # Calculate confidence based on data completeness
            confidence = self._calculate_actor_confidence(actor_row, techniques)
            
            profile = ThreatActor(
                actor_id=actor_row['id'],
                name=actor_row['name'],
                type=actor_row['type'],
                origin=actor_row['origin'],
                sophistication=actor_row['sophistication'],
                techniques=techniques,
                campaigns=campaigns,
                targets=targets,
                confidence=confidence
            )
            
            profiles.append(profile)
            
            # Cache in local database
            self._cache_threat_actor(profile)
        
        logger.info(f"Profiled {len(profiles)} threat actors")
        return profiles
    
    def detect_attack_campaigns(self) -> List[AttackCampaign]:
        """
        Detect and analyze attack campaigns using pattern recognition
        
        Returns:
            List of identified attack campaigns
        """
        campaigns = []
        
        if self.threat_actions is None:
            logger.warning("No threat action data available")
            return campaigns
        
        # Group threat actions by similarity and temporal patterns
        campaign_clusters = self._cluster_threat_actions()
        
        for cluster_id, actions in campaign_clusters.items():
            if len(actions) < 2:  # Skip single-action "campaigns"
                continue
                
            campaign = self._create_campaign_from_cluster(cluster_id, actions)
            campaigns.append(campaign)
            
            # Cache in local database
            self._cache_attack_campaign(campaign)
        
        logger.info(f"Detected {len(campaigns)} attack campaigns")
        return campaigns
    
    def extract_indicators(self, text: str) -> Dict[str, List[str]]:
        """
        Extract indicators of compromise from text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary of IOC types and their values
        """
        indicators = {
            'ip_addresses': [],
            'domains': [],
            'file_hashes': [],
            'email_addresses': [],
            'urls': [],
            'registry_keys': [],
            'file_paths': []
        }
        
        # IP addresses
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        indicators['ip_addresses'] = re.findall(ip_pattern, text)
        
        # Domains
        domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
        indicators['domains'] = re.findall(domain_pattern, text)
        
        # File hashes (MD5, SHA1, SHA256)
        md5_pattern = r'\b[a-f0-9]{32}\b'
        sha1_pattern = r'\b[a-f0-9]{40}\b'
        sha256_pattern = r'\b[a-f0-9]{64}\b'
        
        indicators['file_hashes'].extend(re.findall(md5_pattern, text, re.IGNORECASE))
        indicators['file_hashes'].extend(re.findall(sha1_pattern, text, re.IGNORECASE))
        indicators['file_hashes'].extend(re.findall(sha256_pattern, text, re.IGNORECASE))
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        indicators['email_addresses'] = re.findall(email_pattern, text)
        
        # URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        indicators['urls'] = re.findall(url_pattern, text)
        
        # Remove duplicates
        for ioc_type in indicators:
            indicators[ioc_type] = list(set(indicators[ioc_type]))
        
        return indicators
    
    def calculate_threat_score(self, threat_data: Dict[str, Any]) -> float:
        """
        Calculate comprehensive threat score
        
        Args:
            threat_data: Dictionary containing threat information
            
        Returns:
            Threat score (0.0 - 1.0)
        """
        score = 0.0
        
        # Severity weighting
        severity_weights = {
            'Critical': 1.0,
            'High': 0.8,
            'Medium': 0.6,
            'Low': 0.4,
            'Info': 0.2
        }
        
        severity = threat_data.get('severity', 'Medium')
        score += severity_weights.get(severity, 0.6) * 0.3
        
        # Confidence weighting
        confidence = threat_data.get('confidence', 0.5)
        score += confidence * 0.2
        
        # Recency weighting (newer threats score higher)
        if 'timestamp' in threat_data:
            try:
                timestamp = datetime.fromisoformat(threat_data['timestamp'])
                days_old = (datetime.now() - timestamp).days
                recency_score = max(0, 1 - (days_old / 365))  # Decay over a year
                score += recency_score * 0.2
            except:
                score += 0.1  # Default for unparseable timestamps
        
        # Actor sophistication weighting
        sophistication_weights = {
            'Very High': 1.0,
            'High': 0.8,
            'Medium': 0.6,
            'Low': 0.4
        }
        
        sophistication = threat_data.get('sophistication', 'Medium')
        score += sophistication_weights.get(sophistication, 0.6) * 0.2
        
        # Exploit availability
        if threat_data.get('exploit_available', False):
            score += 0.1
        
        return min(1.0, score)  # Cap at 1.0
    
    def correlate_threats(self, threat_ids: List[str]) -> Dict[str, Any]:
        """
        Correlate multiple threats to identify patterns and relationships
        
        Args:
            threat_ids: List of threat IDs to correlate
            
        Returns:
            Correlation analysis results
        """
        correlations = {
            'common_actors': [],
            'common_techniques': [],
            'temporal_patterns': {},
            'geographic_patterns': {},
            'target_patterns': {},
            'correlation_score': 0.0
        }
        
        # Get threat data from database
        threats = self._get_threats_by_ids(threat_ids)
        
        if len(threats) < 2:
            return correlations
        
        # Find common elements
        all_actors = [threat.get('actors', []) for threat in threats]
        all_techniques = [threat.get('techniques', []) for threat in threats]
        
        # Common actors
        if all_actors:
            common_actors = set(all_actors[0])
            for actors in all_actors[1:]:
                common_actors &= set(actors)
            correlations['common_actors'] = list(common_actors)
        
        # Common techniques
        if all_techniques:
            common_techniques = set(all_techniques[0])
            for techniques in all_techniques[1:]:
                common_techniques &= set(techniques)
            correlations['common_techniques'] = list(common_techniques)
        
        # Calculate correlation score
        correlation_score = 0.0
        if correlations['common_actors']:
            correlation_score += len(correlations['common_actors']) * 0.4
        if correlations['common_techniques']:
            correlation_score += len(correlations['common_techniques']) * 0.3
        
        correlations['correlation_score'] = min(1.0, correlation_score)
        
        return correlations
    
    def generate_threat_report(self, threat_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive threat intelligence report
        
        Args:
            threat_id: ID of threat to report on
            
        Returns:
            Comprehensive threat report
        """
        report = {
            'threat_id': threat_id,
            'generated_at': datetime.now().isoformat(),
            'executive_summary': '',
            'threat_details': {},
            'actor_analysis': {},
            'technical_analysis': {},
            'indicators': {},
            'recommendations': [],
            'related_threats': [],
            'risk_assessment': {}
        }
        
        # Get threat data
        threat = self._get_threat_by_id(threat_id)
        if not threat:
            logger.error(f"Threat {threat_id} not found")
            return report
        
        # Populate report sections
        report['threat_details'] = threat
        report['risk_assessment'] = {
            'threat_score': self.calculate_threat_score(threat),
            'confidence': threat.get('confidence', 0.5),
            'impact': threat.get('severity', 'Medium'),
            'likelihood': threat.get('likelihood', 'Medium')
        }
        
        # Generate executive summary
        report['executive_summary'] = self._generate_executive_summary(threat)
        
        # Get related threats
        related_ids = self._find_related_threat_ids(threat_id, limit=5)
        report['related_threats'] = [
            self._get_threat_by_id(rid) for rid in related_ids
        ]
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(threat)
        
        return report
    
    # Helper methods
    
    def _determine_severity(self, cve: Dict[str, Any]) -> str:
        """Determine CVE severity from available data"""
        # Try to extract CVSS score first
        cvss_score = self._extract_cvss_score(cve)
        
        if cvss_score >= 9.0:
            return 'Critical'
        elif cvss_score >= 7.0:
            return 'High'
        elif cvss_score >= 4.0:
            return 'Medium'
        elif cvss_score > 0.0:
            return 'Low'
        else:
            return 'Unknown'
    
    def _extract_cvss_score(self, cve: Dict[str, Any]) -> float:
        """Extract CVSS score from CVE data"""
        # Look for CVSS score in various fields
        score_fields = ['cvss_score', 'baseScore', 'score']
        
        for field in score_fields:
            if field in cve:
                try:
                    return float(cve[field])
                except (ValueError, TypeError):
                    continue
        
        # If no score found, try to extract from description or other fields
        description = cve.get('description', '')
        if 'critical' in description.lower():
            return 9.0
        elif 'high' in description.lower():
            return 7.5
        elif 'medium' in description.lower():
            return 5.0
        elif 'low' in description.lower():
            return 3.0
        
        return 0.0  # Unknown
    
    def _check_exploit_availability(self, cve: Dict[str, Any]) -> bool:
        """Check if exploit is available for CVE"""
        # Simple heuristic - check description for exploit keywords
        description = cve.get('description', '').lower()
        exploit_keywords = ['exploit', 'poc', 'proof of concept', 'metasploit', 'exploit-db']
        
        return any(keyword in description for keyword in exploit_keywords)
    
    def _calculate_exploitation_likelihood(self, cve: Dict[str, Any]) -> float:
        """Calculate likelihood of exploitation"""
        likelihood = 0.0
        
        # Base likelihood on CVSS score
        cvss_score = self._extract_cvss_score(cve)
        likelihood += min(1.0, cvss_score / 10.0) * 0.4
        
        # Increase if exploit is available
        if self._check_exploit_availability(cve):
            likelihood += 0.3
        
        # Increase based on age (newer CVEs are more likely to be exploited)
        try:
            pub_date = datetime.fromisoformat(cve.get('published', '2024-01-01').replace('Z', '+00:00'))
            days_old = (datetime.now() - pub_date).days
            if days_old < 30:
                likelihood += 0.2
            elif days_old < 90:
                likelihood += 0.1
        except:
            pass
        
        # Check if it's a remote code execution vulnerability
        description = cve.get('description', '').lower()
        if 'remote code execution' in description or 'rce' in description:
            likelihood += 0.1
        
        return min(1.0, likelihood)
    
    def _extract_affected_products(self, cve: Dict[str, Any]) -> List[str]:
        """Extract affected products from CVE data"""
        products = []
        
        # Look for product information in various fields
        if 'affected_products' in cve:
            products.extend(cve['affected_products'])
        
        if 'vendor_data' in cve:
            for vendor in cve['vendor_data']:
                if 'product_data' in vendor:
                    products.extend([p.get('product_name', '') for p in vendor['product_data']])
        
        return list(set(products))  # Remove duplicates
    
    def _extract_attack_vectors(self, cve: Dict[str, Any]) -> List[str]:
        """Extract attack vectors from CVE data"""
        vectors = []
        
        description = cve.get('description', '').lower()
        
        # Common attack vectors
        vector_keywords = {
            'network': ['remote', 'network', 'internet'],
            'local': ['local', 'privilege escalation'],
            'physical': ['physical access', 'usb'],
            'social': ['social engineering', 'phishing']
        }
        
        for vector, keywords in vector_keywords.items():
            if any(keyword in description for keyword in keywords):
                vectors.append(vector)
        
        return vectors if vectors else ['unknown']
    
    def _extract_mitigations(self, cve: Dict[str, Any]) -> List[str]:
        """Extract mitigation strategies from CVE data"""
        mitigations = []
        
        # Standard mitigations based on CVE type
        description = cve.get('description', '').lower()
        
        if 'update' in description or 'patch' in description:
            mitigations.append('Apply security updates')
        
        if 'authentication' in description:
            mitigations.append('Implement strong authentication')
        
        if 'input validation' in description:
            mitigations.append('Validate input data')
        
        if 'network' in description:
            mitigations.append('Implement network segmentation')
        
        # Default mitigation
        if not mitigations:
            mitigations.append('Monitor for exploitation attempts')
        
        return mitigations
    
    def _find_related_threats(self, cve: Dict[str, Any]) -> List[str]:
        """Find threats related to this CVE"""
        # For now, return empty list - would implement graph-based similarity search
        return []
    
    def _get_actor_techniques(self, actor_id: str) -> List[str]:
        """Get techniques used by an actor"""
        # Query Neo4j for actor-technique relationships
        with self.neo4j_driver.session() as session:
            result = session.run(
                "MATCH (a:Actor {id: $actor_id})-[:USES]->(t:Technique) RETURN t.name",
                actor_id=actor_id
            )
            return [record["t.name"] for record in result]
    
    def _get_actor_campaigns(self, actor_id: str) -> List[str]:
        """Get campaigns associated with an actor"""
        # Query Neo4j for actor-campaign relationships
        with self.neo4j_driver.session() as session:
            result = session.run(
                "MATCH (a:Actor {id: $actor_id})-[:PARTICIPATES_IN]->(c:Campaign) RETURN c.name",
                actor_id=actor_id
            )
            return [record["c.name"] for record in result]
    
    def _get_actor_targets(self, actor_id: str) -> List[str]:
        """Get typical targets for an actor"""
        # Query Neo4j for actor-target relationships
        with self.neo4j_driver.session() as session:
            result = session.run(
                "MATCH (a:Actor {id: $actor_id})-[:TARGETS]->(t:Target) RETURN t.name",
                actor_id=actor_id
            )
            return [record["t.name"] for record in result]
    
    def _calculate_actor_confidence(self, actor_row: pd.Series, techniques: List[str]) -> float:
        """Calculate confidence score for actor profile"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on available data
        if actor_row['name'] and actor_row['name'] != 'Unknown':
            confidence += 0.1
        if actor_row['type'] and actor_row['type'] != 'Unknown':
            confidence += 0.1
        if actor_row['origin'] and actor_row['origin'] != 'Unknown':
            confidence += 0.1
        if techniques:
            confidence += min(0.2, len(techniques) * 0.05)
        
        return min(1.0, confidence)
    
    def _cluster_threat_actions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Cluster threat actions to identify campaigns"""
        clusters = {}
        
        if self.threat_actions is None:
            return clusters
        
        # Simple clustering based on attack vector and severity
        for _, action in self.threat_actions.iterrows():
            cluster_key = f"{action['attack_vector']}_{action['severity']}"
            
            if cluster_key not in clusters:
                clusters[cluster_key] = []
            
            clusters[cluster_key].append(action.to_dict())
        
        return clusters
    
    def _create_campaign_from_cluster(self, cluster_id: str, actions: List[Dict[str, Any]]) -> AttackCampaign:
        """Create attack campaign from clustered actions"""
        # Extract campaign details from actions
        techniques = []
        indicators = []
        
        for action in actions:
            # Extract techniques and indicators (simplified)
            techniques.append(action.get('name', ''))
            indicators.extend(action.get('indicators', []))
        
        # Calculate success rate and impact
        success_rates = [action.get('avg_success_rate_pct', 0) for action in actions]
        impact_scores = [action.get('financial_impact_usd', 0) for action in actions]
        
        avg_success_rate = np.mean(success_rates) if success_rates else 0.0
        avg_impact = np.mean(impact_scores) if impact_scores else 0.0
        
        campaign = AttackCampaign(
            campaign_id=f"CAMP_{hashlib.md5(cluster_id.encode()).hexdigest()[:8]}",
            name=f"Campaign {cluster_id}",
            actors=[],  # Would be filled from graph analysis
            start_date=datetime.now() - timedelta(days=30),  # Placeholder
            end_date=None,
            techniques=list(set(techniques)),
            indicators=list(set(indicators)),
            targets=[],  # Would be extracted from analysis
            success_rate=avg_success_rate / 100.0,
            impact_score=min(1.0, avg_impact / 1000000.0)  # Normalize to 0-1
        )
        
        return campaign
    
    def _cache_vulnerability_intelligence(self, vuln_intel: VulnerabilityIntelligence):
        """Cache vulnerability intelligence in local database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO vulnerability_intel
            (cve_id, severity, cvss_score, exploit_available, exploitation_likelihood, 
             published_date, data_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            vuln_intel.cve_id,
            vuln_intel.severity,
            vuln_intel.cvss_score,
            int(vuln_intel.exploit_available),
            vuln_intel.exploitation_likelihood,
            vuln_intel.published_date.isoformat(),
            json.dumps(asdict(vuln_intel), default=str)
        ))
        
        conn.commit()
        conn.close()
    
    def _cache_threat_actor(self, actor: ThreatActor):
        """Cache threat actor in local database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO threat_actors
            (actor_id, name, type, origin, sophistication, confidence, data_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            actor.actor_id,
            actor.name,
            actor.type,
            actor.origin,
            actor.sophistication,
            actor.confidence,
            json.dumps(asdict(actor), default=str)
        ))
        
        conn.commit()
        conn.close()
    
    def _cache_attack_campaign(self, campaign: AttackCampaign):
        """Cache attack campaign in local database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO attack_campaigns
            (campaign_id, name, start_date, end_date, success_rate, impact_score, data_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            campaign.campaign_id,
            campaign.name,
            campaign.start_date.isoformat() if campaign.start_date else None,
            campaign.end_date.isoformat() if campaign.end_date else None,
            campaign.success_rate,
            campaign.impact_score,
            json.dumps(asdict(campaign), default=str)
        ))
        
        conn.commit()
        conn.close()
    
    def _get_threats_by_ids(self, threat_ids: List[str]) -> List[Dict[str, Any]]:
        """Get threat data by IDs from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        placeholders = ','.join(['?'] * len(threat_ids))
        cursor.execute(f'''
            SELECT data_json FROM threat_intelligence 
            WHERE threat_id IN ({placeholders})
        ''', threat_ids)
        
        threats = []
        for row in cursor.fetchall():
            threats.append(json.loads(row[0]))
        
        conn.close()
        return threats
    
    def _get_threat_by_id(self, threat_id: str) -> Optional[Dict[str, Any]]:
        """Get single threat by ID"""
        threats = self._get_threats_by_ids([threat_id])
        return threats[0] if threats else None
    
    def _find_related_threat_ids(self, threat_id: str, limit: int = 5) -> List[str]:
        """Find IDs of related threats"""
        # Placeholder - would implement graph-based similarity search
        return []
    
    def _generate_executive_summary(self, threat: Dict[str, Any]) -> str:
        """Generate executive summary for threat"""
        severity = threat.get('severity', 'Unknown')
        threat_type = threat.get('threat_type', 'Unknown')
        
        return f"A {severity.lower()} severity {threat_type.lower()} threat has been identified. " \
               f"This threat requires immediate attention and appropriate response measures."
    
    def _generate_recommendations(self, threat: Dict[str, Any]) -> List[str]:
        """Generate security recommendations for threat"""
        recommendations = []
        
        severity = threat.get('severity', 'Unknown')
        
        if severity in ['Critical', 'High']:
            recommendations.extend([
                "Implement immediate containment measures",
                "Deploy additional monitoring",
                "Review and update incident response procedures"
            ])
        
        recommendations.extend([
            "Monitor for indicators of compromise",
            "Update security signatures and rules",
            "Conduct threat hunting activities",
            "Review security controls effectiveness"
        ])
        
        return recommendations
    
    def close(self):
        """Close all connections"""
        if hasattr(self, 'neo4j_driver'):
            self.neo4j_driver.close()
        
        logger.info("Threat Intelligence Engine closed")


# Example usage and testing
if __name__ == "__main__":
    # Initialize the engine
    engine = ThreatIntelligenceEngine(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password",
        data_dir="../../../"
    )
    
    try:
        # Analyze CVE intelligence
        cve_intel = engine.analyze_cve_intelligence()
        print(f"Analyzed {len(cve_intel)} CVEs")
        
        # Profile threat actors
        actor_profiles = engine.profile_threat_actors()
        print(f"Profiled {len(actor_profiles)} threat actors")
        
        # Detect attack campaigns
        campaigns = engine.detect_attack_campaigns()
        print(f"Detected {len(campaigns)} attack campaigns")
        
        # Test IOC extraction
        test_text = "Malicious IP 192.168.1.100 contacted domain evil.com with hash a1b2c3d4e5f6"
        iocs = engine.extract_indicators(test_text)
        print(f"Extracted IOCs: {iocs}")
        
        # Test threat scoring
        test_threat = {
            'severity': 'High',
            'confidence': 0.8,
            'timestamp': datetime.now().isoformat(),
            'sophistication': 'High',
            'exploit_available': True
        }
        score = engine.calculate_threat_score(test_threat)
        print(f"Threat score: {score}")
        
    finally:
        engine.close()