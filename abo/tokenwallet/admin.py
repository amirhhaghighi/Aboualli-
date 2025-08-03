from django.contrib import admin
from .models import TokenWallet, TokenOrder, TokenTransaction, TokenReward, TokenRewardHistory


@admin.register(TokenWallet)
class TokenWalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(TokenReward)
class TokenRewardAdmin(admin.ModelAdmin):
    list_display = ['test_type', 'token_amount', 'is_active', 'created_at']
    list_filter = ['test_type', 'is_active', 'created_at']
    search_fields = ['test_type', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TokenOrder)
class TokenOrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'order_type', 'token_amount', 'token_price', 'status', 'created_at']
    list_filter = ['order_type', 'status', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['total_value', 'remaining_amount', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(TokenTransaction)
class TokenTransactionAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'seller', 'token_amount', 'token_price', 'total_value', 'created_at']
    list_filter = ['created_at']
    search_fields = ['buyer__username', 'seller__username']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('buyer', 'seller')


@admin.register(TokenRewardHistory)
class TokenRewardHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'test_type', 'token_amount', 'created_at']
    list_filter = ['test_type', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

