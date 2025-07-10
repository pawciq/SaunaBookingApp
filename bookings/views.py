# bookings/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin  # Aby wymagać logowania
from django.contrib import messages  # Do wyświetlania komunikatów
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required

from .models import Sauna, Reservation
from .forms import ReservationForm  # Importuj nasz formularz


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


def sauna_list(request):
    saunas = Sauna.objects.filter(is_active=True).order_by('name')
    return render(request, 'bookings/sauna_list.html', {'saunas': saunas})

@login_required # Dekorator, który wymusza zalogowanie
def my_reservations(request):
    # Pobierz wszystkie rezerwacje dla bieżącego zalogowanego użytkownika
    # Posortowane od najnowszych do najstarszych terminów rozpoczęcia
    user_reservations = Reservation.objects.filter(user=request.user).order_by('-start_time')

    # Opcjonalnie, podziel rezerwacje na nadchodzące i przeszłe
    current_time = datetime.now().astimezone() # Upewnij się, że datetime jest zaimportowane

    upcoming_reservations = user_reservations.filter(end_time__gt=current_time)
    past_reservations = user_reservations.filter(end_time__lte=current_time)

    context = {
        'upcoming_reservations': upcoming_reservations,
        'past_reservations': past_reservations,
    }
    return render(request, 'bookings/my_reservations.html', context)


class SaunaReservationView(LoginRequiredMixin, generic.CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'bookings/sauna_reservation.html'
    context_object_name = 'sauna'  # Zmieniamy nazwę kontekstu na 'sauna'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pobieramy obiekt sauny na podstawie ID z URL
        sauna_id = self.kwargs.get('pk')
        context['sauna'] = get_object_or_404(Sauna, pk=sauna_id)
        return context

    def form_valid(self, form):
        # Pobierz saunę, dla której tworzona jest rezerwacja
        sauna = get_object_or_404(Sauna, pk=self.kwargs.get('pk'))

        # Przypisz bieżącego użytkownika i saunę do instancji rezerwacji
        form.instance.user = self.request.user
        form.instance.sauna = sauna

        # Oblicz end_time (już obliczone w clean formularza, ale upewniamy się)
        start_time = form.cleaned_data['start_time']
        duration_hours = form.cleaned_data['duration_hours']
        # Upewnij się, że masz zaimportowany `datetime` również tutaj na górze pliku,
        # bo `timedelta` używasz razem ze zmienną `start_time` która jest obiektem datetime.
        # W Twoim kodzie masz tylko `from datetime import timedelta`, dodaj też `datetime`
        # Poprawka: from datetime import datetime, timedelta
        end_time = start_time + timedelta(hours=duration_hours)
        form.instance.end_time = end_time

        # Oblicz cenę
        form.instance.total_price = sauna.price_per_hour * duration_hours

        # Domyślny status
        form.instance.status = 'pending'  # Oczekuje na płatność

        # Sprawdzanie kolizji - kluczowy element!
        colliding_reservations = Reservation.objects.filter(
            sauna=sauna,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status__in=['pending', 'paid']
        )
        # exclude(pk=form.instance.pk) jest ważne przy edycji istniejącej rezerwacji
        # W CreateView nie ma jeszcze pk, więc to exclude jest zbędne, ale nie szkodzi.
        # Jeśli dodasz je do exclude w CreateView, upewnij się, że nie rzucasz błędu
        # gdy form.instance.pk jest None. W Django 3+ to jest obsługiwane.

        if colliding_reservations.exists():
            messages.error(self.request, "Wybrany termin koliduje z istniejącą rezerwacją. Proszę wybrać inny termin.")
            return self.form_invalid(form)  # Powróć do formularza z błędem

        # Jeśli nie ma kolizji, zapisz rezerwację
        response = super().form_valid(form)

        # KOMUNIKAT ZMIENIONY:
        messages.success(self.request, "Twoja rezerwacja została wstępnie utworzona! Oczekuje na potwierdzenie.")

        # PRZEKIEROWANIE ZMIENIONE (już było, ale podkreślamy)
        return redirect('home')

    def get_success_url(self):
        # Ta metoda jest potrzebna dla generic.CreateView, ale nadpisujemy form_valid
        return reverse_lazy('home')