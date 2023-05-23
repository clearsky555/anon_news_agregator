from django.contrib import admin

from apps.blog.models import Post, Category


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'created_at', 'updated_at',
    ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'slug', 'id',
    ]