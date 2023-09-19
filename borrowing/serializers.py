from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from book.serializers import BookSerializer
from borrowing.models import Borrowing, Payment
from borrowing.notification_service import send_message
from borrowing.payment_service import create_stripe_session


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay"
        ]


class BorrowingSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
            "is_active",
            "payments",
        ]

    def validate(self, attrs):
        user = self.context["request"].user

        if Payment.objects.filter(
            borrowing__user=user,
            status=Payment.StatusChoices.PENDING
        ).exists():
            raise ValidationError(
                "You cannot borrow a new book."
            )
        return attrs

    def validate_book(self, book):
        if book.inventory == 0:
            raise ValidationError(
                "Currently book is not available"
            )
        return book

    def create(self, validated_data):
        request = self.context["request"]
        book = validated_data["book"]
        user = request.user

        borrowing = Borrowing.objects.create(
            expected_return_date=validated_data["expected_return_date"],
            book=book,
            user=user
        )
        create_stripe_session(request, borrowing)
        book.inventory -= 1
        book.save()
        message = (
                f"New Borrowing:\n"
                f"{book}\n"
                f"Expected return date: {borrowing.expected_return_date}"
            )
        send_message(message)
        return borrowing


class BorrowingListSerializer(BorrowingSerializer):
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


class BorrowingReturnSerializer(BorrowingSerializer):
    expected_return_date = serializers.ReadOnlyField()
    book = BookSerializer(read_only=True, many=False)

    def validate(self, attrs):
        borrowing = self.instance

        if borrowing.actual_return_date is not None:
            raise ValidationError("This book has been returned")

        return attrs

    def save(self, **kwargs):
        borrowing = self.instance
        borrowing.actual_return_date = timezone.now().date()
        borrowing.save()

        book = borrowing.book
        book.inventory += 1
        book.save()

        return borrowing
