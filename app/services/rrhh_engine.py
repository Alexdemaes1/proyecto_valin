from datetime import datetime, time, date, timedelta

class RrhhEngine:
    """
    Motor central de generación de nóminas / reglas de HORARIOS.
    """
    
    @staticmethod
    def calc_nocturnidad(inicio_str: str, fin_str: str, fecha_operativa: date):
        """
        Calcular horas puras y nocturnidad (22 a 06) desde dos strings.
        
        Args:
            inicio_str: "18:00"
            fin_str: "04:00"
            fecha_operativa: date object
            
        Returns: 
            tuple(mins_totales: int, mins_nocturnos: int, dec_nocturno: float)
        """
        # 1. Parsing to real unified datetimes
        hinicio = datetime.strptime(inicio_str, '%H:%M').time()
        hfin = datetime.strptime(fin_str, '%H:%M').time()
        
        # Compose datetimes
        dt_start = datetime.combine(fecha_operativa, hinicio)
        dt_end = datetime.combine(fecha_operativa, hfin)
        
        # Resuelve cruce de medianoche si fin < inicio
        if hfin < hinicio:
            dt_end += timedelta(days=1)
            
        # Calcular los bordes lógicos
        total_delta = dt_end - dt_start
        total_mins = int(total_delta.total_seconds() / 60)
        
        noct_mins = 0
        
        # Iterate over minutes of the span (brute and safe approach)
        # 22:00 = 22, 06:00 = 6
        current_dt = dt_start
        while current_dt < dt_end:
            h = current_dt.hour
            # Between 22:00 (inc) and 06:00 (exc)
            if h >= 22 or h < 6:
                noct_mins += 1
            current_dt += timedelta(minutes=1)
            
        decimal_nocturnos = round(noct_mins / 60.0, 2)
        
        return total_mins, noct_mins, decimal_nocturnos

    @staticmethod
    def get_bonos_por_tipo(codigo_normalizado: str) -> bool:
        """
        Si la dieta u otros bonos aplican basados en el 'tipo_normalizado_interno'
        Valores de dieta: '1', '2', '11', '8', 'C2' (basado en Excel histórico)
        """
        dict_dieta = ['1', '2', '11', '8', 'C2']
        return codigo_normalizado in dict_dieta

    @staticmethod
    def aplica_pernocta(ruta_frigo_codigo: str) -> bool:
        """Devuelve True si la ruta Frigo es SU42, SU44 o SU23"""
        return ruta_frigo_codigo in ['SU42', 'SU44', 'SU23']

    @staticmethod
    def consolidar_dobles_viajes(cargas: list):
        """
        Recibe una lista de dicts con:
        [
            {'inicio': '14:00', 'fin': '22:00', 'tipo':'1'},
            {'inicio': '23:00', 'fin': '03:00', 'tipo':'1'}
        ]
        Devuelve el registro agrupado Tipo 2, o el de mejor tipo combinador, 
        quedándose con min(inicio) y max(fin datetime sumando días).
        """
        # Implementation left to be wired specifically to DB query results.
        pass
