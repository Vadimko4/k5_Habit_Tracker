from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ['owner']

    def validate(self, data):
        # Получаем текущие значения
        is_pleasant = data.get('is_pleasant')
        related_habit = data.get('related_habit')
        reward = data.get('reward')

        # Для случаев частичного обновления (PATCH) используем существующие значения
        if self.instance:
            if is_pleasant is None:
                is_pleasant = self.instance.is_pleasant
            if related_habit is None:
                related_habit = self.instance.related_habit
            if reward is None:
                reward = self.instance.reward
        else:
            # Для создания, если is_pleasant не передан, используем False
            if is_pleasant is None:
                is_pleasant = False

        # Проверка 1: У приятной привычки не может быть связанной привычки или вознаграждения
        if is_pleasant:
            if related_habit:
                raise serializers.ValidationError({
                    'related_habit': 'У приятной привычки не может быть связанной привычки'
                })
            if reward:
                raise serializers.ValidationError({
                    'reward': 'У приятной привычки не может быть вознаграждения'
                })

        # Проверка 2: Для полезной привычки должно быть либо связанная привычка, либо вознаграждение
        if not is_pleasant:
            if not related_habit and not reward:
                raise serializers.ValidationError({
                    'non_field_errors': [
                        'У полезной привычки должно быть либо связанная приятная привычка, либо вознаграждение'
                    ]
                })

        # Проверка 3: Связанная привычка должна быть приятной
        if related_habit and not related_habit.is_pleasant:
            raise serializers.ValidationError({
                'related_habit': 'Связанная привычка должна быть приятной'
            })

        # Проверка 4: Нельзя одновременно иметь и связанную привычку и вознаграждение
        if related_habit and reward:
            raise serializers.ValidationError({
                'non_field_errors': [
                    'Нельзя одновременно указывать и связанную привычку и вознаграждение'
                ]
            })

        return data
