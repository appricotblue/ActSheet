# Generated by Django 4.1.3 on 2023-01-10 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0091_delay_task_request_tb_status_remark_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff_attendance_break_tb',
            name='break_diff',
            field=models.CharField(default='', max_length=100, null=True),
        ),
    ]
