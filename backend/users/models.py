from django.contrib.auth.models import AbstractUser
from django.db import models

from backend.constants import MAX_USER_FIELD_LENGTH


class CustomUser(AbstractUser):
    email = models.EmailField(blank=False, unique=True)
    username = models.CharField(unique=True, max_length=MAX_USER_FIELD_LENGTH)
    first_name = models.CharField(max_length=MAX_USER_FIELD_LENGTH)
    last_name = models.CharField(max_length=MAX_USER_FIELD_LENGTH)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')


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
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
