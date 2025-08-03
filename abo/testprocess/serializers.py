from rest_framework import serializers
from django.contrib.auth.models import User
from gympanel.models import Gym, SportTest
from .models import TestRequest, TestBooking, TestResult, TestCollateral, TestPayment


class UserSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل User"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name']
        read_only_fields = ['id']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class GymSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل Gym"""
    class Meta:
        model = Gym
        fields = ['id', 'name', 'address', 'phone', 'email', 'is_active']
        read_only_fields = ['id']


class SportTestSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل SportTest"""
    gym = GymSerializer(read_only=True)
    
    class Meta:
        model = SportTest
        fields = ['id', 'name', 'description', 'duration', 'price', 'is_active', 'is_private', 'gym']
        read_only_fields = ['id']


class TestPaymentSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل TestPayment"""
    user = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TestPayment
        fields = [
            'id', 'user', 'amount', 'status', 'status_display', 'payment_method',
            'reference_id', 'notes', 'paid_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestPaymentCreateSerializer(serializers.ModelSerializer):
    """سریالایزر برای ایجاد TestPayment جدید"""
    class Meta:
        model = TestPayment
        fields = [
            'amount', 'payment_method', 'reference_id', 'notes'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['test_request'] = self.context['test_request']
        return super().create(validated_data)


class TestCollateralSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل TestCollateral"""
    user = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TestCollateral
        fields = [
            'id', 'user', 'token_amount', 'status', 'status_display',
            'locked_at', 'released_at', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'locked_at', 'created_at', 'updated_at']


class TestCollateralCreateSerializer(serializers.ModelSerializer):
    """سریالایزر برای ایجاد TestCollateral جدید"""
    class Meta:
        model = TestCollateral
        fields = [
            'token_amount', 'notes'
        ]
    
    def validate_token_amount(self, value):
        """بررسی موجودی توکن کافی برای وثیقه"""
        user = self.context['request'].user
        try:
            token_wallet = user.token_wallet
            if token_wallet.balance < value:
                raise serializers.ValidationError("موجودی توکن کافی برای وثیقه وجود ندارد")
        except:
            raise serializers.ValidationError("کیف پول توکن یافت نشد")
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['test_request'] = self.context['test_request']
        return super().create(validated_data)


class TestRequestSerializer(serializers.ModelSerializer):
    """سریالایزر اصلی برای مدل TestRequest"""
    user = UserSerializer(read_only=True)
    sport_test = SportTestSerializer(read_only=True)
    preferred_gyms = GymSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TestRequest
        fields = [
            'id', 'user', 'sport_test', 'preferred_gyms', 'start_date', 'end_date',
            'start_time', 'end_time', 'status', 'status_display', 'notes',
            'collateral_required', 'collateral_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestRequestDetailSerializer(serializers.ModelSerializer):
    """سریالایزر جزئیات برای مدل TestRequest"""
    user = UserSerializer(read_only=True)
    sport_test = SportTestSerializer(read_only=True)
    preferred_gyms = GymSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TestRequest
        fields = [
            'id', 'user', 'sport_test', 'preferred_gyms', 'start_date', 'end_date',
            'start_time', 'end_time', 'status', 'status_display', 'notes',
            'collateral_required', 'collateral_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestRequestCreateSerializer(serializers.ModelSerializer):
    """سریالایزر برای ایجاد TestRequest جدید"""
    class Meta:
        model = TestRequest
        fields = [
            'sport_test', 'preferred_gyms', 'start_date', 'end_date',
            'start_time', 'end_time', 'notes', 'collateral_required', 'collateral_amount'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TestBookingSerializer(serializers.ModelSerializer):
    """سریالایزر اصلی برای مدل TestBooking"""
    test_request = TestRequestSerializer(read_only=True)
    gym = GymSerializer(read_only=True)
    sport_test = SportTestSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TestBooking
        fields = [
            'id', 'test_request', 'gym', 'sport_test', 'user', 'booking_date',
            'start_time', 'end_time', 'status', 'status_display', 'coach_name',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestBookingDetailSerializer(serializers.ModelSerializer):
    """سریالایزر جزئیات برای مدل TestBooking"""
    test_request = TestRequestDetailSerializer(read_only=True)
    gym = GymSerializer(read_only=True)
    sport_test = SportTestSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TestBooking
        fields = [
            'id', 'test_request', 'gym', 'sport_test', 'user', 'booking_date',
            'start_time', 'end_time', 'status', 'status_display', 'coach_name',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestResultSerializer(serializers.ModelSerializer):
    """سریالایزر اصلی برای مدل TestResult"""
    test_booking = TestBookingSerializer(read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    
    class Meta:
        model = TestResult
        fields = [
            'id', 'test_booking', 'result', 'result_display', 'score', 'feedback',
            'coach_notes', 'completed_at', 'reward_given', 'reward_amount', 'test_type',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reward_given', 'reward_amount', 'created_at', 'updated_at']


class TestResultCreateSerializer(serializers.ModelSerializer):
    """سریالایزر برای ایجاد TestResult جدید"""
    class Meta:
        model = TestResult
        fields = [
            'test_booking', 'result', 'score', 'feedback', 'coach_notes', 'completed_at', 'test_type'
        ]
    
    def validate(self, data):
        # بررسی اینکه آیا برای این رزرو قبلاً نتیجه ثبت شده است
        if TestResult.objects.filter(test_booking=data['test_booking']).exists():
            raise serializers.ValidationError("برای این رزرو قبلاً نتیجه ثبت شده است")
        return data


class TestResultUpdateSerializer(serializers.ModelSerializer):
    """سریالایزر برای بروزرسانی TestResult"""
    class Meta:
        model = TestResult
        fields = [
            'result', 'score', 'feedback', 'coach_notes', 'completed_at', 'test_type'
        ] 