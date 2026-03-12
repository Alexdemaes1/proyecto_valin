class AldiEngine:
    """
    Motor para la operativa de ALDI desde Sagunto.
    Calcula lógicas de texto unificado legacy para exportación.
    """
    
    @staticmethod
    def generar_texto_trayecto_aldi(tiendas_nombres: list, base_origen: str = "SAGUNTO") -> str:
        """
        Formatea el string exacto requerido por 'CONTROL ALDI' legacy.
        Ej: "<t1>,<t2>,<t3>,<t4> Y SAGUNTO"
        
        Args:
            tiendas_nombres (list): Nombres mapeados desde la tabla Maestros (hasta 4)
            base_origen (str): Por defecto SAGUNTO.
            
        Returns:
            str: Texto formateado sin comas sueltas.
        """
        validas = [t.strip() for t in tiendas_nombres if isinstance(t, str) and t.strip()]
        
        if not validas:
            return base_origen

        # Unimos las tiendas con coma
        trayecto_tiendas = ", ".join(validas)
        texto_final = f"{trayecto_tiendas} y {base_origen}".upper()
        
        return texto_final
