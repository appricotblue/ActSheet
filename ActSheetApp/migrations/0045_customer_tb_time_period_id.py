# Generated by Django 4.1.3 on 2022-12-22 07:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0044_alter_time_period_tb_period'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer_tb',
            name='time_period_id',
            field=models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='ActSheetApp.time_period_tb'),
        ),
    ]
