from . import serializers
from core.models import Recipe, Tag, Ingredient
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    extend_schema_view,
    OpenApiTypes,
)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "tags",
                OpenApiTypes.STR,
                description="Comma seperated list of tag ids",
            ),
            OpenApiParameter(
                "ingredients",
                OpenApiTypes.STR,
                description="Comma seperated list of ingredient ids",
            ),
        ]
    )
)
class RecipeViewset(viewsets.ModelViewSet):
    """View for managing recipes"""

    serializer_class = serializers.RecipeDetailSerializer
    authentication_classes = [
        TokenAuthentication,
    ]
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = Recipe.objects.all()

    def _params_to_ints(self, qs=""):
        """returns list of ints from query parameter string"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve recipes for the authenticated user"""
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")
        queryset = self.queryset
        if tags:
            """Filter queryset based on tag ids"""
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            """Filter queryset based on ingredient ids"""
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return (
            queryset.filter(
                user=self.request.user,
            )
            .order_by("-id")
            .distinct()
        )

    def get_serializer_class(self):
        """Return the serializer for http methods"""
        if self.action == "list":
            return serializers.RecipeSerializer
        if self.action == "upload_image":
            return serializers.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return super().perform_create(serializer)

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image to the recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "assigned_only",
                OpenApiTypes.STR,
                description="Filter items assigned to recipes , True/False",
                enum=["True", "False"],
            ),
        ]
    )
)
class BaseRecipeAttrViewset(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = [
        TokenAuthentication,
    ]
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        """Retrieve queryset based on the authenticated user"""
        queryset = self.queryset.filter(user=self.request.user)
        assigned_only = self.request.query_params.get("assigned_only")
        if assigned_only and assigned_only.lower() == "true":
            queryset = queryset.filter(recipe__isnull=False).distinct()
        return queryset.order_by("-name")


class TagViewSet(BaseRecipeAttrViewset):
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewset):
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
