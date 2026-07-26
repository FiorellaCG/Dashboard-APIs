[README.md](https://github.com/user-attachments/files/30382702/README.md)
# Dashboard APIs

Dashboard que consume APIs públicas externas (World Bank, OpenWeather, REST Countries vía `countries.dev`) con autenticación de usuarios, 2FA (TOTP) y visualización de datos con gráficas.

## Stack

- **Backend:** Django + Django REST Framework, conectado a SQL Server
- **Frontend:** React (Vite) + Chart.js
- **Base de datos:** SQL Server (Express o superior)
- **Autenticación:** JWT (`djangorestframework-simplejwt`) + 2FA con TOTP (`pyotp`)

---

## Requisitos previos

Antes de empezar, asegúrate de tener instalado:

- **Python 3.12+** ([python.org/downloads](https://www.python.org/downloads/)) — al instalar, marca la casilla **"Add python.exe to PATH"**
- **Node.js 18+** ([nodejs.org](https://nodejs.org/))
- **SQL Server** (Express está bien) con **SSMS** (SQL Server Management Studio)
- **ODBC Driver 17 for SQL Server** ([descarga aquí](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server))
- Git

---

## 1. Clonar el repositorio

```powershell
git clone <url-del-repo>
cd Dashboard
```

## 2. Configurar SQL Server

1. Abre **SSMS** y conéctate a tu instancia local (ej. `localhost\SQLEXPRESS`).
2. Habilita el modo de autenticación mixto si no lo está:
   - Clic derecho en el servidor → **Propiedades** → **Seguridad** → selecciona **"SQL Server and Windows Authentication mode"**
   - Reinicia el servicio de SQL Server después de este cambio
3. En **Seguridad → Inicios de sesión → sa** → Propiedades:
   - Define una contraseña
   - En la pestaña **Estado**, asegúrate que el login esté **Habilitado**
4. Abre una nueva consulta en SSMS y ejecuta el script `dashboard_sqlserver.sql` (está en la raíz del proyecto). Esto crea la base de datos `DashboardAPIs`, todas las tablas, y los datos iniciales (fuentes de datos y widgets).

## 3. Configurar el Backend (Django)

Desde la raíz del proyecto:

```powershell
python -m venv venv
venv\Scripts\activate
pip install django djangorestframework mssql-django pyodbc python-dotenv django-cors-headers requests djangorestframework-simplejwt bcrypt pyotp qrcode[pil]
```

### Crear el archivo `.env`

En la raíz del proyecto (junto a `manage.py`), crea un archivo `.env` con:

```env
DB_NAME=DashboardAPIs
DB_USER=sa
DB_PASSWORD=tu_password_de_sql_server
DB_HOST=localhost\SQLEXPRESS
DJANGO_SECRET_KEY=cualquier_string_aleatorio_largo
OPENWEATHER_API_KEY=tu_api_key_de_openweather
```

> ⚠️ **Cada persona debe usar sus propias credenciales.** No copies el `.env` de otro compañero — la contraseña de SQL Server es local a cada máquina, y cada quien debe generar su propia API key de OpenWeather.

**Para obtener tu OpenWeather API key:**
1. Regístrate gratis en [openweathermap.org/api](https://openweathermap.org/api)
2. Ve a [home.openweathermap.org/api_keys](https://home.openweathermap.org/api_keys) y copia tu key
3. ⏳ Puede tardar hasta un par de horas en activarse después de crearla

> Ajusta `DB_HOST` según tu instancia de SQL Server. Si usas la instancia default (no nombrada), usa solo `localhost` sin `\SQLEXPRESS`.

### Levantar el servidor

```powershell
python manage.py migrate
python manage.py runserver
```

Esto debería levantar el backend en `http://localhost:8000`. Prueba abrir `http://localhost:8000/admin` en el navegador para confirmar que no hay errores.

### Crear un usuario de prueba

Como la tabla `usuarios` es propia del proyecto (no el sistema nativo de Django), no puedes usar `createsuperuser`. Usa este comando en su lugar:

```powershell
python manage.py crear_usuario_prueba --correo test@test.com --password 123456 --nombre Juan --apellido Perez
```

## 4. Configurar el Frontend (React)

En otra terminal, desde la carpeta `mi-proyecto-react`:

```powershell
cd mi-proyecto-react
npm install
npm run dev
```

Esto levanta el frontend en `http://localhost:5173`. Ábrelo en el navegador — deberías ver la pantalla de Login.

---

## Flujo de prueba rápido

1. Entra a `http://localhost:5173`
2. Inicia sesión con el usuario que creaste (`test@test.com` / `123456`)
3. En el Dashboard, prueba cada widget escribiendo un país/código:
   - **PIB por país:** código de 2 letras (ej. `CR`, `MX`, `US`)
   - **Clima actual:** nombre de ciudad (ej. `San Jose`, `Bogota`)
   - **Población por país:** nombre o código de país (ej. `Costa Rica`, `CR`)
4. Opcional: activa el 2FA desde el botón "Configurar 2FA" en el header, escaneando el QR con Google Authenticator o similar

---

## Estructura del proyecto

```
Dashboard/
├── backend/                    # Configuración de Django (settings, urls)
├── dashboard_api/              # App principal: modelos, vistas, servicios
│   ├── models.py               # Modelos mapeados a las tablas SQL (managed=False)
│   ├── authentication.py       # Login, registro, 2FA
│   ├── views.py                # ViewSets y endpoint de dashboard
│   ├── serializers.py
│   ├── management/commands/    # Comando crear_usuario_prueba
│   └── services/
│       └── apis_externas.py    # Integración con World Bank, OpenWeather, countries.dev
├── mi-proyecto-react/          # Frontend React (Vite)
│   └── src/
│       ├── pages/               # Login, Registro, Dashboard, ConfigurarDosFactor
│       ├── components/          # WidgetCard
│       ├── context/              # AuthContext
│       ├── services/             # api.js, authService.js, widgetService.js
│       └── routes/               # ProtectedRoute
├── dashboard_sqlserver.sql     # Script completo de la base de datos
├── manage.py
└── .env                        # NO se sube al repositorio (credenciales locales)
```

---

## Notas importantes

- **`managed = False`**: los modelos de Django no gestionan las tablas (no se pueden alterar con `makemigrations`/`migrate`). Cualquier cambio de estructura se hace directo en SQL Server y se refleja manualmente en `models.py`.
- **Tokens JWT**: el `access_token` dura 2 horas en desarrollo (configurado así para comodidad al probar). Si expira, hay que volver a iniciar sesión o implementar el refresh automático (ya configurado en `api.js` del frontend).
- **`.env` nunca se sube a Git** — está en `.gitignore`. Cada quien crea el suyo localmente.
- **REST Countries**: la API original (`restcountries.com` v3.1) fue discontinuada. El proyecto usa `countries.dev` como alternativa gratuita sin necesidad de API key.

---

## Problemas comunes

| Error | Causa probable | Solución |
|---|---|---|
| `Python was not found` | Terminal nueva sin venv activado, o parado en carpeta incorrecta | `cd` a la raíz del proyecto y correr `venv\Scripts\activate` |
| `Login failed for user 'sa'` | Modo de autenticación mixto deshabilitado, o password no coincide | Revisar pasos de configuración de SQL Server arriba |
| `npm run dev` da "Missing script" | Estás en la carpeta raíz en vez de `mi-proyecto-react` | `cd mi-proyecto-react` antes de correr el comando |
| Widget de clima da 401 | `OPENWEATHER_API_KEY` no configurada o key recién creada (aún no activa) | Verificar `.env`, esperar activación de la key |
| Token expirado (401 en endpoints protegidos) | El access token JWT venció | Volver a iniciar sesión |
