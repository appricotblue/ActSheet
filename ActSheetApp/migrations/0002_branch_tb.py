# Generated by Django 4.1.3 on 2022-11-19 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='branch_tb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=100)),
                ('location', models.CharField(default='', max_length=100)),
            ],
        ),
    ]
