# bookstack/Dockerfile

# 1. Usar una imagen base ligera de Python
FROM python:3.11-slim

# 2. Configurar variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar TODO el proyecto al contenedor
COPY . .

# 6. Establecer el directorio de trabajo en /app/src (donde está manage.py)
WORKDIR /app/src

# 7. Exponer el puerto 8000
EXPOSE 8000

# 8. Comando por defecto 
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]