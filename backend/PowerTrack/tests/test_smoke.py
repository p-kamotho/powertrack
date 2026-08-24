import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_dashboard_requires_login(client):
    response = client.get(reverse("dashboard"))
    assert response.status_code in (301, 302)
