# sauna_booking_app/urls.py
from django.contrib import admin
from django.urls import path, include # Dodaj 'include'
from django.views.generic.base import TemplateView # Importujemy TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), # Dodaj tę linię dla autentykacji
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('bookings/', include('bookings.urls')),# Tymczasowa strona główna
    # Tutaj będziemy dodawać inne ścieżki URL dla naszej aplikacji bookings
]