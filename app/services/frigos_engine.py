class FrigosEngine:
    """
    Motor para resolver dependencias automáticas de Frigoríficos locales y nacionales.
    """
    
    @staticmethod
    def inferir_texto_trayecto_desde_ruta(origen: str, destino: str, trayecto_descripcion: str):
        """
        Retorna la concatenación u oraciones puras exigidas por el "CONTROL FRIGOS"
        (e.g., "SUECA-BARCELONA-SUECA").
        """
        if trayecto_descripcion and trayecto_descripcion.strip():
            return trayecto_descripcion.upper()
        
        # Fallback build    
        return f"{origen} a {destino}".upper()
    
    @staticmethod
    def inferir_facturacion(precio_fijo: float):
        """Si la tarifa es 0, requiere alerta en UI."""
        if not precio_fijo or precio_fijo <= 0:
            return 0.0
        return float(precio_fijo)
