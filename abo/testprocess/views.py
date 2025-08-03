from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from gympanel.models import Gym, SportTest, MemberAttendance, GymTestAvailability, TestReservation
from .models import TestRequest, TestBooking, TestResult, TestCollateral, TestPayment
from .serializers import (
    TestRequestSerializer, TestBookingSerializer, TestResultSerializer,
    TestRequestDetailSerializer, TestBookingDetailSerializer,
    UserSerializer, GymSerializer, SportTestSerializer,
    TestCollateralSerializer, TestPaymentSerializer,
    TestCollateralCreateSerializer, TestPaymentCreateSerializer
)
from django.db import models
from django.db import transaction


class TestRequestViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت درخواست‌های تست"""
    queryset = TestRequest.objects.all()
    serializer_class = TestRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TestRequestDetailSerializer
        return TestRequestSerializer
    
    def get_queryset(self):
        queryset = TestRequest.objects.all()
        user_id = self.request.query_params.get('user', None)
        status_filter = self.request.query_params.get('status', None)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def user_gym_memberships(self, request):
        """دریافت باشگاه‌هایی که کاربر عضو آن‌ها است"""
        from gympanel.models import MemberAttendance
        
        user = request.user
        memberships = MemberAttendance.objects.filter(
            member=user,
            is_active=True
        ).select_related('gym').distinct('gym')
        
        gym_data = []
        for membership in memberships:
            gym_data.append({
                'gym_id': membership.gym.id,
                'gym_name': membership.gym.name,
                'gym_address': membership.gym.address
            })
        
        return Response({
            'user_id': user.id,
            'username': user.username,
            'gym_memberships': gym_data
        })
    
    @action(detail=False, methods=['get'])
    def available_tests(self, request):
        """دریافت تست‌های قابل دسترس برای کاربر"""
        from gympanel.models import SportTest, MemberAttendance
        
        user = request.user
        gym_id = request.query_params.get('gym', None)
        
        # دریافت باشگاه‌هایی که کاربر عضو آن‌ها است
        user_gyms = MemberAttendance.objects.filter(
            member=user,
            is_active=True
        ).values_list('gym_id', flat=True).distinct()
        
        queryset = SportTest.objects.filter(is_active=True)
        
        if gym_id:
            # اگر باشگاه مشخص شده
            gym_id = int(gym_id)
            if gym_id in user_gyms:
                # کاربر عضو این باشگاه است - همه تست‌ها قابل دسترس
                queryset = queryset.filter(gym_id=gym_id)
            else:
                # کاربر عضو نیست - فقط تست‌های عمومی
                queryset = queryset.filter(gym_id=gym_id, is_private=False)
        else:
            # اگر باشگاه مشخص نشده
            # فیلتر بر اساس عضویت کاربر
            queryset = queryset.filter(
                models.Q(is_private=False) |
                models.Q(gym_id__in=user_gyms)
            )
        
        serializer = SportTestSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def _validate_test_request(self, test_request):
        """اعتبارسنجی درخواست تست"""
        # بررسی تاریخ‌ها
        if test_request.start_date < timezone.now().date():
            return False, "تاریخ شروع نمی‌تواند در گذشته باشد"
        
        if test_request.end_date < test_request.start_date:
            return False, "تاریخ پایان نمی‌تواند قبل از تاریخ شروع باشد"
        
        # بررسی ساعات
        if test_request.start_time >= test_request.end_time:
            return False, "ساعت پایان باید بعد از ساعت شروع باشد"
        
        return True, "درخواست معتبر است"
    
    @action(detail=True, methods=['post'])
    def process_booking(self, request, pk=None):
        """پردازش رزرو تست"""
        test_request = self.get_object()
        
        # اعتبارسنجی درخواست
        is_valid, message = self._validate_test_request(test_request)
        if not is_valid:
            return Response({
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # پردازش الگوریتم رزرو
        booking_result = self._process_booking_algorithm(test_request)
        
        if booking_result['success']:
            return Response({
                'message': 'رزرو با موفقیت انجام شد',
                'booking': booking_result['booking']
            })
        else:
            return Response({
                'error': booking_result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def _process_booking_algorithm(self, test_request):
        """الگوریتم پردازش رزرو"""
        # اینجا الگوریتم پیچیده رزرو قرار می‌گیرد
        # فعلاً یک نمونه ساده
        try:
            # انتخاب باشگاه (در اینجا ساده شده)
            gym = Gym.objects.filter(is_active=True).first()
            if not gym:
                return {'success': False, 'message': 'هیچ باشگاه فعالی یافت نشد'}
            
            # ایجاد رزرو
            booking = TestBooking.objects.create(
                test_request=test_request,
                gym=gym,
                sport_test=test_request.sport_test,
                user=test_request.user,
                booking_date=test_request.start_date,
                start_time=test_request.start_time,
                end_time=test_request.end_time
            )
            
            return {'success': True, 'booking': booking}
        except Exception as e:
            return {'success': False, 'message': str(e)}


class TestPaymentViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت پرداخت‌های تست"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TestPayment.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TestPaymentCreateSerializer
        return TestPaymentSerializer
    
    @action(detail=True, methods=['post'])
    def complete_payment(self, request, pk=None):
        """تکمیل پرداخت"""
        payment = self.get_object()
        
        if payment.status == 'completed':
            return Response({
                'error': 'این پرداخت قبلاً تکمیل شده است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            payment.status = 'completed'
            payment.paid_at = timezone.now()
            payment.save()
            
            # بروزرسانی وضعیت درخواست تست
            test_request = payment.test_request
            test_request.status = 'processing'
            test_request.save()
        
        serializer = TestPaymentSerializer(payment)
        return Response(serializer.data)


class TestCollateralViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت وثیقه‌های تست"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TestCollateral.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TestCollateralCreateSerializer
        return TestCollateralSerializer
    
    def create(self, request, *args, **kwargs):
        """ایجاد وثیقه جدید"""
        test_request_id = request.data.get('test_request_id')
        test_request = get_object_or_404(TestRequest, id=test_request_id)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            # قفل توکن‌ها
            user = request.user
            token_wallet, _ = user.token_wallet.objects.get_or_create(user=user)
            
            if token_wallet.balance < serializer.validated_data['token_amount']:
                return Response({
                    'error': 'موجودی توکن کافی نیست'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # کاهش موجودی توکن
            token_wallet.subtract_balance(serializer.validated_data['token_amount'])
            
            # ایجاد وثیقه
            collateral = serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def release_collateral(self, request, pk=None):
        """آزادسازی وثیقه"""
        collateral = self.get_object()
        
        if collateral.status == 'released':
            return Response({
                'error': 'این وثیقه قبلاً آزاد شده است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # آزادسازی توکن‌ها
            user = collateral.user
            token_wallet, _ = user.token_wallet.objects.get_or_create(user=user)
            token_wallet.add_balance(collateral.token_amount)
            
            # بروزرسانی وضعیت وثیقه
            collateral.status = 'released'
            collateral.released_at = timezone.now()
            collateral.save()
        
        serializer = TestCollateralSerializer(collateral)
        return Response(serializer.data)


class TestBookingViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت رزروهای تست"""
    queryset = TestBooking.objects.all()
    serializer_class = TestBookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TestBookingDetailSerializer
        return TestBookingSerializer
    
    def get_queryset(self):
        queryset = TestBooking.objects.all()
        user_id = self.request.query_params.get('user', None)
        status_filter = self.request.query_params.get('status', None)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset


class TestResultViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت نتایج تست"""
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = TestResult.objects.all()
        user_id = self.request.query_params.get('user', None)
        result_filter = self.request.query_params.get('result', None)
        
        if user_id:
            queryset = queryset.filter(test_booking__user_id=user_id)
        if result_filter:
            queryset = queryset.filter(result=result_filter)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        """ایجاد نتیجه تست جدید با بررسی پرداخت و وثیقه"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        test_booking = serializer.validated_data['test_booking']
        test_request = test_booking.test_request
        user = test_booking.user
        
        # بررسی پرداخت
        try:
            payment = test_request.payment
            if payment.status != 'completed':
                return Response({
                    'error': 'ابتدا باید هزینه تست پرداخت شود'
                }, status=status.HTTP_400_BAD_REQUEST)
        except TestPayment.DoesNotExist:
            return Response({
                'error': 'هیچ پرداختی برای این تست ثبت نشده است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # بررسی وثیقه
        try:
            collateral = test_request.collateral
            if collateral.status != 'locked':
                return Response({
                    'error': 'وثیقه باید قفل شده باشد'
                }, status=status.HTTP_400_BAD_REQUEST)
        except TestCollateral.DoesNotExist:
            return Response({
                'error': 'هیچ وثیقه‌ای برای این تست ثبت نشده است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # ایجاد نتیجه
            result = serializer.save()
            
            # اگر تست موفق بود، جایزه بده
            if result.result == 'pass':
                self._give_token_reward(result, user)
            
            # آزادسازی وثیقه
            collateral.status = 'released'
            collateral.released_at = timezone.now()
            collateral.save()
            
            # بروزرسانی موجودی توکن
            token_wallet, _ = user.token_wallet.objects.get_or_create(user=user)
            token_wallet.add_balance(collateral.token_amount)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def _give_token_reward(self, test_result, user):
        """اعطای جایزه توکن"""
        from tokenwallet.models import TokenReward, TokenRewardHistory
        
        # تعیین نوع تست (ساده شده)
        test_type = 'general'
        
        # دریافت مقدار جایزه
        try:
            reward_config = TokenReward.objects.get(test_type=test_type, is_active=True)
            reward_amount = reward_config.token_amount
        except TokenReward.DoesNotExist:
            reward_amount = 5  # مقدار پیش‌فرض
        
        # اضافه کردن به کیف پول توکن
        token_wallet, _ = user.token_wallet.objects.get_or_create(user=user)
        token_wallet.add_balance(reward_amount)
        
        # ثبت تاریخچه جایزه
        TokenRewardHistory.objects.create(
            user=user,
            test_result=test_result,
            token_amount=reward_amount,
            test_type=test_type,
            description=f"جایزه برای تست موفق: {test_result.test_booking.sport_test.name}"
        )
        
        # بروزرسانی نتیجه تست
        test_result.reward_given = True
        test_result.reward_amount = reward_amount
        test_result.test_type = test_type
        test_result.save()
