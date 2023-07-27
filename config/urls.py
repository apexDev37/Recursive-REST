from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("greetings/", include("greetings.urls")),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]
