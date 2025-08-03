from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

# Create your models here.

class FiatWallet(models.Model):
    """مدل کیف پول فیات - کیف پول اصلی کاربر برای مدیریت ریال"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fiat_wallet', verbose_name="کاربر")
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="موجودی (ریال)")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "کیف پول فیات"
        verbose_name_plural = "کیف پول‌های فیات"
    
    def __str__(self):
        return f"کیف پول {self.user.get_full_name()} - موجودی: {self.balance:,} ریال"
    
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
        return f"{self.balance:,} ریال"


class FiatTransaction(models.Model):
    """مدل تراکنش فیات - ثبت تمام تراکنش‌های واریز و برداشت"""
    TRANSACTION_TYPES = [
        ('deposit', 'واریز'),
        ('withdrawal', 'برداشت'),
        ('purchase', 'خرید توکن'),
        ('sale', 'فروش توکن'),
        ('transfer', 'انتقال'),
        ('refund', 'بازگشت'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('processing', 'در حال پردازش'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
        ('cancelled', 'لغو شده'),
    ]
    
    wallet = models.ForeignKey(FiatWallet, on_delete=models.CASCADE, related_name='transactions', verbose_name="کیف پول")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="نوع تراکنش")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="مبلغ (ریال)")
    balance_before = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="موجودی قبل")
    balance_after = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="موجودی بعد")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    reference_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="شماره مرجع")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "تراکنش فیات"
        verbose_name_plural = "تراکنش‌های فیات"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.wallet.user.get_full_name()} - {self.get_transaction_type_display()} - {self.amount:,} ریال"


class FiatDeposit(models.Model):
    """مدل واریز فیات - درخواست‌های واریز کاربران"""
    PAYMENT_METHODS = [
        ('bank_transfer', 'انتقال بانکی'),
        ('online_payment', 'پرداخت آنلاین'),
        ('cash', 'نقدی'),
        ('check', 'چک'),
    ]
    
    wallet = models.ForeignKey(FiatWallet, on_delete=models.CASCADE, related_name='deposits', verbose_name="کیف پول")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="مبلغ (ریال)")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name="روش پرداخت")
    bank_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="نام بانک")
    account_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="شماره حساب")
    receipt_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="شماره رسید")
    is_verified = models.BooleanField(default=False, verbose_name="تایید شده")
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='verified_deposits', verbose_name="تایید کننده")
    verified_at = models.DateTimeField(blank=True, null=True, verbose_name="تاریخ تایید")
    notes = models.TextField(blank=True, null=True, verbose_name="یادداشت‌ها")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "واریز فیات"
        verbose_name_plural = "واریزهای فیات"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.wallet.user.get_full_name()} - واریز {self.amount:,} ریال"


class FiatWithdrawal(models.Model):
    """مدل برداشت فیات - درخواست‌های برداشت کاربران"""
    WITHDRAWAL_METHODS = [
        ('bank_transfer', 'انتقال بانکی'),
        ('cash', 'نقدی'),
        ('check', 'چک'),
    ]
    
    wallet = models.ForeignKey(FiatWallet, on_delete=models.CASCADE, related_name='withdrawals', verbose_name="کیف پول")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="مبلغ (ریال)")
    withdrawal_method = models.CharField(max_length=20, choices=WITHDRAWAL_METHODS, verbose_name="روش برداشت")
    bank_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="نام بانک")
    account_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="شماره حساب")
    account_holder = models.CharField(max_length=100, blank=True, null=True, verbose_name="صاحب حساب")
    is_approved = models.BooleanField(default=False, verbose_name="تایید شده")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='approved_withdrawals', verbose_name="تایید کننده")
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name="تاریخ تایید")
    is_processed = models.BooleanField(default=False, verbose_name="پردازش شده")
    processed_at = models.DateTimeField(blank=True, null=True, verbose_name="تاریخ پردازش")
    notes = models.TextField(blank=True, null=True, verbose_name="یادداشت‌ها")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "برداشت فیات"
        verbose_name_plural = "برداشت‌های فیات"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.wallet.user.get_full_name()} - برداشت {self.amount:,} ریال"
