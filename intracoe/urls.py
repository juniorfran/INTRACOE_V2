"""
URL configuration for intracoe project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views

urlpatterns = [

    path('', views.index, name='index'),  # URL raíz que carga la vista index
    path('admin/', admin.site.urls),
    path('rrhh/', include('RRHH.urls')),
    path('fe/', include('FE.urls')),
    path('contabilidad/', include('CONTABILIDAD.urls')),
    path('informatica/', include('INFORMATICA.urls')),

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
