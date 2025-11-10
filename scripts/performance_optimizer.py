"""
Performance Optimization Layer
Multi-threading, caching, database backend, distributed scanning
"""

import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
import time
import pickle
from collections import defaultdict

try:
    import redis
    redis_available = True
except ImportError:
    redis_available = False


class PerformanceOptimizer:
    """Performance optimization and scaling layer"""
    
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.cache_dir = self.workspace_root / 'data' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Thread pool for concurrent operations
        self.thread_pool = ThreadPoolExecutor(max_workers=8)
        
        # In-memory cache
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'writes': 0
        }
        
        # Redis cache if available
        self.redis_client = None
        if redis_available:
            try:
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=0,
                    decode_responses=False
                )
                self.redis_client.ping()
                print("   ✅ Redis cache connected")
            except:
                print("   ⚠️  Redis not available, using memory cache")
        
        print("⚡ Performance Optimizer initialized")
        print(f"   Thread pool: {8} workers")
        print(f"   Cache: {'Redis' if self.redis_client else 'Memory'}")
    
    
    def parallel_scan(self, scan_targets, scan_function):
        """Execute scans in parallel using thread pool"""
        start_time = time.time()
        
        # Submit all scans to thread pool
        futures = []
        for target in scan_targets:
            future = self.thread_pool.submit(scan_function, target)
            futures.append(future)
        
        # Collect results
        results = []
        for future in futures:
            try:
                result = future.result(timeout=30)
                results.append(result)
            except Exception as e:
                print(f"   ⚠️  Scan failed: {e}")
        
        duration = time.time() - start_time
        
        return {
            'results': results,
            'duration': duration,
            'scans_completed': len(results),
            'scans_requested': len(scan_targets),
            'average_time': duration / max(len(results), 1)
        }
    
    
    def cache_get(self, key, ttl=300):
        """Get value from cache with TTL"""
        # Try Redis first
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    self.cache_stats['hits'] += 1
                    return pickle.loads(value)
                else:
                    self.cache_stats['misses'] += 1
                    return None
            except:
                pass
        
        # Fall back to memory cache
        if key in self.memory_cache:
            cached_item = self.memory_cache[key]
            if datetime.now().timestamp() - cached_item['timestamp'] < ttl:
                self.cache_stats['hits'] += 1
                return cached_item['value']
            else:
                # Expired
                del self.memory_cache[key]
        
        self.cache_stats['misses'] += 1
        return None
    
    
    def cache_set(self, key, value, ttl=300):
        """Set value in cache with TTL"""
        # Try Redis first
        if self.redis_client:
            try:
                self.redis_client.setex(
                    key,
                    ttl,
                    pickle.dumps(value)
                )
                self.cache_stats['writes'] += 1
                return True
            except:
                pass
        
        # Fall back to memory cache
        self.memory_cache[key] = {
            'value': value,
            'timestamp': datetime.now().timestamp()
        }
        self.cache_stats['writes'] += 1
        
        return True
    
    
    def batch_ioc_lookup(self, indicators, ioc_database):
        """Optimized batch IOC lookup with caching"""
        results = {
            'matches': [],
            'cached': 0,
            'lookup_time': 0
        }
        
        start_time = time.time()
        
        for indicator in indicators:
            cache_key = f"ioc:{indicator}"
            
            # Check cache first
            cached = self.cache_get(cache_key, ttl=3600)
            if cached is not None:
                if cached:  # If it's a match
                    results['matches'].append(indicator)
                results['cached'] += 1
                continue
            
            # Perform lookup
            is_match = indicator in ioc_database
            
            # Cache result
            self.cache_set(cache_key, is_match, ttl=3600)
            
            if is_match:
                results['matches'].append(indicator)
        
        results['lookup_time'] = time.time() - start_time
        
        return results
    
    
    def optimize_rule_matching(self, rules, data_points):
        """Optimized rule matching using parallel processing"""
        # Group rules by type for better performance
        rules_by_type = defaultdict(list)
        for rule in rules:
            rule_type = rule.get('type', 'generic')
            rules_by_type[rule_type].append(rule)
        
        matches = []
        
        # Match each data point against relevant rules
        for data in data_points:
            data_type = data.get('type', 'generic')
            relevant_rules = rules_by_type.get(data_type, [])
            
            for rule in relevant_rules:
                if self._quick_match(rule, data):
                    matches.append({
                        'rule': rule['name'],
                        'data': data,
                        'match_time': datetime.now().isoformat()
                    })
        
        return matches
    
    
    def _quick_match(self, rule, data):
        """Fast rule matching"""
        # Simplified matching logic
        if 'pattern' in rule:
            pattern = rule['pattern'].lower()
            data_str = str(data).lower()
            return pattern in data_str
        
        return False
    
    
    def preload_ioc_database(self, ioc_files):
        """Preload and cache IOC database for fast access"""
        print("\n⚡ Preloading IOC database...")
        
        ioc_sets = {
            'ips': set(),
            'domains': set(),
            'hashes': set(),
            'urls': set()
        }
        
        start_time = time.time()
        
        # Use thread pool to load files in parallel
        def load_file(filepath):
            loaded = set()
            try:
                with open(filepath, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            loaded.add(line)
            except:
                pass
            return loaded
        
        futures = []
        for ioc_file in ioc_files:
            future = self.thread_pool.submit(load_file, ioc_file)
            futures.append((ioc_file, future))
        
        # Collect results
        for ioc_file, future in futures:
            try:
                loaded = future.result(timeout=30)
                # Determine type from filename
                filename = Path(ioc_file).name.lower()
                if 'ip' in filename:
                    ioc_sets['ips'].update(loaded)
                elif 'domain' in filename:
                    ioc_sets['domains'].update(loaded)
                elif 'hash' in filename:
                    ioc_sets['hashes'].update(loaded)
                elif 'url' in filename:
                    ioc_sets['urls'].update(loaded)
            except:
                pass
        
        duration = time.time() - start_time
        total_iocs = sum(len(s) for s in ioc_sets.values())
        
        print(f"   ✅ Loaded {total_iocs:,} IOCs in {duration:.2f}s")
        print(f"   Speed: {total_iocs/duration:,.0f} IOCs/second")
        
        # Cache the sets
        for ioc_type, ioc_set in ioc_sets.items():
            self.cache_set(f"ioc_set:{ioc_type}", ioc_set, ttl=3600)
        
        return ioc_sets
    
    
    def distributed_scan(self, targets, scan_func, num_workers=4):
        """Distribute scans across multiple processes"""
        if len(targets) < num_workers:
            # Not worth distributing
            return [scan_func(t) for t in targets]
        
        # Split targets into chunks
        chunk_size = len(targets) // num_workers
        chunks = [targets[i:i+chunk_size] for i in range(0, len(targets), chunk_size)]
        
        # Use process pool for true parallelism
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(self._scan_chunk, chunk, scan_func) for chunk in chunks]
            
            all_results = []
            for future in futures:
                try:
                    results = future.result(timeout=60)
                    all_results.extend(results)
                except Exception as e:
                    print(f"   ⚠️  Process failed: {e}")
        
        return all_results
    
    
    def _scan_chunk(self, targets, scan_func):
        """Scan a chunk of targets"""
        return [scan_func(t) for t in targets]
    
    
    def get_performance_stats(self):
        """Get performance statistics"""
        return {
            'cache_stats': self.cache_stats,
            'cache_hit_rate': self.cache_stats['hits'] / max(self.cache_stats['hits'] + self.cache_stats['misses'], 1),
            'cache_type': 'redis' if self.redis_client else 'memory',
            'thread_pool_workers': 8,
            'memory_cache_size': len(self.memory_cache)
        }
    
    
    def cleanup(self):
        """Cleanup resources"""
        self.thread_pool.shutdown(wait=False)
        if self.redis_client:
            self.redis_client.close()


