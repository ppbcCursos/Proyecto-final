# Folio · El mes, entre líneas

Aplicación local para consultar novedades editoriales en castellano por mes,
autoría y editorial. Interfaz Svelte 5 + TypeScript + Vite; servidor FastAPI;
catálogo persistente en SQLite.

El catálogo inicial contiene **12 libros, 6 autores y 4 editoriales ficticios**,
los mismos de `maquetas.html`. Cada respuesta cita registros y fragmentos.
Los enlaces editoriales de la vista Fuentes son reales y se investigaron el
16/10/2026; no son el origen de esos datos inventados. Todavía no hay un
recolector automático de páginas o PDF.

El servidor RAG se arranca con **`uv run servidor.py`**, en el puerto 8000.
Usa embeddings y la API de respuestas de OpenAI, con la clave que ya existe
en `.env`. El chat Svelte envía la pregunta y los últimos 20 mensajes a
`/api/preguntar`; la biblioteca carga `/api/documentos`, con filtros de texto,
mes y editorial. Todas las peticiones del navegador son relativas a `/api` y
Vite las redirige al servidor Python. La clave solo se lee en el servidor;
no se usa ninguna variable `VITE_` con credenciales.

La interfaz reproduce las vistas de la maqueta: consultas con citas, la misma
conversación en «Cuando no consta», biblioteca de documentos y registros,
detalle del libro y su documento de origen, y fuentes y cobertura. El botón
«Ver las tres consultas de ejemplo» hace las consultas al RAG en orden; no
se generan consultas al modelo al abrir la página. «Probar una fecha futura»
añade la preferencia temporal y una pregunta futura a la misma conversación.
Puedes seleccionar años anteriores; si no hay registros se indica expresamente.
«Nueva conversación» borra el historial del chat. Se conserva mientras navegas
entre las vistas y se reinicia al recargar la aplicación.
`openai`, `python-dotenv`, `numpy`, `fastapi` y `uvicorn[standard]` están
instalados con `uv add`. `tzdata` permite calcular la fecha real de Madrid.

## Servidor RAG y pruebas con curl

En una terminal, desde la carpeta del proyecto:

```powershell
uv run servidor.py
```

Si ya están activos los servicios de Folio, usa `detener.ps1` antes de iniciar
otra instancia en el mismo puerto. `iniciar.ps1` también arranca este servidor.
La documentación interactiva está en http://127.0.0.1:8000/docs.

En otra terminal PowerShell, las cuatro peticiones de la maqueta:

```powershell
# 1. Libros de septiembre de 2026: seis libros con sus fuentes.
curl.exe --noproxy "*" -sS -H "Content-Type: application/json" --data-binary "@ejemplos/mes.json" http://127.0.0.1:8000/api/preguntar

# 2. Autores del año y sus libros: seis autores, doce libros.
curl.exe --noproxy "*" -sS -H "Content-Type: application/json" --data-binary "@ejemplos/autores.json" http://127.0.0.1:8000/api/preguntar

# 3. Editoriales del año: cuatro editoriales; recuentos 4, 4, 2 y 2.
curl.exe --noproxy "*" -sS -H "Content-Type: application/json" --data-binary "@ejemplos/editoriales.json" http://127.0.0.1:8000/api/preguntar

# 4. Noviembre de 2026: no consta a fecha de consulta 16/10/2026.
curl.exe --noproxy "*" -sS -H "Content-Type: application/json" --data-binary "@ejemplos/futuro.json" http://127.0.0.1:8000/api/preguntar

# Documentos y registros de la página de biblioteca.
curl.exe --noproxy "*" -sS http://127.0.0.1:8000/api/documentos
```

Los archivos JSON evitan los problemas de escape y codificación del cuerpo en
PowerShell. Se pueden editar. `--noproxy "*"` evita enviar las peticiones locales
al proxy. Las consultas sin coincidencias se pueden probar con
`ejemplos/sin-coincidencias.json`; una continuación del historial, con
`ejemplos/continuacion.json`.

`POST /api/preguntar` recibe:

