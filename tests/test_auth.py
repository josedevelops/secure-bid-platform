# test_auth.py — tests for signup and login endpoints
# we test the happy path and the important failure cases
# every test gets a clean database via the rollback fixture in conftest.py

import pytest


async def test_signup_success(client):
    # happy path — valid data creates a user and returns correct fields
    response = await client.post("/api/v1/auth/signup", json={
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "Testpass1!"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@test.com"
    assert data["member_type"] == "buyer"
    assert data["is_active"] is True
    # password must never appear in the response
    assert "password" not in data
    assert "hashed_password" not in data


async def test_signup_duplicate_username(client):
    # signing up twice with same username returns 400 with correct error code
    await client.post("/api/v1/auth/signup", json={
        "username": "dupeuser",
        "email": "dupeuser@test.com",
        "password": "Testpass1!"
    })
    response = await client.post("/api/v1/auth/signup", json={
        "username": "dupeuser",
        "email": "different@test.com",
        "password": "Testpass1!"
    })
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "DUPLICATE_RESOURCE"


async def test_signup_duplicate_email(client):
    # signing up twice with same email returns 400 with correct error code
    await client.post("/api/v1/auth/signup", json={
        "username": "user1",
        "email": "shared@test.com",
        "password": "Testpass1!"
    })
    response = await client.post("/api/v1/auth/signup", json={
        "username": "user2",
        "email": "shared@test.com",
        "password": "Testpass1!"
    })
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "DUPLICATE_RESOURCE"


async def test_signup_invalid_body(client):
    # missing required fields returns structured validation error
    response = await client.post("/api/v1/auth/signup", json={
        "username": "x"
    })
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "VALIDATION_ERROR"
    # errors is a list of field-level failures
    assert isinstance(response.json()["detail"]["errors"], list)


async def test_login_success(client):
    # happy path — valid credentials return a token
    await client.post("/api/v1/auth/signup", json={
        "username": "loginuser",
        "email": "loginuser@test.com",
        "password": "Testpass1!"
    })
    response = await client.post("/api/v1/auth/login", json={
        "username": "loginuser",
        "password": "Testpass1!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client):
    # wrong password returns 401 with INVALID_CREDENTIALS code
    await client.post("/api/v1/auth/signup", json={
        "username": "loginuser2",
        "email": "loginuser2@test.com",
        "password": "Testpass1!"
    })
    response = await client.post("/api/v1/auth/login", json={
        "username": "loginuser2",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"


async def test_login_nonexistent_user(client):
    # user that doesn't exist returns 401 — same error as wrong password
    # we never reveal whether the username exists
    response = await client.post("/api/v1/auth/login", json={
        "username": "ghostuser",
        "password": "Testpass1!"
    })
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"


async def test_protected_route_no_token(client):
    # hitting a protected route without a token returns structured 401
    response = await client.get("/api/v1/profile/me")
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "HTTP_ERROR"


async def test_protected_route_invalid_token(client):
    # hitting a protected route with a bad token returns 401
    response = await client.get(
        "/api/v1/profile/me",
        headers={"Authorization": "Bearer badtoken"}
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"
