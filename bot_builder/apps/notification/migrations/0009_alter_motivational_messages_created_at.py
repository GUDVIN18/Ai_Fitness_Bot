# Generated by Django 5.1.1 on 2025-01-10 10:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0008_alter_motivational_messages_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='motivational_messages',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 1, 10, 10, 5, tzinfo=datetime.timezone.utc), verbose_name='Дата создания'),
        ),
    ]
