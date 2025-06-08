from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BinStatusViewSet, BinAlertsViewSet

router = DefaultRouter()
router.register(r'bin-status', BinStatusViewSet)
router.register(r'bin-alerts', BinAlertsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
