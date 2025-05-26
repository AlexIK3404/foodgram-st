from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from .models import (
    CustomUser, Ingredient, Recipe, RecipeIngredient,
    Favorite, CartItem, Follow
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(source='profile.avatar', read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'avatar')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'unit')  # полe `unit` в модели


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True
    )
    name = serializers.CharField(source='ingredient.name', read_only=True)
    unit = serializers.CharField(
        source='ingredient.unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'title', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            False if user.is_anonymous
            else obj.in_favorites.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            False if user.is_anonymous
            else obj.in_cart.filter(user=user).exists()
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField(
        child=serializers.DictField(), write_only=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'image', 'title', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
        for item in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=item['id'],
                amount=item['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if ingredients_data is not None:
            instance.recipeingredient_set.all().delete()
            for item in ingredients_data:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient_id=item['id'],
                    amount=item['amount']
                )
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='recipe.id', read_only=True)
    title = serializers.CharField(source='recipe.title', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True
    )

    class Meta:
        model = Favorite
        fields = ('id', 'title', 'image', 'cooking_time')


class CartItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='recipe.id', read_only=True)
    title = serializers.CharField(source='recipe.title', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True
    )

    class Meta:
        model = CartItem
        fields = ('id', 'title', 'image', 'cooking_time')


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField()
    image = serializers.ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='author.email', read_only=True)
    id = serializers.IntegerField(source='author.id', read_only=True)
    username = serializers.CharField(source='author.username', read_only=True)
    first_name = serializers.CharField(
        source='author.first_name',
        read_only=True
    )
    last_name = serializers.CharField(
        source='author.last_name',
        read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.ImageField(
        source='author.profile.avatar',
        read_only=True
    )

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        limit = int(self.context['request'].query_params.get(
            'recipes_limit',
            3)
        )
        recipes = Recipe.objects.filter(author=obj.author)[:limit]
        return SubscriptionRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
