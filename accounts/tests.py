from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .utils import generate_reset_token, store_reset_token, verify_reset_token

User = get_user_model()


class UserRegistrationTestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.valid_payload = {
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "testpassword123",
            "password_confirm": "testpassword123",
        }

    def test_user_registration_success(self):
        response = self.client.post(self.register_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_user_registration_password_mismatch(self):
        payload = self.valid_payload.copy()
        payload["password_confirm"] = "differentpassword"
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_email(self):
        User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="password123",
        )
        response = self.client.post(self.register_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTestCase(APITestCase):
    def setUp(self):
        self.login_url = reverse("login")
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            full_name="Test User",
            password="testpassword123",
        )

    def test_user_login_success(self):
        payload = {"email": "test@example.com", "password": "testpassword123"}
        response = self.client.post(self.login_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)

    def test_user_login_invalid_credentials(self):
        payload = {"email": "test@example.com", "password": "wrongpassword"}
        response = self.client.post(self.login_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordResetTestCase(APITestCase):
    def setUp(self):
        self.forgot_password_url = reverse("forgot_password")
        self.reset_password_url = reverse("reset_password")
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            full_name="Test User",
            password="testpassword123",
        )

    def test_forgot_password_success(self):
        payload = {"email": "test@example.com"}
        response = self.client.post(self.forgot_password_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_password_success(self):
        token = generate_reset_token()
        store_reset_token("test@example.com", token)

        payload = {
            "token": token,
            "new_password": "newpassword123",
            "new_password_confirm": "newpassword123",
        }
        response = self.client.post(self.reset_password_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_password_invalid_token(self):
        payload = {
            "token": "invalid-token",
            "new_password": "newpassword123",
            "new_password_confirm": "newpassword123",
        }
        response = self.client.post(self.reset_password_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RedisUtilsTestCase(TestCase):
    def setUp(self):
        cache.clear()

    def test_store_and_verify_token(self):
        email = "test@example.com"
        token = generate_reset_token()

        store_reset_token(email, token, expires_in=60)

        self.assertTrue(verify_reset_token(email, token))
        self.assertFalse(verify_reset_token(email, "wrong-token"))
        self.assertFalse(verify_reset_token("wrong@example.com", token))

    def tearDown(self):
        cache.clear()
