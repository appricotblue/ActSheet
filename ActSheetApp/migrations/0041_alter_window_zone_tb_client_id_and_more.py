# Generated by Django 4.1.3 on 2022-12-21 05:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0040_window_zone_tb_client_id_zone_tb_client_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='window_zone_tb',
            name='client_id',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='ActSheetApp.client_tb'),
        ),
        migrations.AlterField(
            model_name='zone_tb',
            name='client_id',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='ActSheetApp.client_tb'),
        ),
    ]