# Generated by Django 5.1.1 on 2024-12-30 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0014_botuser_products'),
    ]

    operations = [
        migrations.CreateModel(
            name='Text_Castom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('condition', models.TextField(verbose_name='Привязка')),
                ('text', models.TextField(verbose_name='Текст')),
            ],
            options={
                'verbose_name': 'Редактор текстово',
                'verbose_name_plural': 'Кнопки',
            },
        ),
    ]