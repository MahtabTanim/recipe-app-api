"""
Tests for the Recipe APIs
"""

import tempfile
import os
from PIL import Image
from django.urls import reverse
from django.test import TestCase
from decimal import Decimal
from core.models import Ingredient, Recipe, Tag
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

recipes_url = reverse("recipe:recipe-list")


def recipe_detail_url(recipe_id):
    """Returns recipe detail url"""
    return reverse(
        "recipe:recipe-detail",
        args=[
            recipe_id,
        ],
    )


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


def image_upload_url(recipe_id):
    """Return image upload url"""
    return reverse("recipe:recipe-upload-image", args=[recipe_id])


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

    def test_retrieve_recipes(self):
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

    def test_get_recipe_detail(self):
        """Test the recipe detail"""
        recipe = create_recipe(self.user)
        url = recipe_detail_url(recipe.id)
        res = self.client.get(url)
        serialized = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serialized.data)

    def test_create_recipe(self):
        """Test creating a new recipe"""
        payload = {
            "title": "Test Recipe",
            "time_minutes": 5,
            "price": Decimal(5.00),
            "description": "Test",
            "link": "fjsdj/afjednkjs.com",
        }
        res = self.client.post(recipes_url, payload)
        recipe = Recipe.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipe.user, self.user)
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

    def test_partial_update(self):
        """Test partial update of a recipe"""
        recipe = create_recipe(
            user=self.user,
            title="Original Title",
            link="somelink/link",
        )
        payload = {
            "title": "new title",
        }
        recipe_url = recipe_detail_url(recipe.id)
        res = self.client.patch(recipe_url, payload)
        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, "somelink/link")
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of a recipe"""
        recipe = create_recipe(
            user=self.user,
            title="Test Recipe",
            time_minutes=5,
            price=Decimal(5.00),
            description="Test",
            link="fjsdj/afjednkjs.com",
        )
        payload = {
            "title": "Changed Title",
            "time_minutes": 10,
            "price": Decimal(770.00),
            "description": "Changed Description",
            "link": "changed/link",
        }
        recipe_url = recipe_detail_url(recipe.id)
        res = self.client.put(recipe_url, payload)
        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Tet changing the recipe user returns an error"""
        other_user = get_user_model().objects.create_user(
            email="test2@example.com",
            password="testpassword",
            first_name="testname",
            last_name="lastname",
            username="test2user",
        )
        recipe = create_recipe(user=self.user)
        payload = {
            "user": other_user,
        }
        recipe_url = recipe_detail_url(recipe.id)
        res = self.client.patch(recipe_url, payload)
        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Tests Deleting a recipe is successfull"""
        recipe = create_recipe(user=self.user)
        recipe_url = recipe_detail_url(recipe.id)
        res = self.client.delete(recipe_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_error(self):
        """Test trying to delete other users recipe gives error"""
        other_user = get_user_model().objects.create_user(
            email="test2@example.com",
            password="testpassword",
            first_name="testname",
            last_name="lastname",
            username="test2user",
        )
        recipe = create_recipe(user=other_user)
        recipe_url = recipe_detail_url(recipe.id)
        res = self.client.delete(recipe_url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Create Recipe with new tags"""
        payload = {
            "title": "Test Recipe",
            "time_minutes": 5,
            "price": Decimal(5.00),
            "description": "Test",
            "link": "fjsdj/afjednkjs.com",
            "tags": [
                {"name": "tag1"},
                {"name": "tag2"},
            ],
        }
        res = self.client.post(recipes_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload["tags"]:
            exists = recipe.tags.filter(
                name=tag["name"],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Create Recipe with existing tags"""
        tag1 = Tag.objects.create(name="tag1", user=self.user)
        payload = {
            "title": "Test Recipe",
            "time_minutes": 5,
            "price": Decimal(5.00),
            "description": "Test",
            "link": "fjsdj/afjednkjs.com",
            "tags": [
                {"name": "tag1"},
                {"name": "tag2"},
            ],
        }
        res = self.client.post(recipes_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag1, recipe.tags.all())
        for tag in payload["tags"]:
            exists = recipe.tags.filter(
                name=tag["name"],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_updating_recipe(self):
        """Test : create tags while updating the recipe"""
        recipe = create_recipe(self.user)
        payload = {
            "tags": [
                {"name": "tag1"},
            ]
        }
        url = recipe_detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name="tag1")
        recipe.refresh_from_db()
        self.assertIn(new_tag, recipe.tags.all())

    def test_assign_existing_tags_while_updating_recipe(self):
        """Test assigning tags while updating recipe"""
        tag1 = Tag.objects.create(name="tag1", user=self.user)
        tag2 = Tag.objects.create(name="tag2", user=self.user)
        recipe = create_recipe(self.user)
        recipe.tags.add(tag1)
        payload = {
            "tags": [
                {"name": "tag2"},
            ]
        }
        url = recipe_detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format="json")
        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag2, recipe.tags.all())
        self.assertNotIn(tag1, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clear tags from a recipe"""
        tag1 = Tag.objects.create(name="tag1", user=self.user)
        recipe = create_recipe(self.user)
        recipe.tags.add(tag1)
        payload = {"tags": []}
        url = recipe_detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format="json")
        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredients(self):
        """Test Create Recipe with new ingredients"""
        payload = {
            "title": "Test Recipe",
            "time_minutes": 5,
            "price": Decimal(5.00),
            "description": "Test",
            "link": "fjsdj/afjednkjs.com",
            "ingredients": [
                {"name": "ing1"},
                {"name": "ing2"},
            ],
        }
        res = self.client.post(recipes_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name=ingredient["name"],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):
        """Create Recipe with existing Ingredients"""
        ingredient1 = Ingredient.objects.create(name="ing1", user=self.user)
        payload = {
            "title": "Test Recipe",
            "time_minutes": 5,
            "price": Decimal(5.00),
            "description": "Test",
            "link": "fjsdj/afjednkjs.com",
            "ingredients": [
                {"name": "ing1"},
                {"name": "ing2"},
            ],
        }
        res = self.client.post(recipes_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient1, recipe.ingredients.all())
        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name=ingredient["name"],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredients_on_updating_recipe(self):
        """Test : create ingredients while updating the recipe"""
        recipe = create_recipe(self.user)
        payload = {
            "ingredients": [
                {"name": "ing1"},
            ]
        }
        url = recipe_detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user, name="ing1")
        recipe.refresh_from_db()
        self.assertEqual(recipe.ingredients.count(), 1)
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_assign_existing_ingredients_while_updating_recipe(self):
        """Test assigning ingredient while updating recipe"""
        ingredient1 = Ingredient.objects.create(name="ing1", user=self.user)
        ingredient2 = Ingredient.objects.create(name="ing2", user=self.user)
        recipe = create_recipe(self.user)
        recipe.ingredients.add(ingredient1)
        payload = {
            "ingredients": [
                {"name": "ing2"},
            ]
        }
        url = recipe_detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format="json")
        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test clearing ingredients from a recipe"""
        ingredient1 = Ingredient.objects.create(name="ing1", user=self.user)
        recipe = create_recipe(self.user)
        recipe.ingredients.add(ingredient1)
        payload = {"ingredients": []}
        url = recipe_detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format="json")
        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_recipe_filter_by_tag(self):
        """Test recipe filter by tag"""
        r1 = create_recipe(self.user, title="recipe1")
        r2 = create_recipe(self.user, title="recipe2")
        r3 = create_recipe(self.user, title="recipe3")
        tag1 = Tag.objects.create(name="tag1", user=self.user)
        tag2 = Tag.objects.create(name="tag2", user=self.user)
        r1.tags.add(tag1)
        r2.tags.add(tag2)
        params = {"tags": f"{tag1.id},{tag2.id}"}
        res = self.client.get(recipes_url, params)
        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_recipe_filter_by_ingredient(self):
        """Test recipe filter by ingredient"""
        r1 = create_recipe(self.user, title="recipe1")
        r2 = create_recipe(self.user, title="recipe2")
        r3 = create_recipe(self.user, title="recipe3")
        ing1 = Ingredient.objects.create(name="ing1", user=self.user)
        ing2 = Ingredient.objects.create(name="ign2", user=self.user)
        r1.ingredients.add(ing1)
        r2.ingredients.add(ing2)
        params = {"ingredients": f"{ing1.id},{ing2.id}"}
        res = self.client.get(recipes_url, params)
        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)


class ImageUplaodTests(TestCase):
    """Tests for uploading  recipe image"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword",
            first_name="testname",
            last_name="lastname",
            username="testuser",
        )
        self.client.force_authenticate(user=self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        return self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading image to recipe"""
        url = image_upload_url(recipe_id=self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            payload = {"image": image_file}
            res = self.client.post(url, payload, format="multipart")
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_bad_image(self):
        """Test uploading bad image"""
        url = image_upload_url(recipe_id=self.recipe.id)
        payload = {"image": "notanimage"}
        res = self.client.post(url, payload, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
