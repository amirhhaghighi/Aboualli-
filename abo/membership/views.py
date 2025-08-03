from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
from gympanel.models import Gym
from .models import (
    MembershipPlan, Membership, MembershipPayment, 
    MembershipReview, MembershipHistory, GymMembershipRequest
)
from .serializers import (
    MembershipPlanSerializer, MembershipSerializer, MembershipPaymentSerializer,
    MembershipReviewSerializer, MembershipHistorySerializer, GymMembershipRequestSerializer,
    MembershipPlanCreateSerializer, MembershipCreateSerializer, MembershipPaymentCreateSerializer,
    MembershipReviewCreateSerializer, GymMembershipRequestCreateSerializer
)


class MembershipPlanViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت طرح‌های عضویت"""
    queryset = MembershipPlan.objects.all()
    serializer_class = MembershipPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MembershipPlanCreateSerializer
        return MembershipPlanSerializer
    
    def get_queryset(self):
        queryset = MembershipPlan.objects.filter(is_active=True)
        gym_id = self.request.query_params.get('gym', None)
        plan_type = self.request.query_params.get('plan_type', None)
        
        if gym_id:
            queryset = queryset.filter(gym_id=gym_id)
        if plan_type:
            queryset = queryset.filter(plan_type=plan_type)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def available_plans(self, request):
        """دریافت طرح‌های عضویت قابل دسترس"""
        gym_id = request.query_params.get('gym', None)
        
        if not gym_id:
            return Response({
                'error': 'شناسه باشگاه الزامی است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        plans = MembershipPlan.objects.filter(
            gym_id=gym_id,
            is_active=True
        ).select_related('gym')
        
        serializer = MembershipPlanSerializer(plans, many=True)
        return Response(serializer.data)


class MembershipViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت عضویت‌ها"""
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MembershipCreateSerializer
        return MembershipSerializer
    
    def get_queryset(self):
        return Membership.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active_memberships(self, request):
        """دریافت عضویت‌های فعال کاربر"""
        active_memberships = Membership.objects.filter(
            user=request.user,
            status='active'
        ).select_related('gym', 'plan')
        
        serializer = MembershipSerializer(active_memberships, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def renew_membership(self, request, pk=None):
        """تمدید عضویت"""
        membership = self.get_object()
        
        if not membership.can_renew():
            return Response({
                'error': 'امکان تمدید این عضویت وجود ندارد'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # محاسبه تاریخ‌های جدید
            new_end_date = membership.end_date + timedelta(days=membership.plan.duration_days)
            
            # بروزرسانی عضویت
            membership.end_date = new_end_date
            membership.save()
            
            # ثبت تاریخچه
            MembershipHistory.objects.create(
                membership=membership,
                action='renewed',
                description='عضویت تمدید شد',
                created_by=request.user
            )
        
        serializer = MembershipSerializer(membership)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel_membership(self, request, pk=None):
        """لغو عضویت"""
        membership = self.get_object()
        
        if membership.status not in ['active', 'pending']:
            return Response({
                'error': 'امکان لغو این عضویت وجود ندارد'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            membership.status = 'cancelled'
            membership.save()
            
            # ثبت تاریخچه
            MembershipHistory.objects.create(
                membership=membership,
                action='cancelled',
                description='عضویت لغو شد',
                created_by=request.user
            )
        
        serializer = MembershipSerializer(membership)
        return Response(serializer.data)


class MembershipPaymentViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت پرداخت‌های عضویت"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MembershipPayment.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MembershipPaymentCreateSerializer
        return MembershipPaymentSerializer
    
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
            
            # فعال‌سازی عضویت
            membership = payment.membership
            membership.status = 'active'
            membership.save()
            
            # ثبت تاریخچه
            MembershipHistory.objects.create(
                membership=membership,
                action='payment_completed',
                description=f'پرداخت {payment.amount:,} ریال تکمیل شد',
                created_by=request.user
            )
        
        serializer = MembershipPaymentSerializer(payment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_payment_from_wallet(self, request):
        """ایجاد پرداخت از کیف پول"""
        membership_id = request.data.get('membership_id')
        amount = request.data.get('amount')
        
        if not membership_id or not amount:
            return Response({
                'error': 'شناسه عضویت و مبلغ الزامی است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        membership = get_object_or_404(Membership, id=membership_id, user=request.user)
        
        # بررسی موجودی کیف پول
        try:
            fiat_wallet = request.user.fiat_wallet
            if fiat_wallet.balance < amount:
                return Response({
                    'error': 'موجودی کافی نیست'
                }, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({
                'error': 'کیف پول یافت نشد'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # کسر از کیف پول
            fiat_wallet.subtract_balance(amount)
            
            # ایجاد پرداخت
            payment = MembershipPayment.objects.create(
                membership=membership,
                user=request.user,
                amount=amount,
                payment_method='wallet',
                status='completed',
                paid_at=timezone.now()
            )
            
            # فعال‌سازی عضویت
            membership.status = 'active'
            membership.save()
            
            # ثبت تاریخچه
            MembershipHistory.objects.create(
                membership=membership,
                action='payment_completed',
                description=f'پرداخت {amount:,} ریال از کیف پول',
                created_by=request.user
            )
        
        serializer = MembershipPaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MembershipReviewViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت نظرات عضویت"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MembershipReview.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MembershipReviewCreateSerializer
        return MembershipReviewSerializer
    
    @action(detail=False, methods=['get'])
    def gym_reviews(self, request):
        """دریافت نظرات یک باشگاه"""
        gym_id = request.query_params.get('gym', None)
        
        if not gym_id:
            return Response({
                'error': 'شناسه باشگاه الزامی است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reviews = MembershipReview.objects.filter(
            membership__gym_id=gym_id,
            is_public=True
        ).select_related('user', 'membership__gym')
        
        serializer = MembershipReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class MembershipHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet برای مشاهده تاریخچه عضویت"""
    serializer_class = MembershipHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MembershipHistory.objects.filter(membership__user=self.request.user)


class GymMembershipRequestViewSet(viewsets.ModelViewSet):
    """ViewSet برای مدیریت درخواست‌های عضویت"""
    serializer_class = GymMembershipRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return GymMembershipRequestCreateSerializer
        return GymMembershipRequestSerializer
    
    def get_queryset(self):
        # اگر کاربر ادمین باشگاه است، درخواست‌های باشگاه‌هایش را ببیند
        if hasattr(self.request.user, 'administered_gyms') and self.request.user.administered_gyms.exists():
            return GymMembershipRequest.objects.filter(gym__admin=self.request.user)
        # در غیر این صورت، درخواست‌های خودش را ببیند
        return GymMembershipRequest.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve_request(self, request, pk=None):
        """تایید درخواست عضویت (فقط ادمین باشگاه)"""
        membership_request = self.get_object()
        
        # بررسی اینکه کاربر ادمین این باشگاه است
        if not (request.user.is_staff or membership_request.gym.admin == request.user):
            return Response({
                'error': 'فقط ادمین باشگاه می‌تواند درخواست‌ها را تایید کند'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if membership_request.status != 'pending':
            return Response({
                'error': 'فقط درخواست‌های در انتظار قابل تایید هستند'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # تایید درخواست
            membership_request.status = 'approved'
            membership_request.save()
            
            # ایجاد عضویت
            membership = Membership.objects.create(
                user=membership_request.user,
                gym=membership_request.gym,
                plan=membership_request.plan,
                status='pending',
                start_date=membership_request.requested_start_date,
                end_date=membership_request.requested_start_date + timedelta(days=membership_request.plan.duration_days)
            )
            
            # ثبت تاریخچه
            MembershipHistory.objects.create(
                membership=membership,
                action='created',
                description='عضویت از درخواست تایید شده ایجاد شد',
                created_by=request.user
            )
        
        serializer = GymMembershipRequestSerializer(membership_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject_request(self, request, pk=None):
        """رد درخواست عضویت (فقط ادمین باشگاه)"""
        membership_request = self.get_object()
        
        # بررسی اینکه کاربر ادمین این باشگاه است
        if not (request.user.is_staff or membership_request.gym.admin == request.user):
            return Response({
                'error': 'فقط ادمین باشگاه می‌تواند درخواست‌ها را رد کند'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if membership_request.status != 'pending':
            return Response({
                'error': 'فقط درخواست‌های در انتظار قابل رد هستند'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        admin_notes = request.data.get('admin_notes', '')
        
        membership_request.status = 'rejected'
        membership_request.admin_notes = admin_notes
        membership_request.save()
        
        serializer = GymMembershipRequestSerializer(membership_request)
        return Response(serializer.data)

