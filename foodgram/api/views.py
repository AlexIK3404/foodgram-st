from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import viewsets, mixins, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Recipe, Ingredient, Favorite, CartItem, Follow
from .serializers import (
    RecipeReadSerializer, RecipeWriteSerializer,
    IngredientSerializer,
    FavoriteSerializer, CartItemSerializer,
    SubscriptionSerializer
)
from .permissions import IsAuthorOrReadOnlyPermission

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    """
    /api/recipes/            GET, POST
    /api/recipes/{id}/       GET, PATCH, DELETE
    /api/recipes/{id}/favorite/      POST, DELETE
    /api/recipes/{id}/shopping_cart/ POST, DELETE
    /api/recipes/{id}/get-link/      GET
    """
    queryset = Recipe.objects.all().order_by('-pub_date')
    permission_classes = [IsAuthorOrReadOnlyPermission]
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            Favorite.objects.get_or_create(user=request.user, recipe=recipe)
            serializer = FavoriteSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        fav = get_object_or_404(Favorite, user=request.user, recipe=recipe)
        fav.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            CartItem.objects.get_or_create(user=request.user, recipe=recipe)
            serializer = CartItemSerializer(recipe,
                                            context={'request': request}
                                            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        item = get_object_or_404(CartItem, user=request.user, recipe=recipe)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['get'],
            permission_classes=[permissions.AllowAny],
            url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = request.build_absolute_uri(f'/s/{recipe.short_id}/')
        return Response({'short-link': short_link})


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/ingredients/       GET
    /api/ingredients/{id}/  GET
    """
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']


class SubscriptionViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    /api/users/subscriptions/       GET
    /api/users/{id}/subscribe/      POST, DELETE
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        if author == request.user:
            return Response(
                {'errors': 'Нельзя подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'POST':
            follow, created = Follow.objects.get_or_create(user=request.user,
                                                           author=author)
            if not created:
                return Response(
                    {'errors': 'Вы уже подписаны'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscriptionSerializer(
                follow,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # DELETE
        follow = get_object_or_404(Follow, user=request.user, author=author)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
