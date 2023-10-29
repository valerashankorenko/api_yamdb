from django.contrib import admin

from .models import Category, Genre, Title, TitleGenre


class TitleAdmin(admin.ModelAdmin):
    search_fields = ('year', 'name', 'category__name', 'genre__name')


admin.site.register(Title, TitleAdmin)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(TitleGenre)
