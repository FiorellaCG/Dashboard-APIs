/* ============================================================
   BASE DE DATOS: DashboardAPIs
   Proyecto: Dashboard de conexión a APIs públicas (Grupo 3)
   Motor: SQL Server (T-SQL)
   ============================================================ */

-- Crear la base de datos (ejecutar una sola vez)
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'DashboardAPIs')
BEGIN
    CREATE DATABASE DashboardAPIs;
END
GO

USE DashboardAPIs;
GO

/* ============================================================
   TABLA ROLES
   ============================================================ */
IF OBJECT_ID('dbo.roles', 'U') IS NOT NULL DROP TABLE dbo.roles;
GO
CREATE TABLE dbo.roles (
    id_rol      INT IDENTITY(1,1) PRIMARY KEY,
    nombre      NVARCHAR(50) NOT NULL,
    descripcion NVARCHAR(255) NULL
);
GO

/* ============================================================
   TABLA USUARIOS
   ============================================================ */
IF OBJECT_ID('dbo.usuarios', 'U') IS NOT NULL DROP TABLE dbo.usuarios;
GO
CREATE TABLE dbo.usuarios (
    id_usuario      INT IDENTITY(1,1) PRIMARY KEY,
    nombre          NVARCHAR(100) NOT NULL,
    apellido        NVARCHAR(100) NULL,
    correo          NVARCHAR(150) NOT NULL UNIQUE,
    password_hash   NVARCHAR(255) NOT NULL,       -- nunca texto plano, guardar hash (bcrypt/argon2)
    telefono        NVARCHAR(20) NULL,
    estado          NVARCHAR(20) NOT NULL DEFAULT 'activo'
                        CONSTRAINT CK_usuarios_estado CHECK (estado IN ('activo','inactivo','bloqueado')),
    dos_factor      BIT NOT NULL DEFAULT 0,
    fecha_registro  DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    id_rol          INT NOT NULL,
    CONSTRAINT FK_usuarios_roles FOREIGN KEY (id_rol) REFERENCES dbo.roles(id_rol)
);
GO
CREATE INDEX IX_usuarios_correo ON dbo.usuarios(correo);
GO

/* ============================================================
   TABLA AUTENTICACION 2FA
   ============================================================ */
IF OBJECT_ID('dbo.autenticacion_2fa', 'U') IS NOT NULL DROP TABLE dbo.autenticacion_2fa;
GO
CREATE TABLE dbo.autenticacion_2fa (
    id_usuario          INT PRIMARY KEY,
    metodo              NVARCHAR(20) NOT NULL
                            CONSTRAINT CK_2fa_metodo CHECK (metodo IN ('totp','sms','email')),
    secreto             NVARCHAR(255) NULL,        -- si usas un proveedor externo (Auth0/Okta/Firebase) puede ir vacío
    verificado          BIT NOT NULL DEFAULT 0,
    fecha_activacion    DATETIME2 NULL,
    CONSTRAINT FK_2fa_usuarios FOREIGN KEY (id_usuario) REFERENCES dbo.usuarios(id_usuario)
);
GO

/* ============================================================
   TABLA TIPOS_TRANSACCION (catálogo de códigos de bitácora)
   ============================================================ */
IF OBJECT_ID('dbo.tipos_transaccion', 'U') IS NOT NULL DROP TABLE dbo.tipos_transaccion;
GO
CREATE TABLE dbo.tipos_transaccion (
    codigo  NVARCHAR(10) PRIMARY KEY,
    nombre  NVARCHAR(100) NOT NULL
);
GO

/* ============================================================
   TABLA BITACORA
   ============================================================ */
IF OBJECT_ID('dbo.bitacora', 'U') IS NOT NULL DROP TABLE dbo.bitacora;
GO
CREATE TABLE dbo.bitacora (
    id_bitacora         INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario          INT NULL,
    codigo_transaccion  NVARCHAR(10) NULL,
    accion              NVARCHAR(100) NOT NULL,
    descripcion         NVARCHAR(500) NULL,
    fecha               DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    ip                  NVARCHAR(45) NULL,
    CONSTRAINT FK_bitacora_usuarios FOREIGN KEY (id_usuario) REFERENCES dbo.usuarios(id_usuario),
    CONSTRAINT FK_bitacora_tipo_transaccion FOREIGN KEY (codigo_transaccion) REFERENCES dbo.tipos_transaccion(codigo)
);
GO
CREATE INDEX IX_bitacora_usuario ON dbo.bitacora(id_usuario);
GO

/* ============================================================
   TABLA FUENTES DE DATOS (catálogo de APIs externas)
   ============================================================ */
IF OBJECT_ID('dbo.fuentes_datos', 'U') IS NOT NULL DROP TABLE dbo.fuentes_datos;
GO
CREATE TABLE dbo.fuentes_datos (
    id_fuente       INT IDENTITY(1,1) PRIMARY KEY,
    nombre          NVARCHAR(100) NOT NULL,     -- 'World Bank', 'OpenWeather', 'REST Countries'
    url_base        NVARCHAR(255) NOT NULL,
    tipo_dato       NVARCHAR(50) NULL,          -- 'economico', 'clima', 'geografico'
    activa          BIT NOT NULL DEFAULT 1
);
GO

/* ============================================================
   TABLA WIDGETS (catálogo de widgets disponibles)
   ============================================================ */
