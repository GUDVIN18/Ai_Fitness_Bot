# Generated by Django 5.1.1 on 2024-12-24 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0010_botuser_allergies_alter_botuser_age_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='last_message_id',
            field=models.BigIntegerField(blank=True, help_text='ID последнего отправленного сообщения с кнопками', null=True),
        ),
    ]
