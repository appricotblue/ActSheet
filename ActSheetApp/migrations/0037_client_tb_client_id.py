# Generated by Django 4.1.3 on 2022-12-19 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0036_task_tb_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='client_tb',
            name='client_id',
            field=models.CharField(default='', max_length=100),
        ),
    ]
