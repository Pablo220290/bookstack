# src/catalog/tests/test_models.py

from django.test import TestCase
from catalog.models import Autor

class ModelTests(TestCase):
    """
    Tests para los modelos (propiedades y métodos).
    """
    
    def test_autor_full_name_property(self):
        """
        Prueba la propiedad @property 'full_name'.
        """
        autor = Autor(first_name="Jane", last_name="Austen")
        self.assertEqual(autor.full_name, "Jane Austen")

    def test_autor_str_representation(self):
        """
        Prueba el método __str__ del modelo Autor.
        """
        autor = Autor(first_name="Jane", last_name="Austen")
        self.assertEqual(str(autor), "Austen, Jane")