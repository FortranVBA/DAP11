import time
from locust import HttpUser, task, between

class UserLogin(HttpUser):
    wait_time = between(1, 2.5)

    @task
    def login_book(self):
        self.client.get('/')
        self.client.post('/showSummary', data={'email': 'john@simplylift.co'})
        self.client.get('/book/Fall%20Classic/Simply%20Lift')
        self.client.post('/purchasePlaces', 
            data={'club': "Simply Lift", 'competition': "Fall Classic", 'places': 5})
        self.client.get('/logout')

    @task(3)
    def login_logout(self):
        self.client.get('/')
        self.client.post('/showSummary', data={'email': 'john@simplylift.co'})
        self.client.get('/logout')
        