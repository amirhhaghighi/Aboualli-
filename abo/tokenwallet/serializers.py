from rest_framework import serializers
from django.contrib.auth.models import User
from .models import TokenWallet, TokenOrder, TokenTransaction, TokenReward, TokenRewardHistory


class UserSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل User"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name']
        read_only_fields = ['id']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class TokenWalletSerializer(serializers.ModelSerializer):
    """سریالایزر اصلی برای مدل TokenWallet"""
    user = UserSerializer(read_only=True)
    balance_display = serializers.CharField(source='get_balance_display', read_only=True)
    
    class Meta:
        model = TokenWallet
        fields = [
            'id', 'user', 'balance', 'balance_display', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'balance', 'created_at', 'updated_at']


class TokenRewardSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل TokenReward"""
    test_type_display = serializers.CharField(source='get_test_type_display', read_only=True)
    
    class Meta:
        model = TokenReward
        fields = [
            'id', 'test_type', 'test_type_display', 'token_amount', 'is_active',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TokenOrderSerializer(serializers.ModelSerializer):
    """سریالایزر اصلی برای مدل TokenOrder"""
    user = UserSerializer(read_only=True)
    order_type_display = serializers.CharField(source='get_order_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TokenOrder
        fields = [
            'id', 'user', 'order_type', 'order_type_display', 'token_amount',
            'token_price', 'total_value', 'remaining_amount', 'status', 'status_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_value', 'remaining_amount', 'created_at', 'updated_at']


class TokenOrderCreateSerializer(serializers.ModelSerializer):
    """سریالایزر برای ایجاد TokenOrder جدید"""
    class Meta:
        model = TokenOrder
        fields = ['order_type', 'token_amount']
    
    def validate(self, data):
        """بررسی موجودی کافی برای سفارش"""
        user = self.context['request'].user
        order_type = data.get('order_type')
        token_amount = data.get('token_amount')
        
        if order_type == 'sell':
            # بررسی موجودی توکن برای فروش
            try:
                token_wallet = user.token_wallet
                if token_wallet.balance < token_amount:
                    raise serializers.ValidationError("موجودی توکن کافی برای فروش وجود ندارد")
            except TokenWallet.DoesNotExist:
                raise serializers.ValidationError("کیف پول توکن یافت نشد")
        
        elif order_type == 'buy':
            # بررسی موجودی فیات برای خرید
            try:
                fiat_wallet = user.fiat_wallet
                # قیمت ثابت (مثلاً 1000 ریال)
                token_price = 1000
                total_cost = token_amount * token_price
                if fiat_wallet.balance < total_cost:
                    raise serializers.ValidationError("موجودی ریال کافی برای خرید وجود ندارد")
            except:
                raise serializers.ValidationError("کیف پول فیات یافت نشد")
        
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        # قیمت ثابت
        validated_data['token_price'] = 1000
        return super().create(validated_data)


class TokenTransactionSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل TokenTransaction"""
    buyer = UserSerializer(read_only=True)
    seller = UserSerializer(read_only=True)
    
    class Meta:
        model = TokenTransaction
        fields = [
            'id', 'buyer', 'seller', 'buy_order', 'sell_order', 'token_amount',
            'token_price', 'total_value', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TokenRewardHistorySerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل TokenRewardHistory"""
    user = UserSerializer(read_only=True)
    test_type_display = serializers.CharField(source='get_test_type_display', read_only=True)
    
    class Meta:
        model = TokenRewardHistory
        fields = [
            'id', 'user', 'test_result', 'token_amount', 'test_type', 'test_type_display',
            'description', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TokenWalletBalanceSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش موجودی کیف پول توکن"""
    user = UserSerializer(read_only=True)
    balance_display = serializers.CharField(source='get_balance_display', read_only=True)
    
    class Meta:
        model = TokenWallet
        fields = ['id', 'user', 'balance', 'balance_display', 'is_active']


class TokenOrderSummarySerializer(serializers.ModelSerializer):
    """سریالایزر خلاصه سفارشات"""
    order_type_display = serializers.CharField(source='get_order_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TokenOrder
        fields = [
            'id', 'order_type', 'order_type_display', 'token_amount', 'token_price',
            'total_value', 'status', 'status_display', 'created_at'
        ] 