IF OBJECT_ID('dbo.widgets', 'U') IS NOT NULL DROP TABLE dbo.widgets;
GO
CREATE TABLE dbo.widgets (
    id_widget       INT IDENTITY(1,1) PRIMARY KEY,
    nombre          NVARCHAR(100) NOT NULL,
    tipo_grafico    NVARCHAR(20) NOT NULL
                        CONSTRAINT CK_widgets_tipo CHECK (tipo_grafico IN ('barras','lineas','pastel','mapa','tabla')),
    id_fuente       INT NULL,
    descripcion     NVARCHAR(255) NULL,
    activo          BIT NOT NULL DEFAULT 1,
    CONSTRAINT FK_widgets_fuentes FOREIGN KEY (id_fuente) REFERENCES dbo.fuentes_datos(id_fuente)
);
GO

/* ============================================================
   TABLA USUARIO_WIDGET (personalización del panel por usuario)

   NOTA DE DISEÑO: se usa un id_usuario_widget propio como PRIMARY KEY
   (en vez de una llave compuesta id_usuario + id_widget) porque Django
   no soporta llaves primarias compuestas de forma nativa. La combinación
   (id_usuario, id_widget) se mantiene como restricción UNIQUE para
   seguir garantizando que un usuario no repita el mismo widget dos veces.
   ============================================================ */
IF OBJECT_ID('dbo.usuario_widget', 'U') IS NOT NULL DROP TABLE dbo.usuario_widget;
GO
CREATE TABLE dbo.usuario_widget (
    id_usuario_widget  INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario         INT NOT NULL,
    id_widget          INT NOT NULL,
    visible            BIT NOT NULL DEFAULT 1,
    orden              INT NULL,
    configuracion      NVARCHAR(MAX) NULL,   -- JSON: {"pais":"CR","indicador":"PIB"}
    CONSTRAINT UQ_usuario_widget UNIQUE (id_usuario, id_widget),
    CONSTRAINT FK_uw_usuarios FOREIGN KEY (id_usuario) REFERENCES dbo.usuarios(id_usuario),
    CONSTRAINT FK_uw_widgets FOREIGN KEY (id_widget) REFERENCES dbo.widgets(id_widget)
);
GO

/* ============================================================
   TABLA HISTORIAL_CONSULTAS (parámetros de cada consulta a la API)
   ============================================================ */
IF OBJECT_ID('dbo.historial_consultas', 'U') IS NOT NULL DROP TABLE dbo.historial_consultas;
GO
CREATE TABLE dbo.historial_consultas (
    id_consulta     INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario      INT NULL,
    id_fuente       INT NULL,
    pais            NVARCHAR(100) NULL,
    categoria       NVARCHAR(100) NULL,
    fecha_inicio    DATE NULL,
    fecha_fin       DATE NULL,
    fecha_consulta  DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_hc_usuarios FOREIGN KEY (id_usuario) REFERENCES dbo.usuarios(id_usuario),
    CONSTRAINT FK_hc_fuentes FOREIGN KEY (id_fuente) REFERENCES dbo.fuentes_datos(id_fuente)
);
GO

/* ============================================================
   TABLA DATOS_API (resultado/caché de las llamadas a las APIs)
   ============================================================ */
IF OBJECT_ID('dbo.datos_api', 'U') IS NOT NULL DROP TABLE dbo.datos_api;
GO
CREATE TABLE dbo.datos_api (
    id_dato         INT IDENTITY(1,1) PRIMARY KEY,
    id_consulta     INT NOT NULL,
    fuente          NVARCHAR(50) NOT NULL,      -- 'openweather','worldbank','restcountries'
    indicador       NVARCHAR(100) NULL,         -- 'temperatura','PIB','poblacion'
    pais            NVARCHAR(100) NULL,
    valor           FLOAT NULL,
    unidad          NVARCHAR(30) NULL,
    fecha_dato      DATE NULL,                  -- fecha a la que corresponde el dato
    payload_json    NVARCHAR(MAX) NULL,         -- respuesta cruda de la API, por si se necesita completa
    fecha_consulta  DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_datos_consulta FOREIGN KEY (id_consulta) REFERENCES dbo.historial_consultas(id_consulta)
);
GO
CREATE INDEX IX_datos_api_pais ON dbo.datos_api(pais);
CREATE INDEX IX_datos_api_fecha ON dbo.datos_api(fecha_dato);
GO

/* ============================================================
   DATOS INICIALES (seed data)
   Fuentes de datos y widgets base para que el dashboard funcione
   apenas se crea la base de datos, sin pasos manuales adicionales.
   ============================================================ */

INSERT INTO fuentes_datos (nombre, url_base, tipo_dato, activa)
VALUES
    ('World Bank', 'https://api.worldbank.org/v2', 'economico', 1),
    ('OpenWeather', 'https://api.openweathermap.org/data/2.5', 'clima', 1),
    ('REST Countries', 'https://countries.dev', 'geografico', 1);
GO

INSERT INTO tipos_transaccion (codigo, nombre)
VALUES
    ('001', 'Ingreso a la aplicacion'),
    ('002', 'Modificacion de informacion'),
    ('003', 'Consulta de informacion'),
    ('004', 'Eliminacion');
GO

INSERT INTO widgets (nombre, tipo_grafico, id_fuente, descripcion, activo)
VALUES
    ('PIB por país', 'barras',
        (SELECT id_fuente FROM fuentes_datos WHERE nombre = 'World Bank'),
        'Muestra el PIB del país seleccionado', 1),
    ('Clima actual', 'lineas',
        (SELECT id_fuente FROM fuentes_datos WHERE nombre = 'OpenWeather'),
        'Temperatura actual de la ciudad seleccionada', 1),
    ('Población por país', 'pastel',
        (SELECT id_fuente FROM fuentes_datos WHERE nombre = 'REST Countries'),
        'Población total del país seleccionado', 1);
GO

PRINT 'Base de datos, tablas y datos iniciales creados correctamente.';