# Generated by Django 4.1.3 on 2022-12-25 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0063_delay_task_request_tb_status_changed_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delay_task_request_tb',
            name='status_changed_by',
            field=models.CharField(default='', max_length=100, null=True),
        ),
    ]
