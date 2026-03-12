# Sistema de Gestión Valin (v1.0)
Aplicación local de escritorio basada en Flask para la gestión logística de **Transportes Valin e Hijos S.A.**

## 🚀 Cómo empezar (Rápido)

1. **Doble clic en `LANZAR_APP.bat`**: Este archivo hará todo por ti:
   - Creará el entorno virtual.
   - Instalará las librerías necesarias.
   - Configurará la base de datos inicial.
   - Abrirá el navegador y lanzará la aplicación automáticamente.

## 🛠️ Instalación manual (Opcional)

## ⚙️ Configuración del Sincronizador y Google Drive

Este sistema está diseñado por **Transportes Valin** para ser portable. Al clonar el repositorio y ejecutar el `.bat`:
1. **Rutas Dinámicas:** El sistema detecta automáticamente dónde está instalado, eliminando la necesidad de configurar rutas absolutas manualmente.
2. **Vínculo con Google Drive:** Desde el **Dashboard**, puedes configurar:
   - La carpeta raíz del equipo en Drive.
   - El nombre del archivo de base de datos maestra.
   - La ruta al Excel legacy (`.xlsm`) para importar datos maestros.
3. **Persistencia:** La configuración se guarda en `local_settings.json` y se puede versionar en Git si se desea compartir entre terminales similares.
4. **Migración Express:** Si configuras el "Excel Legacy", aparecerá un botón en el Dashboard para cargar automáticamente todos los **Camiones, Chóferes y Granjas** al nuevo sistema.

## 👥 Usuarios por Defecto
- **Usuario:** `admin`
- **Contraseña:** `10041004`

## 🛠️ Estructura del Sistema

- **Pollo Vivo:** Planificación con algoritmo inverso (basado en hora de llegada a matadero).
- **Frigos/Aldi:** Gestión de rutas nacionales y entregas multitienda.
- **RRHH:** Motor de consolidación que agrupa viajes, calcula nocturnidades (22:00 a 06:00) y detecta "dobles viajes" (Tipo 2).
- **Exportaciones:** Generación de PDFs para conductores y Excel para nóminas/contabilidad.

## 🔒 Seguridad para GitHub
El archivo `.gitignore` ya está configurado para **excluir**:
- El entorno virtual (`venv/`)
- Tus bases de datos locales (`instance/`)
- Tus configuraciones privadas de Google Drive (`local_settings.json`)
- El archivo `.env`

Puedes subir el código a GitHub sin riesgo de filtrar datos corporativos.
