from rest_framework import viewsets

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
