from django.contrib import admin

from apps.community.models import Community


# Register your models here.
@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = [
        'creator',
        'title',
        'slug',
        'description',
        'is_private',
    ]
