from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from book.models import Book
from borrowing.models import Borrowing, Payment
from borrowing.notification_service import send_message


class BorrowingSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs=attrs)
        book = Book.objects.get(id=attrs["book"].id)
        book.inventory -= 1
        if book.inventory >= 0:
            book.save()
            message = (
                f"New Borrowing:\n"
                f"{book}\n"
                f"Expected return date: {data['expected_return_date']}"
            )
            send_message(message)
            return data
        else:
            raise ValidationError("Book not available")

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
            "is_active"
        ]


class BorrowingListSerializer(serializers.ModelSerializer):
    book_info = serializers.CharField(read_only=True, source="book")
    user_full_name = serializers.CharField(read_only=True, source="user")

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
            "book_info",
            "user",
            "user_full_name",
            "is_active"
        ]


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book_info = serializers.CharField(read_only=True, source="book")
    user_full_name = serializers.CharField(read_only=True, source="user")

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "book_info",
            "user",
            "user_full_name",
            "is_active"
        ]


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = [
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay"
        ]
