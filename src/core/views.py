# src/core/views.py

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_spectacular.utils import extend_schema
from .serializers import TokenOutputSerializer

@extend_schema(
    summary="Autenticación (Obtener Token JWT)",
    description="Obtiene un par de tokens (Access y Refresh) a cambio de username y password.",
    request=TokenObtainPairSerializer,
    responses={200: TokenOutputSerializer} 
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista de login personalizada para aplicar un Rate Limiting estricto.
    """
    throttle_scope = 'login_attempt'