if __name__ == '__main__':
    import sys
    from pathlib import Path
    
    workspace = Path(__file__).parent.parent
    
    print("=" * 70)
    print("⚡ PERFORMANCE OPTIMIZER - DEMO")
    print("=" * 70)
    print()
    
    optimizer = PerformanceOptimizer(workspace)
    
    # Test parallel scanning
    print("\n🔄 Testing Parallel Scan...")
    def dummy_scan(target):
        time.sleep(0.1)  # Simulate work
        return {'target': target, 'result': 'clean'}
    
    targets = list(range(20))
    result = optimizer.parallel_scan(targets, dummy_scan)
    print(f"   Scanned {result['scans_completed']} targets in {result['duration']:.2f}s")
    print(f"   Average time per scan: {result['average_time']:.2f}s")
    print(f"   Speedup: {len(targets) * 0.1 / result['duration']:.1f}x")
    
    # Test caching
    print("\n💾 Testing Cache Performance...")
    test_data = {'threat': 'malware', 'severity': 'HIGH'}
    
    optimizer.cache_set('test_key', test_data, ttl=300)
    cached = optimizer.cache_get('test_key')
    print(f"   Cache write/read: {'✅' if cached == test_data else '❌'}")
    
    # Test batch IOC lookup
    print("\n🔍 Testing Batch IOC Lookup...")
    test_indicators = ['192.168.1.1', '10.0.0.1', '203.0.113.42'] * 100
    test_database = {'192.168.1.1', '203.0.113.42'}
    
    lookup_result = optimizer.batch_ioc_lookup(test_indicators, test_database)
    print(f"   Looked up {len(test_indicators)} indicators")
    print(f"   Matches: {len(lookup_result['matches'])}")
    print(f"   Cached: {lookup_result['cached']} ({lookup_result['cached']/len(test_indicators)*100:.1f}%)")
    print(f"   Lookup time: {lookup_result['lookup_time']:.4f}s")
    
    # Display stats
    print("\n📊 Performance Statistics:")
    stats = optimizer.get_performance_stats()
    print(f"   Cache hit rate: {stats['cache_hit_rate']*100:.1f}%")
    print(f"   Cache type: {stats['cache_type']}")
    print(f"   Thread pool workers: {stats['thread_pool_workers']}")
    print(f"   Memory cache size: {stats['memory_cache_size']}")
    
    optimizer.cleanup()
    
    print("\n✅ Performance Optimization Demo complete!")
