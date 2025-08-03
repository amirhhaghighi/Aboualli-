from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TokenWalletViewSet, 
    TokenOrderViewSet, 
    TokenTransactionViewSet, 
    TokenRewardViewSet,
    TokenRewardHistoryViewSet
)

router = DefaultRouter()
router.register(r'wallets', TokenWalletViewSet, basename='token-wallet')
router.register(r'orders', TokenOrderViewSet, basename='token-order')
router.register(r'transactions', TokenTransactionViewSet, basename='token-transaction')
router.register(r'rewards', TokenRewardViewSet, basename='token-reward')
router.register(r'reward-history', TokenRewardHistoryViewSet, basename='token-reward-history')

app_name = 'tokenwallet'

urlpatterns = [
    path('api/', include(router.urls)),
]
