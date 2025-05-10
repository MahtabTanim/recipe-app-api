"""Test for djaango admin modification"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminTest(TestCase):
    "Tests for django admin"

    def setUp(self):
        """create user and client"""

        self.client = Client()
        email = "test@example.com"
        password = "testpassword"
        first_name = "testname"
        last_name = "lastname"
        username = "testuser"
        self.admin_user = get_user_model().objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            username=username,
        )
        self.user = get_user_model().objects.create_user(
            email="testuser@testuser.com",
            password=password,
            first_name=first_name,
            last_name=last_name,
            username=username + first_name,
        )
        self.client.force_login(self.admin_user)

    def test_user_list(self):
        """Test the users are listed on page"""
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)
        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.username)
        self.assertContains(res, self.user.last_name)

    def test_edit_user_page(self):
        """Tests if edit user page is working"""
        url = reverse(
            "admin:core_user_change",
            args=[
                self.user.id,
            ],
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_create_new_user_page(self):
        """Tests the create user page"""
        url = reverse(
            "admin:core_user_add",
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
