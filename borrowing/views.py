import stripe
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.models import Borrowing, Payment
from borrowing.notification_service import send_message
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer,
    PaymentSerializer,
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

        if self.action == "book_return":
            return BorrowingReturnSerializer

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
        serializer = self.get_serializer(borrowing, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"success": "Your book was successfully returned"},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=int,
                description="Filter by users id (ex. ?user_id=1,2)"
            ),
            OpenApiParameter(
                name="is_active",
                type=bool,
                description="Filter by is active (ex. ?is_active=true)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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

    @action(
        detail=True,
        methods=["GET"],
        url_path="success"
    )
    def payment_success(self, request, pk=None):
        """Endpoint to handle a successful payment"""
        payment = get_object_or_404(Payment, pk=pk)

        session = stripe.checkout.Session.retrieve(payment.session_id)
        if session.payment_status == "paid":
            payment.status = Payment.StatusChoices.PAID
            payment.save()

            message = (
                f"Payment {payment.id}: was successful.\n"
                f"Type: {payment.type}\n"
                f"Borrowing: {payment.borrowing}"
            )
            send_message(message)

            return Response(
                {"success": "Payment was successful."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Payment was not successful."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        methods=["GET"],
        detail=True,
        url_path="cancel"
    )
    def payment_cancel(self, request, pk=None):
        """Endpoint to handle a canceled payment"""
        return Response(
            "Cancel: payment canceled",
            status=status.HTTP_200_OK
        )
