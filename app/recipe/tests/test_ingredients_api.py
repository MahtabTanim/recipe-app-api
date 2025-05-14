"""
Tests for the Ingredient APIs
"""

from django.urls import reverse
from django.test import TestCase
from core.models import Ingredient
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from recipe.serializers import IngredientSerializer
from .test_recipe_api import create_recipe

ingredients_url = reverse("recipe:ingredient-list")


def ingredient_detail_url(ingredient_id):
    return reverse(
        "recipe:ingredient-detail",
        args=[
            ingredient_id,
        ],
    )


def create_user(**kwargs):
    """Creates and return a new user"""
    data = {
        "email": "test@example.com",
        "password": "testpassword",
        "first_name": "testname",
        "last_name": "lastname",
        "username": "testuser",
    }
    data.update(kwargs)
    return get_user_model().objects.create_user(**data)


class PublicIngredientsAPITests(TestCase):
    """Tests for unauthenticated users"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call the the method"""
        res = self.client.get(ingredients_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Tests for authenticated users"""

    def setUp(self):
        """Setup Tests Data"""
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients(self):
        """Test Ingredients List"""
        Ingredient.objects.create(user=self.user, name="Ing1")
        Ingredient.objects.create(user=self.user, name="Ing2")
        res = self.client.get(ingredients_url)
        ingrdients = Ingredient.objects.all().order_by("-name")
        serialized = IngredientSerializer(ingrdients, many=True)
        self.assertEqual(serialized.data, res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_ingredients_limited_to_user(self):
        """Test Ingredients is listed based on authenticated user"""
        other_user = create_user(
            email="Test@ddsdds.com",
            username="ussername2",
        )
        ingredient1 = Ingredient.objects.create(user=self.user, name="Ing1")
        Ingredient.objects.create(user=other_user, name="Ing2")
        res = self.client.get(ingredients_url)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient1.name)
        self.assertEqual(res.data[0]["id"], ingredient1.id)

    def test_update_ingredient(self):
        """Update Ingredients based on id"""
        ingredient = Ingredient.objects.create(user=self.user, name="Ing1")
        payload = {
            "name": "New name",
        }
        ingredient_url = ingredient_detail_url(ingredient_id=ingredient.id)
        res = self.client.patch(ingredient_url, payload)
        ingredient.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.name, payload["name"])

    def test_delete_ingredient(self):
        """Test delete Ingredient from db"""
        ingredient = Ingredient.objects.create(user=self.user, name="Ing1")
        ingredient_url = ingredient_detail_url(ingredient_id=ingredient.id)
        res = self.client.delete(ingredient_url)
        ingredient = Ingredient.objects.filter(user=self.user)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ingredient.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Filter ingredients those are assigned to recipes"""
        r1 = create_recipe(user=self.user)
        ingredient1 = Ingredient.objects.create(user=self.user, name="Ing1")
        ingredient2 = Ingredient.objects.create(user=self.user, name="Ing2")
        ingredient3 = Ingredient.objects.create(user=self.user, name="Ing3")
        r1.ingredients.add(ingredient1)
        r1.ingredients.add(ingredient2)
        params = {"assigned_only": True}
        res = self.client.get(ingredients_url, params)
        s1 = IngredientSerializer(ingredient1)
        s2 = IngredientSerializer(ingredient2)
        s3 = IngredientSerializer(ingredient3)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Filter unique ingredients those are assigned to recipes"""
        r1 = create_recipe(user=self.user)
        r2 = create_recipe(user=self.user)
        ingredient1 = Ingredient.objects.create(user=self.user, name="Ing1")
        ingredient2 = Ingredient.objects.create(user=self.user, name="Ing2")
        r1.ingredients.add(ingredient1)
        r2.ingredients.add(ingredient1)
        params = {"assigned_only": True}
        res = self.client.get(ingredients_url, params)
        s1 = IngredientSerializer(ingredient1)
        s2 = IngredientSerializer(ingredient2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)
        self.assertEqual(len(res.data), 1)
