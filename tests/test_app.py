from urllib.parse import quote

from src.app import activities


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_available_activities(client):
    # Arrange
    expected_activity = "Chess Club"
    expected_fields = {
        "description",
        "schedule",
        "max_participants",
        "participants",
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    response_activities = response.json()
    assert expected_activity in response_activities
    assert set(response_activities[expected_activity]) == expected_fields


def test_signup_adds_student_to_activity(client):
    # Arrange
    activity_name = "Chess Club"
    activity_path = quote(activity_name)
    email = "new.student@mergington.edu"
    expected_message = f"Signed up {email} for {activity_name}"

    # Act
    response = client.post(
        f"/activities/{activity_path}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": expected_message}
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_student(client):
    # Arrange
    activity_name = "Chess Club"
    activity_path = quote(activity_name)
    email = "michael@mergington.edu"
    expected_detail = "Student already signed up for this activity"

    # Act
    response = client.post(
        f"/activities/{activity_path}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": expected_detail}
    assert activities[activity_name]["participants"].count(email) == 1


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"
    activity_path = quote(activity_name)
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_path}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_requires_email(client):
    # Arrange
    activity_path = quote("Chess Club")

    # Act
    response = client.post(f"/activities/{activity_path}/signup")

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "email"]


def test_unregister_removes_student_from_activity(client):
    # Arrange
    activity_name = "Chess Club"
    activity_path = quote(activity_name)
    email = "michael@mergington.edu"
    expected_message = f"Unregistered {email} from {activity_name}"

    # Act
    response = client.delete(
        f"/activities/{activity_path}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": expected_message}
    assert email not in activities[activity_name]["participants"]


def test_unregister_rejects_student_not_in_activity(client):
    # Arrange
    activity_name = "Chess Club"
    activity_path = quote(activity_name)
    email = "not.enrolled@mergington.edu"
    expected_detail = "Student is not signed up for this activity"

    # Act
    response = client.delete(
        f"/activities/{activity_path}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": expected_detail}


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"
    activity_path = quote(activity_name)
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_path}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_requires_email(client):
    # Arrange
    activity_path = quote("Chess Club")

    # Act
    response = client.delete(f"/activities/{activity_path}/unregister")

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "email"]