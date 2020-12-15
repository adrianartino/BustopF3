"""Bustop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin #panel de administracion
from django.urls import path #path
from appBustop import views #vistas

from django.conf import settings
from django.conf.urls.static import static
# login, registro, olvido, principalUsuario, buscarRuta, ubicacionRuta, mapaRutaGomez, mapaRutaTorreon, mapaRutaLerdo, quejaUsuario, principalCons, infoCons, quejasCons, usuariosCons, principalAdmin, altaRuta, altaCons, actCons, actUsuario
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('registro/', views.registro),
    path('olvido/', views.olvido),
    path('principalUsuario/', views.principalUsuario),
    path('buscarRuta/', views.buscarRuta),
    path('ubicacionRuta/', views.ubicacionRuta),
    path('mapaRutaGomez/', views.mapaRutaGomez),
    path('mapaRutaTorreon/', views.mapaRutaTorreon),
    path('mapaRutaLerdo/', views.mapaRutaLerdo),
    path('quejaUsuario/', views.quejaUsuario),
    path('principalCons/', views.principalCons),
    path('infoCons/', views.infoCons),
    path('quejasCons/', views.quejasCons),
    path('usuariosCons/', views.usuariosCons),
    path('principalAdmin/', views.principalAdmin),
    path('altaRuta/', views.altaRuta),
    path('altaCons/', views.altaCons),
    path('bajaRuta/', views.bajaRuta),
    path('bajaCons/', views.bajaCons),
    path('actUsuario/', views.actUsuario),
    path('actCons/', views.actCons),
    path('salir/', views.salir),
    path('salirAdmin/', views.salirAdmin),
    path('salirCons/', views.salirCons),
    path('infoRuta/', views.infoRuta),
    path('usuariosAdmin/', views.usuariosAdmin),
    path('verPdf/', views.verPdf),
    path('verPdfBusquedas/', views.verPdfBusquedas),
    path('verPdfUsuarios/', views.verPdfUsuarios)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
