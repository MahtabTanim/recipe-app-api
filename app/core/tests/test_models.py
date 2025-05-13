from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from unittest.mock import patch


def create_user(**kwargs):
    sample = {
        "email": "test@example.com",
        "password": "testpassword",
        "first_name": "testname",
        "last_name": "lastname",
        "username": "testuser",
    }
    sample.update(kwargs)
    return get_user_model().objects.create_user(**sample)


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

    def test_create_recipe(self):
        """Test creating a recipe is successfull"""
        email = "test@example.com"
        password = "testpassword"
        first_name = "testname"
        last_name = "lastname"
        username = "testuser"
        user = get_user_model().objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            username=username,
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title="Test Recipe",
            time_minutes=5,
            price=Decimal(5.00),
            description="Test",
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test for creation of tags"""
        user = create_user(
            email="ttt@ttt.com",
            username="test22",
        )
        tag = models.Tag.objects.create(user=user, name="testtag")
        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test creating an ingredient"""
        user = create_user(
            email="ttt@ttt.com",
            username="test22",
        )
        ingredient = models.Ingredient.objects.create(user=user, name="Ing1")
        self.assertEqual(ingredient.name, str(ingredient))

    @patch("core.models.uuid.uuid4")
    def test_recipe_image_fileptah(self, mock_uuid):
        """Test generating image path"""
        uuid = "test_uuid"
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_fileptah(None, "example.jpg")
        self.assertEqual(file_path, f"uploads/recipe/{uuid}.jpg")
