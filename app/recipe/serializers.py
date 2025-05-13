from core.models import Recipe, Tag, Ingredient
from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only_fields = [
            "id",
        ]


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name"]
        read_only_fields = [
            "id",
        ]


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe List View"""

    ingredients = IngredientSerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "title",
            "ingredients",
            "time_minutes",
            "price",
            "tags",
            "link",
        ]
        read_only_fields = [
            "id",
        ]

    def _get_or_create_tags(self, tags, recipe):
        auth_user = self.context["request"].user
        for tag in tags:
            tag_object, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_object)

    def _get_or_create_ingredients(self, ingredients, recipe):
        auth_user = self.context["request"].user
        for ingredient in ingredients:
            ingredient_object, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_object)

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        ingredients = validated_data.pop("ingredients", [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", [])
        ingredients = validated_data.pop("ingredients", [])
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.ingredients.clear()
        self._get_or_create_tags(tags, instance)
        self._get_or_create_ingredients(ingredients, instance)
        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe Detail Views"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description", "image"]


class RecipeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ["id", "image"]
        read_only_fields = [
            "id",
        ]
        extra_kwargs = {
            "image": {
                "required": True,
            }
        }
