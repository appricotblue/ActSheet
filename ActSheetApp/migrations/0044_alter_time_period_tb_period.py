# Generated by Django 4.1.3 on 2022-12-21 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0043_time_period_tb'),
    ]

    operations = [
        migrations.AlterField(
            model_name='time_period_tb',
            name='period',
            field=models.CharField(default='', max_length=100),
        ),
    ]
