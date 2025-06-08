# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class BinStatus(models.Model):
    id = models.AutoField(primary_key=True)
    bin_id = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    fill_level = models.DecimalField(max_digits=5, decimal_places=2)
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    battery_level = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(blank=True, null=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Bin {self.bin_id} - {self.status}"


    class Meta:
        db_table = 'bin_status'


class BinAlerts(models.Model):
    id = models.AutoField(primary_key=True)
    bin_id = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    alert = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Bin {self.bin_id} - {self.alert}"

    class Meta:
        db_table = 'bin_alerts'


