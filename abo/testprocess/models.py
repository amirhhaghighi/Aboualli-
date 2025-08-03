
from django.db import models
from django.contrib.auth.models import User
from gympanel.models import Gym, SportTest

# Create your models here.

class TestRequest(models.Model):
    """مدل درخواست تست - درخواست کاربر برای رزرو تست"""
    STATUS_CHOICES = [
        ('pending', 'در انتظار بررسی'),
        ('processing', 'در حال پردازش'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
        ('cancelled', 'لغو شده'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_requests', verbose_name="کاربر")
    sport_test = models.ForeignKey(SportTest, on_delete=models.CASCADE, related_name='requests', verbose_name="تست ورزشی")
    preferred_gyms = models.ManyToManyField(Gym, related_name='test_requests', verbose_name="باشگاه‌های مورد علاقه", blank=True, help_text="برای تست‌های خصوصی نیازی به انتخاب نیست")
    start_date = models.DateField(verbose_name="تاریخ شروع")
    end_date = models.DateField(verbose_name="تاریخ پایان")
    start_time = models.TimeField(verbose_name="ساعت شروع")
    end_time = models.TimeField(verbose_name="ساعت پایان")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    notes = models.TextField(blank=True, null=True, verbose_name="یادداشت‌ها")
    # فیلدهای جدید برای وثیقه
    collateral_required = models.BooleanField(default=True, verbose_name="نیاز به وثیقه")
    collateral_amount = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="مقدار توکن وثیقه")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "درخواست تست"
        verbose_name_plural = "درخواست‌های تست"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.sport_test.name} ({self.get_status_display()})"


class TestPayment(models.Model):
    """مدل پرداخت تست - ثبت پرداخت‌های تست"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
        ('cancelled', 'لغو شده'),
    ]
    
    test_request = models.OneToOneField(TestRequest, on_delete=models.CASCADE, related_name='payment', verbose_name="درخواست تست")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_payments', verbose_name="کاربر")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="مبلغ (ریال)")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name="وضعیت پرداخت")
    payment_method = models.CharField(max_length=50, blank=True, null=True, verbose_name="روش پرداخت")
    reference_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="شماره مرجع")
    notes = models.TextField(blank=True, null=True, verbose_name="یادداشت‌ها")
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name="تاریخ پرداخت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "پرداخت تست"
        verbose_name_plural = "پرداخت‌های تست"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.amount:,} ریال"


class TestCollateral(models.Model):
    """مدل وثیقه تست - وثیقه‌های توکن برای تست‌ها"""
    COLLATERAL_STATUS_CHOICES = [
        ('locked', 'قفل شده'),
        ('released', 'آزاد شده'),
        ('forfeited', 'مصادره شده'),
    ]
    
    test_request = models.OneToOneField(TestRequest, on_delete=models.CASCADE, related_name='collateral', verbose_name="درخواست تست")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_collaterals', verbose_name="کاربر")
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="مقدار توکن وثیقه")
    status = models.CharField(max_length=20, choices=COLLATERAL_STATUS_CHOICES, default='locked', verbose_name="وضعیت وثیقه")
    locked_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ قفل")
    released_at = models.DateTimeField(blank=True, null=True, verbose_name="تاریخ آزادسازی")
    notes = models.TextField(blank=True, null=True, verbose_name="یادداشت‌ها")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "وثیقه تست"
        verbose_name_plural = "وثیقه‌های تست"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.token_amount} توکن ({self.get_status_display()})"


class TestBooking(models.Model):
    """مدل رزرو تست - رزرو نهایی تست"""
    STATUS_CHOICES = [
        ('confirmed', 'تایید شده'),
        ('cancelled', 'لغو شده'),
        ('completed', 'تکمیل شده'),
    ]
    
    test_request = models.OneToOneField(TestRequest, on_delete=models.CASCADE, related_name='booking', verbose_name="درخواست تست")
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='test_bookings', verbose_name="باشگاه")
    sport_test = models.ForeignKey(SportTest, on_delete=models.CASCADE, related_name='bookings', verbose_name="تست ورزشی")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_bookings', verbose_name="کاربر")
    booking_date = models.DateField(verbose_name="تاریخ رزرو")
    start_time = models.TimeField(verbose_name="ساعت شروع")
    end_time = models.TimeField(verbose_name="ساعت پایان")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed', verbose_name="وضعیت")
    coach_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="نام مربی")
    notes = models.TextField(blank=True, null=True, verbose_name="یادداشت‌ها")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "رزرو تست"
        verbose_name_plural = "رزروهای تست"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.sport_test.name} - {self.gym.name}"


class TestResult(models.Model):
    """مدل نتیجه تست - نتایج تست‌های انجام شده"""
    RESULT_CHOICES = [
        ('pass', 'قبول'),
        ('fail', 'رد'),
        ('pending', 'در انتظار'),
    ]
    
    test_booking = models.OneToOneField(TestBooking, on_delete=models.CASCADE, related_name='result', verbose_name="رزرو تست")
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, default='pending', verbose_name="نتیجه")
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="نمره")
    feedback = models.TextField(blank=True, null=True, verbose_name="بازخورد")
    coach_notes = models.TextField(blank=True, null=True, verbose_name="یادداشت مربی")
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name="تاریخ تکمیل")
    # فیلدهای جدید برای جایزه
    reward_given = models.BooleanField(default=False, verbose_name="جایزه داده شده")
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="مقدار توکن جایزه")
    test_type = models.CharField(max_length=20, blank=True, null=True, verbose_name="نوع تست")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "نتیجه تست"
        verbose_name_plural = "نتایج تست"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.test_booking.user.get_full_name()} - {self.get_result_display()}"
