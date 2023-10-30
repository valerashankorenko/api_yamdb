from django.contrib import admin

from .models import Category, Genre, Title, TitleGenre, User


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Title)
admin.site.register(TitleGenre)


@admin.register(User)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'email', 'username', 'first_name', 'last_name', 'role', 'bio'
    )
    list_display_links = ('email', 'username')
    search_fields = ('email', 'username')
    empty_value_display = '-пусто-'
