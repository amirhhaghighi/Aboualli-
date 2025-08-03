from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from gympanel.models import Gym
from testprocess.models import TestBooking
from .models import Coach, CoachGymList, TestAssignment, CoachProfile, CoachTestAvailability
from .serializers import (
    CoachSerializer, CoachGymListSerializer, TestAssignmentSerializer,
    CoachDetailSerializer, TestAssignmentDetailSerializer,
    UserSerializer, GymSerializer, TestBookingSerializer,
    CoachProfileSerializer, CoachTestAvailabilitySerializer
)


class CoachViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت مربیان"""
    queryset = Coach.objects.all()
    serializer_class = CoachSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CoachDetailSerializer
        return CoachSerializer
    
    def get_queryset(self):
        queryset = Coach.objects.all()
        specialization = self.request.query_params.get('specialization', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if specialization:
            queryset = queryset.filter(specialization=specialization)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset
    
    @action(detail=True, methods=['get'])
    def gym_list(self, request, pk=None):
        """دریافت لیست باشگاه‌های یک مربی"""
        coach = self.get_object()
        gym_list = CoachGymList.objects.filter(coach=coach)
        serializer = CoachGymListSerializer(gym_list, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def test_assignments(self, request, pk=None):
        """دریافت تخصیص‌های تست یک مربی"""
        coach = self.get_object()
        assignments = TestAssignment.objects.filter(coach=coach)
        serializer = TestAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def accepted_tests(self, request, pk=None):
        """دریافت تست‌های پذیرفته شده یک مربی"""
        coach = self.get_object()
        assignments = TestAssignment.objects.filter(
            coach=coach,
            status='accepted'
        )
        serializer = TestAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """دریافت پروفایل مربی"""
        coach = self.get_object()
        try:
            profile = coach.profile
            serializer = CoachProfileSerializer(profile)
            return Response(serializer.data)
        except CoachProfile.DoesNotExist:
            return Response({
                'error': 'پروفایل یافت نشد'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def test_availability(self, request, pk=None):
        coach = self.get_object()
        availabilities = CoachTestAvailability.objects.filter(coach=coach)
        serializer = CoachTestAvailabilitySerializer(availabilities, many=True)
        return Response(serializer.data)


class CoachProfileViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت پروفایل مربیان"""
    queryset = CoachProfile.objects.all()
    serializer_class = CoachProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CoachProfile.objects.all()
        is_complete = self.request.query_params.get('is_profile_complete', None)
        
        if is_complete is not None:
            queryset = queryset.filter(is_profile_complete=is_complete.lower() == 'true')
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def complete_profile(self, request, pk=None):
        """تکمیل پروفایل مربی"""
        profile = self.get_object()
        
        # بررسی تکمیل فیلدهای ضروری
        required_fields = ['address', 'emergency_contact', 'certifications']
        missing_fields = [field for field in required_fields if not getattr(profile, field)]
        
        if missing_fields:
            return Response({
                'error': f'فیلدهای زیر باید تکمیل شوند: {", ".join(missing_fields)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        profile.is_profile_complete = True
        profile.save()
        
        serializer = self.get_serializer(profile)
        return Response({
            'message': 'پروفایل با موفقیت تکمیل شد',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class CoachGymListViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت لیست باشگاه‌های مربیان"""
    queryset = CoachGymList.objects.all()
    serializer_class = CoachGymListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CoachGymList.objects.all()
        coach_id = self.request.query_params.get('coach', None)
        gym_id = self.request.query_params.get('gym', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if coach_id:
            queryset = queryset.filter(coach_id=coach_id)
        if gym_id:
            queryset = queryset.filter(gym_id=gym_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset


class CoachTestAvailabilityViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت انتظار پذیرش تست‌ها"""
    queryset = CoachTestAvailability.objects.all()
    serializer_class = CoachTestAvailabilitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CoachTestAvailability.objects.all()
        coach_id = self.request.query_params.get('coach', None)
        date = self.request.query_params.get('date', None)
        is_available = self.request.query_params.get('is_available', None)
        
        if coach_id:
            queryset = queryset.filter(coach_id=coach_id)
        if date:
            queryset = queryset.filter(date=date)
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')
            
        return queryset


class TestAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت تخصیص تست‌ها"""
    queryset = TestAssignment.objects.all()
    serializer_class = TestAssignmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TestAssignmentDetailSerializer
        return TestAssignmentSerializer
    
    def get_queryset(self):
        queryset = TestAssignment.objects.all()
        coach_id = self.request.query_params.get('coach', None)
        status_filter = self.request.query_params.get('status', None)
        
        if coach_id:
            queryset = queryset.filter(coach_id=coach_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """پذیرش تست توسط مربی"""
        assignment = self.get_object()
        
        if assignment.status != 'pending':
            return Response({
                'error': 'فقط تخصیص‌های در انتظار قابل پذیرش هستند'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # بررسی اینکه آیا تست هنوز در وضعیت مناسب است
        test_booking = assignment.test_booking
        if test_booking.status != 'confirmed':
            return Response({
                'error': 'فقط رزروهای تایید شده قابل پذیرش هستند'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # پذیرش تست
        assignment.status = 'accepted'
        assignment.accepted_at = timezone.now()
        assignment.save()
        
        # بروزرسانی اطلاعات مربی در رزرو تست
        test_booking.coach_name = assignment.coach.user.get_full_name()
        test_booking.save()
        
        # رد سایر تخصیص‌های این تست
        other_assignments = TestAssignment.objects.filter(
            test_booking=test_booking,
            status='pending'
        ).exclude(id=assignment.id)
        
        for other_assignment in other_assignments:
            other_assignment.status = 'rejected'
            other_assignment.notes = 'تست توسط مربی دیگری پذیرفته شد'
            other_assignment.save()
        
        serializer = self.get_serializer(assignment)
        return Response({
            'message': 'تست با موفقیت پذیرفته شد',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """رد تست توسط مربی"""
        assignment = self.get_object()
        
        if assignment.status != 'pending':
            return Response({
                'error': 'فقط تخصیص‌های در انتظار قابل رد هستند'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        assignment.status = 'rejected'
        assignment.notes = request.data.get('notes', 'رد شده توسط مربی')
        assignment.save()
        
        serializer = self.get_serializer(assignment)
        return Response({
            'message': 'تست رد شد',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """لغو تست توسط مربی - بدون محدودیت زمانی"""
        assignment = self.get_object()
        
        if assignment.status not in ['accepted', 'pending']:
            return Response({
                'error': 'فقط تست‌های پذیرفته شده یا در انتظار قابل لغو هستند'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        assignment.status = 'cancelled'
        assignment.cancelled_at = timezone.now()
        assignment.cancellation_reason = request.data.get('reason', 'لغو شده توسط مربی')
        assignment.save()
        
        serializer = self.get_serializer(assignment)
        return Response({
            'message': 'تست با موفقیت لغو شد',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def pending_tests(self, request):
        """Get pending tests for assignment - only to active coaches"""
        pending_bookings = TestBooking.objects.filter(
            status='confirmed',
            assignment__isnull=True
        )
        
        # Group bookings by gym
        gym_assignments = {}
        for booking in pending_bookings:
            gym_id = booking.gym.id
            if gym_id not in gym_assignments:
                gym_assignments[gym_id] = []
            gym_assignments[gym_id].append(booking)
        
        created_assignments = []
        for gym, bookings in gym_assignments.items():
            # Get only active coaches for this gym
            coaches = Coach.objects.filter(
                gym_list__gym=gym,
                gym_list__is_active=True,
                is_active=True
            )
            
            for booking in bookings:
                for coach in coaches:
                    # Check if coach is available for this date
                    coach_availability = CoachTestAvailability.objects.filter(
                        coach=coach,
                        date=booking.booking_date,
                        is_available=True
                    ).first()
                    
                    # If no availability record exists, assume available (default behavior)
                    # If availability record exists and is_available=False, skip this coach
                    if coach_availability and not coach_availability.is_available:
                        continue
                    
                    assignment, created = TestAssignment.objects.get_or_create(
                        test_booking=booking,
                        coach=coach,
                        defaults={'status': 'pending'}
                    )
                    if created:
                        created_assignments.append(assignment)
        
        serializer = TestAssignmentSerializer(created_assignments, many=True)
        return Response({
            'message': f'{len(created_assignments)} تخصیص جدید ایجاد شد',
            'assignments': serializer.data
        }, status=status.HTTP_200_OK)
