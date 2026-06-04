import copy

from fastapi.testclient import TestClient
from src.app import app, activities

BASE_ACTIVITIES = copy.deepcopy(activities)
client = TestClient(app)


def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(BASE_ACTIVITIES))


def setup_function(function):
    reset_activities()


def test_root_redirects_to_static_index():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_available_activities():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_adds_participant():
    # Arrange
    email = "newstudent@mergington.edu"
    url = "/activities/Chess%20Club/signup"
    params = {"email": email}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    email = "duplicate@mergington.edu"
    url = "/activities/Chess%20Club/signup"
    params = {"email": email}

    # Act
    first_response = client.post(url, params=params)
    second_response = client.post(url, params=params)

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up"


def test_signup_invalid_activity_returns_404():
    # Arrange
    url = "/activities/Nonexistent/signup"
    params = {"email": "someone@mergington.edu"}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
