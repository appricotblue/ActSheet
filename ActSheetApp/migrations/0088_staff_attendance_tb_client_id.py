# Generated by Django 4.1.3 on 2023-01-05 06:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0087_remove_staff_attendance_tb_client_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff_attendance_tb',
            name='client_id',
            field=models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='ActSheetApp.client_tb'),
        ),
    ]