from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MembershipPlanViewSet, MembershipViewSet, MembershipPaymentViewSet,
    MembershipReviewViewSet, MembershipHistoryViewSet, GymMembershipRequestViewSet
)

router = DefaultRouter()
router.register(r'plans', MembershipPlanViewSet, basename='membership-plan')
router.register(r'memberships', MembershipViewSet, basename='membership')
router.register(r'payments', MembershipPaymentViewSet, basename='membership-payment')
router.register(r'reviews', MembershipReviewViewSet, basename='membership-review')
router.register(r'history', MembershipHistoryViewSet, basename='membership-history')
router.register(r'requests', GymMembershipRequestViewSet, basename='gym-membership-request')

urlpatterns = [
    path('api/', include(router.urls)),
] 