"""
Tests for the Mergington High School API
Using AAA (Arrange-Act-Assert) testing pattern
"""
import pytest


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index.html"""
        # Arrange - No special setup needed

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestActivitiesGET:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        # Arrange - No special setup needed

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activities_have_required_fields(self, client):
        """Test that activities have all required fields"""
        # Arrange - No special setup needed

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity_info in data.items():
            assert "description" in activity_info
            assert "schedule" in activity_info
            assert "max_participants" in activity_info
            assert "participants" in activity_info

    def test_activities_count(self, client):
        """Test that we have the expected number of activities"""
        # Arrange - No special setup needed

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert len(data) == 9  # Based on the current activities in app.py


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client, sample_email):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert activity_name in data["message"]

    def test_signup_nonexistent_activity(self, client, sample_email):
        """Test signup for non-existent activity"""
        # Arrange
        nonexistent_activity = "Fake Club"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity.replace(' ', '%20')}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 404
        error_data = response.json()
        assert "Activity not found" in error_data["detail"]

    def test_signup_duplicate(self, client):
        """Test that duplicate signup is rejected"""
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup",
            params={"email": existing_email}
        )

        # Assert
        assert response.status_code == 400
        error_data = response.json()
        assert "already signed up" in error_data["detail"]

    def test_signup_activity_becomes_full(self, client):
        """Test signup when activity reaches max capacity"""
        # Arrange
        activity = "Basketball Team"  # max_participants: 15, currently 1 participant
        overflow_email = "overflow@mergington.edu"

        # Fill the activity to max capacity
        for i in range(14):  # Add 14 more to reach 15 total
            email = f"student{i}@mergington.edu"
            client.post(
                f"/activities/{activity.replace(' ', '%20')}/signup",
                params={"email": email}
            )

        # Act - Try to add one more (should fail)
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup",
            params={"email": overflow_email}
        )

        # Assert
        assert response.status_code == 400
        error_data = response.json()
        assert "Activity is full" in error_data["detail"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/unregister endpoint"""

    def test_unregister_successful(self, client):
        """Test successful unregister from an activity"""
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.delete(
            "/activities/unregister",
            params={"activity": activity_name, "email": existing_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert existing_email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_nonexistent_activity(self, client, sample_email):
        """Test unregister from non-existent activity"""
        # Arrange
        nonexistent_activity = "Fake Club"

        # Act
        response = client.delete(
            "/activities/unregister",
            params={"activity": nonexistent_activity, "email": sample_email}
        )

        # Assert
        assert response.status_code == 404
        error_data = response.json()
        assert "Activity not found" in error_data["detail"]

    def test_unregister_not_registered(self, client, sample_email):
        """Test unregister when student is not signed up"""
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            "/activities/unregister",
            params={"activity": activity_name, "email": sample_email}
        )

        # Assert
        assert response.status_code == 400
        error_data = response.json()
        assert "not signed up" in error_data["detail"]