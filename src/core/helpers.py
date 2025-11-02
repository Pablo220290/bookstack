# src/core/helpers.py

from rest_framework.response import Response
from rest_framework import status

def api_success_response(data, status_code=status.HTTP_200_OK):
    """
    Formato estandarizado para respuestas de éxito (2xx).
    """
    return Response(
        {
            'status': 'success',
            'data': data
        },
        status=status_code
    )