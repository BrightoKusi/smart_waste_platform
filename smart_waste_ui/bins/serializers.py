from rest_framework import serializers
from .models import BinStatus, BinAlerts

class BinStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = BinStatus
        fields = '__all__'

class BinAlertsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BinAlerts
        fields = '__all__'