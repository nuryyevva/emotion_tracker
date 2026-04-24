import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from .v1.auth import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)


class TestAuth:
    """Тесты для авторизации"""

    def test_register_success(self):
        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "StrongPass123!",
                "name": "New User"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User registered successfully"
        assert "user_id" in data

    def test_register_duplicate_email(self):
        # Первая регистрация
        client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "StrongPass123!",
                "name": "First User"
            }
        )
        # Вторая регистрация с тем же email
        response = client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "StrongPass123!",
                "name": "Second User"
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.text

    def test_login_success(self):
        # Сначала регистрируем пользователя
        client.post(
            "/auth/register",
            json={
                "email": "login@example.com",
                "password": "StrongPass123!",
                "name": "Login User"
            }
        )

        response = client.post(
            "/auth/login",
            json={
                "email": "login@example.com",
                "password": "StrongPass123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        # Регистрируем пользователя
        client.post(
            "/auth/register",
            json={
                "email": "wrongpass@example.com",
                "password": "CorrectPass123!",
                "name": "Wrong Pass User"
            }
        )

        response = client.post(
            "/auth/login",
            json={
                "email": "wrongpass@example.com",
                "password": "WrongPass123!"
            }
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.text

    def test_login_nonexistent_email(self):
        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "AnyPass123!"
            }
        )
        assert response.status_code == 401

    def test_refresh_token_success(self):
        # Регистрируем и логинимся
        client.post(
            "/auth/register",
            json={
                "email": "refresh@example.com",
                "password": "StrongPass123!",
                "name": "Refresh User"
            }
        )

        login_response = client.post(
            "/auth/login",
            json={
                "email": "refresh@example.com",
                "password": "StrongPass123!"
            }
        )

        refresh_token = login_response.json()["refresh_token"]

        # Обновляем токен
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self):
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "invalid-token-123"}
        )
        assert response.status_code == 401

    def test_logout_success(self):
        # Регистрируем и логинимся
        client.post(
            "/auth/register",
            json={
                "email": "logout@example.com",
                "password": "StrongPass123!",
                "name": "Logout User"
            }
        )

        login_response = client.post(
            "/auth/login",
            json={
                "email": "logout@example.com",
                "password": "StrongPass123!"
            }
        )

        refresh_token = login_response.json()["refresh_token"]

        # Выход
        response = client.post(
            "/auth/logout",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

        # Попытка использовать тот же refresh-токен после выхода
        refresh_response = client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 401


def test_auth_service_methods():
    """Тесты для вспомогательных методов"""
    from .v1.auth import hash_password, verify_password, generate_access_token, generate_refresh_token

    # Тест хеширования
    password = "MySecret123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPass", hashed) is False

    # Тест генерации токенов
    access_token = generate_access_token()
    refresh_token = generate_refresh_token()
    assert len(access_token) > 0
    assert len(refresh_token) > 0
    assert access_token != refresh_token