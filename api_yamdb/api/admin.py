from django.contrib import admin

from .models import Category, Genre, Title, TitleGenre


class TitleAdmin(admin.ModelAdmin):
    search_fields = ('year', 'name', 'category__name', 'genre__name')


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Title, TitleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(TitleGenre)
