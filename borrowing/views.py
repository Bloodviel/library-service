from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.models import Borrowing, Payment
from borrowing.notification_service import send_message
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    PaymentSerializer
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        return BorrowingSerializer

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(user_id=self.request.user.id)

        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if user_id:
            user_ids = self._params_to_ints(user_id)
            queryset = queryset.filter(user_id__in=user_ids)

        if is_active:
            if is_active == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    @action(
        methods=["PUT"],
        detail=True,
        url_path="return",
        permission_classes=(IsAuthenticated,)
    )
    def book_return(self, request, pk=None):
        """Endpoint for users to return book"""
        borrowing = self.get_object()
        book = borrowing.book
        if borrowing.actual_return_date is None:
            borrowing.actual_return_date = timezone.now().date()
            borrowing.save()
            message = (
                f"Borrowing:\n"
                f"{book}\n"
                f"Expected return date: {borrowing.expected_return_date}\n"
                f"Actual return data: {borrowing.actual_return_date}\n"
                f"Successful.\n"
                f"Have a nice day!"
            )
            send_message(message)
            book.inventory += 1
            book.save()
        else:
            raise ValidationError(
                "This book has been returned"
            )
        return Response(status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(borrowing__user=self.request.user)

        return queryset
