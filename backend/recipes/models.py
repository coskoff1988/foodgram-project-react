from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from backend.constants import (
    MAX_FIELD_LENGTH,
    MIN_FIELD_VALUE,
    MAX_FIELD_VALUE,
    MAX_STR_LENGTH
)
from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_FIELD_LENGTH,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=MAX_FIELD_LENGTH,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:MAX_STR_LENGTH]


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_FIELD_LENGTH,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_FIELD_LENGTH,
        verbose_name='Единица измерения'
    )

    def __str__(self):
        return self.name[:MAX_STR_LENGTH]

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    name = models.CharField(
        max_length=MAX_FIELD_LENGTH,
        verbose_name='Название'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                MIN_FIELD_VALUE,
                message='Минимальное время приготовления %(limit_value)s минут'
            ),
            MaxValueValidator(
                MAX_FIELD_VALUE,
                message='Максимальное время приготовления '
                        '%(limit_value)s минут'
            )
        ]
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    image = models.ImageField(verbose_name='Изображение рецепта')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pk',)

    def __str__(self):
        return self.name[:MAX_STR_LENGTH]


class IngredientToRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_to_recipes',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_to_recipes',
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                MIN_FIELD_VALUE,
                message='Минимальное количество %(limit_value)s'
            ),
            MaxValueValidator(
                MAX_FIELD_VALUE,
                message='Максимальное количество %(limit_value)s'
            )
        ]
    )

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class AbsractUserRecipe(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user[:MAX_STR_LENGTH]} - {self.recipe[:MAX_STR_LENGTH]}'


class Favorite(AbsractUserRecipe):
    class Meta:
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='favorite_user_recipe_unique_constraint'
            )
        ]


class ShoppingCart(AbsractUserRecipe):
    class Meta:
        default_related_name = 'shopping_carts'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='shopping_cart_user_recipe_unique_constraint'
            )
        ]
