from django.urls import path
from . import views

#renombrar el archivo
urlpatterns = [
    path("autenticacion/", views.autenticacion, name="autenticacion"),
]
