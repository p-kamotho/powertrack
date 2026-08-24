import pytest

@pytest.mark.django_db
def test_api_requires_authentication(client):
    response = client.get("/api/meters/")
    assert response.status_code in (401, 403)
