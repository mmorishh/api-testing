"""Load testing with Locust"""

import subprocess
import time
import requests
import logging
import os
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BenchmarkRunner:
    """Load testing with Locust"""
    
    def __init__(self):
        self.services = {
            'fastapi': {'url': 'http://localhost:8000/api/health', 'port': 8000, 'name': 'FastAPI'},
            'flask': {'url': 'http://localhost:5000/api/health', 'port': 5000, 'name': 'Flask'},
        }
        self.results = {}
        os.makedirs("results", exist_ok=True)
    
    def wait_for_services(self):
        """Wait for all services to be ready"""
        logger.info("Waiting for services...")
        for name, service in self.services.items():
            for i in range(30):
                try:
                    response = requests.get(service['url'], timeout=5)
                    if response.status_code == 200:
                        logger.info(f"{service['name']} ready")
                        break
                except:
                    pass
                time.sleep(2)
            else:
                logger.error(f"{service['name']} not ready")
                return False
        return True
    
    def run_load_test(self, framework, users, duration):
        """Run Locust load test and save CSV"""
        service = self.services[framework]
        host = f"http://localhost:{service['port']}"
        spawn_rate = max(users // 5, 1)
        
        cmd = [
            sys.executable, "-m", "locust", "-f", "locustfile.py",
            "--host", host,
            "--users", str(users),
            "--spawn-rate", str(spawn_rate),
            "--run-time", f"{duration}s",
            "--headless",
            "--csv", f"results/locust_{framework}_{users}"
        ]
        
        logger.info(f"Running: {service['name']} - {users} users for {duration}s")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 60)
            
            # Parse CSV file
            stats_file = f"results/locust_{framework}_{users}_stats.csv"
            
            if os.path.exists(stats_file):
                return self._parse_csv(stats_file, framework, users, service['name'])
            else:
                logger.error(f"CSV file not found: {stats_file}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"Test timeout for {service['name']}")
        except Exception as e:
            logger.error(f"Error: {e}")
        
        return None
    
    def _parse_csv(self, filename, framework, users, name):
        """Parse Locust CSV stats file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if len(lines) < 2:
                return None
            
            # Find aggregated row
            for line in lines[1:]:
                parts = line.strip().split(',')
                if len(parts) >= 8 and parts[0] == 'Aggregated':
                    return {
                        'framework': framework,
                        'name': name,
                        'users': users,
                        'scenario': self._get_scenario_name(users),
                        'rps': float(parts[7]) if parts[7] else 0,
                        'avg_latency': float(parts[4]) if parts[4] else 0,
                        'p95_latency': float(parts[9]) if len(parts) > 9 and parts[9] else 0,
                        'failures': int(parts[2]) if parts[2] else 0,
                        'total_requests': int(parts[1]) if parts[1] else 0,
                    }
            
            # If no aggregated, take last line
            if len(lines) > 1:
                parts = lines[-1].strip().split(',')
                if len(parts) >= 8:
                    return {
                        'framework': framework,
                        'name': name,
                        'users': users,
                        'scenario': self._get_scenario_name(users),
                        'rps': float(parts[7]) if parts[7] else 0,
                        'avg_latency': float(parts[4]) if parts[4] else 0,
                        'p95_latency': float(parts[9]) if len(parts) > 9 and parts[9] else 0,
                        'failures': int(parts[2]) if parts[2] else 0,
                        'total_requests': int(parts[1]) if parts[1] else 0,
                    }
            
        except Exception as e:
            logger.error(f"Parse error: {e}")
        
        return None
    
    def _get_scenario_name(self, users):
        if users <= 10:
            return "light"
        elif users <= 50:
            return "medium"
        else:
            return "heavy"
    
    def run_all(self):
        """Run all test scenarios"""
        scenarios = [
            {'users': 10, 'duration': 30, 'name': 'Light'},
            {'users': 50, 'duration': 60, 'name': 'Medium'},
            {'users': 100, 'duration': 90, 'name': 'Heavy'},
        ]
        
        for framework in self.services.keys():
            self.results[framework] = []
            for scenario in scenarios:
                logger.info(f"\n{'='*50}")
                logger.info(f"{scenario['name']} Load for {self.services[framework]['name']}")
                logger.info(f"{'='*50}")
                
                result = self.run_load_test(framework, scenario['users'], scenario['duration'])
                if result:
                    self.results[framework].append(result)
                    logger.info(f"  RPS: {result['rps']:.1f}")
                    logger.info(f"  Avg Latency: {result['avg_latency']:.1f}ms")
                    logger.info(f"  P95 Latency: {result['p95_latency']:.1f}ms")
                else:
                    logger.error(f"  Test failed")
                
                time.sleep(5)
    
    def generate_report(self):
        """Generate report from CSV data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/load_test_report_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Load Test Report: FastAPI vs Flask\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
            
            f.write("## Results\n\n")
            f.write("| Framework | Scenario | Users | RPS | Avg Latency (ms) | P95 Latency (ms) |\n")
            f.write("|-----------|----------|-------|-----|------------------|------------------|\n")
            
            for framework, results in self.results.items():
                for r in results:
                    f.write(f"| {r['name']} | {r['scenario']} | {r['users']} | "
                           f"{r['rps']:.1f} | {r['avg_latency']:.1f} | {r['p95_latency']:.1f} |\n")
        
        logger.info(f"Report saved: {filename}")
        return filename


def main():
    runner = BenchmarkRunner()
    if runner.wait_for_services():
        runner.run_all()
        report = runner.generate_report()
        logger.info(f"\n✅ Load tests complete! Report: {report}")
    else:
        logger.error("Services not ready")


if __name__ == "__main__":
    main()