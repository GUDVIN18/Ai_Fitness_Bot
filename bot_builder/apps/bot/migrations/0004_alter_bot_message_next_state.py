# Generated by Django 5.1.1 on 2024-09-26 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_alter_bot_button_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bot_message',
            name='next_state',
            field=models.CharField(default='', max_length=255, verbose_name='Ожидается ли изменение состояния на ввод'),
        ),
    ]
