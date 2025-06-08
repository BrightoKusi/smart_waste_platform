from django.contrib import admin
from .models import BinStatus, BinAlerts
# Register your models here.
admin.site.register(BinStatus)
admin.site.register(BinAlerts)