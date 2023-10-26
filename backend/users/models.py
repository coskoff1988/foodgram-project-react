from django.contrib.auth.models import AbstractUser
from django.db import models

from backend.constants import MAX_USER_FIELD_LENGTH, MAX_STR_LENGTH


class CustomUser(AbstractUser):
    email = models.EmailField(blank=False, unique=True)
    username = models.CharField(unique=True, max_length=MAX_USER_FIELD_LENGTH)
    first_name = models.CharField(max_length=MAX_USER_FIELD_LENGTH)
    last_name = models.CharField(max_length=MAX_USER_FIELD_LENGTH)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        ordering = ('last_name',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return (f'{self.first_name[:MAX_STR_LENGTH]} '
                f'{self.last_name[:MAX_STR_LENGTH]}')


class Follow(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )
    follower = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'follower'),
                name='follow_author_follower_unique_constraint'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('follower')),
                name='follow_author_follower_check_constraint'
            )
        ]
        ordering = ('follower__last_name',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (f'{self.author.last_name[:MAX_STR_LENGTH]} '
                f'{self.follower.last_name[:MAX_STR_LENGTH]}')
