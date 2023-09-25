from django.db import models


class Book(models.Model):
    BOOKS_COVER_CHOICES = [
        ("H", "Hard"),
        ("S", "Soft"),
    ]

    title = models.CharField(max_length=63)
    author = models.CharField(max_length=63)
    cover = models.CharField(
        max_length=1,
        choices=BOOKS_COVER_CHOICES,
    )
    inventory = models.PositiveIntegerField(default=0)
    daily_free = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.title} - {self.daily_free}"
