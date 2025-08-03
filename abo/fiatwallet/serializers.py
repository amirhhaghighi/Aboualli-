from rest_framework import serializers
from django.contrib.auth.models import User
from .models import FiatWallet, FiatTransaction, FiatDeposit, FiatWithdrawal


class UserSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل User"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name']
        read_only_fields = ['id']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class FiatWalletSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل FiatWallet"""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    balance_display = serializers.SerializerMethodField()
    
    class Meta:
        model = FiatWallet
        fields = [
            'id', 'user', 'user_id', 'balance', 'balance_display',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'balance', 'created_at', 'updated_at']
    
    def get_balance_display(self, obj):
        return obj.get_balance_display()


class FiatTransactionSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل FiatTransaction"""
    wallet = FiatWalletSerializer(read_only=True)
    wallet_id = serializers.PrimaryKeyRelatedField(
        queryset=FiatWallet.objects.all(),
        source='wallet',
        write_only=True
    )
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = FiatTransaction
        fields = [
            'id', 'wallet', 'wallet_id', 'transaction_type', 'transaction_type_display',
            'amount', 'balance_before', 'balance_after', 'status', 'status_display',
            'reference_id', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'balance_before', 'balance_after', 'created_at', 'updated_at']


class FiatDepositSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل FiatDeposit"""
    wallet = FiatWalletSerializer(read_only=True)
    wallet_id = serializers.PrimaryKeyRelatedField(
        queryset=FiatWallet.objects.all(),
        source='wallet',
        write_only=True
    )
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    verified_by = UserSerializer(read_only=True)
    verified_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='verified_by',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = FiatDeposit
        fields = [
            'id', 'wallet', 'wallet_id', 'amount', 'payment_method', 'payment_method_display',
            'bank_name', 'account_number', 'receipt_number', 'is_verified',
            'verified_by', 'verified_by_id', 'verified_at', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_verified', 'verified_at', 'created_at', 'updated_at']


class FiatWithdrawalSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل FiatWithdrawal"""
    wallet = FiatWalletSerializer(read_only=True)
    wallet_id = serializers.PrimaryKeyRelatedField(
        queryset=FiatWallet.objects.all(),
        source='wallet',
        write_only=True
    )
    withdrawal_method_display = serializers.CharField(source='get_withdrawal_method_display', read_only=True)
    approved_by = UserSerializer(read_only=True)
    approved_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='approved_by',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = FiatWithdrawal
        fields = [
            'id', 'wallet', 'wallet_id', 'amount', 'withdrawal_method', 'withdrawal_method_display',
            'bank_name', 'account_number', 'account_holder', 'is_approved', 'is_processed',
            'approved_by', 'approved_by_id', 'approved_at', 'processed_at', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_approved', 'is_processed', 'approved_at', 'processed_at', 'created_at', 'updated_at']


# سریالایزرهای ترکیبی برای نمایش اطلاعات کامل
class FiatWalletDetailSerializer(serializers.ModelSerializer):
    """سریالایزر کامل برای نمایش جزئیات کیف پول"""
    user = UserSerializer(read_only=True)
    transactions = FiatTransactionSerializer(many=True, read_only=True)
    deposits = FiatDepositSerializer(many=True, read_only=True)
    withdrawals = FiatWithdrawalSerializer(many=True, read_only=True)
    balance_display = serializers.SerializerMethodField()
    
    class Meta:
        model = FiatWallet
        fields = [
            'id', 'user', 'balance', 'balance_display', 'is_active',
            'transactions', 'deposits', 'withdrawals', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'balance', 'created_at', 'updated_at']
    
    def get_balance_display(self, obj):
        return obj.get_balance_display()


class FiatTransactionDetailSerializer(serializers.ModelSerializer):
    """سریالایزر کامل برای نمایش جزئیات تراکنش"""
    wallet = FiatWalletDetailSerializer(read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = FiatTransaction
        fields = [
            'id', 'wallet', 'transaction_type', 'transaction_type_display',
            'amount', 'balance_before', 'balance_after', 'status', 'status_display',
            'reference_id', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'balance_before', 'balance_after', 'created_at', 'updated_at']


class FiatDepositDetailSerializer(serializers.ModelSerializer):
    """سریالایزر کامل برای نمایش جزئیات واریز"""
    wallet = FiatWalletSerializer(read_only=True)
    verified_by = UserSerializer(read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = FiatDeposit
        fields = [
            'id', 'wallet', 'amount', 'payment_method', 'payment_method_display',
            'bank_name', 'account_number', 'receipt_number', 'is_verified',
            'verified_by', 'verified_at', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_verified', 'verified_at', 'created_at', 'updated_at']


class FiatWithdrawalDetailSerializer(serializers.ModelSerializer):
    """سریالایزر کامل برای نمایش جزئیات برداشت"""
    wallet = FiatWalletSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    withdrawal_method_display = serializers.CharField(source='get_withdrawal_method_display', read_only=True)
    
    class Meta:
        model = FiatWithdrawal
        fields = [
            'id', 'wallet', 'amount', 'withdrawal_method', 'withdrawal_method_display',
            'bank_name', 'account_number', 'account_holder', 'is_approved', 'is_processed',
            'approved_by', 'approved_at', 'processed_at', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_approved', 'is_processed', 'approved_at', 'processed_at', 'created_at', 'updated_at']


# سریالایزرهای مخصوص عملیات
class DepositRequestSerializer(serializers.ModelSerializer):
    """سریالایزر برای درخواست واریز"""
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = FiatDeposit
        fields = [
            'id', 'amount', 'payment_method', 'payment_method_display',
            'bank_name', 'account_number', 'receipt_number', 'notes',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WithdrawalRequestSerializer(serializers.ModelSerializer):
    """سریالایزر برای درخواست برداشت"""
    withdrawal_method_display = serializers.CharField(source='get_withdrawal_method_display', read_only=True)
    
    class Meta:
        model = FiatWithdrawal
        fields = [
            'id', 'amount', 'withdrawal_method', 'withdrawal_method_display',
            'bank_name', 'account_number', 'account_holder', 'notes',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WalletBalanceSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش موجودی کیف پول"""
    user = UserSerializer(read_only=True)
    balance_display = serializers.SerializerMethodField()
    
    class Meta:
        model = FiatWallet
        fields = ['id', 'user', 'balance', 'balance_display', 'is_active']
        read_only_fields = ['id', 'balance', 'is_active']
    
    def get_balance_display(self, obj):
        return obj.get_balance_display() 