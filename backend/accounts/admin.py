from django.contrib import admin
from .models import Interest, UserProfile


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'current_level')
    search_fields = ('user__email', 'name')
    list_filter = ('current_level',)
