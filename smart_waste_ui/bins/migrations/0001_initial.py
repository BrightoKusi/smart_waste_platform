# Generated by Django 5.2.2 on 2025-06-08 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BinAlerts',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bin_id', models.CharField(blank=True, max_length=100, null=True)),
                ('timestamp', models.DateTimeField(blank=True, null=True)),
                ('alert', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'bin_alerts',
            },
        ),
        migrations.CreateModel(
            name='BinStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bin_id', models.CharField(max_length=50)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=10)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=10)),
                ('fill_level', models.DecimalField(decimal_places=2, max_digits=5)),
                ('temperature', models.DecimalField(decimal_places=2, max_digits=5)),
                ('battery_level', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('status', models.CharField(blank=True, max_length=20, null=True)),
                ('timestamp', models.DateTimeField()),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'bin_status',
            },
        ),
    ]
