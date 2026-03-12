from datetime import datetime, timedelta

class ViajesEngine:
    """
    Motor cronológico inverso de Pollo Vivo.
    Implementa el cálculo desde "Matadero" hacia atrás cuidando la medianoche.
    """
    
    @staticmethod
    def calculate_reverse_times(hora_llegada_matadero_str: str, trayecto_min: int, carga_min: int, operacion_date: datetime.date):
        """
        Calcula hora_carga, hora_salida y fecha real de las mismas.
        
        Args:
            hora_llegada_matadero_str (str): "03:00"
            trayecto_min (int): Minutos desde catálogo Granja (ej 120)
            carga_min (int): Minutos de carga (ej 60)
            operacion_date (date): Fecha del día planificado "Planificacion Dia"
            
        Returns:
            dict: Con string HH:MM y datetime real
        """
        # Parse the input strings
        hm = datetime.strptime(hora_llegada_matadero_str, "%H:%M")
        llegada_dt = datetime.combine(operacion_date, hm.time())
        
        # Ojo: Si la llegada al matadero es a las 01:00, probablemente pertenece a la 
        # operativa de la madrugada siguiente. El usuario planifica "El día 4", 
        # pero las 01:00 del día 4 es técnicamente la madrugada del día 5. A nivel 
        # Excel, se solía solapar. Si es menor de ej. 12:00PM asume que es la noche siguiente.
        # Pero nos fiaremos tal cual a la fecha base que entra + horas.
        
        # Algoritmo inverso crudo
        # H_CARGA = LLEGADA - TRAYECTO - CARGA
        carga_dt = llegada_dt - timedelta(minutes=(trayecto_min + carga_min))
        
        # H_SALIDA = H_CARGA - TRAYECTO
        salida_dt = carga_dt - timedelta(minutes=trayecto_min)
        
        # FIN aporx = LLEGADA + 1 h
        fin_dt = llegada_dt + timedelta(hours=1)
        
        return {
            "llegada_dt": llegada_dt,
            "carga_dt": carga_dt,
            "salida_dt": salida_dt,
            "fin_dt": fin_dt,
            "llegada_str": llegada_dt.strftime("%H:%M"),
            "carga_str": carga_dt.strftime("%H:%M"),
            "salida_str": salida_dt.strftime("%H:%M"),
            "fin_str": fin_dt.strftime("%H:%M"),
            # Banderas por si la salida cayó en el día anterior al operativo (cruzó medianoche)
            "cruza_dia_anterior": salida_dt.date() < operacion_date
        }
