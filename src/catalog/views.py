# src/catalog/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from . import services
from . import serializers
from core.helpers import api_success_response
from drf_spectacular.utils import extend_schema 
from rest_framework.pagination import PageNumberPagination 
from django.core.cache import cache 
from rest_framework.decorators import action 
from . import tasks 
from .models import Autor, Libro
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

class AutorViewSet(viewsets.ViewSet):
    """
    ViewSet para el CRUD de Autores.
    Utiliza la capa de servicios y los helpers de respuesta.
    """
    queryset = Autor.objects.none()
    serializer_class = serializers.AutorOutputSerializer
    
    # --- 2. DEFINIR LOS FILTROS, BÚSQUEDA Y ORDENAMIENTO ---
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Campos para filtro exacto 
    filterset_fields = ['last_name', 'birth_date']
    
    # Campos para búsqueda de texto 
    search_fields = ['first_name', 'last_name', 'biography']
    
    # Campos por los que se puede ordenar 
    # book_count viene del 'annotate' en el servicio
    ordering_fields = ['last_name', 'first_name', 'birth_date', 'book_count']
    
    @extend_schema(
        summary="Listar autores",
        responses=serializers.AutorOutputSerializer(many=True) 
    )
    def list(self, request):
        """
        Listar todos los autores que son paginados, cacheado y pueden ser filtrados.
        """
        # 1. Clave de caché dinámica
        cache_key = f'autores_list_{request.query_params.urlencode()}'
        
        # 2. Intentar obtener el QUERYSET cacheado
        cached_queryset = cache.get(cache_key)

        if not cached_queryset:
            # --- CACHE MISS ---
            # 3. Si no está en caché, hacemos el trabajo pesado
            queryset = services.list_autores()

            # 4. Aplicar filtros, búsqueda y ordenamiento
            for backend in list(self.filter_backends):
                queryset = backend().filter_queryset(request, queryset, self)
            
            # 5. Convertir el queryset a una lista para cachearlo
            cached_queryset = list(queryset)
            
            # 6. Guardar la lista (el resultado de la DB) en el caché
            cache.set(cache_key, cached_queryset, timeout=300)
        
        # --- LÓGICA DE VISTA ---
        # 7. Paginar la lista (ya sea del caché o recién consultada)
        paginator = PageNumberPagination()
        paginated_autores = paginator.paginate_queryset(cached_queryset, request)
        
        # 8. Serializar
        serializer = serializers.AutorOutputSerializer(paginated_autores, many=True)
        
        # 9. Devolver la respuesta paginada y con headers de Rate Limit
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Crear un nuevo autor",
        request=serializers.AutorInputSerializer,     
        responses={201: serializers.AutorOutputSerializer} 
    )
    def create(self, request):
        """
        Crear un nuevo autor.
        """
        serializer = serializers.AutorInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        autor = services.create_autor(data=serializer.validated_data)
        
        output_serializer = serializers.AutorOutputSerializer(autor)
        
        # --- 4. INVALIDACIÓN DE CACHÉ ---
        cache.delete_pattern('autores_list_*')
        # --- FIN INVALIDACIÓN ---
        
        return api_success_response(
            data=output_serializer.data, 
            status_code=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="Obtener un autor por ID",
        responses=serializers.AutorOutputSerializer 
    )
    def retrieve(self, request, pk=None):
        """
        Obtener un autor por su PK.
        """
        autor = services.get_autor(pk=pk)
        serializer = serializers.AutorOutputSerializer(autor)
        return api_success_response(data=serializer.data)

    @extend_schema(
        summary="Actualizar un autor",
        request=serializers.AutorInputSerializer,     
        responses=serializers.AutorOutputSerializer 
    )
    def update(self, request, pk=None):
        """
        Actualizar un autor existente.
        """
        autor = services.get_autor(pk=pk)
        
        serializer = serializers.AutorInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        autor_actualizado = services.update_autor(autor=autor, data=serializer.validated_data)
        
        output_serializer = serializers.AutorOutputSerializer(autor_actualizado)
        
        # --- INVALIDACIÓN DE CACHÉ ---
        cache.delete_pattern('autores_list_*')
        # --- FIN INVALIDACIÓN ---
        
        return api_success_response(data=output_serializer.data)
        
    @extend_schema(
        summary="Actualizar un autor (parcial)",
        request=serializers.AutorInputSerializer,    
        responses=serializers.AutorOutputSerializer  
    )
    def partial_update(self, request, pk=None):
        """
        Actualizar un autor existente (parcial).
        """
        autor = services.get_autor(pk=pk)
        
        serializer = serializers.AutorInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        autor_actualizado = services.update_autor(autor=autor, data=serializer.validated_data)
        
        output_serializer = serializers.AutorOutputSerializer(autor_actualizado)
        
        # --- INVALIDACIÓN DE CACHÉ---
        cache.delete_pattern('autores_list_*')
        # --- FIN INVALIDACIÓN ---
        
        return api_success_response(data=output_serializer.data)

    @extend_schema(summary="Eliminar un autor")
    def destroy(self, request, pk=None):
        """
        Eliminar un autor.
        """
        autor = services.get_autor(pk=pk)
        services.delete_autor(autor=autor)
        
        # --- INVALIDACIÓN DE CACHÉ ---
        cache.delete_pattern('autores_list_*')
        cache.delete_pattern('libros_list_*') 
        # --- FIN INVALIDACIÓN ---
        
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    @extend_schema(
        summary="Generar reporte de autor",
        description="Inicia una tarea asíncrona (10 seg) para generar un reporte.",
        request=None,
        responses={202: {"description": "La generación del reporte ha comenzado."}}
    )
    @action(detail=True, methods=['post'])
    def generate_report(self, request, pk=None):
        """
        Llama a una tarea Celery para generar un reporte.
        """
        autor = services.get_autor(pk=pk)
        tasks.generate_author_report.delay(str(autor.id))
        return Response(
            {"status": "La generación del reporte ha comenzado."}, 
            status=status.HTTP_202_ACCEPTED
        )


