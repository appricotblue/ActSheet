# Generated by Django 4.1.3 on 2022-12-23 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0053_alter_customer_tb_conversion_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer_tb',
            name='conversion_percentage',
            field=models.IntegerField(default='', null=True),
        ),
    ]
