from rest_framework import serializers

from borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):

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
