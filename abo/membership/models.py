from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from gympanel.models import Gym

# Create your models here.

class MembershipPlan(models.Model):
    """مدل طرح‌های عضویت باشگاه"""
    PLAN_TYPE_CHOICES = [
        ('monthly', 'ماهانه'),
        ('quarterly', 'سه‌ماهه'),
        ('yearly', 'سالانه'),
        ('custom', 'سفارشی'),
    ]
    
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='membership_plans', verbose_name="باشگاه")
    name = models.CharField(max_length=200, verbose_name="نام طرح")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, verbose_name="نوع طرح")
    duration_days = models.PositiveIntegerField(verbose_name="مدت به روز")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت (ریال)")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    max_members = models.PositiveIntegerField(blank=True, null=True, verbose_name="حداکثر تعداد اعضا")
    features = models.JSONField(default=dict, blank=True, verbose_name="امکانات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "طرح عضویت"
        verbose_name_plural = "طرح‌های عضویت"
        ordering = ['gym', 'price']
    
    def __str__(self):
        return f"{self.gym.name} - {self.name} ({self.get_plan_type_display()})"


class Membership(models.Model):
    """مدل عضویت کاربران در باشگاه‌ها"""
    STATUS_CHOICES = [
        ('active', 'فعال'),
        ('expired', 'منقضی شده'),
        ('cancelled', 'لغو شده'),
        ('suspended', 'معلق'),
        ('pending', 'در انتظار تایید'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships', verbose_name="کاربر")
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='members', verbose_name="باشگاه")
    plan = models.ForeignKey(MembershipPlan, on_delete=models.CASCADE, related_name='memberships', verbose_name="طرح عضویت")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    start_date = models.DateField(verbose_name="تاریخ شروع")
    end_date = models.DateField(verbose_name="تاریخ پایان")
    auto_renew = models.BooleanField(default=False, verbose_name="تمدید خودکار")
    notes = models.TextField(blank=True, null=True, verbose_name="یادداشت‌ها")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "عضویت"
        verbose_name_plural = "عضویت‌ها"
        ordering = ['-created_at']
        unique_together = ['user', 'gym', 'status']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.gym.name} ({self.get_status_display()})"
    
    def is_active(self):
        """بررسی فعال بودن عضویت"""
        today = timezone.now().date()
        return (
            self.status == 'active' and 
            self.start_date <= today <= self.end_date
        )
    
    def days_remaining(self):
        """تعداد روزهای باقی‌مانده"""
        today = timezone.now().date()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days
    
    def can_renew(self):
        """بررسی امکان تمدید"""
        return self.status in ['active', 'expired'] and self.auto_renew


class MembershipPayment(models.Model):
    """مدل پرداخت‌های عضویت"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
        ('cancelled', 'لغو شده'),
        ('refunded', 'بازگشت'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('online', 'آنلاین'),
        ('cash', 'نقدی'),
        ('bank_transfer', 'انتقال بانکی'),
        ('wallet', 'کیف پول'),
    ]
    
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='payments', verbose_name="عضویت")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='membership_payments', verbose_name="کاربر")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="مبلغ (ریال)")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name="روش پرداخت")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name="وضعیت پرداخت")
    reference_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="شماره مرجع")
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="شناسه تراکنش")
    notes = models.TextField(blank=True, null=True, verbose_name="یادداشت‌ها")
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name="تاریخ پرداخت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "پرداخت عضویت"
        verbose_name_plural = "پرداخت‌های عضویت"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.amount:,} ریال ({self.get_status_display()})"


class MembershipReview(models.Model):
    """مدل نظرات و امتیازدهی عضویت"""
    membership = models.OneToOneField(Membership, on_delete=models.CASCADE, related_name='review', verbose_name="عضویت")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='membership_reviews', verbose_name="کاربر")
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="امتیاز")
    comment = models.TextField(blank=True, null=True, verbose_name="نظر")
    is_public = models.BooleanField(default=True, verbose_name="عمومی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "نظر عضویت"
        verbose_name_plural = "نظرات عضویت"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.rating}/5"


class MembershipHistory(models.Model):
    """مدل تاریخچه عضویت"""
    ACTION_CHOICES = [
        ('created', 'ایجاد شد'),
        ('activated', 'فعال شد'),
        ('renewed', 'تمدید شد'),
        ('cancelled', 'لغو شد'),
        ('expired', 'منقضی شد'),
        ('suspended', 'معلق شد'),
        ('payment_completed', 'پرداخت تکمیل شد'),
        ('payment_failed', 'پرداخت ناموفق'),
    ]
    
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='history', verbose_name="عضویت")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="عملیات")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='membership_actions', verbose_name="ایجاد شده توسط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    
    class Meta:
        verbose_name = "تاریخچه عضویت"
        verbose_name_plural = "تاریخچه عضویت‌ها"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.membership} - {self.get_action_display()}"


class GymMembershipRequest(models.Model):
    """مدل درخواست عضویت در باشگاه"""
    STATUS_CHOICES = [
        ('pending', 'در انتظار بررسی'),
        ('approved', 'تایید شده'),
        ('rejected', 'رد شده'),
        ('cancelled', 'لغو شده'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='membership_requests', verbose_name="کاربر")
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='membership_requests', verbose_name="باشگاه")
    plan = models.ForeignKey(MembershipPlan, on_delete=models.CASCADE, related_name='requests', verbose_name="طرح درخواستی")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    requested_start_date = models.DateField(verbose_name="تاریخ شروع درخواستی")
    notes = models.TextField(blank=True, null=True, verbose_name="یادداشت‌ها")
    admin_notes = models.TextField(blank=True, null=True, verbose_name="یادداشت ادمین")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "درخواست عضویت"
        verbose_name_plural = "درخواست‌های عضویت"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.gym.name} ({self.get_status_display()})"
