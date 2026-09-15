from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


ORIGINAL_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(ORIGINAL_ACTIVITIES))
    yield
    app_module.activities.clear()
    app_module.activities.update(deepcopy(ORIGINAL_ACTIVITIES))


def test_successful_signup_adds_participant_to_activity():
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_400():
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"

    # Act
    first_signup = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    second_signup = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert first_signup.status_code == 200
    assert second_signup.status_code == 400
    assert "already signed up" in second_signup.json()["detail"]


def test_unregister_participant_removes_email_from_activity():
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    email = "remove-me@mergington.edu"
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_400():
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    email = "not-registered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]
