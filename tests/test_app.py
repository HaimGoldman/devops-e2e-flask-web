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
def test_index_returns_html(mock_db, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = [0]
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.get('/')
    assert response.status_code == 200
    assert b'text/html' in response.content_type.encode()
    assert 'מנהל תקציב'.encode('utf-8') in response.data

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
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [(100.0,), (50.0,)]
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.get('/stats')
    assert response.status_code == 200
    assert response.json['total_income'] == 100.0
    assert response.json['total_expenses'] == 50.0
    assert response.json['balance'] == 50.0

@patch('app.get_db_connection')
def test_add_transaction(mock_db, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.post('/transactions', data={
        'amount': '150.00',
        'category': 'משכורת',
        'description': 'משכורת חודשית',
        'type': 'income'
    })
    assert response.status_code in (200, 302)
    mock_cursor.execute.assert_called_once()

@patch('app.get_db_connection')
def test_delete_transaction(mock_db, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.post('/transactions/1/delete')
    assert response.status_code in (200, 302)
    mock_cursor.execute.assert_called_once()
