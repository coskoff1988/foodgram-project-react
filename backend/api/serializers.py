from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (
    Tag,
    Ingredient,
    IngredientToRecipe,
    Recipe,
    Favorite,
    ShoppingCart,
)
from users.models import Follow, CustomUser


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and user.follower.filter(
            author=obj
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientToRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = IngredientToRecipeSerializer(
        many=True,
        source='ingredients_to_recipes'
    )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_user(self):
        return self.context['request'].user

    def get_is_favorited(self, obj):
        user = self.get_user()
        return user.is_authenticated and user.favorites.filter(
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.get_user()
        return user.is_authenticated and user.shopping_carts.filter(
            recipe=obj
        ).exists()


class IngredientToRecipeWriteSerializer(IngredientToRecipeSerializer):
    class Meta:
        model = IngredientToRecipe
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = IngredientToRecipeWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time')

    def validate(self, attrs):
        if not attrs.get('tags'):
            raise ValidationError('Поле тегов не может быть пустым')
        if not attrs.get('tags'):
            raise ValidationError('Поле ингредиентов не может быть пустым')
        if not attrs.get('image'):
            raise ValidationError('Поле изображения не может быть пустым')
        return attrs

    def validate_tags(self, value):
        if not value:
            raise ValidationError('Поле тегов не может быть пустым')
        if len(value) != len(set(value)):
            raise ValidationError('Теги не могут повторяться')
        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError('Поле ингредиентов не может быть пустым')
        pks = [
            ingredient_data['ingredient']['id']
            for ingredient_data in value
        ]
        if len(pks) != len(set(pks)):
            raise ValidationError('Ингредиенты не могут повторяться')
        return value

    def add_ingredients(self, recipe, ingredients_data):
        ingredients_to_recipe = []
        for ingredient_data in ingredients_data:
            ingredients_to_recipe.append(
                IngredientToRecipe(
                    recipe=recipe,
                    ingredient=ingredient_data['ingredient']['id'],
                    amount=ingredient_data['amount']
                )
            )
        IngredientToRecipe.objects.bulk_create(ingredients_to_recipe)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = super().update(instance, validated_data)
        recipe.tags.clear()
        recipe.tags.set(tags)
        recipe.ingredients_to_recipes.all().delete()
        self.add_ingredients(recipe, ingredients_data)
        return recipe


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowUserSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
        )
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'

    def validate(self, attrs):
        if attrs['author'] == attrs['follower']:
            raise ValidationError('Автор не может подписаться сам на себя')
        return attrs


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'
