from django.urls import path

from config.settings.base import API_VERSION
from greetings import views

app_name = 'greetings'
api_version: str = API_VERSION.GREETINGS

urlpatterns = [
    path(f"{api_version}greetings/", views.list_greetings, name='list_greetings'),
    path(f"{api_version}greeting/", views.save_custom_greeting, name='save_custom_greeting'),
]
