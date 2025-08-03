from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from .models import FiatWallet, FiatTransaction, FiatDeposit, FiatWithdrawal
from .serializers import (
    FiatWalletSerializer, FiatWalletDetailSerializer, WalletBalanceSerializer,
    FiatTransactionSerializer, FiatTransactionDetailSerializer,
    FiatDepositSerializer, FiatDepositDetailSerializer, DepositRequestSerializer,
    FiatWithdrawalSerializer, FiatWithdrawalDetailSerializer, WithdrawalRequestSerializer
)


class FiatWalletViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت کیف پول‌های فیات"""
    queryset = FiatWallet.objects.all()
    serializer_class = FiatWalletSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FiatWalletDetailSerializer
        elif self.action == 'list':
            return FiatWalletSerializer
        return FiatWalletSerializer
    
    def get_queryset(self):
        """فیلتر کردن کیف پول‌ها بر اساس کاربر"""
        if self.request.user.is_staff:
            return FiatWallet.objects.all()
        return FiatWallet.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        """نمایش موجودی کیف پول"""
        wallet = self.get_object()
        serializer = WalletBalanceSerializer(wallet)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_balance(self, request, pk=None):
        """افزودن موجودی به کیف پول (فقط برای ادمین)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'فقط ادمین می‌تواند موجودی اضافه کند'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        wallet = self.get_object()
        amount = request.data.get('amount')
        
        if not amount or amount <= 0:
            return Response(
                {'error': 'مبلغ باید بزرگتر از صفر باشد'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = Decimal(str(amount))
            with transaction.atomic():
                balance_before = wallet.balance
                wallet.add_balance(amount)
                balance_after = wallet.balance
                
                # ایجاد تراکنش
                FiatTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='deposit',
                    amount=amount,
                    balance_before=balance_before,
                    balance_after=balance_after,
                    status='completed',
                    description='افزودن موجودی توسط ادمین'
                )
            
            serializer = WalletBalanceSerializer(wallet)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'خطا در افزودن موجودی: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class FiatTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet برای مشاهده تراکنش‌های فیات"""
    queryset = FiatTransaction.objects.all()
    serializer_class = FiatTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FiatTransactionDetailSerializer
        return FiatTransactionSerializer
    
    def get_queryset(self):
        """فیلتر کردن تراکنش‌ها بر اساس کاربر"""
        if self.request.user.is_staff:
            return FiatTransaction.objects.all()
        return FiatTransaction.objects.filter(wallet__user=self.request.user)


class FiatDepositViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت واریزهای فیات"""
    queryset = FiatDeposit.objects.all()
    serializer_class = FiatDepositSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FiatDepositDetailSerializer
        elif self.action == 'create':
            return DepositRequestSerializer
        return FiatDepositSerializer
    
    def get_queryset(self):
        """فیلتر کردن واریزها بر اساس کاربر"""
        if self.request.user.is_staff:
            return FiatDeposit.objects.all()
        return FiatDeposit.objects.filter(wallet__user=self.request.user)
    
    def perform_create(self, serializer):
        """ایجاد درخواست واریز"""
        wallet = get_object_or_404(FiatWallet, user=self.request.user)
        serializer.save(wallet=wallet)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """تایید واریز (فقط برای ادمین)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'فقط ادمین می‌تواند واریز را تایید کند'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        deposit = self.get_object()
        
        if deposit.is_verified:
            return Response(
                {'error': 'این واریز قبلاً تایید شده است'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # تایید واریز
                deposit.is_verified = True
                deposit.verified_by = request.user
                deposit.verified_at = timezone.now()
                deposit.save()
                
                # افزودن موجودی به کیف پول
                wallet = deposit.wallet
                balance_before = wallet.balance
                wallet.add_balance(deposit.amount)
                balance_after = wallet.balance
                
                # ایجاد تراکنش
                FiatTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='deposit',
                    amount=deposit.amount,
                    balance_before=balance_before,
                    balance_after=balance_after,
                    status='completed',
                    reference_id=f'DEP-{deposit.id}',
                    description=f'واریز تایید شده - {deposit.get_payment_method_display()}'
                )
            
            serializer = FiatDepositDetailSerializer(deposit)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'خطا در تایید واریز: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class FiatWithdrawalViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت برداشت‌های فیات"""
    queryset = FiatWithdrawal.objects.all()
    serializer_class = FiatWithdrawalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FiatWithdrawalDetailSerializer
        elif self.action == 'create':
            return WithdrawalRequestSerializer
        return FiatWithdrawalSerializer
    
    def get_queryset(self):
        """فیلتر کردن برداشت‌ها بر اساس کاربر"""
        if self.request.user.is_staff:
            return FiatWithdrawal.objects.all()
        return FiatWithdrawal.objects.filter(wallet__user=self.request.user)
    
    def perform_create(self, serializer):
        """ایجاد درخواست برداشت"""
        wallet = get_object_or_404(FiatWallet, user=self.request.user)
        
        # بررسی موجودی کافی
        if wallet.balance < serializer.validated_data['amount']:
            raise serializers.ValidationError('موجودی کافی نیست')
        
        serializer.save(wallet=wallet)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """تایید برداشت (فقط برای ادمین)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'فقط ادمین می‌تواند برداشت را تایید کند'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        withdrawal = self.get_object()
        
        if withdrawal.is_approved:
            return Response(
                {'error': 'این برداشت قبلاً تایید شده است'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # بررسی موجودی کافی
                wallet = withdrawal.wallet
                if wallet.balance < withdrawal.amount:
                    return Response(
                        {'error': 'موجودی کیف پول کافی نیست'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # تایید برداشت
                withdrawal.is_approved = True
                withdrawal.approved_by = request.user
                withdrawal.approved_at = timezone.now()
                withdrawal.save()
                
                # کسر موجودی از کیف پول
                balance_before = wallet.balance
                wallet.subtract_balance(withdrawal.amount)
                balance_after = wallet.balance
                
                # ایجاد تراکنش
                FiatTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='withdrawal',
                    amount=withdrawal.amount,
                    balance_before=balance_before,
                    balance_after=balance_after,
                    status='completed',
                    reference_id=f'WTH-{withdrawal.id}',
                    description=f'برداشت تایید شده - {withdrawal.get_withdrawal_method_display()}'
                )
            
            serializer = FiatWithdrawalDetailSerializer(withdrawal)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'خطا در تایید برداشت: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """پردازش برداشت (فقط برای ادمین)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'فقط ادمین می‌تواند برداشت را پردازش کند'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        withdrawal = self.get_object()
        
        if not withdrawal.is_approved:
            return Response(
                {'error': 'برداشت باید ابتدا تایید شود'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if withdrawal.is_processed:
            return Response(
                {'error': 'این برداشت قبلاً پردازش شده است'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        withdrawal.is_processed = True
        withdrawal.processed_at = timezone.now()
        withdrawal.save()
        
        serializer = FiatWithdrawalDetailSerializer(withdrawal)
        return Response(serializer.data)
