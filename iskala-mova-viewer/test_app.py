import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    resp = client.get('/api/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'healthy'

def test_get_latest_capsule(client):
    resp = client.get('/api/capsule/latest')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'mova' in data
    assert 'jalm' in data

def test_capsules_list(client):
    resp = client.get('/api/capsules')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)

def test_save_and_get_capsule(client, tmp_path):
    # Зберігаємо нову капсулу
    capsule = {
        "mova": {"short": "Тест", "full": "Тест повний"},
        "jalm": {"short": "{}", "full": "{}"},
        "code": {"short": "test()", "full": "def test():\n    pass"},
        "log": {"short": "[INFO] Тест", "full": "[INFO] Тест виконано"},
        "error": {"short": "Error", "full": "Test error"}
    }
    resp = client.post('/api/capsule', json=capsule)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success']
    filename = data['filename']

    # Отримуємо цю ж капсулу
    resp2 = client.get(f'/api/capsule/{filename}')
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert data2['mova']['short'] == "Тест"
    assert data2['jalm']['short'] == "{}"

def test_validation_invalid_data(client):
    # Тест з неповними даними
    invalid_capsule = {
        "mova": {"short": "Тест"}
    }
    resp = client.post('/api/capsule', json=invalid_capsule)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data

def test_validation_missing_layers(client):
    # Тест з відсутніми шарами
    incomplete_capsule = {
        "mova": {"short": "Тест", "full": "Тест"},
        "jalm": {"short": "{}", "full": "{}"}
    }
    resp = client.post('/api/capsule', json=incomplete_capsule)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data 