from django.contrib import admin

from .models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'contributor', 'is_approved', 'created_at')
    list_filter = ('category', 'is_approved')
    search_fields = ('title', 'contributor__email', 'url')
    list_editable = ('is_approved',)
    readonly_fields = ('created_at',)
