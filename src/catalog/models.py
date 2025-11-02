# src/catalog/models.py

from django.db import models
import uuid

class Autor(models.Model):
    """
    Modelo para representar a un Autor.
    """
    #  Hago uso de UUID como Primary de manera a evitar posibles ataques en la secuencialidad del ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellido", db_index=True)
    biography = models.TextField(blank=True, null=True, verbose_name="Biografía")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Fecha de Nacimiento", db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autores"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Libro(models.Model):
    """
    Modelo para representar un Libro.
    La relación con Autor es Muchos a Muchos.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, verbose_name="Título")
    summary = models.TextField(blank=True, null=True, verbose_name="Resumen")
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN", db_index=True)
    publication_date = models.DateField(verbose_name="Fecha de Publicación", db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Un libro puede tener muchos autores, y un autor muchos libros.
    autores = models.ManyToManyField(
        Autor,
        related_name='libros',
        verbose_name="Autores"
    )

    class Meta:
        verbose_name = "Libro"
        verbose_name_plural = "Libros"
        ordering = ['-publication_date']

    def __str__(self):
        return self.title