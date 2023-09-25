from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from book.models import Book
from book.serializers import BookSerializer

BOOK_URL = reverse("book:book-list")


def sample_book(**params):
    defaults = {
        "title": "Test Book",
        "author": "Random Author",
        "cover": "Hard",
        "inventory": 10,
        "daily_free": 5,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def detail_url(book_id: int):
    return reverse("book:book-detail", args=[book_id])


class BookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.book = {
            "title": "Test Book",
            "author": "Random Author",
            "cover": "S",
            "inventory": 10,
            "daily_free": 5,
        }

    def test_list_book(self):
        sample_book()
        res = self.client.get(BOOK_URL)
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_book(self):
        book = sample_book()
        res = self.client.get(detail_url(book.id))
        serializer = BookSerializer(book, many=False)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_for_unauthenticated(self):
        res = self.client.post(BOOK_URL, self.book)

        self.assertEqual(res.status_code, 401)

    def test_create_book_for_user(self):
        self.user = get_user_model().objects.create_user(
            email="test@mail.com",
            password="12345randompass"
        )
        self.client.force_authenticate(self.user)
        res = self.client.post(BOOK_URL, self.book)

        self.assertEqual(res.status_code, 403)

    def test_create_book_for_admin(self):
        self.user = get_user_model().objects.create_user(
            email="test@mail.com",
            password="12345randompass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)
        res = self.client.post(BOOK_URL, self.book)

        self.assertEqual(res.status_code, 201)
