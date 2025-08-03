from rest_framework import viewsets, status
from django.db import models
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from .models import TokenWallet, TokenOrder, TokenTransaction, TokenReward, TokenRewardHistory
from .serializers import (
    TokenWalletSerializer, TokenOrderSerializer, TokenTransactionSerializer,
    TokenRewardSerializer, TokenRewardHistorySerializer, TokenOrderCreateSerializer,
    TokenWalletBalanceSerializer, TokenOrderSummarySerializer
)


class TokenWalletViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت کیف پول توکن"""
    serializer_class = TokenWalletSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TokenWallet.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_wallet(self, request):
        """دریافت کیف پول توکن کاربر"""
        wallet, created = TokenWallet.objects.get_or_create(user=request.user)
        serializer = TokenWalletSerializer(wallet)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def balance(self, request):
        """دریافت موجودی کیف پول توکن"""
        wallet, created = TokenWallet.objects.get_or_create(user=request.user)
        serializer = TokenWalletBalanceSerializer(wallet)
        return Response(serializer.data)


class TokenOrderViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت سفارشات توکن"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TokenOrder.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TokenOrderCreateSerializer
        return TokenOrderSerializer
    
    def create(self, request, *args, **kwargs):
        """ایجاد سفارش جدید و اجرای موتور تطبیق"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            # ایجاد سفارش
            order = serializer.save()
            
            # اجرای موتور تطبیق FIFO
            self._execute_fifo_matching(order)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def _execute_fifo_matching(self, new_order):
        """موتور تطبیق FIFO"""
        if new_order.order_type == 'buy':
            # جستجوی سفارشات فروش موجود
            sell_orders = TokenOrder.objects.filter(
                order_type='sell',
                status='pending',
                remaining_amount__gt=0
            ).order_by('created_at')  # FIFO
            
            for sell_order in sell_orders:
                if new_order.remaining_amount <= 0:
                    break
                
                # محاسبه مقدار قابل تطبیق
                match_amount = min(new_order.remaining_amount, sell_order.remaining_amount)
                
                # ایجاد تراکنش
                self._create_transaction(new_order, sell_order, match_amount)
                
                # بروزرسانی سفارشات
                self._update_order_status(new_order, sell_order, match_amount)
        
        elif new_order.order_type == 'sell':
            # جستجوی سفارشات خرید موجود
            buy_orders = TokenOrder.objects.filter(
                order_type='buy',
                status='pending',
                remaining_amount__gt=0
            ).order_by('created_at')  # FIFO
            
            for buy_order in buy_orders:
                if new_order.remaining_amount <= 0:
                    break
                
                # محاسبه مقدار قابل تطبیق
                match_amount = min(new_order.remaining_amount, buy_order.remaining_amount)
                
                # ایجاد تراکنش
                self._create_transaction(buy_order, new_order, match_amount)
                
                # بروزرسانی سفارشات
                self._update_order_status(buy_order, new_order, match_amount)
    
    def _create_transaction(self, buy_order, sell_order, amount):
        """ایجاد تراکنش تطبیق شده"""
        # قیمت ثابت
        token_price = 1000
        total_value = amount * token_price
        
        # ایجاد تراکنش
        transaction = TokenTransaction.objects.create(
            buyer=buy_order.user,
            seller=sell_order.user,
            buy_order=buy_order,
            sell_order=sell_order,
            token_amount=amount,
            token_price=token_price,
            total_value=total_value
        )
        
        # بروزرسانی موجودی‌ها
        self._update_wallets(buy_order.user, sell_order.user, amount, total_value)
        
        return transaction
    
    def _update_wallets(self, buyer, seller, token_amount, total_value):
        """بروزرسانی موجودی کیف پول‌ها"""
        # کاهش موجودی فیات خریدار
        buyer_fiat_wallet = buyer.fiat_wallet
        buyer_fiat_wallet.subtract_balance(total_value)
        
        # افزایش موجودی فیات فروشنده
        seller_fiat_wallet = seller.fiat_wallet
        seller_fiat_wallet.add_balance(total_value)
        
        # افزایش موجودی توکن خریدار
        buyer_token_wallet, _ = TokenWallet.objects.get_or_create(user=buyer)
        buyer_token_wallet.add_balance(token_amount)
        
        # کاهش موجودی توکن فروشنده
        seller_token_wallet, _ = TokenWallet.objects.get_or_create(user=seller)
        seller_token_wallet.subtract_balance(token_amount)
    
    def _update_order_status(self, buy_order, sell_order, matched_amount):
        """بروزرسانی وضعیت سفارشات"""
        # بروزرسانی سفارش خرید
        buy_order.remaining_amount -= matched_amount
        if buy_order.remaining_amount == 0:
            buy_order.status = 'completed'
        else:
            buy_order.status = 'partial'
        buy_order.save()
        
        # بروزرسانی سفارش فروش
        sell_order.remaining_amount -= matched_amount
        if sell_order.remaining_amount == 0:
            sell_order.status = 'completed'
        else:
            sell_order.status = 'partial'
        sell_order.save()
    
    @action(detail=False, methods=['get'])
    def order_book(self, request):
        """دریافت کتاب سفارشات"""
        buy_orders = TokenOrder.objects.filter(
            order_type='buy',
            status='pending',
            remaining_amount__gt=0
        ).order_by('-created_at')[:10]
        
        sell_orders = TokenOrder.objects.filter(
            order_type='sell',
            status='pending',
            remaining_amount__gt=0
        ).order_by('created_at')[:10]
        
        return Response({
            'buy_orders': TokenOrderSummarySerializer(buy_orders, many=True).data,
            'sell_orders': TokenOrderSummarySerializer(sell_orders, many=True).data
        })


class TokenTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet برای مشاهده تراکنش‌های توکن"""
    serializer_class = TokenTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return TokenTransaction.objects.filter(
            models.Q(buyer=user) | models.Q(seller=user)
        )
    
    @action(detail=False, methods=['get'])
    def my_transactions(self, request):
        """دریافت تراکنش‌های کاربر"""
        user = request.user
        transactions = TokenTransaction.objects.filter(
            models.Q(buyer=user) | models.Q(seller=user)
        ).order_by('-created_at')
        
        serializer = TokenTransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class TokenRewardViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet برای مشاهده جایزه‌های توکن"""
    serializer_class = TokenRewardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TokenReward.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def my_rewards(self, request):
        """دریافت جایزه‌های کاربر"""
        user = request.user
        rewards = TokenRewardHistory.objects.filter(user=user).order_by('-created_at')
        
        serializer = TokenRewardHistorySerializer(rewards, many=True)
        return Response(serializer.data)


class TokenRewardHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet برای مشاهده تاریخچه جایزه‌های توکن"""
    serializer_class = TokenRewardHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TokenRewardHistory.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_history(self, request):
        """دریافت تاریخچه جایزه‌های کاربر"""
        user = request.user
        history = TokenRewardHistory.objects.filter(user=user).order_by('-created_at')
        
        serializer = TokenRewardHistorySerializer(history, many=True)
        return Response(serializer.data)

