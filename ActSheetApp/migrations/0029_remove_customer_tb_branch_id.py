# Generated by Django 4.1.3 on 2022-12-06 11:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0028_customer_tb_branch_id_customer_tb_job_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer_tb',
            name='branch_id',
        ),
    ]