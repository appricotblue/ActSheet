# Generated by Django 4.1.3 on 2022-11-29 10:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0016_alter_staff_tb_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='task_tb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(default='', max_length=100)),
                ('title', models.CharField(default='', max_length=100)),
                ('description', models.TextField(default='')),
                ('start_date', models.DateTimeField(default='', max_length=100)),
                ('end_date', models.DateTimeField(default='', max_length=100)),
                ('start_time', models.CharField(default='', max_length=100)),
                ('end_time', models.CharField(default='', max_length=100)),
                ('required_hrs', models.CharField(default='', max_length=100)),
                ('created_at', models.CharField(default='', max_length=100)),
                ('updated_at', models.CharField(default='', max_length=100)),
                ('agent_id', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='ActSheetApp.agent_tb')),
                ('job_id', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='ActSheetApp.job_tb')),
            ],
        ),
    ]
