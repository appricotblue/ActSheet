# Generated by Django 4.1.3 on 2022-11-22 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0007_team_leader_tb'),
    ]

    operations = [
        migrations.AddField(
            model_name='team_leader_tb',
            name='phone',
            field=models.CharField(default='', max_length=100),
        ),
    ]
