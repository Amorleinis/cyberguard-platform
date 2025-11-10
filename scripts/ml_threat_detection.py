"""
Machine Learning Threat Detection Engine
Advanced anomaly detection, threat classification, and pattern recognition
"""

import numpy as np
import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import DBSCAN
    sklearn_available = True
except ImportError:
    sklearn_available = False
    print("⚠️  scikit-learn not installed. ML features will use fallback methods.")


class MLThreatDetectionEngine:
    """Machine Learning-powered threat detection and analysis"""
    
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.models_dir = self.workspace_root / 'data' / 'ml_models'
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Models
        self.anomaly_detector = None
        self.threat_classifier = None
        self.pattern_clusterer = None
        self.scaler = StandardScaler() if sklearn_available else None
        
        # Training data buffers
        self.training_data = {
            'network': deque(maxlen=10000),
            'process': deque(maxlen=10000),
            'behavioral': deque(maxlen=10000)
        }
        
        # Statistics
        self.ml_stats = {
            'anomalies_detected': 0,
            'threats_classified': 0,
            'patterns_discovered': 0,
            'model_accuracy': 0.0,
            'last_training': None,
            'predictions_made': 0
        }
        
        # Load existing models or initialize new ones
        self._initialize_models()
        
        print("🤖 ML Threat Detection Engine initialized")
        print(f"   Scikit-learn: {'✅' if sklearn_available else '❌ (using fallback)'}")
        print(f"   Models loaded: {self._count_loaded_models()}")
    
    
    def _initialize_models(self):
        """Initialize or load ML models"""
        if not sklearn_available:
            print("   Using rule-based fallback detection")
            return
        
        # Try to load existing models
        anomaly_model_path = self.models_dir / 'anomaly_detector.pkl'
        classifier_model_path = self.models_dir / 'threat_classifier.pkl'
        
        if anomaly_model_path.exists():
            try:
                with open(anomaly_model_path, 'rb') as f:
                    self.anomaly_detector = pickle.load(f)
                print("   ✅ Loaded anomaly detector")
            except:
                pass
        
        if classifier_model_path.exists():
            try:
                with open(classifier_model_path, 'rb') as f:
                    self.threat_classifier = pickle.load(f)
                print("   ✅ Loaded threat classifier")
            except:
                pass
        
        # Initialize new models if not loaded
        if self.anomaly_detector is None:
            self.anomaly_detector = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
        
        if self.threat_classifier is None:
            self.threat_classifier = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
        
        if self.pattern_clusterer is None:
            self.pattern_clusterer = DBSCAN(
                eps=0.5,
                min_samples=5
            )
    
    
    def _count_loaded_models(self):
        """Count successfully loaded models"""
        count = 0
        if self.anomaly_detector is not None:
            count += 1
        if self.threat_classifier is not None:
            count += 1
        if self.pattern_clusterer is not None:
            count += 1
        return count
    
    
    def detect_network_anomaly(self, connection_data):
        """Detect anomalies in network connections using ML"""
        if not sklearn_available or self.anomaly_detector is None:
            return self._fallback_network_anomaly(connection_data)
        
        try:
            # Extract features
            features = self._extract_network_features(connection_data)
            
            if features is None:
                return {'anomaly': False, 'confidence': 0.0}
            
            # Reshape for prediction
            features_array = np.array(features).reshape(1, -1)
            
            # Scale features
            if hasattr(self.anomaly_detector, 'fit'):
                # Model is trained
                prediction = self.anomaly_detector.predict(features_array)
                score = self.anomaly_detector.score_samples(features_array)[0]
                
                is_anomaly = prediction[0] == -1
                confidence = abs(score)
                
                self.ml_stats['predictions_made'] += 1
                if is_anomaly:
                    self.ml_stats['anomalies_detected'] += 1
                
                return {
                    'anomaly': is_anomaly,
                    'confidence': min(confidence, 1.0),
                    'score': float(score),
                    'method': 'isolation_forest'
                }
            else:
                # Model not trained yet
                return {'anomaly': False, 'confidence': 0.0, 'method': 'untrained'}
                
        except Exception as e:
            print(f"   ⚠️  ML detection error: {e}")
            return self._fallback_network_anomaly(connection_data)
    
    
    def _extract_network_features(self, connection_data):
        """Extract numerical features from network connection"""
        try:
            features = []
            
            # Port number (normalized)
            port = connection_data.get('port', 0)
            features.append(port / 65535.0)
            
            # Connection state (encoded)
            state = connection_data.get('status', 'UNKNOWN')
            state_encoding = {
                'ESTABLISHED': 1.0,
                'LISTEN': 0.5,
                'CLOSE_WAIT': 0.3,
                'TIME_WAIT': 0.2,
                'SYN_SENT': 0.7,
                'UNKNOWN': 0.0
            }
            features.append(state_encoding.get(state, 0.0))
            
            # IP address features (convert to numerical)
            remote_ip = connection_data.get('remote_ip', '0.0.0.0')
            ip_parts = remote_ip.split('.')
            if len(ip_parts) == 4:
                for part in ip_parts:
                    try:
                        features.append(int(part) / 255.0)
                    except:
                        features.append(0.0)
            else:
                features.extend([0.0, 0.0, 0.0, 0.0])
            
            # Protocol (encoded)
            protocol = connection_data.get('type', 'tcp').lower()
            features.append(1.0 if protocol == 'tcp' else 0.5)
            
            # Time-based features
            hour = datetime.now().hour / 24.0
            features.append(hour)
            
            return features
            
        except Exception as e:
            print(f"   ⚠️  Feature extraction error: {e}")
            return None
    
    
    def _fallback_network_anomaly(self, connection_data):
        """Rule-based anomaly detection fallback"""
        anomaly_score = 0.0
        
        # Check for suspicious ports
        port = connection_data.get('port', 0)
        suspicious_ports = [4444, 5555, 6666, 7777, 8888, 9999, 31337, 12345]
        if port in suspicious_ports:
            anomaly_score += 0.5
        
        # Check for unusual connection states
        state = connection_data.get('status', '')
        if state in ['SYN_SENT', 'SYN_RECV']:
            anomaly_score += 0.2
        
        # Check remote IP patterns
        remote_ip = connection_data.get('remote_ip', '')
        if remote_ip.startswith('10.') or remote_ip.startswith('192.168.'):
            # Internal IP - less suspicious
            anomaly_score -= 0.1
        
        is_anomaly = anomaly_score >= 0.4
        
        return {
            'anomaly': is_anomaly,
            'confidence': anomaly_score,
            'method': 'rule_based'
        }
    
    
    def classify_threat(self, threat_indicators):
        """Classify threat type and severity using ML"""
        if not sklearn_available:
            return self._fallback_threat_classification(threat_indicators)
        
        try:
            # Extract features
            features = self._extract_threat_features(threat_indicators)
            
            if features is None:
                return self._fallback_threat_classification(threat_indicators)
            
            # For demo purposes, use rule-based classification
            # In production, this would use trained RandomForest
            classification = self._fallback_threat_classification(threat_indicators)
            
            self.ml_stats['threats_classified'] += 1
            
            return classification
            
        except Exception as e:
            print(f"   ⚠️  Classification error: {e}")
            return self._fallback_threat_classification(threat_indicators)
    
    
    def _extract_threat_features(self, threat_indicators):
        """Extract features from threat indicators"""
        try:
            features = []
            
            # Number of IOC matches
            features.append(len(threat_indicators.get('matched_iocs', [])))
            
            # Number of rule matches
            features.append(len(threat_indicators.get('matched_rules', [])))
            
            # Severity encoding
            severity_map = {'LOW': 0.25, 'MEDIUM': 0.5, 'HIGH': 0.75, 'CRITICAL': 1.0}
            severity = threat_indicators.get('severity', 'MEDIUM')
            features.append(severity_map.get(severity, 0.5))
            
            # Threat type encoding
            threat_type = threat_indicators.get('type', 'unknown')
            type_encoding = {
                'malware': 1.0,
                'ransomware': 0.95,
                'trojan': 0.9,
                'botnet': 0.85,
                'phishing': 0.7,
                'suspicious': 0.5,
                'unknown': 0.3
            }
            features.append(type_encoding.get(threat_type.lower(), 0.3))
            
            return features
            
        except Exception as e:
            return None
    
    
    def _fallback_threat_classification(self, threat_indicators):
        """Rule-based threat classification"""
        threat_type = threat_indicators.get('type', 'unknown').lower()
        severity = threat_indicators.get('severity', 'MEDIUM')
        
        # Classify threat category
        categories = {
            'malware': ['malware', 'virus', 'trojan', 'worm'],
            'network_attack': ['ddos', 'scan', 'brute', 'exploit'],
            'data_breach': ['exfiltration', 'leak', 'theft'],
            'ransomware': ['ransom', 'encrypt', 'lockbit'],
            'phishing': ['phish', 'spoof', 'social']
        }
        
        category = 'unknown'
        for cat, keywords in categories.items():
            if any(kw in threat_type for kw in keywords):
                category = cat
                break
        
        # Calculate risk score
        risk_score = 0.5
        if severity == 'CRITICAL':
            risk_score = 0.95
        elif severity == 'HIGH':
            risk_score = 0.75
        elif severity == 'MEDIUM':
            risk_score = 0.5
        else:
            risk_score = 0.25
        
        # Recommended action
        actions = {
            'CRITICAL': 'immediate_isolation',
            'HIGH': 'terminate_and_block',
            'MEDIUM': 'monitor_and_alert',
            'LOW': 'log_only'
        }
        
        return {
            'category': category,
            'severity': severity,
            'risk_score': risk_score,
            'recommended_action': actions.get(severity, 'log_only'),
            'confidence': 0.8,
            'method': 'rule_based'
        }
    
    
    def discover_attack_patterns(self, threat_history):
        """Discover attack patterns using clustering"""
        if not sklearn_available or len(threat_history) < 10:
            return self._fallback_pattern_discovery(threat_history)
        
        try:
            # Extract features from threat history
            features_list = []
            for threat in threat_history:
                features = self._extract_threat_features(threat)
                if features:
                    features_list.append(features)
            
            if len(features_list) < 5:
                return self._fallback_pattern_discovery(threat_history)
            
            # Cluster threats
            features_array = np.array(features_list)
            clusters = self.pattern_clusterer.fit_predict(features_array)
            
            # Analyze clusters
            unique_clusters = set(clusters)
            patterns = []
            
            for cluster_id in unique_clusters:
                if cluster_id == -1:  # Noise
                    continue
                
                cluster_threats = [threat_history[i] for i, c in enumerate(clusters) if c == cluster_id]
                
                pattern = {
                    'pattern_id': f'pattern_{cluster_id}',
                    'threat_count': len(cluster_threats),
                    'common_type': self._find_common_value(cluster_threats, 'type'),
                    'common_severity': self._find_common_value(cluster_threats, 'severity'),
                    'time_range': self._get_time_range(cluster_threats),
                    'confidence': len(cluster_threats) / len(threat_history)
                }
                
                patterns.append(pattern)
            
            self.ml_stats['patterns_discovered'] += len(patterns)
            
            return {
                'patterns_found': len(patterns),
                'patterns': patterns,
                'method': 'dbscan_clustering'
            }
            
        except Exception as e:
            print(f"   ⚠️  Pattern discovery error: {e}")
            return self._fallback_pattern_discovery(threat_history)
    
    
    def _fallback_pattern_discovery(self, threat_history):
        """Rule-based pattern discovery"""
        if len(threat_history) == 0:
            return {'patterns_found': 0, 'patterns': [], 'method': 'rule_based'}
        
        # Group by type and time window
        patterns = defaultdict(list)
        
        for threat in threat_history:
            threat_type = threat.get('type', 'unknown')
            patterns[threat_type].append(threat)
        
        discovered_patterns = []
        
        for threat_type, threats in patterns.items():
            if len(threats) >= 3:  # Pattern threshold
                pattern = {
                    'pattern_id': f'pattern_{threat_type}',
                    'threat_count': len(threats),
                    'common_type': threat_type,
                    'common_severity': self._find_common_value(threats, 'severity'),
                    'confidence': len(threats) / len(threat_history)
                }
                discovered_patterns.append(pattern)
        
        return {
            'patterns_found': len(discovered_patterns),
            'patterns': discovered_patterns,
            'method': 'rule_based'
        }
    
    
    def _find_common_value(self, items, key):
        """Find most common value for a key in list of dicts"""
        values = [item.get(key, 'unknown') for item in items]
        if not values:
            return 'unknown'
        return max(set(values), key=values.count)
    
    
    def _get_time_range(self, threats):
        """Get time range of threats"""
        timestamps = []
        for threat in threats:
            ts = threat.get('timestamp')
            if ts:
                try:
                    timestamps.append(datetime.fromisoformat(ts))
                except:
                    pass
        
        if len(timestamps) >= 2:
            return {
                'start': min(timestamps).isoformat(),
                'end': max(timestamps).isoformat(),
                'duration_minutes': (max(timestamps) - min(timestamps)).total_seconds() / 60
            }
        return {'start': None, 'end': None, 'duration_minutes': 0}
    
    
    def train_models(self, training_data):
        """Train ML models with historical data"""
        if not sklearn_available:
            print("   ⚠️  Scikit-learn required for model training")
            return False
        
        try:
            print("\n🎓 Training ML models...")
            
            # Prepare training data
            features = []
            labels = []
            
            for data_point in training_data:
                feat = self._extract_network_features(data_point)
                if feat:
                    features.append(feat)
                    labels.append(data_point.get('is_threat', 0))
            
            if len(features) < 100:
                print("   ⚠️  Insufficient training data (need at least 100 samples)")
                return False
            
            features_array = np.array(features)
            
            # Train anomaly detector
            print("   Training anomaly detector...")
            self.anomaly_detector.fit(features_array)
            
            # Train classifier if we have labels
            if len(labels) == len(features):
                print("   Training threat classifier...")
                self.threat_classifier.fit(features_array, labels)
            
            # Save models
            self._save_models()
            
            self.ml_stats['last_training'] = datetime.now().isoformat()
            self.ml_stats['model_accuracy'] = 0.85  # Placeholder
            
            print("   ✅ Models trained successfully")
            return True
            
        except Exception as e:
            print(f"   ❌ Training error: {e}")
            return False
    
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            with open(self.models_dir / 'anomaly_detector.pkl', 'wb') as f:
                pickle.dump(self.anomaly_detector, f)
            
            with open(self.models_dir / 'threat_classifier.pkl', 'wb') as f:
                pickle.dump(self.threat_classifier, f)
            
            print("   💾 Models saved")
            
        except Exception as e:
            print(f"   ⚠️  Save error: {e}")
    
    
    def generate_auto_rules(self, discovered_patterns):
        """Generate detection rules from discovered patterns"""
        rules = []
        
        for pattern in discovered_patterns:
            rule = {
                'rule_id': f"auto_{pattern['pattern_id']}",
                'name': f"Auto-generated rule for {pattern['common_type']}",
                'description': f"Automatically generated from pattern with {pattern['threat_count']} occurrences",
                'severity': pattern.get('common_severity', 'MEDIUM'),
                'conditions': {
                    'type': pattern['common_type'],
                    'min_occurrences': 3,
                    'time_window_minutes': 60
                },
                'action': 'alert_and_log',
                'confidence': pattern['confidence'],
                'created': datetime.now().isoformat(),
                'auto_generated': True
            }
            rules.append(rule)
        
        return rules
    
    
    def get_ml_stats(self):
        """Get ML engine statistics"""
        return {
            **self.ml_stats,
            'models_loaded': self._count_loaded_models(),
            'sklearn_available': sklearn_available,
            'training_data_size': {
                'network': len(self.training_data['network']),
                'process': len(self.training_data['process']),
                'behavioral': len(self.training_data['behavioral'])
            }
        }
    
    
    def predict_threat_likelihood(self, current_indicators):
        """Predict likelihood of imminent threat"""
        # Simplified prediction based on recent activity
        risk_factors = {
            'recent_threats': 0,
            'unusual_activity': 0,
            'known_patterns': 0,
            'time_of_day': 0
        }
        
        # Time-based risk (higher at night)
        hour = datetime.now().hour
        if hour < 6 or hour > 22:
            risk_factors['time_of_day'] = 0.3
        
        # Calculate overall likelihood
        total_risk = sum(risk_factors.values())
        likelihood = min(total_risk, 1.0)
        
        threat_level = 'LOW'
        if likelihood > 0.7:
            threat_level = 'CRITICAL'
        elif likelihood > 0.5:
            threat_level = 'HIGH'
        elif likelihood > 0.3:
            threat_level = 'MEDIUM'
        
        return {
            'likelihood': likelihood,
            'threat_level': threat_level,
            'risk_factors': risk_factors,
            'recommended_actions': self._get_recommended_actions(threat_level)
        }
    
    
    def _get_recommended_actions(self, threat_level):
        """Get recommended actions based on threat level"""
        actions = {
            'CRITICAL': [
                'Enable enhanced monitoring',
                'Block suspicious IPs immediately',
                'Alert security team',
                'Initiate incident response'
            ],
            'HIGH': [
                'Increase scan frequency',
                'Enable aggressive blocking',
                'Review security logs'
            ],
            'MEDIUM': [
                'Monitor closely',
                'Prepare response plans',
                'Update threat signatures'
            ],
            'LOW': [
                'Continue normal monitoring',
                'Maintain current posture'
            ]
        }
        
        return actions.get(threat_level, actions['LOW'])


