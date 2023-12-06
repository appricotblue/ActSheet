# Generated by Django 4.1.3 on 2023-01-05 06:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0086_alter_job_tb_actual_end_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staff_attendance_tb',
            name='client_id',
        ),
        migrations.RemoveField(
            model_name='staff_attendance_tb',
            name='short_break_in_1',
        ),
        migrations.RemoveField(
            model_name='staff_attendance_tb',
            name='short_break_in_2',
        ),
        migrations.RemoveField(
            model_name='staff_attendance_tb',
            name='short_break_in_3',
        ),
        migrations.RemoveField(
            model_name='staff_attendance_tb',
            name='short_break_in_4',
        ),
        migrations.RemoveField(
            model_name='staff_attendance_tb',
            name='short_break_out_1',
        ),
        migrations.RemoveField(
            model_name='staff_attendance_tb',
            name='short_break_out_2',
        ),
        migrations.RemoveField(
            model_name='staff_attendance_tb',
            name='short_break_out_3',
        ),
        migrations.RemoveField(
            model_name='staff_attendance_tb',
            name='short_break_out_4',
        ),
        migrations.CreateModel(
            name='staff_attendance_break_tb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('out_time', models.CharField(default='', max_length=100, null=True)),
                ('in_time', models.CharField(default='', max_length=100, null=True)),
                ('break_type', models.CharField(default='', max_length=100, null=True)),
                ('created_at', models.DateTimeField(default='', max_length=100)),
                ('updated_at', models.DateTimeField(default='', max_length=100)),
                ('attendance_id', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='ActSheetApp.staff_attendance_tb')),
            ],
        ),
    ]
