# Generated by Django 4.1.3 on 2022-12-19 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0035_client_tb_status_job_tb_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='task_tb',
            name='status',
            field=models.CharField(default='Pending', max_length=100),
        ),
    ]
