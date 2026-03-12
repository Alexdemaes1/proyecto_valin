from .base import BaseModel
from .auth import User, Role, AuditLog
from .maestros import Vehiculo, Conductor, Granja, RutaFrigo, Tienda, Simbologia
from .operaciones import PlanificacionDia, ViajePollo, ServicioFrigo, ServicioAldi
from .rrhh import JornadaEmpleado, FichaEmpleadoSnapshot

# Al importar este archivo en __init__.py de /app, Alembic/SQLAlchemy
# detectará todos estos modelos para crear las tablas.
