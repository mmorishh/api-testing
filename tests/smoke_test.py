"""Smoke tests - API availability"""

import requests


def test_services():
    """Check API health"""
    services = {
        'fastapi': 'http://localhost:8000/api/health',
        'flask': 'http://localhost:5000/api/health'
    }
    
    all_ok = True
    print("\n=== Smoke Tests ===")
    
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ {name}: OK")
            else:
                print(f"✗ {name}: Status {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"✗ {name}: {e}")
            all_ok = False
    
    return all_ok


def test_crud_cycle():
    """Test complete CRUD cycle"""
    print("\n=== CRUD Cycle Test ===")
    
    for name, url in [('fastapi', 'http://localhost:8000'), ('flask', 'http://localhost:5000')]:
        print(f"\nTesting {name}:")
        
        try:
            # CREATE
            resp = requests.post(f"{url}/api/items/", json={"name": "Test Item", "price": 99.99}, timeout=10)
            if resp.status_code != 201:
                print(f"  ✗ CREATE failed: {resp.status_code}")
                return False
            item_id = resp.json()['id']
            print(f"  ✓ CREATE: id={item_id}")
            
            # READ
            resp = requests.get(f"{url}/api/items/{item_id}", timeout=10)
            if resp.status_code != 200:
                print(f"  ✗ READ failed: {resp.status_code}")
                return False
            print(f"  ✓ READ: name={resp.json()['name']}")
            
            # UPDATE
            resp = requests.put(f"{url}/api/items/{item_id}", json={"price": 149.99}, timeout=10)
            if resp.status_code != 200:
                print(f"  ✗ UPDATE failed: {resp.status_code}")
                return False
            print(f"  ✓ UPDATE: price={resp.json()['price']}")
            
            # DELETE
            resp = requests.delete(f"{url}/api/items/{item_id}", timeout=10)
            if resp.status_code != 204:
                print(f"  ✗ DELETE failed: {resp.status_code}")
                return False
            print(f"  ✓ DELETE: OK")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    return True


if __name__ == "__main__":
    test_services()
    test_crud_cycle()