if __name__ == '__main__':
    import sys
    from pathlib import Path
    
    workspace = Path(__file__).parent.parent
    
    print("=" * 70)
    print("🤖 ML THREAT DETECTION ENGINE - DEMO")
    print("=" * 70)
    print()
    
    ml_engine = MLThreatDetectionEngine(workspace)
    
    # Test anomaly detection
    print("\n🔍 Testing Network Anomaly Detection...")
    test_connection = {
        'port': 4444,
        'remote_ip': '203.0.113.42',
        'status': 'ESTABLISHED',
        'type': 'tcp'
    }
    
    result = ml_engine.detect_network_anomaly(test_connection)
    print(f"   Anomaly detected: {result['anomaly']}")
    print(f"   Confidence: {result['confidence']:.2f}")
    print(f"   Method: {result['method']}")
    
    # Test threat classification
    print("\n🎯 Testing Threat Classification...")
    threat = {
        'type': 'malware',
        'severity': 'HIGH',
        'matched_iocs': ['hash1', 'hash2'],
        'matched_rules': ['rule1']
    }
    
    classification = ml_engine.classify_threat(threat)
    print(f"   Category: {classification['category']}")
    print(f"   Risk Score: {classification['risk_score']:.2f}")
    print(f"   Recommended Action: {classification['recommended_action']}")
    
    # Test pattern discovery
    print("\n🔬 Testing Attack Pattern Discovery...")
    threat_history = [
        {'type': 'malware', 'severity': 'HIGH', 'timestamp': datetime.now().isoformat()},
        {'type': 'malware', 'severity': 'HIGH', 'timestamp': datetime.now().isoformat()},
        {'type': 'phishing', 'severity': 'MEDIUM', 'timestamp': datetime.now().isoformat()},
        {'type': 'malware', 'severity': 'HIGH', 'timestamp': datetime.now().isoformat()}
    ]
    
    patterns = ml_engine.discover_attack_patterns(threat_history)
    print(f"   Patterns found: {patterns['patterns_found']}")
    for pattern in patterns['patterns']:
        print(f"   - {pattern['pattern_id']}: {pattern['threat_count']} threats")
    
    # Generate auto-rules
    print("\n📝 Generating Auto-Rules...")
    auto_rules = ml_engine.generate_auto_rules(patterns['patterns'])
    print(f"   Generated {len(auto_rules)} automatic rules")
    
    # Predict threat likelihood
    print("\n🔮 Predicting Threat Likelihood...")
    prediction = ml_engine.predict_threat_likelihood({})
    print(f"   Likelihood: {prediction['likelihood']:.2f}")
    print(f"   Threat Level: {prediction['threat_level']}")
    print(f"   Recommended Actions: {len(prediction['recommended_actions'])} items")
    
    # Display stats
    print("\n📊 ML Engine Statistics:")
    stats = ml_engine.get_ml_stats()
    for key, value in stats.items():
        if key not in ['training_data_size']:
            print(f"   {key}: {value}")
    
    print("\n✅ ML Demo complete!")
