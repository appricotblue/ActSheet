# Generated by Django 4.1.3 on 2022-12-03 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0025_alter_customer_tb_staff_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer_tb',
            name='conversion_to',
            field=models.CharField(default='', max_length=100),
        ),
    ]
