#!/bin/bash

# Detener la ejecución si un comando falla
set -e

echo "Desplegando la aplicación Bookstack..."

# 1. Construir o reconstruir las imágenes
echo "Construyendo imágenes de Docker..."
docker-compose build

# 2. Levantar los servicios en modo 'detached' (background)
echo "Iniciando servicios (App y DB)..."
docker-compose up -d

# 3. Esperar a que PostgreSQL esté listo
echo "Esperando 10 segundos a que PostgreSQL se inicie completamente..."
sleep 10

# 4. Ejecutar migraciones
echo "Ejecutando migraciones de Django..."
docker-compose exec app python manage.py migrate

# 5. Cargar los datos iniciales (fixtures)
echo "Cargando datos iniciales (fixtures)..."
docker-compose exec app python manage.py loaddata initial_data

echo ""
echo "¡Despliegue completado!"
echo "Tu aplicación está corriendo en http://localhost:8000"
echo "La API está disponible en http://localhost:8000/api/v1/schema/swagger-ui/"
echo ""
echo "---"
echo "NOTA: La base de datos de Docker es NUEVA. Debes crear un superusuario."
echo "Ejecuta el siguiente comando para crear uno:"
echo "docker-compose exec app python manage.py createsuperuser"
echo "---"