# Generated by Django 5.1.1 on 2024-12-21 11:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0018_botuser_count_generation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='botuser',
            name='count_generation',
        ),
    ]
