import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.get_db_connection')
def test_hello_world(mock_db, client):
    mock_conn = MagicMock()
    mock_db.return_value = mock_conn
    
    response = client.get('/')
    assert response.status_code == 200
    assert b"Hello World!" in response.data

@patch('app.get_db_connection')
def test_health_endpoint(mock_db, client):
    mock_conn = MagicMock()
    mock_db.return_value = mock_conn
    
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
    assert response.json['database'] == 'connected'

@patch('app.get_db_connection')
def test_stats_endpoint(mock_db, client):
    mock_count = 3
    
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [mock_count]
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn
    
    response = client.get('/stats')
    assert response.status_code == 200
    assert response.json['last_hour'] == mock_count
    assert response.json['last_day'] == mock_count
    assert response.json['last_week'] == mock_count
    assert response.json['last_month'] == mock_count
