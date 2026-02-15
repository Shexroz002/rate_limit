from locust import HttpUser, task, between
import random

class RateLimiterUser(HttpUser):
    wait_time = between(0.5, 2)
    host = "http://localhost:8000"

    @task
    def get_posts(self):
        self.client.get("/api/v1/posts")

    @task
    def get_users(self):
        user_id = str(random.randint(1, 1000))
        self.client.get("/api/v1/users", headers={"X-User-ID": user_id})

    @task
    def login(self):
        self.client.post("/api/v1/login")