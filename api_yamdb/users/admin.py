from django.contrib import admin

from .models import User


@admin.register(User)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'email', 'username', 'first_name', 'last_name', 'role', 'bio'
    )
    list_display_links = ('email', 'username')
    search_fields = ('email', 'username')
    empty_value_display = '-пусто-'