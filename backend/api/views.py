from django.core.files.base import ContentFile
from django.db.models import Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilterSet, RecipeFilterSet
from api.mixins import CreateDestroyM2MMixin
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    TagSerializer,
    ShoppingCartSerializer,
    IngredientSerializer,
    FollowSerializer,
    FavoriteSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShortRecipeSerializer,
    FollowUserSerializer
)
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientToRecipe
)
from users.models import CustomUser


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilterSet


class RecipeViewSet(ModelViewSet, CreateDestroyM2MMixin):
    http_method_names = ('get', 'post', 'patch', 'delete')
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def create(self, request, *args, **kwargs):
        serializer = RecipeWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        read_serializer = self.get_serializer(
            serializer.save(
                author=request.user
            )
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = RecipeWriteSerializer(
            instance=self.get_object(),
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        read_serializer = self.get_serializer(
            serializer.save()
        )
        return Response(read_serializer.data)

    @action(detail=True, serializer_class=ShoppingCartSerializer,
            methods=('POST', 'DELETE'), permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, *args, **kwargs):
        if request.method == 'POST':
            return self.create_m2m(
                ShortRecipeSerializer,
                'user',
                'shopping_carts',
                'recipe',
                'Рецепт уже находится в корзине',
            )
        return self.destroy_m2m(
            'shopping_carts',
            'recipe',
            Recipe,
            'Рецепт не находится в корзине'
        )

    @action(detail=False, serializer_class=ShoppingCartSerializer,
            methods=('GET',), permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, *args, **kwargs):
        ingredients_data = IngredientToRecipe.objects.filter(
            recipe__shopping_carts__user=request.user
        ).values(
            'amount',
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            total_amount=Sum('amount')
        )
        strings = ['Список необходимых ингредиентов:']
        for ingredient_data in ingredients_data:
            strings.append(
                '{ingredient__name} ({ingredient__measurement_unit}) '
                '- {total_amount}'.format(
                    **ingredient_data
                )
            )
        return FileResponse(
            ContentFile('\n'.join(strings).encode()),
            as_attachment=True,
            filename='ingredients.txt'
        )

    @action(detail=True, serializer_class=FavoriteSerializer,
            methods=('POST', 'DELETE'), permission_classes=(IsAuthenticated,))
    def favorite(self, request, *args, **kwargs):
        if request.method == 'POST':
            return self.create_m2m(
                ShortRecipeSerializer,
                'user',
                'favorites',
                'recipe',
                'Рецепт уже находится в избранном',
            )
        return self.destroy_m2m(
            'favorites',
            'recipe',
            Recipe,
            'Рецепт не находится в избранном'
        )


class CustomUserViewSet(UserViewSet, CreateDestroyM2MMixin):
    lookup_field = 'pk'

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    def get_queryset(self):
        if self.action == 'subscriptions':
            return CustomUser.objects.filter(
                following__follower=self.request.user
            )
        return super().get_queryset()

    @action(detail=True, serializer_class=FollowSerializer,
            permission_classes=(IsAuthenticatedOrReadOnly,),
            methods=('POST', 'DELETE'))
    def subscribe(self, request, *args, **kwargs):
        if request.method == 'POST':
            return self.create_m2m(
                FollowUserSerializer,
                'follower',
                'follower',
                'author',
                'Вы уже подписаны на этого автора'
            )
        return self.destroy_m2m(
            'follower',
            'author',
            CustomUser,
            'Вы ещё не подписаны на этого автора'
        )

    @action(detail=False, serializer_class=FollowUserSerializer,
            methods=('GET',), permission_classes=(IsAuthenticated,))
    def subscriptions(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