```json
{
  "pregunta": "¿Y qué editoriales y cuántos libros?",
  "historial": [
    {"role": "user", "content": "Libros de septiembre de 2026"},
    {"role": "assistant", "content": "Constan seis libros en la muestra."}
  ]
}
```

El historial admite `role`/`content` o `rol`/`contenido`, con roles de usuario
y asistente; no admite un rol de sistema. Sirve para resolver referencias a un
mes o año anterior. El contenido previo del asistente nunca es una fuente.

La respuesta validada incluye `respuesta`, `estado`, `motivo`, `fecha_consulta`,
`pregunta_contextualizada`, `modelo_usado`, `fuentes`, `libros`, `autores` y
`editoriales`. Cada fuente lleva `documento_id`, `documento`, `registro_id`,
`fragmento`, `similitud` y `datos_ficticios`. Los libros y los grupos tienen
campos y cantidades estructurados. No se acepta texto o JSON sin validar.

`GET /api/documentos` devuelve cuatro documentos y doce registros en esta
muestra, con fragmentos y metadatos. Admite filtros `buscar`, `mes` (por ejemplo
`2026-09`) y `editorial`. Las búsquedas de fichas y fechas se aplican a la misma
entrada, no a entradas distintas de un documento.

### Índice persistente y criterio de no respuesta

El diseño toma como referencia `../iagen-api-casos/rag.py`:

1. Genera `data/documentos/DOC-001.md` a `DOC-004.md` desde el catálogo SQLite.
   Son documentos derivados; el origen de los registros es el catálogo local.
2. Usa `text-embedding-3-small` para un vector por registro y normaliza con NumPy.
3. Guarda la matriz y el manifiesto en `data/rag/indice.npz`, con SHA-256 del
   contenido, identificadores y modelo. Carga sin pickle. La huella detecta
   cambios aunque se mantenga el mismo número de registros. La escritura es
   atómica. Los arranques siguientes reutilizan esos embeddings.
4. Busca por similitud coseno, con umbral inicial `0.30`. Si nada alcanza el
   umbral, devuelve `No consta en los datos.` sin llamar al modelo de respuestas.
   Para comprobar la similitud sí necesita el embedding de la pregunta.
5. Fechas futuras y periodos sin registros se descartan antes de cualquier
   llamada de consulta. `modelo_usado: false` se refiere al modelo de respuestas.
6. El modelo `gpt-6-luna`, como en la referencia, selecciona IDs y tipo de
   respuesta mediante Structured Outputs. El servidor comprueba los IDs y
   compone el texto, los recuentos y las fuentes desde los registros locales.
   Para recuentos mensuales o anuales se incluyen **todos** los registros del
   periodo; el top-k de cuatro fragmentos no se confunde con el total.

`RAG_MODELO`, `RAG_MODELO_EMBEDDINGS`, `RAG_UMBRAL` y `RAG_K` se pueden configurar
en `.env`. No se ha modificado la clave existente. Una caída del servicio o un
problema de credenciales devuelve HTTP 503, nunca una respuesta inventada.

Para preparar o verificar el índice sin abrir el puerto HTTP:

```powershell
uv run servidor.py --preparar-indice
```

La primera preparación hace una petición de embeddings para los doce registros.
Repetirla muestra «Embeddings reutilizados del disco». Los archivos del índice
están excluidos de Git; los datos se pueden regenerar desde el código y SQLite.
No se indexan las páginas editoriales reales ni se atribuyen a ellas los libros
ficticios. Las fechas de consulta son reales; los tests fijan 16/10/2026.

