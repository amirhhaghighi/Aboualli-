from django.db import models
from django.contrib.auth.models import User
from gympanel.models import Gym
from testprocess.models import TestBooking

# Create your models here.

class Coach(models.Model):
    """مدل مربی - اطلاعات کلی مربیان"""
    SPECIALIZATION_CHOICES = [
        ('fitness', 'تناسب اندام'),
        ('strength', 'قدرتی'),
        ('cardio', 'قلبی عروقی'),
        ('flexibility', 'انعطاف‌پذیری'),
        ('sports', 'ورزش‌های تخصصی'),
        ('rehabilitation', 'توانبخشی'),
        ('nutrition', 'تغذیه'),
        ('general', 'عمومی'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coach_profile', verbose_name="کاربر")
    specialization = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES, default='general', verbose_name="تخصص")
    experience_years = models.PositiveIntegerField(default=0, verbose_name="سال‌های تجربه")
    certification = models.TextField(blank=True, null=True, verbose_name="مدارک و گواهینامه‌ها")
    bio = models.TextField(blank=True, null=True, verbose_name="بیوگرافی")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="نرخ ساعتی")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    is_verified = models.BooleanField(default=False, verbose_name="تایید شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "مربی"
        verbose_name_plural = "مربیان"
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_specialization_display()}"


class CoachProfile(models.Model):
    """مدل پروفایل مربی - اطلاعات تکمیلی مربی"""
    coach = models.OneToOneField(Coach, on_delete=models.CASCADE, related_name='profile', verbose_name="مربی")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="شماره تماس")
    address = models.TextField(blank=True, null=True, verbose_name="آدرس")
    education = models.TextField(blank=True, null=True, verbose_name="تحصیلات")
    achievements = models.TextField(blank=True, null=True, verbose_name="دستاوردها")
    social_media = models.JSONField(blank=True, null=True, verbose_name="شبکه‌های اجتماعی")
    profile_picture = models.ImageField(upload_to='coach_profiles/', blank=True, null=True, verbose_name="عکس پروفایل")
    is_profile_complete = models.BooleanField(default=False, verbose_name="پروفایل تکمیل شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "پروفایل مربی"
        verbose_name_plural = "پروفایل‌های مربیان"
    
    def __str__(self):
        return f"پروفایل {self.coach.user.get_full_name()}"


class CoachGymList(models.Model):
    """مدل لیست باشگاه‌های مربی - باشگاه‌هایی که مربی در آن‌ها کار می‌کند"""
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='gym_list', verbose_name="مربی")
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='coach_list', verbose_name="باشگاه")
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name="سمت")
    start_date = models.DateField(verbose_name="تاریخ شروع")
    end_date = models.DateField(blank=True, null=True, verbose_name="تاریخ پایان")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    notes = models.TextField(blank=True, null=True, verbose_name="یادداشت‌ها")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "باشگاه مربی"
        verbose_name_plural = "باشگاه‌های مربیان"
        unique_together = ['coach', 'gym']
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.coach.user.get_full_name()} - {self.gym.name}"


class CoachTestAvailability(models.Model):
    """مدل در دسترس بودن مربی برای تست‌ها"""
    DAY_CHOICES = [
        ('monday', 'دوشنبه'),
        ('tuesday', 'سه‌شنبه'),
        ('wednesday', 'چهارشنبه'),
        ('thursday', 'پنج‌شنبه'),
        ('friday', 'جمعه'),
        ('saturday', 'شنبه'),
        ('sunday', 'یکشنبه'),
    ]
    
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='test_availabilities', verbose_name="مربی")
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES, verbose_name="روز هفته")
    start_time = models.TimeField(verbose_name="ساعت شروع")
    end_time = models.TimeField(verbose_name="ساعت پایان")
    is_available = models.BooleanField(default=True, verbose_name="در دسترس")
    max_tests_per_day = models.PositiveIntegerField(default=5, verbose_name="حداکثر تست در روز")
    notes = models.TextField(blank=True, null=True, verbose_name="یادداشت‌ها")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "در دسترس بودن مربی"
        verbose_name_plural = "در دسترس بودن مربیان"
        unique_together = ['coach', 'day_of_week']
        ordering = ['coach', 'day_of_week']
    
    def __str__(self):
        return f"{self.coach.user.get_full_name()} - {self.get_day_of_week_display()}"


class TestAssignment(models.Model):
    """مدل تخصیص تست - تخصیص تست‌ها به مربیان"""
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('accepted', 'پذیرفته شده'),
        ('rejected', 'رد شده'),
        ('cancelled', 'لغو شده'),
        ('completed', 'تکمیل شده'),
    ]
    
    test_booking = models.OneToOneField(TestBooking, on_delete=models.CASCADE, related_name='assignment', verbose_name="رزرو تست")
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='test_assignments', verbose_name="مربی")
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_assignments_made', verbose_name="تخصیص دهنده")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ تخصیص")
    accepted_at = models.DateTimeField(blank=True, null=True, verbose_name="تاریخ پذیرش")
    rejected_at = models.DateTimeField(blank=True, null=True, verbose_name="تاریخ رد")
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="دلیل رد")
    notes = models.TextField(blank=True, null=True, verbose_name="یادداشت‌ها")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "تخصیص تست"
        verbose_name_plural = "تخصیص‌های تست"
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.coach.user.get_full_name()} - {self.test_booking.sport_test.name}"
