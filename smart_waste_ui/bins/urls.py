from django.urls import path
from .views import BinStatusList, BinAlertsList

urlpatterns = [
    path('bin-status/', BinStatusList.as_view(), name='bin-status'),
    path('bin-alerts/', BinAlertsList.as_view(), name='bin-alerts'),
]