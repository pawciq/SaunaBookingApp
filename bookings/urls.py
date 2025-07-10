# bookings/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('saunas/', views.sauna_list, name='sauna_list'),
    path('saunas/<int:pk>/reserve/', views.SaunaReservationView.as_view(), name='sauna_reserve'),
    path('my_reservations/', views.my_reservations, name='my_reservations'),
]