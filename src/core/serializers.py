# src/core/serializers.py

from rest_framework import serializers

class TokenOutputSerializer(serializers.Serializer):
    """
    Serializer para la respuesta del endpoint de login (Solo para Swagger).
    """
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)