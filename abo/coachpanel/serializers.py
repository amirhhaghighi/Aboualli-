from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Coach, CoachProfile, CoachGymList, CoachTestAvailability, TestAssignment
from gympanel.models import Gym
from testprocess.models import TestBooking


class UserSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل User"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name']
        read_only_fields = ['id']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class CoachSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل Coach"""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    specialization_display = serializers.CharField(source='get_specialization_display', read_only=True)
    
    class Meta:
        model = Coach
        fields = [
            'id', 'user', 'user_id', 'specialization', 'specialization_display',
            'experience_years', 'certification', 'bio', 'hourly_rate',
            'is_active', 'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CoachProfileSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل CoachProfile"""
    coach = CoachSerializer(read_only=True)
    coach_id = serializers.PrimaryKeyRelatedField(
        queryset=Coach.objects.all(),
        source='coach',
        write_only=True
    )
    
    class Meta:
        model = CoachProfile
        fields = [
            'id', 'coach', 'coach_id', 'phone', 'address', 'education',
            'achievements', 'social_media', 'profile_picture',
            'is_profile_complete', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GymSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل Gym"""
    class Meta:
        model = Gym
        fields = ['id', 'name', 'address', 'phone']


class CoachGymListSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل CoachGymList"""
    coach = CoachSerializer(read_only=True)
    coach_id = serializers.PrimaryKeyRelatedField(
        queryset=Coach.objects.all(),
        source='coach',
        write_only=True
    )
    gym = GymSerializer(read_only=True)
    gym_id = serializers.PrimaryKeyRelatedField(
        queryset=Gym.objects.all(),
        source='gym',
        write_only=True
    )
    
    class Meta:
        model = CoachGymList
        fields = [
            'id', 'coach', 'coach_id', 'gym', 'gym_id', 'position',
            'start_date', 'end_date', 'is_active', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CoachTestAvailabilitySerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل CoachTestAvailability"""
    coach = CoachSerializer(read_only=True)
    coach_id = serializers.PrimaryKeyRelatedField(
        queryset=Coach.objects.all(),
        source='coach',
        write_only=True
    )
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = CoachTestAvailability
        fields = [
            'id', 'coach', 'coach_id', 'day_of_week', 'day_of_week_display',
            'start_time', 'end_time', 'is_available', 'max_tests_per_day',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestBookingSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل TestBooking"""
    class Meta:
        model = TestBooking
        fields = ['id', 'sport_test', 'member', 'booking_date', 'status']


class TestAssignmentSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل TestAssignment"""
    coach = CoachSerializer(read_only=True)
    coach_id = serializers.PrimaryKeyRelatedField(
        queryset=Coach.objects.all(),
        source='coach',
        write_only=True
    )
    test_booking = TestBookingSerializer(read_only=True)
    test_booking_id = serializers.PrimaryKeyRelatedField(
        queryset=TestBooking.objects.all(),
        source='test_booking',
        write_only=True
    )
    assigned_by = UserSerializer(read_only=True)
    assigned_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_by',
        write_only=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TestAssignment
        fields = [
            'id', 'test_booking', 'test_booking_id', 'coach', 'coach_id',
            'assigned_by', 'assigned_by_id', 'status', 'status_display',
            'assigned_at', 'accepted_at', 'rejected_at', 'rejection_reason',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'assigned_at', 'created_at', 'updated_at']


# سریالایزرهای ترکیبی برای نمایش اطلاعات کامل
class CoachDetailSerializer(serializers.ModelSerializer):
    """سریالایزر کامل برای نمایش جزئیات مربی"""
    user = UserSerializer(read_only=True)
    profile = CoachProfileSerializer(read_only=True)
    gym_list = CoachGymListSerializer(many=True, read_only=True)
    test_availabilities = CoachTestAvailabilitySerializer(many=True, read_only=True)
    specialization_display = serializers.CharField(source='get_specialization_display', read_only=True)
    
    class Meta:
        model = Coach
        fields = [
            'id', 'user', 'specialization', 'specialization_display',
            'experience_years', 'certification', 'bio', 'hourly_rate',
            'is_active', 'is_verified', 'profile', 'gym_list',
            'test_availabilities', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CoachListSerializer(serializers.ModelSerializer):
    """سریالایزر برای لیست مربیان"""
    user = UserSerializer(read_only=True)
    specialization_display = serializers.CharField(source='get_specialization_display', read_only=True)
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = Coach
        fields = [
            'id', 'user', 'specialization', 'specialization_display',
            'experience_years', 'hourly_rate', 'is_active', 'is_verified',
            'profile_picture', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_profile_picture(self, obj):
        if hasattr(obj, 'profile') and obj.profile.profile_picture:
            return obj.profile.profile_picture.url
        return None


class TestAssignmentDetailSerializer(serializers.ModelSerializer):
    """سریالایزر کامل برای نمایش جزئیات تخصیص تست"""
    coach = CoachDetailSerializer(read_only=True)
    test_booking = TestBookingSerializer(read_only=True)
    assigned_by = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TestAssignment
        fields = [
            'id', 'test_booking', 'coach', 'assigned_by', 'status',
            'status_display', 'assigned_at', 'accepted_at', 'rejected_at',
            'rejection_reason', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'assigned_at', 'created_at', 'updated_at']
