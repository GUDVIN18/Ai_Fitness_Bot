# Generated by Django 5.1.1 on 2025-01-08 13:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0020_alter_payment_options_motivational_messages'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Motivational_Messages',
        ),
    ]