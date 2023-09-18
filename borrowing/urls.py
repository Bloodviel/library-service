from rest_framework.routers import DefaultRouter

from borrowing.views import BorrowingViewSet, PaymentViewSet

router = DefaultRouter()
router.register("borrowings", BorrowingViewSet)
router.register("payments", PaymentViewSet)


urlpatterns = router.urls

app_name = "borrowing"
