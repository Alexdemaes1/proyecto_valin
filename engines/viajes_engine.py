"""
Motor cronológico inverso de Pollo Vivo.
Calcula horarios restando desde la hora de llegada al matadero.

Este módulo NO depende de Flask ni de la base de datos.
Puede testearse de forma independiente.
"""

from datetime import datetime, timedelta


class ViajesEngine:

    @staticmethod
    def calculate_reverse_times(hora_llegada_matadero_str, trayecto_min, carga_min, operacion_date):
        """
        Calcula hora_carga, hora_salida y hora_fin desde la hora de llegada al matadero.

        Args:
            hora_llegada_matadero_str (str): Hora de llegada, formato "HH:MM" (ej: "03:00")
            trayecto_min (int): Minutos de trayecto desde la granja (ej: 120)
            carga_min (int): Minutos de carga en granja (ej: 60)
            operacion_date (date): Fecha del día planificado

        Returns:
            dict con claves: llegada_str, carga_str, salida_str, fin_str, cruza_dia_anterior
        """
        hm = datetime.strptime(hora_llegada_matadero_str, "%H:%M")
        llegada_dt = datetime.combine(operacion_date, hm.time())

        # Carga = Llegada - Trayecto - Carga
        carga_dt = llegada_dt - timedelta(minutes=(trayecto_min + carga_min))

        # Salida de Sueca = Carga - Trayecto
        salida_dt = carga_dt - timedelta(minutes=trayecto_min)

        # Fin aproximado = Llegada + 1 hora
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
            "cruza_dia_anterior": salida_dt.date() < operacion_date
        }
