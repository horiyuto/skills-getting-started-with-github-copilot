"""Tests for the Mergington High School API"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test"""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client):
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert len(data) >= 4

    def test_get_activities_contains_expected_fields(self, client):
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for name, details in data.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        # Arrange
        activity = "Chess Club"
        email = "test_student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in activities[activity]["participants"]

    def test_signup_duplicate_returns_400(self, client):
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # already registered

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity]["participants"]

    def test_unregister_not_registered_returns_400(self, client):
        # Arrange
        activity = "Chess Club"
        email = "nobody@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 400

    def test_unregister_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 404


class TestRoot:
    """Tests for the GET / endpoint"""

    def test_root_redirects(self, client):
        # Arrange & Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
