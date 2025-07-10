# bookings/forms.py
from django import forms
from .models import Reservation
from datetime import datetime, timedelta


class ReservationForm(forms.ModelForm):
    # Wybieramy konkretne pole daty/czasu z inputem HTML5
    # Data i godzina będą wybierane w jednym polu (datetime-local)
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M'],
        label="Data i godzina rozpoczęcia"
    )
    # Czas trwania (w godzinach), zamiast ręcznie ustawiać end_time
    duration_hours = forms.IntegerField(
        min_value=1,
        max_value=4,  # Możesz dostosować maksymalny czas trwania
        initial=1,
        label="Czas trwania (godziny)"
    )

    class Meta:
        model = Reservation
        # Pomijamy 'end_time', 'total_price', 'status', 'user', 'sauna', 'payment_id'
        # Te pola będą ustawiane automatycznie w widoku.
        fields = ['start_time', 'duration_hours']

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        duration_hours = cleaned_data.get('duration_hours')

        if start_time and duration_hours:
            # Oblicz end_time na podstawie start_time i duration_hours
            end_time = start_time + timedelta(hours=duration_hours)
            cleaned_data['end_time'] = end_time

            # Walidacja: upewnij się, że data jest w przyszłości
            if start_time < datetime.now().astimezone(start_time.tzinfo):
                raise forms.ValidationError("Nie można rezerwować sauny na przeszłe terminy.")

            # Walidacja: upewnij się, że godzina rozpoczęcia jest pełną godziną lub półgodziną
            # Przykładowo, jeśli chcesz zezwolić tylko na rezerwacje zaczynające się o pełnych godzinach
            # if start_time.minute != 0:
            #     raise forms.ValidationError("Rezerwacje muszą zaczynać się o pełnych godzinach.")

            # Walidacja: Sprawdzanie dostępności sauny (zostanie zrobione w widoku, ale można też tutaj)
            # Na tym etapie nie mamy dostępu do wybranej sauny, więc lepiej to zrobić w widoku.

        return cleaned_data