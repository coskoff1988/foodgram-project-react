import django_filters

from recipes.models import Recipe, Ingredient, Tag


class RecipeFilterSet(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = django_filters.NumberFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        return queryset.filter(
            favorites__user=self.request.user
        ) if user.is_authenticated and value == 1 else queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        return queryset.filter(
            shopping_carts__user=self.request.user
        ) if user.is_authenticated and value == 1 else queryset


class IngredientFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
