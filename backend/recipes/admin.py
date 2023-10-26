from django.contrib import admin

from .models import (
    Ingredient,
    Recipe,
    Tag,
    IngredientToRecipe,
    Favorite,
    ShoppingCart
)


class IngredientToRecipeInline(admin.TabularInline):
    model = IngredientToRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientToRecipeInline]
    list_display = ['name', 'author', 'cooking_time']
    list_filter = ['tags', 'author']
    search_fields = ['name', 'text', 'author__username']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    search_fields = ['name']
    list_filter = ['measurement_unit']


@admin.register(Favorite)
@admin.register(ShoppingCart)
class UserRecipeAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']
    list_select_related = ['user', 'recipe']
