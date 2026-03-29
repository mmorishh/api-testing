"""Locust load testing scenarios"""

from locust import HttpUser, task, between
import random


class FastAPIUser(HttpUser):
    wait_time = between(0.5, 2)
    host = "http://localhost:8000"
    
    @task(3)
    def list_items(self):
        self.client.get("/api/items/")
    
    @task(2)
    def create_item(self):
        self.client.post("/api/items/", json={
            "name": f"Test {random.randint(1, 1000)}",
            "price": 99.99
        })
    
    @task(2)
    def get_item(self):
        self.client.get(f"/api/items/{random.randint(1, 100)}")
    
    @task(1)
    def health_check(self):
        self.client.get("/api/health")


class FlaskUser(HttpUser):
    wait_time = between(0.5, 2)
    host = "http://localhost:5000"
    
    @task(3)
    def list_items(self):
        self.client.get("/api/items/")
    
    @task(2)
    def create_item(self):
        self.client.post("/api/items/", json={
            "name": f"Test {random.randint(1, 1000)}",
            "price": 99.99
        })
    
    @task(2)
    def get_item(self):
        self.client.get(f"/api/items/{random.randint(1, 100)}")
    
    @task(1)
    def health_check(self):
        self.client.get("/api/health")