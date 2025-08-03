from django.contrib import admin
from .models import FiatWallet, FiatTransaction, FiatDeposit, FiatWithdrawal


@admin.register(FiatWallet)
class FiatWalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(FiatTransaction)
class FiatTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'transaction_type', 'amount', 'status', 'created_at']
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['wallet__user__username', 'reference_id', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('wallet__user')


@admin.register(FiatDeposit)
class FiatDepositAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'amount', 'payment_method', 'is_verified', 'created_at']
    list_filter = ['payment_method', 'is_verified', 'created_at']
    search_fields = ['wallet__user__username', 'receipt_number', 'bank_name']
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['verify_deposits']
    
    def verify_deposits(self, request, queryset):
        """تایید واریزهای انتخاب شده"""
        for deposit in queryset.filter(is_verified=False):
            deposit.is_verified = True
            deposit.verified_by = request.user
            deposit.save()
            
            # افزایش موجودی کیف پول
            wallet = deposit.wallet
            wallet.add_balance(deposit.amount)
            
            # ثبت تراکنش
            FiatTransaction.objects.create(
                wallet=wallet,
                transaction_type='deposit',
                amount=deposit.amount,
                balance_before=wallet.balance - deposit.amount,
                balance_after=wallet.balance,
                status='completed',
                reference_id=f"DEP-{deposit.id}",
                description=f"واریز {deposit.amount:,} ریال"
            )
        
        self.message_user(request, f"{queryset.count()} واریز تایید شد")
    
    verify_deposits.short_description = "تایید واریزهای انتخاب شده"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('wallet__user', 'verified_by')


@admin.register(FiatWithdrawal)
class FiatWithdrawalAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'amount', 'withdrawal_method', 'is_approved', 'is_processed', 'created_at']
    list_filter = ['withdrawal_method', 'is_approved', 'is_processed', 'created_at']
    search_fields = ['wallet__user__username', 'account_number', 'bank_name']
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['approve_withdrawals', 'process_withdrawals']
    
    def approve_withdrawals(self, request, queryset):
        """تایید برداشت‌های انتخاب شده"""
        for withdrawal in queryset.filter(is_approved=False):
            wallet = withdrawal.wallet
            if wallet.balance >= withdrawal.amount:
                withdrawal.is_approved = True
                withdrawal.approved_by = request.user
                withdrawal.save()
                
                # کاهش موجودی کیف پول
                balance_before = wallet.balance
                wallet.subtract_balance(withdrawal.amount)
                
                # ثبت تراکنش
                FiatTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='withdrawal',
                    amount=withdrawal.amount,
                    balance_before=balance_before,
                    balance_after=wallet.balance,
                    status='completed',
                    reference_id=f"WTH-{withdrawal.id}",
                    description=f"برداشت {withdrawal.amount:,} ریال"
                )
        
        self.message_user(request, f"{queryset.count()} برداشت تایید شد")
    
    def process_withdrawals(self, request, queryset):
        """پردازش برداشت‌های انتخاب شده"""
        for withdrawal in queryset.filter(is_approved=True, is_processed=False):
            withdrawal.is_processed = True
            withdrawal.save()
        
        self.message_user(request, f"{queryset.count()} برداشت پردازش شد")
    
    approve_withdrawals.short_description = "تایید برداشت‌های انتخاب شده"
    process_withdrawals.short_description = "پردازش برداشت‌های انتخاب شده"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('wallet__user', 'approved_by')
