# Folio · El mes, entre líneas

Aplicación local para consultar novedades editoriales en castellano por mes,
autoría y editorial. Interfaz Svelte 5 + TypeScript + Vite; servidor FastAPI;
catálogo persistente en SQLite.

El catálogo inicial contiene **12 libros, 6 autores y 4 editoriales ficticios**,
los mismos de `maquetas.html`. Cada respuesta cita registros y fragmentos.
Los enlaces editoriales de la vista Fuentes son reales y se investigaron el
16/10/2026; no son el origen de esos datos inventados. Todavía no hay un
recolector automático de páginas o PDF.

Las consultas actuales son guiadas y deterministas: no consumen la API de
OpenAI y funcionan sin clave. `openai`, `python-dotenv`, `numpy`, `fastapi` y
`uvicorn[standard]` están instalados con `uv add`, como se solicitó. `tzdata`
permite calcular la fecha real en `Europe/Madrid` también en Windows.

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
# Terminal 1: FastAPI, puerto 8000, recarga al modificar src/.
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
uv run python -m uvicorn folio.api:app --reload --reload-dir src
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
tests/test_api.py        Pruebas con base y reloj aislados
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
