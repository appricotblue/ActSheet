# Generated by Django 4.1.3 on 2022-12-25 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ActSheetApp', '0057_complaint_ticket_tb'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff_tb',
            name='image',
            field=models.ImageField(null=True, upload_to='image'),
        ),
    ]