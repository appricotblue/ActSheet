# Generated by Django 4.1.3 on 2022-12-23 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0050_task_tb_request_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task_request_tb',
            name='created_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='task_request_tb',
            name='updated_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
    ]
