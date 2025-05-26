from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewSet,
    IngredientViewSet,
    SubscriptionViewSet,
)

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(
    r'users/subscriptions',
    SubscriptionViewSet,
    basename='subscription'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:id>/subscribe/',
         SubscriptionViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='user-subscribe'),
]
