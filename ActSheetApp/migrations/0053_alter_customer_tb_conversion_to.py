# Generated by Django 4.1.3 on 2022-12-23 19:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0052_alter_admin_tb_created_at_alter_admin_tb_updated_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer_tb',
            name='conversion_to',
            field=models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='ActSheetApp.staff_tb'),
        ),
    ]
