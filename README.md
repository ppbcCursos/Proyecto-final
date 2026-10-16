# Folio · Novedades editoriales

Aplicación local para consultar libros en castellano por mes, autor y editorial.
El chat mantiene el historial y muestra documentos, registros y fragmentos como
fuentes. Incluye un buscador de documentos y la ficha de cada libro.

Los datos son **ficticios**: 12 libros, 6 autores y 4 editoriales, tomados de
`maquetas.html` y generados en SQLite. Los documentos están en `data/documentos/`.
La página Fuentes enlaza catálogos reales de Penguin, Planeta, Anagrama y Siruela;
esos enlaces no acreditan los libros inventados ni se importan automáticamente.
El RAG guarda sus embeddings en disco y responde «No consta en los datos» cuando
no encuentra respaldo. La clave solo se lee en el servidor desde `.env`.

## Arranque

Necesita Python con `uv`, Node.js y npm. Ejecuta `uv sync --locked` y, en `web/`,
`npm install`. Crea `.env` a partir de `.env.example` y configura tu clave.
Desde la raíz, en dos terminales:

```powershell
# Servidor FastAPI, puerto 8000
uv run servidor.py
```

```powershell
# Interfaz Svelte + TypeScript, puerto 5173
.\scripts\web.ps1
# Alternativa con Node en PATH: cd web; npm run dev
```

Abre **http://127.0.0.1:5173/**. Vite redirige `/api` al servidor Python.

## Preguntas comprobadas

- ¿Qué libros se han publicado en septiembre de 2026? → 6 libros con fuentes.
- ¿Qué autores han publicado en 2026 y qué libros? → 6 autores y 12 libros.
- ¿Qué editoriales han publicado en 2026 y cuántos libros? → 4, 4, 2 y 2.
- No me preguntes por fechas futuras a la del día de la consulta. → Se aplica el límite.
- ¿Qué libros se han publicado en enero de 2027? → «No consta» a 16/10/2026.
- ¿Cuál es la masa de la Luna? → «No consta», sin inventar una respuesta.

Los cuerpos JSON para probar con curl están en `ejemplos/`. Validación:
39 pruebas del servidor; Svelte/TypeScript y compilación correctos; consultas,
fuentes, filtros, cambio de año y errores de conexión probados en Chrome.

Consulta la memoria [entregable.pdf](entregable.pdf) y las [capturas](capturas/).
