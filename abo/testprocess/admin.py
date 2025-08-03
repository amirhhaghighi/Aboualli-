from django.contrib import admin
from .models import TestRequest, TestBooking, TestResult, TestCollateral, TestPayment


@admin.register(TestRequest)
class TestRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'sport_test', 'start_date', 'end_date', 'status', 'collateral_required']
    list_filter = ['status', 'collateral_required', 'created_at']
    search_fields = ['user__username', 'sport_test__name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'sport_test')


@admin.register(TestPayment)
class TestPaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__username', 'reference_id']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(TestCollateral)
class TestCollateralAdmin(admin.ModelAdmin):
    list_display = ['user', 'token_amount', 'status', 'locked_at', 'released_at']
    list_filter = ['status', 'locked_at', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['locked_at', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(TestBooking)
class TestBookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'gym', 'sport_test', 'booking_date', 'status']
    list_filter = ['status', 'booking_date', 'created_at']
    search_fields = ['user__username', 'gym__name', 'sport_test__name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'gym', 'sport_test')


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'sport_test', 'result', 'score', 'reward_given', 'created_at']
    list_filter = ['result', 'reward_given', 'created_at']
    search_fields = ['test_booking__user__username', 'test_booking__sport_test__name']
    readonly_fields = ['created_at', 'updated_at']
    
    def user(self, obj):
        return obj.test_booking.user.get_full_name()
    
    def sport_test(self, obj):
        return obj.test_booking.sport_test.name
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'test_booking__user', 'test_booking__sport_test'
        )
