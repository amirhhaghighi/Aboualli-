from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CoachViewSet, CoachGymListViewSet, TestAssignmentViewSet, CoachProfileViewSet, CoachTestAvailabilityViewSet

router = DefaultRouter()
router.register(r'coaches', CoachViewSet)
router.register(r'coach-profiles', CoachProfileViewSet)
router.register(r'coach-gym-list', CoachGymListViewSet)
router.register(r'test-assignments', TestAssignmentViewSet)
router.register(r'coach-test-availabilities', CoachTestAvailabilityViewSet)

app_name = 'coachpanel'

urlpatterns = [
    path('api/', include(router.urls)),
] 