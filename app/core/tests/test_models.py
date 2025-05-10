from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):
    """Tests for Models"""

    def test_create_user_with_email(self):
        """Test user creation with email and password"""
        email = "test@example.com"
        password = "testpassword"
        first_name = "testname"
        last_name = "lastname"
        username = "testuser"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            username=username,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test Email is normalized for new users"""

        sample_emails = [
            ["test1@EXAMPLE.COM", "test1@example.com"],
            ["Test2@EXAMPLE.COM", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@EXAMPLE.COM", "test4@example.com"],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                first_name="first",
                last_name="last",
                password="pass",
                username="user" + email,
            )
            self.assertEqual(user.email, expected)

    def test_new_user_email_address_exists(self):
        """Test: creating user without email or username raises ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                first_name="", last_name="", username="", email=""
            )

    def test_creating_superuser(self):
        """Test creating a supeuser"""

        email = "test@example.com"
        password = "testpassword"
        first_name = "testname"
        last_name = "lastname"
        username = "testuser"
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            username=username,
        )

        self.assertTrue(user.is_superadmin)
        self.assertTrue(user.is_staff)
