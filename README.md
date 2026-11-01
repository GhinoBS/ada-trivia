# Ada 💜 — web de trivia para dos, online

Dos celulares, una misma URL, 10 preguntas aleatorias, cuenta regresiva, puntuación sincronizada y un enlace para invitar. **No es una app instalable.**

## Archivos

| Archivo | Dónde va |
|---|---|
| `app.py` | Repositorio de GitHub (carpeta principal) |
| `requirements.txt` | Repositorio de GitHub (carpeta principal) |
| `.streamlit/config.toml` | Repositorio de GitHub, subcarpeta `.streamlit` |
| `database.sql` | Copia todo su contenido y ejecútalo **una vez** en Supabase → SQL Editor; también puedes guardarlo en GitHub |
| `secrets.example.toml` | Archivo de ejemplo sin claves; las claves reales se ponen en Streamlit → Advanced settings → Secrets |
| `.gitignore` | Repositorio de GitHub, carpeta principal |

## Publicación (sin instalar programas en tu computadora)

1. Crea una cuenta gratis en [GitHub](https://github.com/) (solo tú, **no** las personas que jugarán).
2. En [Supabase](https://supabase.com/dashboard) crea una cuenta y un **proyecto nuevo**, con plan Free. Recuerda la contraseña del proyecto si te la pide. Elige la región más cercana a tus jugadores.
3. Dentro del proyecto Supabase abre **SQL Editor → New query**. Abre `database.sql`, copia **todo** su contenido, pégalo y presiona **Run**. Debe ejecutarse sin errores. Crea 5 tablas, 5 funciones y 24 preguntas.
4. Dentro de Supabase abre **Project Settings → API Keys** (o el botón **Connect**). Copia la **Project URL** (algo como `https://xxxx.supabase.co`) y la **Secret API key** que **empieza con `sb_secret_`**. Si no ves la clave nueva, ve a la pestaña **Publishable and secret API keys** y créala. No uses `sb_publishable_` para el backend.
5. En GitHub, pulsa **+ → New repository**, ponle nombre `ada-trivia` y elige **Public**. Pulsa **Create repository**.
6. Dentro del repositorio, pulsa **Add file → Upload files**. Sube `app.py`, `requirements.txt`, `database.sql`, `README.md`, `secrets.example.toml` y `.gitignore`. Presiona **Commit changes**. Para la subcarpeta `.streamlit`, pulsa **Add file → Create new file** y escribe en el nombre `.streamlit/config.toml`; pega el contenido del archivo descargado de ese nombre y guarda con **Commit changes**. GitHub suele ocultar archivos con punto al seleccionarlos; no olvides `.gitignore`.
7. Ve a [Streamlit Community Cloud](https://share.streamlit.io/) e inicia sesión usando GitHub. Haz clic en **Create app**, selecciona el repositorio `ada-trivia`, rama `main` y archivo principal `app.py`.
8. En **App URL** (si está libre), escribe `ada-trivia`. Abre **Advanced settings → Secrets** y pega el texto siguiente, sustituyendo los valores por los tuyos:

   ```toml
   SUPABASE_URL = "https://TU-PROYECTO.supabase.co"
   SUPABASE_SECRET_KEY = "sb_secret_TU_CLAVE_REAL"
   ```

9. Pulsa **Save** y luego **Deploy**. La URL final será la asignada por Streamlit, idealmente `https://ada-trivia.streamlit.app` si el subdominio está libre.
10. Comprueba que la app sea **pública**: en Streamlit, abre **Settings → Sharing** y selecciona **This app is public and searchable** si no estuviera marcada. Así tu novia no tendrá que iniciar sesión.
11. Desde tu celular abre la URL: escribe tu nombre y presiona **Crear sala e invitar**. Pulsa **Enviar por WhatsApp** o copia la URL de invitación. Tu novia abre **ese enlace** en su navegador, escribe su nombre y toca **Unirme a la sala**. Empieza una cuenta regresiva de 5 segundos y luego 10 preguntas. No hace falta computadora encendida, cuenta ni instalación para jugar.

## Importante: enlaces de sala y privacidad

- El enlace para compartir tiene **solo** `?room=XXXXXXXX`; lo pueden abrir desde cualquier navegador.
- Después de entrar, **tu propia dirección de navegador** también incluirá un `?me=...` privado para permitir reconectar después de recargar. **No compartas la barra de direcciones completa**; comparte únicamente el enlace que aparece dentro de Ada, bajo **Enlace para invitar**.
- Las claves secretas nunca deben subirse a GitHub: solamente se pegan en el campo **Secrets** de Streamlit Community Cloud.
- Las personas que juegan **no se registran**. Los servicios **GitHub, Streamlit y Supabase** sí requieren cuentas del **propietario** para configurar el proyecto.
- Supabase Free puede pausar proyectos por inactividad y Streamlit Community Cloud puede poner apps en reposo. La primera apertura después de un periodo inactivo podría demorar y podría requerir que el propietario reactive Supabase desde su panel. La disponibilidad inmediata 24/7 no se garantiza en planes gratuitos.
- Esta versión utiliza **consulta de cambios cada segundo** desde Streamlit, no un WebSocket directamente a Supabase. La lógica de puntajes y plazos reside en la base de datos, por lo que el estado compartido es único.
- Cada partida tiene 2 jugadores como máximo. Si ambos pierden el enlace/token privado, deben crear otra sala.

## Diagnóstico rápido

**«Falta configurar ... Secrets»**: revisa las dos variables en Advanced settings → Secrets y reinicia la app.

**«Could not find the function ...»**: ejecuta el archivo SQL completo en el proyecto correcto. Si acabas de ejecutarlo, espera unos segundos y recarga la web. En casos raros, ejecuta `NOTIFY pgrst, 'reload schema';` desde SQL Editor.

**«Invalid API key» / «permission denied»**: usa la clave `sb_secret_...` (secreta) y la URL del mismo proyecto Supabase.

**«Esta partida ya comenzó»**: crea una nueva sala; no se admite entrar como tercer jugador ni después de empezar.

**Se ven pantallas distintas**: verifica que ambas personas abrieron la misma sala (`room=...`). Si una perdió su URL personal, necesita empezar en una nueva sala.

## Licencia

Proyecto de ejemplo para personalizar y publicar. Sin garantías de disponibilidad comercial.
