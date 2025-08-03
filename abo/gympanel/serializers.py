from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Gym, GymCapacity, MemberAttendance, GymSchedule, SportTest, TestReservation, GymTestAvailability


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class GymSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gym
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class GymCapacitySerializer(serializers.ModelSerializer):
    gym_name = serializers.CharField(source='gym.name', read_only=True)
    
    class Meta:
        model = GymCapacity
        fields = '__all__'
        read_only_fields = ['created_at']


class MemberAttendanceSerializer(serializers.ModelSerializer):
    gym_name = serializers.CharField(source='gym.name', read_only=True)
    member_name = serializers.CharField(source='member.get_full_name', read_only=True)
    
    class Meta:
        model = MemberAttendance
        fields = '__all__'
        read_only_fields = ['created_at']


class GymScheduleSerializer(serializers.ModelSerializer):
    gym_name = serializers.CharField(source='gym.name', read_only=True)
    
    class Meta:
        model = GymSchedule
        fields = '__all__'


class GymTestAvailabilitySerializer(serializers.ModelSerializer):
    gym_name = serializers.CharField(source='gym.name', read_only=True)
    
    class Meta:
        model = GymTestAvailability
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SportTestSerializer(serializers.ModelSerializer):
    gym_name = serializers.CharField(source='gym.name', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    is_private_display = serializers.CharField(source='get_is_private_display', read_only=True)
    
    class Meta:
        model = SportTest
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class TestReservationSerializer(serializers.ModelSerializer):
    gym_name = serializers.CharField(source='gym.name', read_only=True)
    sport_test_name = serializers.CharField(source='sport_test.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TestReservation
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# Serializers for nested data
class GymDetailSerializer(serializers.ModelSerializer):
    capacities = GymCapacitySerializer(many=True, read_only=True)
    schedules = GymScheduleSerializer(many=True, read_only=True)
    sport_tests = SportTestSerializer(many=True, read_only=True)
    test_availabilities = GymTestAvailabilitySerializer(many=True, read_only=True)
    
    class Meta:
        model = Gym
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SportTestDetailSerializer(serializers.ModelSerializer):
    gym = GymSerializer(read_only=True)
    reservations = TestReservationSerializer(many=True, read_only=True)
    
    class Meta:
        model = SportTest
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at'] 