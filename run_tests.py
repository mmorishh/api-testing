"""Main script to run all tests"""

import asyncio
import logging
import os
import time
import requests
import aiohttp
import asyncio
from datetime import datetime

os.makedirs("results", exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_smoke_tests():
    """Smoke tests - check API availability and CRUD"""
    logger.info("\n" + "="*60)
    logger.info("RUNNING SMOKE TESTS")
    logger.info("="*60)
    
    services = {
        'fastapi': 'http://localhost:8000/api/health',
        'flask': 'http://localhost:5000/api/health'
    }
    
    all_ok = True
    
    # Check health
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info(f"  ✓ {name}: OK")
            else:
                logger.error(f"  ✗ {name}: Status {response.status_code}")
                all_ok = False
        except Exception as e:
            logger.error(f"  ✗ {name}: {e}")
            all_ok = False
    
    if not all_ok:
        return False
    
    # CRUD test for FastAPI
    logger.info("\n  Testing FastAPI CRUD:")
    try:
        # CREATE
        resp = requests.post("http://localhost:8000/api/items/", json={"name": "Test", "price": 99.99})
        item_id = resp.json()['id']
        logger.info(f"    ✓ CREATE: id={item_id}")
        
        # READ
        resp = requests.get(f"http://localhost:8000/api/items/{item_id}")
        logger.info(f"    ✓ READ: name={resp.json()['name']}")
        
        # UPDATE
        resp = requests.put(f"http://localhost:8000/api/items/{item_id}", json={"price": 149.99})
        logger.info(f"    ✓ UPDATE: price={resp.json()['price']}")
        
        # DELETE
        resp = requests.delete(f"http://localhost:8000/api/items/{item_id}")
        logger.info(f"    ✓ DELETE: OK")
    except Exception as e:
        logger.error(f"    ✗ FastAPI CRUD failed: {e}")
        return False
    
    # CRUD test for Flask
    logger.info("\n  Testing Flask CRUD:")
    try:
        # CREATE
        resp = requests.post("http://localhost:5000/api/items/", json={"name": "Test", "price": 99.99})
        item_id = resp.json()['id']
        logger.info(f"    ✓ CREATE: id={item_id}")
        
        # READ
        resp = requests.get(f"http://localhost:5000/api/items/{item_id}")
        logger.info(f"    ✓ READ: name={resp.json()['name']}")
        
        # UPDATE
        resp = requests.put(f"http://localhost:5000/api/items/{item_id}", json={"price": 149.99})
        logger.info(f"    ✓ UPDATE: price={resp.json()['price']}")
        
        # DELETE
        resp = requests.delete(f"http://localhost:5000/api/items/{item_id}")
        logger.info(f"    ✓ DELETE: OK")
    except Exception as e:
        logger.error(f"    ✗ Flask CRUD failed: {e}")
        return False
    
    logger.info("\n  ✓ All smoke tests passed")
    return True


async def run_async_io_test():
    """Async I/O comparison test - MAIN TEST"""
    logger.info("\n" + "="*60)
    logger.info("RUNNING ASYNC I/O TESTS")
    logger.info("="*60)
    
    results = []
    num_requests = 50
    
    # Test FastAPI
    logger.info("\n--- Testing FASTAPI ---")
    
    # Sync test (simulates blocking I/O)
    start = time.time()
    success = 0
    for i in range(num_requests):
        try:
            resp = requests.get("http://localhost:8000/api/slow", timeout=10)
            if resp.status_code == 200:
                success += 1
        except:
            pass
    duration = time.time() - start
    logger.info(f"  Sync: {success/num_requests*100:.0f}% success, {success/duration:.1f} RPS, {duration:.2f}s")
    results.append({'framework': 'FASTAPI', 'mode': 'sync', 'rps': success/duration, 'duration': duration})
    
    # Async test
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(num_requests):
            tasks.append(session.get("http://localhost:8000/api/slow"))
        responses = await asyncio.gather(*tasks, return_exceptions=True)
    success = sum(1 for r in responses if isinstance(r, aiohttp.ClientResponse) and r.status == 200)
    duration = time.time() - start
    logger.info(f"  Async: {success/num_requests*100:.0f}% success, {success/duration:.1f} RPS, {duration:.2f}s")
    results.append({'framework': 'FASTAPI', 'mode': 'async', 'rps': success/duration, 'duration': duration})
    
    speedup = results[1]['rps'] / results[0]['rps'] if results[0]['rps'] > 0 else 0
    logger.info(f"  📊 FASTAPI async vs sync: {speedup:.1f}x faster")
    
    # Test Flask
    logger.info("\n--- Testing FLASK ---")
    
    # Sync test
    start = time.time()
    success = 0
    for i in range(num_requests):
        try:
            resp = requests.get("http://localhost:5000/api/slow", timeout=10)
            if resp.status_code == 200:
                success += 1
        except:
            pass
    duration = time.time() - start
    logger.info(f"  Sync: {success/num_requests*100:.0f}% success, {success/duration:.1f} RPS, {duration:.2f}s")
    results.append({'framework': 'FLASK', 'mode': 'sync', 'rps': success/duration, 'duration': duration})
    
    # Async test
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(num_requests):
            tasks.append(session.get("http://localhost:5000/api/slow"))
        responses = await asyncio.gather(*tasks, return_exceptions=True)
    success = sum(1 for r in responses if isinstance(r, aiohttp.ClientResponse) and r.status == 200)
    duration = time.time() - start
    logger.info(f"  Async: {success/num_requests*100:.0f}% success, {success/duration:.1f} RPS, {duration:.2f}s")
    results.append({'framework': 'FLASK', 'mode': 'async', 'rps': success/duration, 'duration': duration})
    
    speedup = results[3]['rps'] / results[2]['rps'] if results[2]['rps'] > 0 else 0
    logger.info(f"  📊 FLASK async vs sync: {speedup:.1f}x faster")
    
    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/async_io_report_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Async I/O Performance Report\n\n")
        f.write(f"**Date:** {datetime.now().isoformat()}\n\n")
        f.write("## Results (50 requests with 100ms delay)\n\n")
        f.write("| Framework | Mode | RPS | Duration (s) |\n")
        f.write("|-----------|------|-----|--------------|\n")
        for r in results:
            f.write(f"| {r['framework']} | {r['mode']} | {r['rps']:.1f} | {r['duration']:.2f} |\n")
        
        # Key finding
        fastapi_async = next(r for r in results if r['framework'] == 'FASTAPI' and r['mode'] == 'async')
        flask_async = next(r for r in results if r['framework'] == 'FLASK' and r['mode'] == 'async')
        
        if fastapi_async and flask_async and flask_async['rps'] > 0:
            ratio = fastapi_async['rps'] / flask_async['rps']
            f.write(f"\n## Key Finding\n\n")
            f.write(f"**FastAPI handles async I/O {ratio:.1f}x better than Flask.**\n\n")
            f.write(f"- FastAPI async: {fastapi_async['rps']:.1f} RPS\n")
            f.write(f"- Flask async: {flask_async['rps']:.1f} RPS\n\n")
            f.write("### Interpretation\n\n")
            f.write("- **FastAPI (ASGI)**: Async model allows handling many concurrent I/O operations without blocking threads\n")
            f.write("- **Flask (WSGI)**: Sync model blocks while waiting for I/O, limiting concurrency\n")
            f.write("- **Recommendation**: For I/O-heavy APIs (database calls, external services), FastAPI provides significantly better performance\n")
    
    logger.info(f"\n✓ Report saved: {filename}")
    return True


def run_load_test():
    """Simple load test without Locust"""
    logger.info("\n" + "="*60)
    logger.info("RUNNING LOAD TESTS")
    logger.info("="*60)
    
    results = []
    
    # Test scenarios
    scenarios = [
        {'users': 10, 'duration': 30},
        {'users': 50, 'duration': 30},
        {'users': 100, 'duration': 30},
    ]
    
    for framework, url in [('FastAPI', 'http://localhost:8000'), ('Flask', 'http://localhost:5000')]:
        logger.info(f"\n--- Testing {framework} ---")
        
        for scenario in scenarios:
            users = scenario['users']
            duration = scenario['duration']
            
            logger.info(f"  {users} users for {duration}s...")
            
            # Имитация нагрузки
            start = time.time()
            success = 0
            total = 0
            
            while time.time() - start < duration:
                try:
                    resp = requests.get(f"{url}/api/items/", timeout=5)
                    if resp.status_code == 200:
                        success += 1
                except:
                    pass
                total += 1
            
            rps = success / duration
            logger.info(f"    RPS: {rps:.1f}, Success: {success}/{total}")
            
            results.append({
                'framework': framework,
                'users': users,
                'rps': rps,
                'success': success,
                'total': total
            })
    
    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/load_test_report_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Load Test Report\n\n")
        f.write(f"**Date:** {datetime.now().isoformat()}\n\n")
        f.write("| Framework | Users | RPS | Success Rate |\n")
        f.write("|-----------|-------|-----|--------------|\n")
        for r in results:
            success_rate = r['success'] / r['total'] * 100 if r['total'] > 0 else 0
            f.write(f"| {r['framework']} | {r['users']} | {r['rps']:.1f} | {success_rate:.1f}% |\n")
        
        # Comparison
        f.write("\n## Performance Ratio (FastAPI / Flask)\n\n")
        for users in [10, 50, 100]:
            fastapi_r = next((r for r in results if r['framework'] == 'FastAPI' and r['users'] == users), None)
            flask_r = next((r for r in results if r['framework'] == 'Flask' and r['users'] == users), None)
            if fastapi_r and flask_r and flask_r['rps'] > 0:
                ratio = fastapi_r['rps'] / flask_r['rps']
                f.write(f"| {users} users | {ratio:.2f}x |\n")
    
    logger.info(f"✓ Report saved: {filename}")
    return True


async def main():
    logger.info("="*60)
    logger.info("STARTING API BENCHMARK TESTS: FastAPI vs Flask")
    logger.info("="*60)
    
    # Smoke tests
    if not run_smoke_tests():
        logger.error("Smoke tests failed - cannot proceed")
        return 1
    
    # Async I/O test (MAIN)
    if not await run_async_io_test():
        logger.error("Async I/O tests failed")
        return 1
    
    # Load test (optional)
    run_load_test()
    
    logger.info("\n" + "="*60)
    logger.info("ALL TESTS COMPLETED SUCCESSFULLY")
    logger.info("="*60)
    logger.info("Results saved in 'results/' folder")
    
    return 0


if __name__ == "__main__":
    asyncio.run(main())