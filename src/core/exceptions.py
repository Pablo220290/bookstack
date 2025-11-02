# src/core/exceptions.py

from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.response import Response

# --- 1. Definición de Excepciones Propias ---

class BusinessValidationError(APIException):
    """
    Excepción personalizada para errores de lógica de negocio (400).
    Usar esta en lugar de ValidationError de DRF cuando sea un error
    de regla de negocio, no solo de formato de datos.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Error en la lógica de negocio.'
    default_code = 'business_error'

class ResourceNotFoundError(APIException):
    """
    Excepción para recursos no encontrados (404).
    La usaremos en nuestros servicios en lugar de Http404 de Django.
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Recurso no encontrado.'
    default_code = 'not_found'

class DuplicateResourceError(APIException):
    """
    Excepción para creación de recursos duplicados (409).
    Ej: Intentar crear un Autor con un email que ya existe.
    """
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'El recurso ya existe.'
    default_code = 'conflict'


# --- 2. Handler Estándar Global ---

def custom_exception_handler(exc, context):
    """
    Manejador de excepciones global para DRF.
    Formatea todas las respuestas de error en un formato JSON estándar.
    """
    # Primero, obtenemos la respuesta de error estándar de DRF
    response = exception_handler(exc, context)

    # Si es una excepción que DRF ya maneja (APIException, Http404, etc.)
    if response is not None:
        
        # Si es un error de validación de serializer, 'detail' es un dict
        if isinstance(response.data.get('detail'), dict):
            details = response.data['detail']
        elif 'detail' in response.data:
            details = response.data['detail']
        else:
            details = response.data

        # Estandarizamos el formato de error
        response.data = {
            'status': 'error',
            'message': exc.default_detail if hasattr(exc, 'default_detail') else 'Error',
            'code': exc.default_code if hasattr(exc, 'default_code') else 'error',
            'details': details
        }

    # Si DRF no sabe manejar la excepción (ej. un error 500 de Python)
    elif not isinstance(exc, APIException):
        response = Response(
            {
                'status': 'error',
                'message': 'Ocurrió un error inesperado en el servidor.',
                'code': 'server_error',
                'details': str(exc)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response