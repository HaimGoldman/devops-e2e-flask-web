import pytest
import requests
import time
import os

BASE_URL = os.getenv('APP_URL', 'http://flask-web-svc')

@pytest.fixture(scope="module")
def wait_for_app():
    """Wait for app to be ready before running tests"""
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f'{BASE_URL}/health', timeout=2)
            if response.status_code == 200:
                print("\nApp is ready")
                return
        except:
            print(f"Waiting for app... ({i+1}/{max_retries})")
            time.sleep(2)
    pytest.fail("App failed to start")

def test_health_endpoint(wait_for_app):
    response = requests.get(f'{BASE_URL}/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert data['database'] == 'connected'

def test_hello_endpoint(wait_for_app):
    response = requests.get(f'{BASE_URL}/')
    assert response.status_code == 200
    assert 'Hello World' in response.text

def test_stats_endpoint(wait_for_app):
    num_visits = 3
    
    for _ in range(num_visits):
        requests.get(f'{BASE_URL}/')
        time.sleep(0.5)
    
    response = requests.get(f'{BASE_URL}/stats')
    assert response.status_code == 200
    data = response.json()
    
    assert 'last_hour' in data
    assert 'last_day' in data
    assert 'last_week' in data
    assert 'last_month' in data
   
    assert data['last_hour'] >= num_visits
    assert data['last_day'] >= num_visits
    assert data['last_week'] >= num_visits
    assert data['last_month'] >= num_visits
