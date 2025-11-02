# src/catalog/services.py

from django.db import transaction
from django.db.models import Count
from .models import Autor, Libro
from core.exceptions import ResourceNotFoundError, BusinessValidationError, DuplicateResourceError
from typing import List, Dict, Any
import uuid

# --- Servicios de AUTOR ---

def list_autores():
    """
    Servicio para listar autores con 'annotate'.
    Añade 'book_count' a cada autor.
    """
    queryset = Autor.objects.annotate(
        book_count=Count('libros')
    ).order_by('last_name', 'first_name')
    
    return queryset

def create_autor(*, data: Dict[str, Any]) -> Autor:
    """
    Servicio para crear un nuevo autor.
    'data' es un diccionario ya validado por el serializer.
    """
    autor = Autor.objects.create(**data)
    return autor

def get_autor(*, pk: uuid.UUID) -> Autor:
    """
    Servicio para obtener un autor por su PK (UUID).
    Lanza ResourceNotFoundError si no existe.
    """
    try:
        return Autor.objects.get(pk=pk)
    except Autor.DoesNotExist:
        raise ResourceNotFoundError(detail=f"Autor con id={pk} no encontrado.")

def update_autor(*, autor: Autor, data: Dict[str, Any]) -> Autor:
    """
    Servicio para actualizar un autor existente.
    Recibe la instancia del autor y los datos validados.
    """
    autor.first_name = data.get('first_name', autor.first_name)
    autor.last_name = data.get('last_name', autor.last_name)
    autor.biography = data.get('biography', autor.biography)
    autor.birth_date = data.get('birth_date', autor.birth_date)
    autor.save()
    return autor

def delete_autor(*, autor: Autor):
    """
    Servicio para eliminar un autor.
    """
    autor.delete()


# --- Servicios de LIBRO ---

def list_libros():
    """
    Servicio para listar todos los libros.
    Usa 'prefetch_related' para optimizar la consulta M2M.
    """
    queryset = Libro.objects.all().prefetch_related('autores')
    return queryset

@transaction.atomic
def create_libro(*, data: Dict[str, Any]) -> Libro:
    """
    Servicio para crear un nuevo libro.
    Maneja la lógica M2M y validaciones de negocio.
    """
    # --- Validación de Negocio 1: ISBN Único ---
    isbn = data.get('isbn')
    if Libro.objects.filter(isbn=isbn).exists():
        raise DuplicateResourceError(detail=f"Ya existe un libro con el ISBN {isbn}.")

    autores_ids = data.pop('autores', [])
    
    # --- Validación de Negocio 2: Autores existen ---
    autores = Autor.objects.filter(id__in=autores_ids)
    if autores.count() != len(autores_ids):
        found_ids = set(autores.values_list('id', flat=True))
        invalid_ids = [str(uid) for uid in autores_ids if uid not in found_ids]
        raise BusinessValidationError(detail=f"IDs de autor no encontrados: {invalid_ids}")
    
    # Creamos el libro
    libro = Libro.objects.create(**data)
    
    # Asignamos autores
    libro.autores.set(autores)
    
    return libro

def get_libro(*, pk: uuid.UUID) -> Libro:
    """
    Servicio para obtener un libro por su PK (UUID).
    Optimizamos la consulta con 'prefetch_related'.
    """
    try:
        queryset = Libro.objects.all().prefetch_related('autores')
        return queryset.get(pk=pk)
    except Libro.DoesNotExist:
        raise ResourceNotFoundError(detail=f"Libro con id={pk} no encontrado.")

@transaction.atomic
def update_libro(*, libro: Libro, data: Dict[str, Any]) -> Libro:
    """
    Servicio para actualizar un libro.
    """
    # --- Validación de Negocio 1: ISBN Único (si cambia) ---
    isbn = data.get('isbn', libro.isbn)
    if isbn != libro.isbn and Libro.objects.filter(isbn=isbn).exists():
        raise DuplicateResourceError(detail=f"Ya existe otro libro con el ISBN {isbn}.")

    autores_ids = data.pop('autores', None)

    # Actualizamos campos simples
    libro.title = data.get('title', libro.title)
    libro.summary = data.get('summary', libro.summary)
    libro.isbn = isbn
    libro.publication_date = data.get('publication_date', libro.publication_date)
    
    # Si se proporcionó una nueva lista de autores, la actualizamos
    if autores_ids is not None:
        # --- Validación de Negocio 2: Autores existen ---
        autores = Autor.objects.filter(id__in=autores_ids)
        if autores.count() != len(autores_ids):
            found_ids = set(autores.values_list('id', flat=True))
            invalid_ids = [str(uid) for uid in autores_ids if uid not in found_ids]
            raise BusinessValidationError(detail=f"IDs de autor no encontrados: {invalid_ids}")
        
        libro.autores.set(autores)
        
    libro.save()
    return libro

def delete_libro(*, libro: Libro):
    """
    Servicio para eliminar un libro.
    """
    libro.delete()