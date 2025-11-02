# 🚀 Bookstack API

Boostack es una API RESTful robusta, escalable y de alto rendimiento, construida con Django y Django Rest Framework, que sigue las mejores prácticas de rendimiento seguridad y mantenibilidad.

---

## ✨ Características Principales

Este proyecto implementa:

- **Arquitectura Limpia:** Sigue una estricta **Capa de Servicios** (`services.py`) que aísla toda la lógica de negocio de las vistas y serializadores.
- **Contenerización Completa:** Entorno 100% "dockerizado" con `docker-compose`, incluyendo la app, la base de datos PostgreSQL, un caché de **Redis** y un trabajador de **Celery**.
- **Autenticación Moderna:** Flujo de autenticación seguro basado en **JWT (JSON Web Tokens)** con tokens de acceso y refresco (`simplejwt`).
- **Tareas Asíncronas:** Uso de **Celery** y Redis como _broker_ para manejar tareas pesadas (como la simulación de generación de reportes) en segundo plano, sin bloquear la API.
- **Caché de Alto Rendimiento:** Implementación de **Redis** para cachear respuestas de la API (como las listas paginadas) y una estrategia de invalidación de caché inteligente.
- **Seguridad:**
  - **Permisos:** Endpoints protegidos que requieren autenticación.
  - **Rate Limiting:** Protección contra ataques de fuerza bruta y DoS, con un límite estricto en el login (`5/minuto`) y límites globales para usuarios (`1000/hora`).
- **API Potente y Eficiente:**
  - **Paginación:** Las listas de resultados están paginadas para un rendimiento óptimo.
  - **Filtros, Búsqueda y Ordenamiento:** La API soporta filtrado complejo (ej. por rangos de fecha), búsqueda de texto (`?search=...`) y ordenamiento (`?ordering=...`).
  - **Optimización de DB:** Uso de **Índices de Base de Datos** (`db_index=True`) en campos clave para acelerar las consultas de los filtros.
- **Documentación Completa:** Documentación interactiva de la API generada automáticamente con **Swagger (OpenAPI)** gracias a `drf-spectacular`.
- **Testing:** Incluye una suite de tests unitarios (para modelos y servicios) y tests de integración (para la API).
- **Script de Despliegue:** Un script `deploy.sh` de bash para construir y levantar todo el entorno con un solo comando.

---

## 🏛️ Arquitectura

El proyecto está organizado en una arquitectura de capas desacoplada:

1.  **Capa de Vistas (`views.py`)**

    - Actúa como un "controlador de tráfico" delgado.
    - **Responsabilidades:** Manejar el HTTP (Request/Response), la autenticación, la paginación, el cacheo y la limitación de tasa (Rate Limiting).
    - Llama a la capa de servicios con los datos validados.

2.  **Capa de Serializers (`serializers.py`)**

    - Son simples (sin lógica de negocio).
    - **Input Serializers:** Definen la _forma_ de los datos que entran.
    - **Output Serializers:** Definen la _forma_ del JSON que sale.

3.  **Capa de Servicios (`services.py`)**

    - Es el "cerebro" de la aplicación.
    - **Contiene toda la lógica de negocio**: todas las consultas a la base de datos (`annotate`, `prefetch_related`), la lógica de creación/actualización y el lanzamiento de excepciones personalizadas (`BusinessValidationError`, `ResourceNotFoundError`).

4.  **Capa Core (`core/`)**
    - Contiene código transversal al proyecto:
    - `exceptions.py`: Manejador global de excepciones.
    - `views.py` / `serializers.py`: Personalizaciones para el login con JWT.

---

## 💻 Stack Tecnológico

- **Backend:** Python, Django
- **API:** Django Rest Framework (DRF), DRF Simple JWT
- **Base de Datos:** PostgreSQL
- **Caché y Cola de Tareas:** Redis
- **Tareas Asíncronas:** Celery
- **Contenerización:** Docker & Docker Compose
- **Documentación API:** `drf-spectacular` (OpenAPI 3 / Swagger)
- **Testing:** `unittest` (APITestCase, TestCase)

---

## 🏁 Cómo Empezar (Despliegue con Docker)

Este es el método recomendado. Levanta todos los servicios (app, db, redis, worker) automáticamente.

**Requisitos:** Tener Docker y Docker Compose instalados.

1.  **Clonar el repositorio:**

    ```bash
    git clone [https://github.com/Pablo220290/bookstack.git](https://github.com/Pablo220290/bookstack.git)
    cd bookstack
    ```

2.  **Preparar el Script de Despliegue:**
    (Solo necesitas hacer esto una vez para darle a Git permisos de ejecución).

    _Si estás en **Windows** (usando Git Bash), ejecuta:_

    ```bash
    git update-index --chmod=+x deploy.sh
    ```

    _Si estás en **Linux/macOS**, ejecuta:_

    ```bash
    chmod +x deploy.sh
    ```

3.  **Ejecutar el script de despliegue:**

    ```bash
    ./deploy.sh
    ```

    Este script automáticamente:

    - Construirá las imágenes de Docker.
    - Levantará los 4 contenedores (app, db, redis, worker).
    - Esperará a que la DB esté lista.
    - Ejecutará las migraciones (`migrate`).
    - Cargará los datos iniciales (`loaddata initial_data`).

4.  **Crear un Superusuario:**
    La base de datos de Docker es nueva. Para poder obtener un token, debes crear un usuario:

    ```bash
    docker-compose exec app python manage.py createsuperuser
    ```

5.  **¡Listo! Accede a la aplicación:**
    - **Documentación API (Swagger):** `http://localhost:8000/api/v1/schema/swagger-ui/`
    - **Django Admin:** `http://localhost:8000/admin/`

---

## 🕹️ Uso de la API (Flujo de Autenticación)

Accede a la [Documentación de Swagger](http://localhost:8000/api/v1/schema/swagger-ui/) para ver e interactuar con todos los endpoints.

**Flujo de Autenticación JWT:**

1.  Ve al endpoint `POST /api/v1/auth/token/`.
2.  Usa el `username` y `password` de tu superusuario en el cuerpo de la petición.
3.  Recibirás dos tokens: `access` y `refresh`.
4.  Copia el token `access`.
5.  Haz clic en el botón verde **"Authorize"** en la parte superior derecha de Swagger.
6.  En el diálogo `jwtAuth (Bearer)`, pega el `access` token (solo el token, sin prefijos).
7.  ¡Listo! Ya puedes ejecutar peticiones en los endpoints protegidos. Si tu token de acceso expira, usa el `refresh` token en el endpoint `POST /api/v1/auth/token/refresh/` para obtener uno nuevo.

---

## 🧪 Testing

Para ejecutar la suite completa de tests (unitarios y de integración):

```bash
# Asegúrate de que tu entorno Docker esté corriendo
docker-compose exec app python manage.py test catalog
```