class LibroViewSet(viewsets.ViewSet):
    """
    ViewSet para el CRUD de Libros.
    """
    queryset = Libro.objects.none()
    serializer_class = serializers.LibroOutputSerializer
    
    # --- 2. DEFINIR LOS FILTROS, BÚSQUEDA Y ORDENAMIENTO ---
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Filtros para rangos de fechas y campos exactos
    filterset_fields = {
        'publication_date': ['gte', 'lte', 'exact'], 
        'isbn': ['exact'],
        'autores__id': ['exact'], 
    }
    
    # Búsqueda de texto
    search_fields = ['title', 'summary', 'autores__first_name', 'autores__last_name']
    
    # Ordenamiento
    ordering_fields = ['title', 'publication_date']
    
    
    @extend_schema(
        summary="Listar libros",
        responses=serializers.LibroOutputSerializer(many=True)
    )
    def list(self, request):
        """
        Listar todos los libros (paginado, cacheado, filtrado).
        """
        # 1. Clave de caché dinámica
        cache_key = f'libros_list_{request.query_params.urlencode()}'
        
        # 2. Intentar obtener el QUERYSET cacheado
        cached_queryset = cache.get(cache_key)
        
        if not cached_queryset:
            # --- CACHE MISS ---
            queryset = services.list_libros()

            for backend in list(self.filter_backends):
                queryset = backend().filter_queryset(request, queryset, self)
            
            cached_queryset = list(queryset)
            
            cache.set(cache_key, cached_queryset, timeout=300)
        
        # --- LÓGICA DE VISTA ---
        paginator = PageNumberPagination()
        paginated_libros = paginator.paginate_queryset(cached_queryset, request)
        
        serializer = serializers.LibroOutputSerializer(paginated_libros, many=True)
        
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Crear un nuevo libro",
        request=serializers.LibroInputSerializer,
        responses={201: serializers.LibroOutputSerializer}
    )
    def create(self, request):
        serializer = serializers.LibroInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        libro = services.create_libro(data=serializer.validated_data)
        
        libro_creado = services.get_libro(pk=libro.pk)
        output_serializer = serializers.LibroOutputSerializer(libro_creado)
        
        # --- 4. INVALIDACIÓN DE CACHÉ ---
        cache.delete_pattern('libros_list_*')
        cache.delete_pattern('autores_list_*')
        # --- FIN INVALIDACIÓN ---
        
        return api_success_response(
            data=output_serializer.data, 
            status_code=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="Obtener un libro por ID",
        responses=serializers.LibroOutputSerializer
    )
    def retrieve(self, request, pk=None):
        libro = services.get_libro(pk=pk)
        serializer = serializers.LibroOutputSerializer(libro)
        return api_success_response(data=serializer.data)

    @extend_schema(
        summary="Actualizar un libro ",
        request=serializers.LibroInputSerializer,
        responses=serializers.LibroOutputSerializer
    )
    def update(self, request, pk=None):
        libro = services.get_libro(pk=pk)
        
        serializer = serializers.LibroInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        libro_actualizado = services.update_libro(libro=libro, data=serializer.validated_data)
        
        output_serializer = serializers.LibroOutputSerializer(libro_actualizado)
        
        # --- 4. INVALIDACIÓN DE CACHÉ ---
        cache.delete_pattern('libros_list_*')
        cache.delete_pattern('autores_list_*')
        # --- FIN INVALIDACIÓN ---
        
        return api_success_response(data=output_serializer.data)
        
    @extend_schema(
        summary="Actualizar un libro (parcial)",
        request=serializers.LibroInputSerializer,
        responses=serializers.LibroOutputSerializer
    )
    def partial_update(self, request, pk=None):
        libro = services.get_libro(pk=pk)
        
        serializer = serializers.LibroInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        libro_actualizado = services.update_libro(libro=libro, data=serializer.validated_data)
        
        output_serializer = serializers.LibroOutputSerializer(libro_actualizado)
        
        # --- 4. INVALIDACIÓN DE CACHÉ ---
        cache.delete_pattern('libros_list_*')
        cache.delete_pattern('autores_list_*')
        # --- FIN INVALIDACIÓN ---
        
        return api_success_response(data=output_serializer.data)

    @extend_schema(summary="Eliminar un libro")
    def destroy(self, request, pk=None):
        libro = services.get_libro(pk=pk)
        services.delete_libro(libro=libro)
        
        # --- 4. INVALIDACIÓN DE CACHÉ ---
        cache.delete_pattern('libros_list_*')
        cache.delete_pattern('autores_list_*')
        # --- FIN INVALIDACIÓN ---
        
        return Response(status=status.HTTP_204_NO_CONTENT)