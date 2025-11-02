# src/catalog/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'autores', views.AutorViewSet, basename='autor')
router.register(r'libros', views.LibroViewSet, basename='libro')
urlpatterns = [
    path('', include(router.urls)),
]