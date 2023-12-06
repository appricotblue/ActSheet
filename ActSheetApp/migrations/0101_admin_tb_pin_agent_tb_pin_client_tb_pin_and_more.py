# Generated by Django 4.1.3 on 2023-02-10 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0100_branch_tb_cc'),
    ]

    operations = [
        migrations.AddField(
            model_name='admin_tb',
            name='pin',
            field=models.CharField(default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='agent_tb',
            name='pin',
            field=models.CharField(default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='client_tb',
            name='pin',
            field=models.CharField(default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='team_leader_tb',
            name='pin',
            field=models.CharField(default='', max_length=100, null=True),
        ),
    ]