# src/catalog/tests/test_services.py

from django.test import TestCase
from catalog.models import Autor
from catalog import services
from core.exceptions import DuplicateResourceError, BusinessValidationError
import uuid

class ServiceTests(TestCase):
    """
    Tests unitarios (o de integración de lógica) para la capa de servicios.
    """
    
    # Cargamos los fixtures para probar las consultas
    fixtures = ['initial_data.json']

    def setUp(self):
        self.autor_orwell = Autor.objects.get(last_name='Orwell')

    def test_list_autores_service(self):
        """
        Prueba que el servicio 'list_autores' devuelva el 'book_count'.
        """
        autores = services.list_autores()
        
        # Buscamos al autor Tolkien
        tolkien = next(a for a in autores if a.last_name == 'Tolkien')
        
        # Probamos el 'annotate' como operacion directamente
        self.assertEqual(tolkien.book_count, 2)

    def test_create_libro_service_isbn_duplicado(self):
        """
        Prueba que el servicio 'create_libro' lance 'DuplicateResourceError'.
        """
        data = {
            "title": "Un libro falso",
            "isbn": "9780451524935", 
            "publication_date": "2025-01-01",
            "autores": [self.autor_orwell.id]
        }
        
        # Verificamos que la excepción correcta es lanzada
        with self.assertRaises(DuplicateResourceError):
            services.create_libro(data=data)

    def test_create_libro_service_autor_invalido(self):
        """
        Prueba que el servicio 'create_libro' lance 'BusinessValidationError'
        si el UUID del autor no existe.
        """
        data = {
            "title": "Otro libro falso",
            "isbn": "1234567890123",
            "publication_date": "2025-01-01",
            "autores": [uuid.uuid4()] 
        }
        
        with self.assertRaises(BusinessValidationError):
            services.create_libro(data=data)