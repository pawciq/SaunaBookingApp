from django.db import models

# Create your models here.
# bookings/models.py
from django.db import models
from django.contrib.auth.models import User # Importujemy model User do powiązania rezerwacji z użytkownikiem

class Sauna(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nazwa sauny")
    description = models.TextField(blank=True, verbose_name="Opis")
    capacity = models.PositiveIntegerField(default=1, verbose_name="Pojemność (osoby)")
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Cena za godzinę")
    is_active = models.BooleanField(default=True, verbose_name="Aktywna")

    class Meta:
        verbose_name = "Sauna"
        verbose_name_plural = "Sauny"
        ordering = ['name'] # Domyślne sortowanie w panelu admina

    def __str__(self):
        return self.name

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Oczekuje na płatność'),
        ('paid', 'Opłacona'),
        ('cancelled', 'Anulowana'),
        ('completed', 'Zrealizowana'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations', verbose_name="Użytkownik")
    sauna = models.ForeignKey(Sauna, on_delete=models.CASCADE, related_name='reservations', verbose_name="Sauna")
    start_time = models.DateTimeField(verbose_name="Czas rozpoczęcia")
    end_time = models.DateTimeField(verbose_name="Czas zakończenia")
    total_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Całkowita cena")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status rezerwacji")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    payment_id = models.CharField(max_length=255, blank=True, null=True, unique=True, verbose_name="ID płatności (Przelewy24)")

    class Meta:
        verbose_name = "Rezerwacja"
        verbose_name_plural = "Rezerwacje"
        # Ograniczenie: nie można rezerwować tej samej sauny w tym samym czasie.
        # Należy pamiętać, że to ograniczenie na poziomie bazy danych.
        # W widokach będziemy musieli dodać logikę sprawdzania dostępności
        # w całym przedziale czasowym, a nie tylko w punkcie.
        unique_together = ('sauna', 'start_time', 'end_time')
        ordering = ['start_time']

    def __str__(self):
        return f"Rezerwacja {self.sauna.name} przez {self.user.username} od {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    # Dodaj metodę do obliczania czasu trwania rezerwacji w godzinach
    def get_duration_in_hours(self):
        duration = self.end_time - self.start_time
        return duration.total_seconds() / 3600