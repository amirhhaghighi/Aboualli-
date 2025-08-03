from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

# Create your models here.

class TokenWallet(models.Model):
    """مدل کیف پول توکن - کیف پول اصلی کاربر برای مدیریت توکن‌های داخلی"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='token_wallet', verbose_name="کاربر")
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="موجودی توکن")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "کیف پول توکن"
        verbose_name_plural = "کیف پول‌های توکن"
    
    def __str__(self):
        return f"کیف پول توکن {self.user.get_full_name()} - موجودی: {self.balance} توکن"
    
    def add_balance(self, amount):
        """افزودن موجودی به کیف پول"""
        if amount > 0:
            self.balance += amount
            self.save()
            return True
        return False
    
    def subtract_balance(self, amount):
        """کاهش موجودی از کیف پول"""
        if amount > 0 and self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False
    
    def get_balance_display(self):
        """نمایش موجودی به صورت فرمت شده"""
        return f"{self.balance} توکن"


class TokenReward(models.Model):
    """مدل سیستم جایزه توکن - مقدار توکن برای هر تست موفق"""
    TEST_TYPES = [
        ('fitness', 'تناسب اندام'),
        ('strength', 'قدرتی'),
        ('cardio', 'قلبی عروقی'),
        ('flexibility', 'انعطاف‌پذیری'),
        ('sports', 'ورزش‌های تخصصی'),
        ('rehabilitation', 'توانبخشی'),
        ('general', 'عمومی'),
    ]
    
    test_type = models.CharField(max_length=20, choices=TEST_TYPES, verbose_name="نوع تست")
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="مقدار توکن جایزه")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "جایزه توکن"
        verbose_name_plural = "جایزه‌های توکن"
        unique_together = ['test_type']
    
    def __str__(self):
        return f"{self.get_test_type_display()} - {self.token_amount} توکن"


class TokenOrder(models.Model):
    """مدل سفارش توکن - سفارشات خرید و فروش توکن"""
    ORDER_TYPES = [
        ('buy', 'خرید'),
        ('sell', 'فروش'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('partial', 'نیمه تکمیل'),
        ('completed', 'تکمیل شده'),
        ('cancelled', 'لغو شده'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='token_orders', verbose_name="کاربر")
    order_type = models.CharField(max_length=10, choices=ORDER_TYPES, verbose_name="نوع سفارش")
    token_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="مقدار توکن")
    token_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت واحد (ریال)")
    total_value = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="ارزش کل (ریال)")
    remaining_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="مقدار باقی‌مانده")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "سفارش توکن"
        verbose_name_plural = "سفارشات توکن"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_order_type_display()} {self.token_amount} توکن"
    
    def save(self, *args, **kwargs):
        """محاسبه خودکار ارزش کل"""
        if not self.total_value:
            self.total_value = self.token_amount * self.token_price
        if not self.remaining_amount:
            self.remaining_amount = self.token_amount
        super().save(*args, **kwargs)


class TokenTransaction(models.Model):
    """مدل تراکنش توکن - تراکنش‌های تطبیق شده"""
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='token_buy_transactions', verbose_name="خریدار")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='token_sell_transactions', verbose_name="فروشنده")
    buy_order = models.ForeignKey(TokenOrder, on_delete=models.CASCADE, related_name='buy_transactions', verbose_name="سفارش خرید")
    sell_order = models.ForeignKey(TokenOrder, on_delete=models.CASCADE, related_name='sell_transactions', verbose_name="سفارش فروش")
    token_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="مقدار توکن")
    token_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت واحد (ریال)")
    total_value = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="ارزش کل (ریال)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    
    class Meta:
        verbose_name = "تراکنش توکن"
        verbose_name_plural = "تراکنش‌های توکن"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.buyer.get_full_name()} ← {self.seller.get_full_name()} - {self.token_amount} توکن"


class TokenRewardHistory(models.Model):
    """مدل تاریخچه جایزه توکن - ثبت جایزه‌های دریافتی"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='token_rewards', verbose_name="کاربر")
    test_result = models.ForeignKey('testprocess.TestResult', on_delete=models.CASCADE, related_name='token_rewards', verbose_name="نتیجه تست")
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="مقدار توکن جایزه")
    test_type = models.CharField(max_length=20, choices=TokenReward.TEST_TYPES, verbose_name="نوع تست")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    
    class Meta:
        verbose_name = "تاریخچه جایزه توکن"
        verbose_name_plural = "تاریخچه جایزه‌های توکن"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.token_amount} توکن برای {self.get_test_type_display()}"

