# Generated by Django 4.1.3 on 2022-12-23 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0051_alter_task_request_tb_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin_tb',
            name='created_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='admin_tb',
            name='updated_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='agent_tb',
            name='created_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='agent_tb',
            name='updated_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='branch_tb',
            name='created_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='branch_tb',
            name='updated_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='client_tb',
            name='created_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='client_tb',
            name='updated_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='customer_tb',
            name='created_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='customer_tb',
            name='updated_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='job_tb',
            name='created_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='job_tb',
            name='updated_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='shift_tb',
            name='created_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='shift_tb',
            name='updated_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='staff_attendance_tb',
            name='created_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='staff_attendance_tb',
            name='updated_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='staff_tb',
            name='created_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='staff_tb',
            name='updated_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='task_tb',
            name='created_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='task_tb',
            name='updated_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='team_leader_tb',
            name='created_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='team_leader_tb',
            name='updated_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='time_period_tb',
            name='created_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='time_period_tb',
            name='updated_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='window_zone_tb',
            name='created_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='window_zone_tb',
            name='updated_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='zone_tb',
            name='created_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='zone_tb',
            name='updated_at',
            field=models.DateTimeField(default='', max_length=100),
        ),
    ]
