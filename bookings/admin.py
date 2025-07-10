from django.contrib import admin

# Register your models here.
# bookings/admin.py
from django.contrib import admin
from .models import Sauna, Reservation # Importujemy nasze modele

# Rejestrujemy model Sauna
@admin.register(Sauna)
class SaunaAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'price_per_hour', 'is_active') # Pola wyświetlane na liście
    list_filter = ('is_active',) # Filtr boczny
    search_fields = ('name', 'description') # Pola do wyszukiwania

# Rejestrujemy model Reservation
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'sauna', 'start_time', 'end_time', 'total_price', 'status', 'payment_id')
    list_filter = ('status', 'sauna', 'start_time') # Filtry boczna
    search_fields = ('user__username', 'sauna__name', 'payment_id') # Pola do wyszukiwania
    raw_id_fields = ('user', 'sauna') # Umożliwia łatwiejsze wyszukiwanie userów i saun po ID
    date_hierarchy = 'start_time' # Hierarchiczne daty
    readonly_fields = ('created_at',) # Pole tylko do odczytu