from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone



class TelegramBotConfig(models.Model):
    bot_token = models.CharField(max_length=100)
    is_activ = models.BooleanField(null=False, blank=False, default=False, verbose_name="Is active")

    def __str__(self):
        return f'{self.bot_token}'

    class Meta:
        verbose_name = "Токен"
        verbose_name_plural = "Токены"





class BotUser(models.Model):
    tg_id = models.BigIntegerField(unique=True, verbose_name="ID Telegram")
    first_name = models.CharField(max_length=250, verbose_name="Имя пользователя", blank=True, null=True)
    last_name = models.CharField(max_length=250, verbose_name="Фамилия пользователя", blank=True, null=True)
    username = models.CharField(max_length=250, verbose_name="Username пользователя", blank=True, null=True)
    language = models.CharField(max_length=250, verbose_name="Язык пользователя", blank=True, null=True)

    premium = models.BooleanField(verbose_name="Имеет ли пользователь премиум-аккаунт", default=False, blank=True, null=True)
    # state = models.CharField(max_length=110, choices=STATE_CHOICES, default='')
    state = models.CharField(max_length=255, help_text='Состояние')

    last_message_id = models.BigIntegerField(null=True, blank=True, help_text="ID последнего отправленного сообщения с кнопками")
    last_input_message_id = models.BigIntegerField(null=True, blank=True, help_text="ID последнего отправленного сообщения без кнопок")


    #Для бота
    CHOOCE = ['ru', 'en']
    language_chooce = models.CharField(max_length=4, choices=[(x, x) for x in CHOOCE], verbose_name="Выбор языка", blank=True, null=True)
    gender = models.CharField(max_length=222, verbose_name="Гендр", blank=True, null=True)
    age = models.CharField(max_length=222, verbose_name="Возраст", blank=True, null=True)
    massa = models.CharField(max_length=222, verbose_name="Вес", blank=True, null=True)
    height = models.CharField(max_length=222, verbose_name="Рост (в см)", blank=True, null=True)
    purpose = models.CharField(max_length=222, verbose_name="Выбранная цель", blank=True, null=True)
    allergies = models.TextField(verbose_name="Наличие аллергии", blank=True, null=True)
    protein = models.TextField(verbose_name="Категория протеина исходя из цели", blank=True, null=True)
    training_frequency = models.BigIntegerField(verbose_name="Частота тренировок в неделю", blank=True, null=True)
    products = models.TextField(verbose_name="Выбранные продукты", blank=True, null=True)

    #Меню и подписка
    menu = models.TextField(verbose_name="Меню", blank=True, null=True)
    subscription = models.BooleanField(verbose_name="Подписка", default=False, blank=True, null=True)
    subscribe_data_start = models.DateField(null=True, blank=True)
    subscribe_data_end = models.DateField(null=True, blank=True)

    #Последний совет
    council = models.TextField(verbose_name="Последний совет", blank=True, null=True)
    temporary_training_id = models.BigIntegerField(verbose_name="ID временной тренировки", blank=True, null=True)


    def __str__(self):
        return f"user_object {self.tg_id} {self.username}"

    class Meta:
        verbose_name = "Пользователь бота"
        verbose_name_plural = "Пользователи бота"






class Bot_Message(models.Model):
    text = models.TextField(verbose_name="Текст сообщения")
    current_state =  models.CharField(max_length=110, verbose_name="К какому состоянию привязана?", default=None, unique=True)
    next_state = models.CharField(max_length=255, verbose_name="Ссылка на состояние при вводе", default=None, null=True, blank=True)
    anyway_link = models.CharField(max_length=110, help_text="На какое состояние пебрасывает пользователя", null=True, blank=True, unique=True)
    handler = models.CharField(max_length=255, verbose_name="Имя функции обработчика", null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.text[:50]}... (Состояние: {self.current_state if self.current_state is not None else self.anyway_link})"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"



class Bot_Commands(models.Model):
    text = models.CharField(max_length=255, verbose_name="Текст команды")
    trigger = models.ForeignKey(Bot_Message, on_delete=models.SET_NULL, null=True, blank=True, related_name='triggered_commands', verbose_name="Связанное сообщение")

    def __str__(self):
        return f"{self.text} (Триггер: {self.trigger})"

    class Meta:
        verbose_name = "Команду / reply кнопку"
        verbose_name_plural = "Команды / reply кнопки"



class Bot_Button(models.Model):
    text = models.CharField(max_length=255, verbose_name="Текст кнопки")
    message_trigger = models.ForeignKey(Bot_Message, on_delete=models.SET_NULL, null=True, blank=True, related_name='message_triggered', verbose_name="Связанное сообщение")
    data = models.CharField(max_length=255, verbose_name='Данные', default='')

    def __str__(self):
        return f"{self.text} (Триггер: {self.message_trigger})"

    class Meta:
        verbose_name = "Кнопку"
        verbose_name_plural = "Кнопки"



class Text_Castom(models.Model):
    condition = models.TextField(verbose_name="Привязка")
    text = models.TextField(verbose_name="Текст")

    class Meta:
        verbose_name = "Редактор текстовок"
        verbose_name_plural = "Редактор текстовок"



class Payment(models.Model):
    payment_id = models.TextField(verbose_name="id заявки")
    status = models.CharField(max_length=255, verbose_name="статус оплаты")
    user_id = models.CharField(max_length=255, verbose_name="id пользоователя")
    created_at = models.DateTimeField(verbose_name="Дата создания", default=timezone.now)

    class Meta:
        verbose_name = "Оплату"
        verbose_name_plural = "Оплаты"



class UserTraining(models.Model):
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name='usertraining', null=True, blank=True)
    name_traning = models.TextField(verbose_name="Название тренировки", null=True, blank=True)
    training_data = models.DateTimeField(verbose_name="Дата и время проведения тренировки", null=True, blank=True)
    status = models.BooleanField(verbose_name="Статус отправки уведа", default=False, blank=True, null=True)

    class Meta:
        verbose_name = "Тренировку"
        verbose_name_plural = "Тренировки"
