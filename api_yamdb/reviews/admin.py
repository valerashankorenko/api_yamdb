from django.contrib import admin

from .models import Category, Genre, Title, TitleGenre, User


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year')
    search_fields = ('year', 'name', 'category__name', 'genre__name')
    list_filter = ('year', 'name', 'category__name', 'genre__name')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    prepopulated_fields = {"slug": ("name",)}


@admin.register(TitleGenre)
class TitleGenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'genre')


@admin.register(User)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'email', 'username', 'first_name', 'last_name', 'role', 'bio'
    )
    list_display_links = ('email', 'username')
    search_fields = ('email', 'username')
    empty_value_display = '-пусто-'
