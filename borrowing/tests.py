import os
from datetime import timedelta

import stripe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from dotenv import load_dotenv

from rest_framework.test import APIClient

from book.models import Book
from borrowing.models import Borrowing

BORROWING_URL = reverse("borrowing:borrowings-list")
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


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


def sample_borrowing(**params):
    defaults = {
        "expected_return_date": timezone.now().date() + timedelta(days=3),
        "book_id": 1,
    }
    defaults.update(**params)
    return Borrowing.objects.create(**defaults)


class BorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@mail.com",
            password="12345randompass"
        )
        self.admin = get_user_model().objects.create_user(
            email="admint@mail.com",
            password="12345randompassadmin",
            is_staff=True
        )

    def test_borrowing_list_auth_required(self):
        res = self.client.get(BORROWING_URL)

        self.assertEqual(res.status_code, 401)

    def test_create_new_borrowing(self):
        user = self.user
        self.client.force_authenticate(user)
        sample_book()
        borrowing = {
            "expected_return_date": timezone.now() + timedelta(days=3),
            "book": 1,
            "user": user.id
        }
        res = self.client.post(BORROWING_URL, borrowing)

        self.assertEqual(res.status_code, 201)

    def test_list_borrowings_admin_see_all(self):
        sample_book()
        sample_book(title="Test 2 Book")
        self.client.force_authenticate(self.user)
        sample_borrowing(user=self.user)
        res_user = self.client.get(BORROWING_URL)
        self.client.force_authenticate(self.admin)
        sample_borrowing(user=self.admin, book_id=2)
        res_admin = self.client.get(BORROWING_URL)

        self.assertNotEqual(res_user.data, res_admin.data)

    def test_filter_borrowings_by_user_id_and_is_active(self):
        sample_book()
        sample_book(title="Test 2 Book")
        self.client.force_authenticate(self.admin)
        sample_borrowing(user=self.user)
        sample_borrowing(
            user=self.admin,
            book_id=2,
            actual_return_date=timezone.now()
        )
        res = self.client.get(BORROWING_URL)
        res_with_params = self.client.get(
            BORROWING_URL,
            {
                "user_id": "1",
                "is_active": "true"
            }
        )

        self.assertNotEqual(res.data, res_with_params.data)

    def test_user_cannot_borrow_if_book_not_available(self):
        book = sample_book(
            inventory=0,
        )

        borrowing = {
            "user": self.user.id,
            "book": book.id,
            "expected_return_date": timezone.now().date() + timedelta(days=14),
        }
        self.client.force_authenticate(user=self.user)
        res = self.client.post(BORROWING_URL, borrowing)

        self.assertEqual(
            res.data["book"][0].title(),
            "Currently Book Is Not Available"
        )
