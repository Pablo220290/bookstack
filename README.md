# 🚀 Bookstack API

Boostrack es una API robusta, escalable y de alto rendimiento, construida con Django y Django Rest Framework, que sigue las mejores prácticas de rendimiento seguridad y mantenibilidad.

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

## 🏛️ Nuestra Arquitectura

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

### Requisitos en la Máquina de Prueba

1.  **Git**
2.  **Docker Desktop** (asegúrate de que esté **corriendo** antes de empezar).
3.  **Git Bash** (en Windows, se instala con Git) para poder ejecutar el script `.sh`.

### Pasos del Despliegue

1.  **Abrir la Terminal Correcta:**

    - **En Windows:** Abre **Git Bash** (¡No uses CMD o PowerShell!).
    - **En Linux/macOS:** Abre tu terminal estándar.

2.  **Clonar el repositorio:**

    ```bash
    git clone [https://github.com/Pablo220290/bookstack.git](https://github.com/Pablo220290/bookstack.git)
    cd bookstack
    ```

3.  **Ejecutar el script de despliegue:**
    Este script construirá, iniciará, migrará y cargará los datos de la aplicación.

    ```bash
    ./deploy.sh
    ```

    _Este proceso tardará varios minutos la primera vez mientras descarga las imágenes de Docker._

4.  **Crear un Superusuario:**
    Una vez que el script termine, la base de datos estará corriendo pero necesitarás un usuario.

    - **En Linux/macOS:**
      ```bash
      docker-compose exec app python manage.py createsuperuser
      ```
    - **En Windows (Git Bash):**
      El comando anterior puede fallar con un error de `TTY`. Usa `winpty` para solucionarlo:
      ```bash
      winpty docker-compose exec app python manage.py createsuperuser
      ```

5.  **¡Listo! Accede a la aplicación:**
    - **Documentación API (Swagger):** `http://localhost:8000/api/v1/schema/swagger-ui/`
    - **Django Admin:** `http://localhost:8000/admin/`

---

## ⚠️ Solución de Problemas Comunes (Troubleshooting)

Si algo falla durante el despliegue, es probable que sea uno de estos problemas:

- **ERROR: `service "app" is not running` (Al ejecutar `migrate` o `loaddata`)**

  - **Causa:** El contenedor `app` o `worker` intentó iniciarse pero "crasheó" (se apagó) inmediatamente. Esto casi siempre es un `ImportError` (falta una librería en `requirements.txt`) o un error de sintaxis en el código de Python.
  - **Solución:** Ejecuta `docker-compose up` (sin el `-d`) en tu terminal. Esto iniciará los contenedores en primer plano y te mostrará el _Traceback_ (el error de Python) que está causando el _crash_.

- **ERROR: `bash: ./deploy.sh: No such file or directory` (El engañoso)**

  - **Causa:** No es que el archivo no exista, sino que sus finales de línea son incorrectos. Git en Windows pudo haberlo clonado con finales de línea `CRLF` en lugar de `LF`.
  - **Solución:** Este repositorio incluye un archivo `.gitattributes` que _debería_ prevenir esto. Si aun así ocurre, abre `deploy.sh` en VS Code, haz clic en **"CRLF"** en la barra inferior derecha, cámbialo a **"LF"** y guarda el archivo.

- **ERROR: `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`**

  - **Causa:** El motor de Docker no está corriendo.
  - **Solución:** Inicia la aplicación **Docker Desktop** desde tu Menú Inicio y espera a que el ícono de la ballena se ponga verde.

- **ERROR: `Superuser creation skipped due to not running in a TTY`**
  - **Causa:** Estás usando Git Bash en Windows, que no maneja bien las sesiones interactivas de Docker.
  - **Solución:** Añade `winpty` al inicio del comando: `winpty docker-compose exec app python manage.py createsuperuser`.

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
7.  ¡Listo! Ya puedes ejecutar peticiones en los endpoints protegidos.

---

## 🧪 Testing

Para ejecutar la suite completa de tests (unitarios y de integración):

```bash
docker-compose exec app python manage.py test catalog
```
