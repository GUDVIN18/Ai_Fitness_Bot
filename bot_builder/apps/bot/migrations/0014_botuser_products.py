# Generated by Django 5.1.1 on 2024-12-25 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0013_botuser_training_frequency'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='products',
            field=models.TextField(blank=True, null=True, verbose_name='Выбранные продукты'),
        ),
    ]