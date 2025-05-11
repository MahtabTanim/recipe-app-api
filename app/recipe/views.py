from . import serializers
from core.models import Recipe
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class RecipeViewset(viewsets.ModelViewSet):
    """View for managing recipes"""

    serializer_class = serializers.RecipeSerializer
    authentication_classes = [
        TokenAuthentication,
    ]
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """Retrieve recipes for the authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by("-id")
