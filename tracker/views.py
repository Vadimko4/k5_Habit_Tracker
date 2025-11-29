from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Habit
from .serializers import HabitSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication


class HabitViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с привычками
    """
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        print(f"=== AUTH HEADER: {request.META.get('HTTP_AUTHORIZATION')}")
        print(f"=== USER: {request.user}")
        print(f"=== IS AUTHENTICATED: {request.user.is_authenticated}")
        return super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """
        Автоматически устанавливаем владельца при создании
        """
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def my_habits(self, request):
        """
        Эндпоинт для получения только своих привычек
        GET /habits/my_habits/
        """
        habits = Habit.objects.filter(owner=request.user)
        serializer = self.get_serializer(habits, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def public_habits(self, request):
        """
        Эндпоинт для получения всех публичных привычек (включая свои)
        GET /habits/public_habits/
        """
        habits = Habit.objects.filter(is_public=True)
        serializer = self.get_serializer(habits, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """
        Переопределяем стандартный list, чтобы он не был доступен напрямую
        Вместо этого направляем пользователя к конкретным эндпоинтам
        """
        return Response({
            "detail": "Используйте специфичные эндпоинты: /habits/my_habits/ или /habits/public_habits/"
        }, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        print("Current user:", self.request.user)
        print("Is authenticated:", self.request.user.is_authenticated)
        serializer.save(owner=self.request.user)
