"""Async I/O performance comparison test"""

import asyncio
import aiohttp
import time
import requests
from typing import Dict, List
from datetime import datetime


class AsyncIOTest:
    """
    Compare async (FastAPI) vs sync (Flask) I/O performance.
    This is the key test showing the main architectural difference.
    """
    
    def __init__(self):
        self.services = {
            'fastapi': 'http://localhost:8000',
            'flask': 'http://localhost:5000'
        }
        self.results = []
    
    def test_sync_io(self, framework: str, url: str, num_requests: int = 50) -> Dict:
        """Synchronous I/O requests - blocks while waiting"""
        slow_url = f"{url}/api/slow"
        
        start = time.time()
        success = 0
        errors = 0
        
        for i in range(num_requests):
            try:
                response = requests.get(slow_url, timeout=10)
                if response.status_code == 200:
                    success += 1
                else:
                    errors += 1
            except Exception:
                errors += 1
        
        duration = time.time() - start
        
        return {
            'framework': framework,
            'type': 'sync',
            'requests': num_requests,
            'success': success,
            'errors': errors,
            'duration': duration,
            'rps': success / duration if duration > 0 else 0,
            'description': 'Synchronous I/O (blocking)'
        }
    
    async def test_async_io(self, framework: str, url: str, num_requests: int = 50) -> Dict:
        """Asynchronous I/O requests - non-blocking"""
        slow_url = f"{url}/api/slow"
        
        async def make_request(session):
            try:
                async with session.get(slow_url) as response:
                    return response.status == 200
            except Exception:
                return False
        
        start = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = [make_request(session) for _ in range(num_requests)]
            results = await asyncio.gather(*tasks)
        
        duration = time.time() - start
        success = sum(results)
        errors = num_requests - success
        
        return {
            'framework': framework,
            'type': 'async',
            'requests': num_requests,
            'success': success,
            'errors': errors,
            'duration': duration,
            'rps': success / duration if duration > 0 else 0,
            'description': 'Asynchronous I/O (non-blocking)'
        }
    
    async def run_comparison(self, num_requests: int = 50) -> List[Dict]:
        """Run complete comparison for both frameworks"""
        self.results = []
        
        print("\n" + "="*60)
        print("ASYNC I/O PERFORMANCE COMPARISON")
        print("Testing behavior under I/O-bound operations")
        print("="*60)
        
        for name, url in self.services.items():
            print(f"\n--- Testing {name.upper()} ---")
            
            # Sync test
            print(f"  Running sync test ({num_requests} requests)...")
            sync_result = self.test_sync_io(name, url, num_requests)
            self.results.append(sync_result)
            print(f"    Sync: {sync_result['rps']:.1f} RPS, {sync_result['duration']:.2f}s")
            
            # Async test
            print(f"  Running async test ({num_requests} requests)...")
            async_result = await self.test_async_io(name, url, num_requests)
            self.results.append(async_result)
            print(f"    Async: {async_result['rps']:.1f} RPS, {async_result['duration']:.2f}s")
            
            # Speedup calculation
            if async_result['rps'] > 0 and sync_result['rps'] > 0:
                speedup = async_result['rps'] / sync_result['rps']
                print(f"\n  📊 {name.upper()} async vs sync: {speedup:.1f}x faster")
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate markdown report"""
        import os
        os.makedirs("results", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/async_io_report_{timestamp}.md"
        
        with open(filename, 'w') as f:
            f.write("# Async I/O Performance Report\n\n")
            f.write(f"**Date:** {datetime.now().isoformat()}\n\n")
            
            f.write("## Why This Test Matters\n\n")
            f.write("- **FastAPI**: Async model (ASGI) - non-blocking I/O\n")
            f.write("- **Flask**: Sync model (WSGI) - blocking I/O\n")
            f.write("- **Test**: 50 concurrent requests with 100ms artificial delay\n\n")
            
            f.write("## Results\n\n")
            f.write("| Framework | Mode | Requests | Duration (s) | RPS | Description |\n")
            f.write("|-----------|------|----------|--------------|-----|-------------|\n")
            
            for r in self.results:
                f.write(f"| {r['framework'].upper()} | {r['type']} | {r['requests']} | "
                       f"{r['duration']:.2f} | {r['rps']:.1f} | {r['description']} |\n")
            
            # Find results for comparison
            fastapi_async = next((r for r in self.results if r['framework'] == 'fastapi' and r['type'] == 'async'), None)
            flask_async = next((r for r in self.results if r['framework'] == 'flask' and r['type'] == 'async'), None)
            
            if fastapi_async and flask_async and flask_async['rps'] > 0:
                ratio = fastapi_async['rps'] / flask_async['rps']
                f.write(f"\n## Key Finding\n\n")
                f.write(f"**FastAPI handles concurrent I/O {ratio:.1f}x better than Flask.**\n\n")
                
                f.write("### Interpretation\n\n")
                f.write("- **FastAPI**: Async model allows handling many concurrent I/O operations without blocking threads\n")
                f.write("- **Flask**: Sync model blocks while waiting for I/O, limiting concurrency\n")
                f.write("- **Recommendation**: For I/O-heavy APIs (database calls, external services), FastAPI provides significantly better performance\n")
        
        return filename


async def main():
    """Run async I/O tests"""
    tester = AsyncIOTest()
    await tester.run_comparison(num_requests=50)
    report = tester.generate_report()
    
    print(f"\n✅ Report saved: {report}")
    
    # Summary table
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for r in tester.results:
        print(f"{r['framework'].upper()} ({r['type']}): {r['rps']:.1f} RPS")


if __name__ == "__main__":
    asyncio.run(main())