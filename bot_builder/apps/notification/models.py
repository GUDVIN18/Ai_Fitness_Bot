from django.db import models
from django.utils import timezone
from apps.bot.models import BotUser
from datetime import timedelta
from django.utils.timezone import now


# Create your models here.
class Motivational_Messages(models.Model):
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name='motivational_messages', null=True, blank=True)
    text = models.TextField(verbose_name="Мотивационное сообщения")
    status = models.BooleanField(verbose_name="Статус", default=False)
    created_at = models.DateTimeField(verbose_name="Дата создания", default=now().replace(second=0, microsecond=0))

    class Meta:
        verbose_name = "Мотивационное сообщение"
        verbose_name_plural = "Мотивационные сообщения"