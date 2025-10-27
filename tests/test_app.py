from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that root path redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Check that we have some activities
    assert len(data) > 0
    # Check structure of an activity
    for activity in data.values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

def test_signup_for_activity():
    """Test signing up for an activity"""
    # Get first available activity
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    
    # Test successful signup
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify participant was added
    activities = client.get("/activities").json()
    assert "test@mergington.edu" in activities[activity_name]["participants"]

def test_duplicate_signup():
    """Test that a student cannot sign up twice"""
    # Get first available activity
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    
    # First signup should succeed
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "duplicate@mergington.edu"}
    )
    assert response.status_code == 200
    
    # Second signup should fail
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "duplicate@mergington.edu"}
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post(
        "/activities/NonExistentActivity/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # Get first available activity
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    
    # First sign up a test participant
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "unregister@mergington.edu"}
    )
    
    # Test successful unregistration
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": "unregister@mergington.edu"}
    )
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert "unregister@mergington.edu" not in activities[activity_name]["participants"]

def test_unregister_not_registered():
    """Test unregistering a student who is not registered"""
    # Get first available activity
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": "notregistered@mergington.edu"}
    )
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]

def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    response = client.delete(
        "/activities/NonExistentActivity/unregister",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]