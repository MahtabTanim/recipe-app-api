from django.urls import reverse
from django.test import TestCase
from decimal import Decimal
from core.models import Recipe
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from recipe.serializers import RecipeSerializer

recipes_url = reverse("recipe:recipe-list")


def create_recipe(user, **params):
    """Create and return Recipe"""
    defaults = {
        "title": "Test Recipe",
        "time_minutes": 5,
        "price": Decimal(5.00),
        "description": "Test",
        "link": "fjsdj/afjednkjs.com",
    }
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeAPITests(TestCase):
    """Tests  for unauthenticated users"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call the the method"""
        res = self.client.get(recipes_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test for authenticated Users"""

    def setUp(self):
        """Setup Tests Data"""
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword",
            first_name="testname",
            last_name="lastname",
            username="testuser",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_reatrieve_recipes(self):
        """Test recipe List"""
        create_recipe(self.user)
        create_recipe(self.user)
        res = self.client.get(recipes_url)
        recipes = Recipe.objects.all().order_by("-id")
        seriralizer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.data, seriralizer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_recipe__limited_to_user(self):
        """Test recipe limited to authenticated user"""
        other_user = get_user_model().objects.create_user(
            email="test2@example.com",
            password="testpassword",
            first_name="testname",
            last_name="lastname",
            username="test2user",
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)
        res = self.client.get(recipes_url)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.data, serializer.data)
