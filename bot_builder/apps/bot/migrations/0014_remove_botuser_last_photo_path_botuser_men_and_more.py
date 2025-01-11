# Generated by Django 5.1.1 on 2024-12-16 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0013_botuser_last_photo_path'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='botuser',
            name='last_photo_path',
        ),
        migrations.AddField(
            model_name='botuser',
            name='men',
            field=models.BooleanField(blank=True, default=True, null=True, verbose_name='Мужчина'),
        ),
        migrations.AddField(
            model_name='botuser',
            name='now_num',
            field=models.IntegerField(blank=True, null=True, verbose_name='Текущее кол-во фото в папке'),
        ),
        migrations.AddField(
            model_name='botuser',
            name='photo_count',
            field=models.IntegerField(blank=True, null=True, verbose_name='Количество фото'),
        ),
        migrations.AddField(
            model_name='botuser',
            name='promt_number',
            field=models.IntegerField(blank=True, null=True, verbose_name='Номер промта'),
        ),
        migrations.AddField(
            model_name='botuser',
            name='women',
            field=models.BooleanField(blank=True, default=True, null=True, verbose_name='Женщина'),
        ),
    ]
