from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import BinStatus, BinAlerts
from .serializers import BinStatusSerializer, BinAlertsSerializer
from django.shortcuts import render, get_object_or_404


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



def dashboard(request):
    bins = BinStatus.objects.order_by('-timestamp')[:5]
    alerts = BinAlerts.objects.order_by('-timestamp')[:5]
    total_bins = BinStatus.objects.values('bin_id').distinct().count()
    return render(request, 'bins/dashboard.html', {
        'bins': bins,
        'alerts': alerts,
        'total_bins': total_bins,
    })

def bin_list(request):
    bins = BinStatus.objects.order_by('-timestamp')[:100]
    return render(request, 'bins/bin_list.html', {'bins': bins})

def bin_detail(request, bin_id):
    bin_statuses = BinStatus.objects.filter(bin_id=bin_id).order_by('-timestamp')[:50]
    alerts = BinAlerts.objects.filter(bin_id=bin_id).order_by('-timestamp')
    return render(request, 'bins/bin_detail.html', {
        'bin_id': bin_id,
        'statuses': bin_statuses,
        'alerts': alerts
    })
