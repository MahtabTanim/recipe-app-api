"""
Tests for the Recipe APIs
"""

from django.urls import reverse
from django.test import TestCase
from .test_recipe_api import create_recipe
from core.models import Tag
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from recipe.serializers import TagSerializer


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


tags_url = reverse("recipe:tag-list")


def tag_detail_url(tag_id):
    return reverse(
        "recipe:tag-detail",
        args=[
            tag_id,
        ],
    )


class PublicTagsAPITests(TestCase):
    """Tests for unauthenticated users"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call the the method"""
        res = self.client.get(tags_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Tests for authenticated users"""

    def setUp(self):
        """Setup Tests Data"""
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """Test Tags List"""
        Tag.objects.create(user=self.user, name="Tag1")
        Tag.objects.create(user=self.user, name="Tag2")
        res = self.client.get(tags_url)
        tags = Tag.objects.all().order_by("-name")
        serialized = TagSerializer(tags, many=True)
        self.assertEqual(serialized.data, res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_tags_limited_to_user(self):
        """Test tags is listed based on authenticated user"""
        other_user = create_user(
            email="Test@ddsdds.com",
            username="ussername2",
        )
        tag1 = Tag.objects.create(user=self.user, name="Tag1")
        Tag.objects.create(user=other_user, name="Tag2")
        res = self.client.get(tags_url)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag1.name)

    def test_update_tag(self):
        """Update tag"""
        tag = Tag.objects.create(user=self.user, name="Tag1")
        payload = {
            "name": "New name",
        }
        tag_url = tag_detail_url(tag_id=tag.id)
        res = self.client.patch(tag_url, payload)
        tag.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag(self):
        tag = Tag.objects.create(user=self.user, name="Tag1")
        tag_url = tag_detail_url(tag_id=tag.id)
        res = self.client.delete(tag_url)
        tags = Tag.objects.filter(user=self.user)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Filter tags those are assigned to recipes"""
        r1 = create_recipe(user=self.user)
        tag1 = Tag.objects.create(user=self.user, name="Tag1")
        tag2 = Tag.objects.create(user=self.user, name="Tag2")
        tag3 = Tag.objects.create(user=self.user, name="Tag3")
        r1.tags.add(tag1)
        r1.tags.add(tag2)
        params = {"assigned_only": True}
        res = self.client.get(tags_url, params)
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        s3 = TagSerializer(tag3)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_filtered_tags_unique(self):
        """Filter unique tags those are assigned to recipes"""
        r1 = create_recipe(user=self.user)
        r2 = create_recipe(user=self.user)
        tag1 = Tag.objects.create(user=self.user, name="Tag1")
        tag2 = Tag.objects.create(user=self.user, name="Tag2")
        r1.tags.add(tag1)
        r2.tags.add(tag1)
        params = {"assigned_only": True}
        res = self.client.get(tags_url, params)
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)
        self.assertEqual(len(res.data), 1)
