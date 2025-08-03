from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from gympanel.models import Gym
from .models import (
    MembershipPlan, Membership, MembershipPayment, 
    MembershipReview, MembershipHistory, GymMembershipRequest
)


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


class MembershipPlanSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل MembershipPlan"""
    gym = GymSerializer(read_only=True)
    plan_type_display = serializers.CharField(source='get_plan_type_display', read_only=True)
    
    class Meta:
        model = MembershipPlan
        fields = [
            'id', 'gym', 'name', 'description', 'plan_type', 'plan_type_display',
            'duration_days', 'price', 'is_active', 'max_members', 'features',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MembershipPlanCreateSerializer(serializers.ModelSerializer):
    """سریالایزر برای ایجاد MembershipPlan جدید"""
    class Meta:
        model = MembershipPlan
        fields = [
            'gym', 'name', 'description', 'plan_type', 'duration_days',
            'price', 'is_active', 'max_members', 'features'
        ]


class MembershipSerializer(serializers.ModelSerializer):
    """سریالایزر اصلی برای مدل Membership"""
    user = UserSerializer(read_only=True)
    gym = GymSerializer(read_only=True)
    plan = MembershipPlanSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active_status = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Membership
        fields = [
            'id', 'user', 'gym', 'plan', 'status', 'status_display',
            'start_date', 'end_date', 'auto_renew', 'notes',
            'is_active_status', 'days_remaining', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_active_status(self, obj):
        return obj.is_active()
    
    def get_days_remaining(self, obj):
        return obj.days_remaining()


class MembershipCreateSerializer(serializers.ModelSerializer):
    """سریالایزر برای ایجاد Membership جدید"""
    class Meta:
        model = Membership
        fields = [
            'gym', 'plan', 'start_date', 'end_date', 'auto_renew', 'notes'
        ]
    
    def validate(self, data):
        """اعتبارسنجی تاریخ‌ها"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise serializers.ValidationError("تاریخ پایان باید بعد از تاریخ شروع باشد")
            
            if start_date < timezone.now().date():
                raise serializers.ValidationError("تاریخ شروع نمی‌تواند در گذشته باشد")
        
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MembershipPaymentSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل MembershipPayment"""
    user = UserSerializer(read_only=True)
    membership = MembershipSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = MembershipPayment
        fields = [
            'id', 'membership', 'user', 'amount', 'payment_method', 'payment_method_display',
            'status', 'status_display', 'reference_id', 'transaction_id', 'notes',
            'paid_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MembershipPaymentCreateSerializer(serializers.ModelSerializer):
    """سریالایزر برای ایجاد MembershipPayment جدید"""
    class Meta:
        model = MembershipPayment
        fields = [
            'membership', 'amount', 'payment_method', 'reference_id', 'transaction_id', 'notes'
        ]
    
    def validate_amount(self, value):
        """بررسی مبلغ پرداخت"""
        if value <= 0:
            raise serializers.ValidationError("مبلغ باید بیشتر از صفر باشد")
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MembershipReviewSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل MembershipReview"""
    user = UserSerializer(read_only=True)
    membership = MembershipSerializer(read_only=True)
    
    class Meta:
        model = MembershipReview
        fields = [
            'id', 'membership', 'user', 'rating', 'comment', 'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MembershipReviewCreateSerializer(serializers.ModelSerializer):
    """سریالایزر برای ایجاد MembershipReview جدید"""
    class Meta:
        model = MembershipReview
        fields = [
            'membership', 'rating', 'comment', 'is_public'
        ]
    
    def validate_rating(self, value):
        """بررسی امتیاز"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("امتیاز باید بین 1 تا 5 باشد")
        return value
    
    def validate(self, data):
        """بررسی اینکه کاربر فقط یک نظر برای هر عضویت داشته باشد"""
        membership = data.get('membership')
        user = self.context['request'].user
        
        if MembershipReview.objects.filter(membership=membership, user=user).exists():
            raise serializers.ValidationError("شما قبلاً برای این عضویت نظر داده‌اید")
        
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MembershipHistorySerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل MembershipHistory"""
    membership = MembershipSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = MembershipHistory
        fields = [
            'id', 'membership', 'action', 'action_display', 'description',
            'created_by', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class GymMembershipRequestSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل GymMembershipRequest"""
    user = UserSerializer(read_only=True)
    gym = GymSerializer(read_only=True)
    plan = MembershipPlanSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = GymMembershipRequest
        fields = [
            'id', 'user', 'gym', 'plan', 'status', 'status_display',
            'requested_start_date', 'notes', 'admin_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GymMembershipRequestCreateSerializer(serializers.ModelSerializer):
    """سریالایزر برای ایجاد GymMembershipRequest جدید"""
    class Meta:
        model = GymMembershipRequest
        fields = [
            'gym', 'plan', 'requested_start_date', 'notes'
        ]
    
    def validate_requested_start_date(self, value):
        """بررسی تاریخ شروع درخواستی"""
        if value < timezone.now().date():
            raise serializers.ValidationError("تاریخ شروع نمی‌تواند در گذشته باشد")
        return value
    
    def validate(self, data):
        """بررسی اینکه کاربر قبلاً درخواست عضویت در این باشگاه نداشته باشد"""
        user = self.context['request'].user
        gym = data.get('gym')
        
        if GymMembershipRequest.objects.filter(user=user, gym=gym, status='pending').exists():
            raise serializers.ValidationError("شما قبلاً درخواست عضویت در این باشگاه را ثبت کرده‌اید")
        
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data) 