Referencias de implementación: [embeddings de OpenAI](https://developers.openai.com/api/docs/guides/embeddings)
y [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses).

## Abrir la aplicación

Desde PowerShell, en esta carpeta:

```powershell
.\iniciar.ps1
```

Inicia ambos servidores en segundo plano, comprueba que responden y guarda sus
registros en `.runtime/`. Abre **http://127.0.0.1:5173**. Vite reenvía `/api` a
**http://127.0.0.1:8000**. Documentación de la API: http://127.0.0.1:8000/docs.

Para detener los procesos creados por ese script:

```powershell
.\detener.ps1
```

También se pueden iniciar en dos terminales, para ver la salida y usar Ctrl+C:

```powershell
# Terminal 1: FastAPI y RAG, puerto 8000.
.\scripts\servidor.ps1

# Terminal 2: Vite, puerto 5173.
.\scripts\web.ps1
```

## Preparar o restaurar las dependencias

```powershell
.\scripts\preparar.ps1
```

El script conserva un `.env` existente, usa `uv sync --locked` y `npm ci`, y
compila la interfaz. Si falta Node.js, instala localmente Node 24 mediante
`uv tool install nodejs-wheel==24.19.0`. Es una distribución de terceros en
PyPI, usada porque las descargas directas de nodejs.org no respondieron.
Las herramientas y las cachés quedan en `.tools/` y `.cache/`.

`scripts/entorno.ps1` añade Node al PATH de la terminal actual y carga los
ajustes de proxy. Para ejecutar comandos manualmente:

```powershell
. .\scripts\entorno.ps1
node -v
npm.cmd -v
uv run servidor.py
# En otra terminal, cargar el entorno, entrar en web/ y ejecutar npm.cmd run dev.
```

La configuración npm local `.npmrc` usa `proxy=${HTTPS_PROXY}` y
`https-proxy=${HTTPS_PROXY}`; se aplica tanto en la raíz como en `web/` mediante
`NPM_CONFIG_USERCONFIG`. El proxy se resuelve desde `.env`, sin guardar su valor
en el archivo de configuración. Se conservan las comprobaciones TLS y se usan
los certificados del sistema. Nunca se envían los accesos locales al proxy.
`npm.cmd` evita depender de la política de ejecución de los lanzadores `.ps1`.

La política de PowerShell de este usuario se dejó permanentemente en
`RemoteSigned`, con autorización del usuario. No forma parte del repositorio.

## Comprobar

```powershell
.\scripts\comprobar.ps1
```

Ejecuta las pruebas de API con `uv run python -m pytest -q`, la revisión de
Svelte/TypeScript (`npm run check`) y la compilación (`npm run build`). Los tests
usan una base temporal y una fecha fija de 16/10/2026; la aplicación usa la fecha
real de Madrid. El catálogo de demostración sigue siendo de 2026.

Ejemplos de consulta:

- ¿Qué libros se han publicado en septiembre de 2026?
- ¿Qué autores han publicado en 2026 y qué libros?
- ¿Qué editoriales han publicado en 2026 y cuántos libros?
- No me preguntes por fechas futuras a la del día de la consulta.

Para periodos posteriores a la consulta se responde **«No consta en los datos»**,
sin títulos ni recuentos. Si un periodo pasado no tiene registros, se explica
que ello no implica que no se publicaran libros en el mercado.

## Estructura y datos

```text
src/folio/api.py          API, exportación y servicio de la interfaz compilada
src/folio/catalog.py      SQLite, búsqueda y evidencias
src/folio/queries.py      Interpretación de consultas y límites temporales
src/folio/sample_data.py  Registros ficticios y enlaces editoriales reales
servidor.py              Entrada del servidor RAG: uv run servidor.py
src/folio/rag.py          Índice persistente, recuperación y respuesta fundamentada
src/folio/rag_models.py   Contratos estructurados de petición, respuesta y fuentes
src/folio/rag_api.py      POST /api/preguntar y GET /api/documentos
tests/                   Pruebas de API y RAG con base, reloj y cliente aislados
ejemplos/                Cuerpos JSON listos para los comandos curl
web/                     Interfaz Svelte + TypeScript, creada con create-vite
scripts/                 Preparación, entorno y comprobaciones
data/folio.sqlite3       Base local; se crea al iniciar y está excluida de Git
maquetas.html            Maqueta original autónoma de cinco vistas
```

La semilla usa identificadores únicos y no duplica libros al reiniciar. No se
modifica ni elimina la base al abrir la aplicación. `.env`, `.venv/`,
`node_modules/`, la base, herramientas, cachés y registros están excluidos de Git.
Se versionan `uv.lock` y `web/package-lock.json` para restaurar las versiones.

Tras `npm run build` dentro de `web/`, FastAPI también sirve la interfaz en
http://127.0.0.1:8000, sin necesidad del servidor de Vite.
