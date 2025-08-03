from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FiatWalletViewSet, FiatTransactionViewSet, FiatDepositViewSet, FiatWithdrawalViewSet

router = DefaultRouter()
router.register(r'wallets', FiatWalletViewSet, basename='fiat-wallet')
router.register(r'transactions', FiatTransactionViewSet, basename='fiat-transaction')
router.register(r'deposits', FiatDepositViewSet, basename='fiat-deposit')
router.register(r'withdrawals', FiatWithdrawalViewSet, basename='fiat-withdrawal')

urlpatterns = [
    path('api/', include(router.urls)),
] 