from django.contrib import admin

from book.models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_free"
        ]
    search_fields = [
        "title",
        "cover",
        "author"
    ]
