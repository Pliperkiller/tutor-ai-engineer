"""
P1: os.environ["MODEL_REGISTRY_API_KEY"] will drop an error since this variable is not registered on the
P2: since the tests are dependent of the excecution order, if delete demoves the model 1 , the get model 1 test will fail
for this reason is important to set a fixture that refreshes the MODELS variable (or what ever is storing the models)
"""


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_not_found_model(client):
    response = client.get("/models/999")
    assert response.status_code == 404


def test_post_noheader(client):
    response = client.post(
        "/models", json={"name": "test-model", "provider": "tester", "max_tokens": 1234}
    )

    assert response.status_code == 401


def test_post_header(client):
    response = client.post(
        "/models",
        json={"name": "test-model", "provider": "tester", "max_tokens": 1234},
        headers={"X-API-Key": "dev-secret-key"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "test-model"


def test_delete_process(client):
    response1 = client.delete("/models/1", headers={"X-API-Key": "dev-secret-key"})
    assert response1.status_code == 204

    response2 = client.get("/models/1")
    assert response2.status_code == 404
