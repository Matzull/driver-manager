# Gestión de ubicación y estado de conductores con FastAPI y SQLite

Este proyecto presenta un backend simple para gestionar conductores y sus posiciones geográficas. Se ha decidido implementar como una API RESTful que permite las siguientes operaciones:

- Actualizar o agregar conductores con su posición.
- Dejar de trackear un conductor.
- Obtener el conductor más cercano a una ubicación dada.

## Estructura del proyecto

```
/driver-manager
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # Archivo principal con los endpoints
│   ├── models.py               # Definición de modelos ORM con SQLAlchemy
│   └── database_manager.py     # Gestión de las operaciones de la base de datos
│
├── tests/
│   ├── __init__.py
│   └── test_api.py             # Conjunto de tests con pytest y TestClient
│
├── drivers.db                  # Base de datos SQLite generada automáticamente
├── pyproject.toml              # Configuración del proyecto y dependencias
└── README.md                   # Esta documentación
```

---

## Cómo funciona

Para mantener consistente la operación de la API, los tres endpoints devuelven datos en formato JSON.

- **Actualizar posición (`PUT /update-position/`)**  
  Envía un JSON con `driver_id` y `position` (coordenadas [lat, lon]). Si el conductor existe, actualiza su posición; si no, lo crea.

- **Detener tracking (`DELETE /stop-tracking/`)**  
  Envía en el parámetro el `driver_id`. Elimina al conductor de la base de datos y su historial de posiciones.

- **Conductor más cercano (`POST /get-closest-driver/`)**  
  Envía la posición `[lat, lon]` en el body JSON. El sistema devuelve el conductor más cercano basado en distancia Euclidiana.

### Base de datos

Como base de datos se utiliza SQLite por su simplicidad. Se han creado dos tablas:

- `drivers`: Almacena el identificador del conductor y su última posición conocida (para mayor eficiencia en la búsqueda).
- `driver_history`: Almacena el historial de posiciones de los conductores (ID del conductor, latitud, longitud).

---

## Validaciones importantes

- `driver_id` debe ser un string no vacío (validado con Pydantic).
- `position` debe ser una tupla/lista con dos números enteros (latitud y longitud).
- Un request inválido devuelve HTTP 422 automáticamente.

---

## Instalación y ejecución

1. Clona el repositorio:

```bash
git clone https://github.com/Matzull/driver_manager.git
cd driver-manager
```

2. Instala dependencias:

```bash
pip install uv
```

3. Ejecuta el servidor:

```bash
uv run fastapi dev .\src\driver_manager\main.py # Windows
uv run fastapi dev ./src/driver_manager/main.py # Linux/Mac
```

4. Accede a la documentación automática en (permite probar los endpoints):

```
http://127.0.0.1:8000/docs
```

---

## Ejemplo de uso (curl)

- Actualizar posición:

```bash
curl -X PUT "http://127.0.0.1:8000/update-position/" -H "Content-Type: application/json" -d '{"driver_id":"driver123","position":[3,4]}'
```

- Buscar conductor más cercano:

```bash
curl -X POST "http://127.0.0.1:8000/get-closest-driver/" -H "Content-Type: application/json" -d '[1,2]'
```

- Parar tracking:

```bash
curl -X DELETE "http://127.0.0.1:8000/stop-tracking/" -H "Content-Type: application/json" -d '{"driver_id":"driver123"}'
```


---

## Testing

Corre la suite de tests con:

```bash
uv run pytest .\src\tests\tests.py # Windows
uv run pytest ./src/tests/tests.py # Linux/Mac
```

Los tests cubren múltiples escenarios: creación, actualización, eliminación, validaciones, búsquedas y operaciones concurrentes.

---

## Consideraciones y mejoras futuras

- Actualmente la distancia es Euclidiana, para geolocalización real se deberían usar otro tipo de distancias.
- Como base de datos se está utilizando un SQLite muy simple, en producción se podría cambiar a PostgreSQL u otra base de datos.
- Se debería utilizar SQLAlchemy Async para conexiones asíncronas a la base de datos.