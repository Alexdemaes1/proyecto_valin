# Transportes Valin e Hijos S.A. — Sistema de Gestión de Tráfico

Aplicación de gestión interna para planificación de viajes, control de frigoríficos y recursos humanos.

---

## Requisitos

- **Windows 10 o superior**
- **Python 3.10 o superior** — [Descargar aquí](https://www.python.org/downloads/)
  - ⚠️ Al instalar, **marcar** la casilla **"Add Python to PATH"**

---

## Instalación

1. Descargue o clone este repositorio en una carpeta del PC
2. Haga **doble clic** en `LANZAR_APP.bat`
3. La primera vez tardará 1-2 minutos

---

## Uso diario

1. Doble clic en `LANZAR_APP.bat`
2. Espere a que se abra el navegador
3. Credenciales: **admin** / **10041004**

> Para detener la aplicación, cierre la ventana negra (consola).

---

## Primer uso

1. Inicie sesión con admin / 10041004
2. En el **Panel de Control**, configure:
   - **Carpeta de Google Drive** (opcional: para compartir datos con otros PCs)
   - **Ruta al Excel** de datos maestros (opcional: para importar vehículos, conductores y granjas)
3. Pulse **Guardar configuración**
4. Si configuró el Excel, pulse **Importar Maestros desde Excel**

---

## Módulos disponibles

| Módulo | Función |
|---|---|
| **Panel de Control** | Configuración, importación, sincronización y copias de seguridad |
| **Maestros** | Gestión de vehículos, conductores y granjas |
| **Viajes** | Planificación diaria de viajes de pollo vivo con cálculo automático de horarios |
| **Frigos** | Listado de servicios de transporte frigorífico |
| **Aldi** | Listado de servicios de reparto a Aldi |
| **RRHH** | Generación de jornadas y cálculo de nocturnidad |

---

## Copias de seguridad

- Se crean **automáticamente** antes de importar, sincronizar o restaurar
- Puede crear una copia manual desde el Panel de Control
- Puede restaurar cualquier copia anterior

---

## Sincronización con Google Drive

Si varios PCs necesitan compartir datos:

1. Configure la misma carpeta de Google Drive en todos los PCs
2. Use **Descargar de Drive** para traer datos
3. Use **Subir a Drive** para compartir cambios
4. El sistema protege contra ediciones simultáneas

---

## Solución de problemas

| Problema | Solución |
|---|---|
| "Python no está instalado" | Instale Python desde python.org y marque "Add Python to PATH" |
| No se abre el navegador | Abra manualmente `http://127.0.0.1:5000` |
| Error al instalar dependencias | Compruebe su conexión a Internet |
| "No se encuentran los archivos" | Si descargó un .zip, extráigalo primero (clic derecho → Extraer todo) |
| Windows pregunta sobre el Firewall | Pulse Cancelar (la app funciona solo en su PC) |
| Errores raros o lentitud | No coloque el proyecto dentro de OneDrive o Dropbox |

---

## Notas importantes

- **No borre** las carpetas `venv/` ni `instance/`
- Si las borra por error, ejecute `LANZAR_APP.bat` de nuevo
- Para sincronizar datos entre PCs, use la función de Google Drive de la app
