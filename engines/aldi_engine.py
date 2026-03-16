"""
Motor de Aldi: generación de texto de trayecto desde tiendas.
"""


class AldiEngine:

    @staticmethod
    def generar_texto_trayecto_aldi(tiendas_nombres, base_origen='SAGUNTO'):
        """
        Formatea el texto de trayecto para el control de Aldi.
        Ejemplo: "AL GEMESI, ALZIRA Y SAGUNTO"

        Args:
            tiendas_nombres (list): Nombres de tiendas (hasta 4)
            base_origen (str): Base de origen, por defecto SAGUNTO

        Returns:
            str: Texto formateado
        """
        validas = [t.strip() for t in tiendas_nombres
                   if isinstance(t, str) and t.strip()]

        if not validas:
            return base_origen

        trayecto = ", ".join(validas)
        return f"{trayecto} y {base_origen}".upper()
