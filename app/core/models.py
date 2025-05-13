from decimal import Decimal
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import os
import uuid


def recipe_image_fileptah(instance, file_name):
    """returns a unique filename"""
    ext = os.path.splitext(file_name)[1]
    file_name = f"{uuid.uuid4()}{ext}"
    return os.path.join("uploads", "recipe", file_name)


class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(
        self,
        first_name,
        last_name,
        username,
        email,
        password=None,
    ):
        """Create save and return a new user"""
        if not email:
            raise ValueError("User must have an email address")
        if not username:
            raise ValueError("Username Cant be left blank")
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        first_name,
        last_name,
        username,
        email,
        password=None,
    ):
        """Create and return Superuser"""
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser):
    """User in the system"""

    # required_fields
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(unique=True, max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=12, blank=True)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
    ]

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_level):
        return True


class Recipe(models.Model):
    """Recipe Model"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=100, blank=True, null=True)
    time_minutes = models.IntegerField(default=0)
    price = models.DecimalField(
        default=Decimal(0),
        max_digits=7,
        decimal_places=2,
    )
    description = models.TextField(null=True, blank=True)
    link = models.CharField(max_length=250, blank=True, null=True)
    tags = models.ManyToManyField("Tag")
    ingredients = models.ManyToManyField("Ingredient")
    image = models.ImageField(null=True, upload_to=recipe_image_fileptah)

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tag model"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient model for recipe"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
