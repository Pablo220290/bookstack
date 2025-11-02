# src/catalog/admin.py

from django.contrib import admin
from .models import Autor, Libro

@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    """
    Configuración del Admin para el modelo Autor.
    """
    list_display = ('first_name', 'last_name', 'birth_date')
    search_fields = ('first_name', 'last_name')


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    """
    Configuración del Admin para el modelo Libro.
    """
    list_display = ('title', 'isbn', 'publication_date')
    search_fields = ('title', 'isbn')
    filter_horizontal = ('autores',)