from django.urls import path

from greetings import views

API_VERSION = "api/v1/"

urlpatterns = [
    path(f"{API_VERSION}greetings/", views.list_greetings),
    path(f"{API_VERSION}greetings/create/", views.save_custom_greeting),
]
