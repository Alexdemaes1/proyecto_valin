"""
Motor de Frigoríficos: generación de texto de trayecto.
"""


class FrigosEngine:

    @staticmethod
    def inferir_texto_trayecto(origen, destino, trayecto_descripcion=''):
        """Genera el texto de trayecto para el control de frigos."""
        if trayecto_descripcion and trayecto_descripcion.strip():
            return trayecto_descripcion.upper()
        return f"{origen} a {destino}".upper()

    @staticmethod
    def inferir_facturacion(precio_fijo):
        """Devuelve el precio o 0 si no hay tarifa definida."""
        if not precio_fijo or precio_fijo <= 0:
            return 0.0
        return float(precio_fijo)
