from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GymViewSet, GymCapacityViewSet, MemberAttendanceViewSet,
    GymScheduleViewSet, SportTestViewSet, TestReservationViewSet, GymTestAvailabilityViewSet
)

router = DefaultRouter()
router.register(r'gyms', GymViewSet)
router.register(r'capacities', GymCapacityViewSet)
router.register(r'attendances', MemberAttendanceViewSet)
router.register(r'schedules', GymScheduleViewSet)
router.register(r'test-availabilities', GymTestAvailabilityViewSet)
router.register(r'sport-tests', SportTestViewSet)
router.register(r'reservations', TestReservationViewSet)

app_name = 'gympanel'

urlpatterns = [
    path('api/', include(router.urls)),
] 