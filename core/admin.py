from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("iso_language", "title", "content")}),
        ("internal", {"fields": ("fts_vector",)}),
    )
    list_display = ("iso_language", "title")
    list_display_links = ("title",)
    list_filter = ("iso_language",)
    readonly_fields = ("fts_vector",)
    search_fields = ("title", "content")
