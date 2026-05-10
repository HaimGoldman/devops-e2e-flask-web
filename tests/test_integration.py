import pytest
import requests
import time
import os

BASE_URL = os.getenv('APP_URL', 'http://flask-web-svc')

@pytest.fixture(scope="module")
def wait_for_app():
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

def test_index_returns_budget_dashboard(wait_for_app):
    response = requests.get(f'{BASE_URL}/')
    assert response.status_code == 200
    assert 'text/html' in response.headers['Content-Type']
    assert 'מנהל תקציב' in response.text

def test_add_and_stats(wait_for_app):
    requests.post(f'{BASE_URL}/transactions', data={
        'amount': '500', 'category': 'משכורת',
        'description': 'test', 'type': 'income'
    })
    requests.post(f'{BASE_URL}/transactions', data={
        'amount': '200', 'category': 'מזון',
        'description': 'test', 'type': 'expense'
    })

    response = requests.get(f'{BASE_URL}/stats')
    assert response.status_code == 200
    data = response.json()
    assert 'total_income' in data
    assert 'total_expenses' in data
    assert 'balance' in data
    assert data['total_income'] >= 500
    assert data['total_expenses'] >= 200
