
from django.contrib import admin
from .models import Gym, GymCapacity, MemberAttendance, GymSchedule, SportTest, TestReservation, GymTestAvailability

# Register your models here.

@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
    list_display = ['name', 'admin', 'phone', 'email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'address', 'phone', 'email', 'admin__username']
    list_editable = ['is_active']
    ordering = ['name']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('admin')

@admin.register(GymCapacity)
class GymCapacityAdmin(admin.ModelAdmin):
    list_display = ['gym', 'capacity', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'gym']
    search_fields = ['gym__name', 'description']
    list_editable = ['capacity', 'is_active']

@admin.register(MemberAttendance)
class MemberAttendanceAdmin(admin.ModelAdmin):
    list_display = ['member', 'gym', 'day_of_week', 'start_time', 'end_time', 'week_start_date', 'is_active']
    list_filter = ['day_of_week', 'is_active', 'week_start_date', 'gym']
    search_fields = ['member__username', 'member__first_name', 'member__last_name', 'gym__name']
    list_editable = ['is_active']
    date_hierarchy = 'week_start_date'

@admin.register(GymSchedule)
class GymScheduleAdmin(admin.ModelAdmin):
    list_display = ['gym', 'day_of_week', 'open_time', 'close_time', 'is_working_day']
    list_filter = ['day_of_week', 'is_working_day', 'gym']
    search_fields = ['gym__name', 'description']
    list_editable = ['open_time', 'close_time', 'is_working_day']

@admin.register(GymTestAvailability)
class GymTestAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['gym', 'date', 'is_available', 'reason', 'created_at']
    list_filter = ['is_available', 'date', 'created_at', 'gym']
    search_fields = ['gym__name', 'reason']
    list_editable = ['is_available']
    date_hierarchy = 'date'

@admin.register(SportTest)
class SportTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'gym', 'difficulty', 'duration', 'price', 'is_private', 'is_active', 'created_at']
    list_filter = ['difficulty', 'is_active', 'is_private', 'created_at', 'gym']
    search_fields = ['name', 'description', 'gym__name']
    list_editable = ['difficulty', 'duration', 'price', 'is_private', 'is_active']
    ordering = ['gym', 'name']

@admin.register(TestReservation)
class TestReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'sport_test', 'gym', 'reservation_date', 'start_time', 'end_time', 'status', 'created_at']
    list_filter = ['status', 'reservation_date', 'created_at', 'gym']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'sport_test__name', 'gym__name']
    list_editable = ['status']
    date_hierarchy = 'reservation_date'
    readonly_fields = ['created_at', 'updated_at']

