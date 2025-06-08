from django.shortcuts import render
from rest_framework import generics
from .models import BinStatus, BinAlerts
from .serializers import BinStatusSerializer, BinAlertsSerializer

# Create your views here.
class BinStatusList(generics.ListAPIView):
    queryset = BinStatus.objects.all().order_by('-timestamp')[:100]
    serializer_class = BinStatusSerializer

class BinAlertsList(generics.ListAPIView):
    queryset = BinAlerts.objects.all().order_by('-timestamp')[:100]
    serializer_class = BinAlertsSerializer