# Generated by Django 4.1.3 on 2022-12-03 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0024_alter_customer_tb_conversion_percentage_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer_tb',
            name='staff_id',
            field=models.CharField(default='', max_length=100),
        ),
    ]