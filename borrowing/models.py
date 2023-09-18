from django.conf import settings
from django.db import models

from book.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(blank=True, null=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    @property
    def total_price(self):
        return (
            self.book.daily_free
            * (self.expected_return_date - self.borrow_date).days
        )

    @property
    def is_active(self):
        return self.actual_return_date is None

    def __str__(self):
        return f"{self.user} - {self.book.title}"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid")
    ]
    PAYMENT_TYPE_CHOICES = [
        ("PAYMENT", "Payment"),
        ("FINE", "Fine")
    ]

    status = models.CharField(max_length=7, choices=PAYMENT_STATUS_CHOICES)
    type = models.CharField(max_length=7, choices=PAYMENT_TYPE_CHOICES)
    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    session_url = models.URLField(
        max_length=255,
        blank=True,
        null=True
    )
    session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    money_to_pay = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    def __str__(self):
        return self.id
