# Generated by Django 4.1.3 on 2022-12-21 05:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0039_staff_attendance_tb_client_id_task_tb_client_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='window_zone_tb',
            name='client_id',
            field=models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='ActSheetApp.client_tb'),
        ),
        migrations.AddField(
            model_name='zone_tb',
            name='client_id',
            field=models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='ActSheetApp.client_tb'),
        ),
    ]