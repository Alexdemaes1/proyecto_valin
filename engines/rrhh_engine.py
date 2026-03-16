"""
Motor de cálculos de RRHH: nocturnidad, bonos, consolidación.

Este módulo NO depende de Flask ni de la base de datos.
"""

from datetime import datetime, timedelta


class RrhhEngine:

    @staticmethod
    def calc_nocturnidad(inicio_str, fin_str, fecha_operativa):
        """
        Calcula horas totales y nocturnidad (22:00 a 06:00).

        Args:
            inicio_str (str): Hora inicio "HH:MM"
            fin_str (str): Hora fin "HH:MM"
            fecha_operativa (date): Fecha del día operativo

        Returns:
            tuple: (mins_totales, mins_nocturnos, decimal_nocturno)
        """
        hinicio = datetime.strptime(inicio_str, '%H:%M').time()
        hfin = datetime.strptime(fin_str, '%H:%M').time()

        dt_start = datetime.combine(fecha_operativa, hinicio)
        dt_end = datetime.combine(fecha_operativa, hfin)

        # Cruce de medianoche: si fin < inicio, sumamos un día
        if hfin < hinicio:
            dt_end += timedelta(days=1)

        total_mins = int((dt_end - dt_start).total_seconds() / 60)

        # Contar minutos nocturnos (22:00 a 06:00)
        noct_mins = 0
        current_dt = dt_start
        while current_dt < dt_end:
            h = current_dt.hour
            if h >= 22 or h < 6:
                noct_mins += 1
            current_dt += timedelta(minutes=1)

        decimal_nocturnos = round(noct_mins / 60.0, 2)
        return total_mins, noct_mins, decimal_nocturnos

    @staticmethod
    def get_bonos_por_tipo(codigo_normalizado):
        """Devuelve True si el tipo de jornada tiene derecho a dieta."""
        tipos_con_dieta = ['1', '2', '11', '8', 'C2']
        return codigo_normalizado in tipos_con_dieta

    @staticmethod
    def aplica_pernocta(ruta_frigo_codigo):
        """Devuelve True si la ruta frigorífica aplica pernocta."""
        return ruta_frigo_codigo in ['SU42', 'SU44', 'SU23']
