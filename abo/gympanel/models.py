from django.db import models

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Gym(models.Model):
    """مدل باشگاه - اطلاعات کلی باشگاه"""
    name = models.CharField(max_length=200, verbose_name="نام باشگاه")
    address = models.TextField(verbose_name="آدرس")
    phone = models.CharField(max_length=20, verbose_name="شماره تماس")
    email = models.EmailField(blank=True, null=True, verbose_name="ایمیل")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='administered_gyms', verbose_name="ادمین باشگاه")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "باشگاه"
        verbose_name_plural = "باشگاه‌ها"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class GymCapacity(models.Model):
    """مدل ظرفیت باشگاه - ظرفیت اعلام شده توسط باشگاه"""
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='capacities', verbose_name="باشگاه")
    capacity = models.PositiveIntegerField(verbose_name="ظرفیت کل")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات ظرفیت")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    
    class Meta:
        verbose_name = "ظرفیت باشگاه"
        verbose_name_plural = "ظرفیت‌های باشگاه"
    
    def __str__(self):
        return f"{self.gym.name} - ظرفیت: {self.capacity}"

class MemberAttendance(models.Model):
    """مدل حضور اعضا - فرم‌های هفتگی حضور ورزشکاران"""
    DAY_CHOICES = [
        ('monday', 'دوشنبه'),
        ('tuesday', 'سه‌شنبه'),
        ('wednesday', 'چهارشنبه'),
        ('thursday', 'پنج‌شنبه'),
        ('friday', 'جمعه'),
        ('saturday', 'شنبه'),
        ('sunday', 'یکشنبه'),
    ]
    
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='attendances', verbose_name="باشگاه")
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances', verbose_name="عضو")
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES, verbose_name="روز هفته")
    start_time = models.TimeField(verbose_name="ساعت شروع")
    end_time = models.TimeField(verbose_name="ساعت پایان")
    week_start_date = models.DateField(verbose_name="تاریخ شروع هفته")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    
    class Meta:
        verbose_name = "حضور عضو"
        verbose_name_plural = "حضور اعضا"
        unique_together = ['gym', 'member', 'day_of_week', 'week_start_date']
    
    def __str__(self):
        return f"{self.member.username} - {self.gym.name} - {self.get_day_of_week_display()}"

class GymSchedule(models.Model):
    """مدل برنامه باشگاه - ساعات کاری و فعالیت باشگاه"""
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='schedules', verbose_name="باشگاه")
    day_of_week = models.CharField(max_length=10, choices=MemberAttendance.DAY_CHOICES, verbose_name="روز هفته")
    open_time = models.TimeField(verbose_name="ساعت باز شدن")
    close_time = models.TimeField(verbose_name="ساعت بسته شدن")
    is_working_day = models.BooleanField(default=True, verbose_name="روز کاری")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    
    class Meta:
        verbose_name = "برنامه باشگاه"
        verbose_name_plural = "برنامه‌های باشگاه"
        unique_together = ['gym', 'day_of_week']
    
    def __str__(self):
        return f"{self.gym.name} - {self.get_day_of_week_display()}"

class GymTestAvailability(models.Model):
    """مدل پذیرش تست باشگاه - اعلام عدم پذیرش تست در روزهای خاص"""
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='test_availabilities', verbose_name="باشگاه")
    date = models.DateField(verbose_name="تاریخ")
    is_available = models.BooleanField(default=True, verbose_name="پذیرش تست")
    reason = models.TextField(blank=True, null=True, verbose_name="دلیل عدم پذیرش")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "پذیرش تست باشگاه"
        verbose_name_plural = "پذیرش تست باشگاه‌ها"
        unique_together = ['gym', 'date']
        ordering = ['-date']
    
    def __str__(self):
        status = "پذیرش تست" if self.is_available else "عدم پذیرش تست"
        return f"{self.gym.name} - {self.date} - {status}"

class SportTest(models.Model):
    """مدل تست‌های ورزشی - تست‌هایی که باشگاه‌ها طراحی می‌کنند"""
    DIFFICULTY_CHOICES = [
        ('easy', 'آسان'),
        ('medium', 'متوسط'),
        ('hard', 'سخت'),
    ]
    
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='sport_tests', verbose_name="باشگاه")
    name = models.CharField(max_length=200, verbose_name="نام تست")
    description = models.TextField(verbose_name="توضیحات تست")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium', verbose_name="سطح دشواری")
    duration = models.PositiveIntegerField(verbose_name="مدت زمان (دقیقه)")
    average_duration = models.PositiveIntegerField(verbose_name="مدت زمان میانگین (دقیقه)", help_text="مدت زمان میانگین برای انجام تست")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت")
    is_private = models.BooleanField(default=False, verbose_name="تست خصوصی", help_text="اگر فعال باشد، فقط برای اعضای این باشگاه قابل دسترس است")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "تست ورزشی"
        verbose_name_plural = "تست‌های ورزشی"
        ordering = ['gym', 'name']
    
    def __str__(self):
        test_type = "خصوصی" if self.is_private else "عمومی"
        return f"{self.gym.name} - {self.name} ({test_type})"

class TestReservation(models.Model):
    """مدل رزرو تست - تست‌های رزرو شده توسط کاربران"""
    STATUS_CHOICES = [
        ('pending', 'در انتظار تایید'),
        ('confirmed', 'تایید شده'),
        ('cancelled', 'لغو شده'),
    ]
    
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='test_reservations', verbose_name="باشگاه")
    sport_test = models.ForeignKey(SportTest, on_delete=models.CASCADE, related_name='reservations', verbose_name="تست ورزشی")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_reservations', verbose_name="کاربر")
    reservation_date = models.DateField(verbose_name="تاریخ رزرو")
    start_time = models.TimeField(verbose_name="ساعت شروع")
    end_time = models.TimeField(verbose_name="ساعت پایان")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    notes = models.TextField(blank=True, null=True, verbose_name="یادداشت‌ها")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "رزرو تست"
        verbose_name_plural = "رزروهای تست"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.sport_test.name} - {self.reservation_date}"
