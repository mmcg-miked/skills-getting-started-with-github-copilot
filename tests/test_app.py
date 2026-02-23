from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory store around each test (AAA pattern).

    Arrange: make a deep copy before the test runs.
    Act: let the test execute.
    Assert: after the test, put the original data back so other tests
    see a clean state.
    """
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    # Arrange: client already created
    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # spot-check a couple of known activity names
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_success():
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")
    # backend state changed
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    activity = "Chess Club"
    existing = activities[activity]["participants"][0]

    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": existing})

    # Assert
    assert resp.status_code == 400
    assert "already signed up" in resp.json().get("detail", "")


def test_remove_participant_success():
    activity = "Chess Club"
    participant = activities[activity]["participants"][0]

    # Act
    resp = client.delete(f"/activities/{activity}/signup", params={"email": participant})

    # Assert
    assert resp.status_code == 200
    assert participant not in activities[activity]["participants"]


def test_remove_participant_not_signed_up():
    activity = "Chess Club"
    bogus = "nobody@mergington.edu"

    # Act
    resp = client.delete(f"/activities/{activity}/signup", params={"email": bogus})

    # Assert
    assert resp.status_code == 404
    assert "not signed up" in resp.json().get("detail", "")
