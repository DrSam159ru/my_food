from django.urls import path

from .views import resolve_shortlink


app_name = 'shortlinks'

urlpatterns = [
    path('<str:code>/', resolve_shortlink, name='resolve'),
    path('<str:code>', resolve_shortlink),
]
