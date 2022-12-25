# Generated by Django 4.1.3 on 2022-12-06 10:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0027_rename_staff_id_customer_tb_staff_ids_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer_tb',
            name='branch_id',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='ActSheetApp.branch_tb'),
        ),
        migrations.AddField(
            model_name='customer_tb',
            name='job_id',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='ActSheetApp.job_tb'),
        ),
    ]
