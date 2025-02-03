from django.urls import path
from . import views

#renombrar el archivo
urlpatterns = [
<<<<<<< HEAD
    ###path("autenticacion/", views.autenticacion, name="autenticacion"),

    path('autenticacion/', views.AutenticacionAPIView.as_view(), name='autenticacion-api'),
=======
    path("autenticacion/", views.autenticacion, name="autenticacion"),
>>>>>>> parent of 1e0a649 (new)
]
