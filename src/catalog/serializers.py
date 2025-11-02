# src/catalog/serializers.py

from rest_framework import serializers
from .models import Autor, Libro 

# --- Serializers de SALIDA (Output) ---

class AutorOutputSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar los datos de un Autor.
    Incluye el campo 'book_count' que será calculado
    por el servicio usando 'annotate'.
    """
    book_count = serializers.IntegerField(read_only=True, required=False)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Autor
        fields = (
            'id', 
            'first_name', 
            'last_name', 
            'full_name', 
            'birth_date', 
            'biography',
            'book_count', 
            'created_at'
        )

class LibroOutputSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar los datos de un Libro.
    Anidamos el serializer de Autor para ver los detalles
    de los autores, no solo sus IDs.
    """
    # Uso el Serializer de Salida de Autor para mostrar
    # los autores de forma anidada y legible.
    autores = AutorOutputSerializer(many=True, read_only=True)

    class Meta:
        model = Libro
        fields = (
            'id', 
            'title', 
            'summary', 
            'isbn', 
            'publication_date', 
            'autores', 
            'created_at'
        )


# --- Serializers de ENTRADA (Input) ---
# Defino los campos que se aceptam para crear/actualizar

class AutorInputSerializer(serializers.Serializer):
    """
    Valida los datos de ENTRADA para crear/actualizar un Autor.
    No es un ModelSerializer, solo valida la forma de los datos.
    """
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    biography = serializers.CharField(required=False, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True)


class LibroInputSerializer(serializers.Serializer):
    """
    Valida los datos de ENTRADA para crear/actualizar un Libro.
    """
    title = serializers.CharField(max_length=255)
    summary = serializers.CharField(required=False, allow_blank=True)
    isbn = serializers.CharField(max_length=13)
    publication_date = serializers.DateField()
    
    autores = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False, 
        write_only=True
    )