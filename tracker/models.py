from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Habit(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название привычки'
    )
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        verbose_name="Обладатель",
        help_text="Укажите обладателя"
    )
    action = models.TextField(
        verbose_name='Действие',
        help_text='Введите действие'
    )
    place = models.TextField(
        blank=True,
        null=True,
        verbose_name='Место выполнения',
        help_text='Введите место выполнения'
    )
    execution_time = models.TimeField(
        verbose_name='Момент выполнения',
        help_text='Задайте момент выполнения'
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name='Приятная привычка'
    )
    frequency_days = models.PositiveIntegerField(
        default=1,
        verbose_name='Периодичность (дней)',
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        help_text='Раз в сколько дней выполнять'
    )
    execution_duration = models.DurationField(
        verbose_name='Длительность выполнения',
        default=timedelta(seconds=120),  # Фиксим ошибку здесь
        validators=[MinValueValidator(timedelta(seconds=1)),
                    MaxValueValidator(timedelta(seconds=120))],  # 1-120 секунд
        help_text='Сколько времени занимает выполнение (ЧЧ:ММ:СС)'
    )
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_to',
        verbose_name='Связанная привычка',
        help_text='Приятная привычка, связанная с текущей'
    )
    reward = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Вознаграждение',
        help_text='Чем себя вознаградить после выполнения'
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name='Можно смотреть всем',
        help_text='Укажите, можно ли показывать данную привычку всем'
    )

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['execution_time']

    def __str__(self):
        return f"{self.name} в {self.execution_time.strftime('%H:%M')}"

    def clean(self):
        errors = {}

        related = self.related_habit

        if self.is_pleasant:
            if related:
                errors['related_habit'] = 'У приятной привычки не может быть связанной привычки'
            if self.reward:
                errors['reward'] = 'У приятной привычки не может быть вознаграждения'
        else:
            # Проверка для полезной привычки: должна иметь либо связанную приятную привычку, либо вознаграждение
            if not related and not self.reward:
                errors[
                    '__all__'] = 'У полезной привычки должно быть либо связанная приятная привычка, либо вознаграждение'
            elif related and self.reward:
                errors['__all__'] = 'Нельзя одновременно указывать и связанную привычку и вознаграждение'

        if related and not related.is_pleasant:
            errors['related_habit'] = 'Связанная привычка должна быть приятной'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Вызываем валидацию перед сохранением"""
        self.full_clean()
        super().save(*args, **kwargs)
