# src/catalog/tests/test_api.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from catalog.models import Autor, Libro

class CatalogAPITests(APITestCase):
    """
    Tests de integración para la API de Catálogo (Libros y Autores).
    """
    fixtures = ['initial_data.json']

    def setUp(self):
        """
        Configuración inicial para cada test.
        Crea un usuario y un token para autenticar las peticiones.
        """
        # 1. Crear usuario y token de prueba
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        self.token = Token.objects.create(user=self.user)
        
        # 2. Autenticar al cliente de prueba
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')

        # 3. URLs útiles
        self.autores_url = reverse('autor-list') # 'autor' es el basename del router
        self.libros_url = reverse('libro-list') # 'libro' es el basename del router
        
        # 4. Obtener un autor de los fixtures para pruebas de detalle/creación
        self.autor_tolkien = Autor.objects.get(last_name='Tolkien')

    # --- Tests de Autenticación ---

    def test_acceso_denegado_sin_token(self):
        """
        Verifica que la API rechace peticiones sin autenticación (401).
        """
        self.client.credentials() 
        response = self.client.get(self.autores_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 'not_authenticated')

    # --- Tests de Autores ---

    def test_listar_autores_con_annotate(self):
        """
        Prueba el Requisito 3: GET /autores/ (con 'book_count' de annotate).
        """
        response = self.client.get(self.autores_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        
        # Buscamos al autor Tolkien en la respuesta
        tolkien_data = next(
            item for item in response.data['data'] if item['last_name'] == 'Tolkien'
        )
        # Verificamos el 'annotate' dentro del test
        self.assertEqual(tolkien_data['book_count'], 2)

    def test_crear_autor(self):
        """
        Prueba POST /autores/ (Crear un nuevo autor).
        """
        data = {
            "first_name": "Ursula K.",
            "last_name": "Le Guin",
            "biography": "Autora de Terramar.",
            "birth_date": "1929-10-21"
        }
        response = self.client.post(self.autores_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['last_name'], 'Le Guin')
        # Verificamos que se creó en la DB
        self.assertTrue(Autor.objects.filter(last_name='Le Guin').exists())

    # --- Tests de Libros ---

    def test_crear_libro(self):
        """
        Prueba POST /libros/ (Crear un libro y asignarle un autor).
        """
        data = {
            "title": "El Silmarillion",
            "summary": "Mitos y leyendas de la Tierra Media.",
            "isbn": "9788445070380",
            "publication_date": "1977-09-15",
            "autores": [str(self.autor_tolkien.id)] 
        }
        response = self.client.post(self.libros_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['title'], 'El Silmarillion')
        self.assertEqual(response.data['data']['autores'][0]['last_name'], 'Tolkien')
        
        # Verificamos la relación M2M
        libro = Libro.objects.get(isbn="9788445070380")
        self.assertEqual(libro.autores.count(), 1)
        self.assertEqual(libro.autores.first(), self.autor_tolkien)

    def test_crear_libro_isbn_duplicado_error(self):
        """
        Prueba la validación de negocio (ISBN duplicado) desde la API (409).
        Usamos el ISBN de '1984' del fixture.
        """
        data = {
            "title": "Un libro falso",
            "isbn": "9780451524935", 
            "publication_date": "2025-01-01",
            "autores": [str(self.autor_tolkien.id)]
        }
        response = self.client.post(self.libros_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['code'], 'conflict')

    def test_crear_libro_autor_invalido_error(self):
        """
        Prueba la validación de negocio (UUID de autor inválido) desde la API (400).
        """
        data = {
            "title": "Otro libro falso",
            "isbn": "1234567890123",
            "publication_date": "2025-01-01",
            "autores": ["00000000-0000-0000-0000-000000000000"] 
        }
        response = self.client.post(self.libros_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'business_error')