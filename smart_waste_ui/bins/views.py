from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import BinStatus, BinAlerts
from .serializers import BinStatusSerializer, BinAlertsSerializer

class BinStatusViewSet(viewsets.ModelViewSet):
    queryset = BinStatus.objects.all().order_by('-timestamp')
    serializer_class = BinStatusSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'bin_id']
    search_fields = ['bin_id', 'status']
    ordering_fields = ['timestamp', 'fill_level', 'temperature']

class BinAlertsViewSet(viewsets.ModelViewSet):
    queryset = BinAlerts.objects.all().order_by('-timestamp')
    serializer_class = BinAlertsSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['bin_id']
    search_fields = ['alert', 'bin_id']
    ordering_fields = ['timestamp']
