from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Gym, GymCapacity, MemberAttendance, GymSchedule, SportTest, TestReservation, GymTestAvailability
from .serializers import (
    GymSerializer, GymDetailSerializer, GymCapacitySerializer, MemberAttendanceSerializer,
    GymScheduleSerializer, SportTestSerializer, SportTestDetailSerializer,
    TestReservationSerializer, GymTestAvailabilitySerializer
)


class GymViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت باشگاه‌ها"""
    queryset = Gym.objects.all()
    serializer_class = GymSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GymDetailSerializer
        return GymSerializer
    
    def get_queryset(self):
        queryset = Gym.objects.filter(is_active=True)
        name = self.request.query_params.get('name', None)
        
        if name:
            queryset = queryset.filter(name__icontains=name)
            
        return queryset
    
    @action(detail=True, methods=['get'])
    def sport_tests(self, request, pk=None):
        """دریافت تست‌های ورزشی یک باشگاه"""
        gym = self.get_object()
        tests = SportTest.objects.filter(gym=gym, is_active=True)
        serializer = SportTestSerializer(tests, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """دریافت برنامه باشگاه"""
        gym = self.get_object()
        schedules = GymSchedule.objects.filter(gym=gym)
        serializer = GymScheduleSerializer(schedules, many=True)
        return Response(serializer.data)


class GymCapacityViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت ظرفیت باشگاه‌ها"""
    queryset = GymCapacity.objects.all()
    serializer_class = GymCapacitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = GymCapacity.objects.filter(is_active=True)
        gym_id = self.request.query_params.get('gym', None)
        
        if gym_id:
            queryset = queryset.filter(gym_id=gym_id)
            
        return queryset


class MemberAttendanceViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت حضور اعضا"""
    serializer_class = MemberAttendanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MemberAttendance.objects.filter(member=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_attendance(self, request):
        """دریافت حضور کاربر"""
        attendances = MemberAttendance.objects.filter(
            member=request.user,
            is_active=True
        ).select_related('gym')
        
        serializer = MemberAttendanceSerializer(attendances, many=True)
        return Response(serializer.data)


class GymScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت برنامه باشگاه‌ها"""
    queryset = GymSchedule.objects.all()
    serializer_class = GymScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = GymSchedule.objects.all()
        gym_id = self.request.query_params.get('gym', None)
        day = self.request.query_params.get('day', None)
        
        if gym_id:
            queryset = queryset.filter(gym_id=gym_id)
        if day:
            queryset = queryset.filter(day_of_week=day)
            
        return queryset


class SportTestViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت تست‌های ورزشی"""
    queryset = SportTest.objects.all()
    serializer_class = SportTestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SportTestDetailSerializer
        return SportTestSerializer
    
    def get_queryset(self):
        queryset = SportTest.objects.filter(is_active=True)
        gym_id = self.request.query_params.get('gym', None)
        difficulty = self.request.query_params.get('difficulty', None)
        is_private = self.request.query_params.get('is_private', None)
        
        if gym_id:
            queryset = queryset.filter(gym_id=gym_id)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if is_private is not None:
            queryset = queryset.filter(is_private=is_private.lower() == 'true')
            
        return queryset
    
    @action(detail=True, methods=['get'])
    def reservations(self, request, pk=None):
        """دریافت رزروهای یک تست"""
        test = self.get_object()
        reservations = TestReservation.objects.filter(sport_test=test)
        serializer = TestReservationSerializer(reservations, many=True)
        return Response(serializer.data)


class TestReservationViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت رزروهای تست"""
    serializer_class = TestReservationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TestReservation.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def confirm_reservation(self, request, pk=None):
        """تایید رزرو تست"""
        reservation = self.get_object()
        
        if reservation.status != 'pending':
            return Response({
                'error': 'فقط رزروهای در انتظار قابل تایید هستند'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reservation.status = 'confirmed'
        reservation.save()
        
        serializer = self.get_serializer(reservation)
        return Response({
            'message': 'رزرو با موفقیت تایید شد',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def cancel_reservation(self, request, pk=None):
        """لغو رزرو تست"""
        reservation = self.get_object()
        
        if reservation.status == 'cancelled':
            return Response({
                'error': 'این رزرو قبلاً لغو شده است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reservation.status = 'cancelled'
        reservation.save()
        
        serializer = self.get_serializer(reservation)
        return Response({
            'message': 'رزرو با موفقیت لغو شد',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class GymTestAvailabilityViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت پذیرش تست باشگاه‌ها"""
    queryset = GymTestAvailability.objects.all()
    serializer_class = GymTestAvailabilitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = GymTestAvailability.objects.all()
        gym_id = self.request.query_params.get('gym', None)
        date = self.request.query_params.get('date', None)
        is_available = self.request.query_params.get('is_available', None)
        
        if gym_id:
            queryset = queryset.filter(gym_id=gym_id)
        if date:
            queryset = queryset.filter(date=date)
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')
            
        return queryset
