# Generated by Django 4.1.3 on 2022-12-22 07:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0047_customer_tb_client_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer_tb',
            name='client_id',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='ActSheetApp.client_tb'),
        ),
    ]
