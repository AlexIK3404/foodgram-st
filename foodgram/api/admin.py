from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Recipe,
    Ingredient,
    RecipeIngredient,
    Favorite,
    CartItem,
    Follow,
)

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name',
                                      'last_name', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    verbose_name = 'Ингредиент в рецепте'
    verbose_name_plural = 'Ингредиенты в рецепте'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'favorites_count')
    search_fields = ('title', 'author__username')
    readonly_fields = ('favorites_count',)
    inlines = (RecipeIngredientInline,)

    def favorites_count(self, obj):
        return obj.in_favorites.count()
    favorites_count.short_description = 'Добавлено в избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')
    search_fields = ('name',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    list_filter = ('recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'added_at')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('added_at',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'added_at')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('added_at',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author', 'created_at')
    search_fields = ('user__username', 'author__username')
    list_filter = ('created_at',)
