# Generated by Django 5.1.1 on 2025-01-10 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0025_alter_bot_commands_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='last_input_message_id',
            field=models.BigIntegerField(blank=True, help_text='ID последнего отправленного сообщения без кнопок', null=True),
        ),
    ]
