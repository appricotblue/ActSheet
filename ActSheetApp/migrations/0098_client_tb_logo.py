# Generated by Django 4.1.3 on 2023-01-30 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0097_staff_attendance_tb_official_break_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client_tb',
            name='logo',
            field=models.ImageField(null=True, upload_to='image'),
        ),
    ]