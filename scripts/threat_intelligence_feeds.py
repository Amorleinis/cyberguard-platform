"""
Real-Time Threat Intelligence Feed Integration
Fetches and integrates live threat intelligence from multiple sources
"""

import requests
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import threading
from collections import defaultdict

class ThreatIntelligenceFeedManager:
    """Manages real-time threat intelligence feeds"""
    
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.feeds_dir = self.workspace_root / 'data' / 'intelligence' / 'feeds'
        self.feeds_dir.mkdir(parents=True, exist_ok=True)
        
        self.active_feeds = []
        self.feed_stats = defaultdict(int)
        self.last_update = {}
        self.new_iocs = {
            'ips': set(),
            'domains': set(),
            'hashes': set(),
            'urls': set()
        }
        
        # Feed sources (using free/public sources)
        self.feed_sources = {
            'abuse_ch_malware': {
                'name': 'Abuse.ch Malware Hashes',
                'url': 'https://urlhaus.abuse.ch/downloads/csv_recent/',
                'type': 'hash',
                'enabled': True,
                'interval': 3600  # 1 hour
            },
            'emerging_threats': {
                'name': 'Emerging Threats IPs',
                'url': 'https://rules.emergingthreats.net/fwrules/emerging-Block-IPs.txt',
                'type': 'ip',
                'enabled': True,
                'interval': 3600
            },
            'malware_domains': {
                'name': 'Malware Domain List',
                'url': 'https://mirror1.malwaredomains.com/files/domains.txt',
                'type': 'domain',
                'enabled': True,
                'interval': 7200  # 2 hours
            },
            'phishing_database': {
                'name': 'PhishTank Database',
                'url': 'http://data.phishtank.com/data/online-valid.csv',
                'type': 'url',
                'enabled': True,
                'interval': 3600
            }
        }
        
        print("📡 Threat Intelligence Feed Manager initialized")
        print(f"   Active feeds: {len([f for f in self.feed_sources.values() if f['enabled']])}")
    
    
    def fetch_feed(self, feed_id):
        """Fetch threat intelligence from a specific feed"""
        feed = self.feed_sources.get(feed_id)
        if not feed or not feed['enabled']:
            return None
        
        try:
            print(f"📥 Fetching {feed['name']}...")
            
            # Check if we should update (based on interval)
            if feed_id in self.last_update:
                elapsed = (datetime.now() - self.last_update[feed_id]).total_seconds()
                if elapsed < feed['interval']:
                    print(f"   ⏭️  Skipping (last update {int(elapsed/60)} minutes ago)")
                    return None
            
            # Fetch with timeout
            response = requests.get(feed['url'], timeout=30, 
                                   headers={'User-Agent': 'CyberGuard-ThreatIntel/1.0'})
            
            if response.status_code == 200:
                # Parse based on feed type
                new_indicators = self._parse_feed_data(response.text, feed['type'])
                
                # Update statistics
                self.feed_stats[feed_id] += len(new_indicators)
                self.last_update[feed_id] = datetime.now()
                
                # Store new IOCs
                if feed['type'] == 'ip':
                    self.new_iocs['ips'].update(new_indicators)
                elif feed['type'] == 'domain':
                    self.new_iocs['domains'].update(new_indicators)
                elif feed['type'] == 'hash':
                    self.new_iocs['hashes'].update(new_indicators)
                elif feed['type'] == 'url':
                    self.new_iocs['urls'].update(new_indicators)
                
                # Save to disk
                self._save_feed_data(feed_id, new_indicators)
                
                print(f"   ✅ Fetched {len(new_indicators)} new indicators")
                return new_indicators
            else:
                print(f"   ❌ Failed: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"   ⏱️  Timeout fetching {feed['name']}")
            return None
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return None
    
    
    def _parse_feed_data(self, data, feed_type):
        """Parse feed data based on type"""
        indicators = set()
        
        try:
            lines = data.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#') or line.startswith(';'):
                    continue
                
                # Parse based on type
                if feed_type == 'ip':
                    # Extract IP addresses
                    parts = line.split()
                    if parts and self._is_valid_ip(parts[0]):
                        indicators.add(parts[0])
                
                elif feed_type == 'domain':
                    # Extract domains
                    parts = line.split()
                    domain = parts[1] if len(parts) > 1 else parts[0]
                    if self._is_valid_domain(domain):
                        indicators.add(domain.lower())
                
                elif feed_type == 'hash':
                    # Extract hashes (MD5, SHA256)
                    parts = line.split(',')
                    if len(parts) > 0:
                        hash_val = parts[0].strip('"').strip()
                        if len(hash_val) in [32, 64]:  # MD5 or SHA256
                            indicators.add(hash_val.lower())
                
                elif feed_type == 'url':
                    # Extract URLs
                    parts = line.split(',')
                    if len(parts) > 1:
                        url = parts[1].strip('"').strip()
                        if url.startswith('http'):
                            indicators.add(url)
        
        except Exception as e:
            print(f"   ⚠️  Parse error: {e}")
        
        return indicators
    
    
    def _is_valid_ip(self, ip):
        """Validate IP address"""
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except:
            return False
    
    
    def _is_valid_domain(self, domain):
        """Validate domain name"""
        if not domain or '.' not in domain:
            return False
        if any(c in domain for c in ['/', ' ', '\t', '<', '>']):
            return False
        return True
    
    
    def _save_feed_data(self, feed_id, indicators):
        """Save feed data to disk"""
        try:
            feed_file = self.feeds_dir / f"{feed_id}_{datetime.now().strftime('%Y%m%d')}.json"
            
            data = {
                'feed_id': feed_id,
                'timestamp': datetime.now().isoformat(),
                'count': len(indicators),
                'indicators': list(indicators)
            }
            
            with open(feed_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"   ⚠️  Save error: {e}")
    
    
    def fetch_all_feeds(self):
        """Fetch all enabled feeds"""
        print("\n📡 Fetching threat intelligence feeds...")
        
        total_new = 0
        for feed_id in self.feed_sources:
            indicators = self.fetch_feed(feed_id)
            if indicators:
                total_new += len(indicators)
        
        print(f"\n✅ Total new indicators: {total_new}")
        return total_new
    
    
    def get_feed_stats(self):
        """Get statistics about feeds"""
        return {
            'total_feeds': len(self.feed_sources),
            'active_feeds': len([f for f in self.feed_sources.values() if f['enabled']]),
            'total_indicators': sum(self.feed_stats.values()),
            'by_feed': dict(self.feed_stats),
            'last_updates': {k: v.isoformat() for k, v in self.last_update.items()},
            'new_iocs': {
                'ips': len(self.new_iocs['ips']),
                'domains': len(self.new_iocs['domains']),
                'hashes': len(self.new_iocs['hashes']),
                'urls': len(self.new_iocs['urls'])
            }
        }
    
    
    def get_new_iocs(self):
        """Get newly discovered IOCs"""
        return {
            'ips': list(self.new_iocs['ips']),
            'domains': list(self.new_iocs['domains']),
            'hashes': list(self.new_iocs['hashes']),
            'urls': list(self.new_iocs['urls'])
        }
    
    
    def start_auto_update(self, interval=3600):
        """Start automatic feed updates"""
        def update_loop():
            while True:
                try:
                    self.fetch_all_feeds()
                except Exception as e:
                    print(f"❌ Feed update error: {e}")
                time.sleep(interval)
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
        print(f"🔄 Auto-update started (every {interval/60:.0f} minutes)")


if __name__ == '__main__':
    # Demo
    import sys
    workspace = Path(__file__).parent.parent
    
    print("=" * 70)
    print("📡 THREAT INTELLIGENCE FEED MANAGER - DEMO")
    print("=" * 70)
    print()
    
    manager = ThreatIntelligenceFeedManager(workspace)
    
    print("\n🔍 Fetching feeds...")
    manager.fetch_all_feeds()
    
    print("\n📊 Feed Statistics:")
    stats = manager.get_feed_stats()
    print(f"   Total feeds: {stats['total_feeds']}")
    print(f"   Active feeds: {stats['active_feeds']}")
    print(f"   Total indicators: {stats['total_indicators']}")
    
    print("\n🆕 New IOCs discovered:")
    print(f"   IPs: {stats['new_iocs']['ips']}")
    print(f"   Domains: {stats['new_iocs']['domains']}")
    print(f"   Hashes: {stats['new_iocs']['hashes']}")
    print(f"   URLs: {stats['new_iocs']['urls']}")
    
    print("\n✅ Demo complete!")
