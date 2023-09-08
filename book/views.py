from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny

from book.models import Book
from book.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminUser,)

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = (AllowAny,)
        return super(BookViewSet, self).get_permissions()
