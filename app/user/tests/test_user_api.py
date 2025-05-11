from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

user_create_url = reverse("user:create")
create_token_url = reverse("user:token")
me_url = reverse("user:me")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITest(TestCase):
    """USER API tests"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Tests if user creation is success on valid data"""
        payload = {
            "first_name": "first",
            "last_name": "last",
            "username": "testuser",
            "email": "admin@admin.com",
            "password": "testpass",
        }
        res = self.client.post(user_create_url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_with_email_exists(self):
        """Tests if a user with same email exists"""
        payload = {
            "first_name": "first",
            "last_name": "last",
            "username": "testuser",
            "email": "admin@admin.com",
            "password": "testpass",
        }
        create_user(**payload)
        res = self.client.post(user_create_url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test if password is more than 6 characters"""
        payload = {
            "first_name": "first",
            "last_name": "last",
            "username": "testuser",
            "email": "admin@admin.com",
            "password": "pas",
        }
        res = self.client.post(user_create_url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = (
            get_user_model().objects.filter(email=payload["email"]).exists()
        )  # noqa
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generate token for a valid user"""
        user_details = {
            "first_name": "first",
            "last_name": "last",
            "username": "testuser",
            "email": "admin@admin.com",
            "password": "testpass",
        }
        create_user(**user_details)
        payload = {
            "email": "admin@admin.com",
            "password": "testpass",
        }
        res = self.client.post(create_token_url, payload)
        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test create token when bad credentials are provided"""
        user_details = {
            "first_name": "first",
            "last_name": "last",
            "username": "testuser",
            "email": "admin@admin.com",
            "password": "testpass",
        }
        create_user(**user_details)
        payload = {
            "email": "admin@admin.com",
            "password": "badpass",
        }
        res = self.client.post(create_token_url, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_pawssword_provided(self):
        """Test create token when blank pass is provided"""
        user_details = {
            "first_name": "first",
            "last_name": "last",
            "username": "testuser",
            "email": "admin@admin.com",
            "password": "testpass",
        }
        create_user(**user_details)
        payload = {
            "email": "admin@admin.com",
            "password": "",
        }
        res = self.client.post(create_token_url, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        res = self.client.get(me_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """Test API request that requires authentication"""

    def setUp(self):
        """Setup authentication for test cases"""
        user_details = {
            "first_name": "first",
            "last_name": "last",
            "username": "testuser",
            "email": "admin@admin.com",
            "password": "testpass",
        }
        self.client = APIClient()
        self.user = create_user(**user_details)
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in users"""
        res = self.client.get(me_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            {
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "username": self.user.username,
                "email": self.user.email,
            },
        )

    def test_post_not_allowed(self):
        """Test POST is not allowed in me Endpoints"""

        res = self.client.post(me_url, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profiles for authorized users"""
        user_details = {
            "first_name": "updated",
            "last_name": "updated",
        }
        res = self.client.patch(me_url, user_details)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, user_details["first_name"])
        self.assertEqual(self.user.last_name, user_details["last_name"])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
