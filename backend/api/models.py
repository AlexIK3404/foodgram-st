import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'{self.username} {self.email}'


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=200, unique=True)
    unit = models.CharField('Ед. измерения', max_length=50)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    title = models.CharField('Название рецепта', max_length=256)
    text = models.TextField('Описание рецепта')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (мин)',
        help_text='Укажите в минутах'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/images/'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    short_id = models.UUIDField(
        'Короткая ссылка',
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.FloatField('Количество')

    class Meta:
        unique_together = ('recipe', 'ingredient')
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient.name}: {self.amount} \
                {self.ingredient.measurement_unit}'


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorites',
        verbose_name='Рецепт'
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user.username} → {self.recipe.name}'


class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_cart',
        verbose_name='Рецепт'
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Элемент списка покупок'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return f'{self.recipe.name} в списке {self.user.username}'


class Follow(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки'
    )

    class Meta:
        unique_together = ('user', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
