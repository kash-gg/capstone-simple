import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture
def client():
    with TestClient(create_app()) as client:
        yield client

def payload(**changes):
    return dict(payer="Asha", payee="Acme", amount="10.25", currency="INR", **{}) | changes

def test_health(client):
    for path in ("/", "/health"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
        assert response.json()['version']

def test_list(client):
    response = client.get('/api/payments')
    assert response.status_code == 200
    assert len(response.json()) == 3
    assert {p['status'] for p in response.json()} == {'COMPLETED', 'PENDING', 'FAILED'}

def test_get_existing_and_missing(client):
    assert client.get('/api/payments/1').json()['id'] == 1
    response = client.get('/api/payments/9999')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Payment not found'

def test_create_and_notify(client):
    response = client.post('/api/payments', json=payload())
    assert response.status_code == 201
    payment = response.json()
    assert payment['amount'] == '10.25'
    assert client.get(f"/api/payments/{payment['id']}").json() == payment
    assert client.get('/api/notifications').json()[0]['payment_id'] == payment['id']

@pytest.mark.parametrize('changes', [
    {'payer': ''}, {'payee': 'x' * 61}, {'amount': '0'}, {'currency': 'GBP', 'amount': '1.234'}
])
def test_invalid_payload(client, changes):
    assert client.post('/api/payments', json=payload(**changes)).status_code == 422

def test_notifications_newest_first(client):
    client.post('/api/payments', json=payload())
    client.post('/api/payments', json=payload())
    response = client.get('/api/notifications')
    assert response.status_code == 200
    notifications = response.json()
    assert len(notifications) == 5
    assert [n['id'] for n in notifications] == [5, 4, 3, 2, 1]
    assert [n['created_at'] for n in notifications] == sorted([n['created_at'] for n in notifications], reverse=True)
