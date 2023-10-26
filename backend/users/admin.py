from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Follow


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['author', 'follower']
    list_select_related = ['author', 'follower']
