from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestRequestViewSet, TestBookingViewSet, TestResultViewSet, TestPaymentViewSet, TestCollateralViewSet

router = DefaultRouter()
router.register(r'requests', TestRequestViewSet, basename='test-request')
router.register(r'bookings', TestBookingViewSet, basename='test-booking')
router.register(r'results', TestResultViewSet, basename='test-result')
router.register(r'payments', TestPaymentViewSet, basename='test-payment')
router.register(r'collaterals', TestCollateralViewSet, basename='test-collateral')

urlpatterns = [
    path('api/', include(router.urls)),
] 