import pytest
from datetime import date
from engines.viajes_engine import ViajesEngine
from engines.rrhh_engine import RrhhEngine
from engines.aldi_engine import AldiEngine

def test_calculo_inverso_madrugada():
    # Llega matadero a las 01:00. Trayecto 1h, Carga 1h. 
    # Debe ser carga 23:00 dia anterior, salida 22:00 dia anterior
    fecha_hoy = date(2026, 3, 5)
    resultado = ViajesEngine.calculate_reverse_times("01:00", 60, 60, fecha_hoy)
    
    assert resultado["llegada_str"] == "01:00"
    assert resultado["carga_str"] == "23:00"
    assert resultado["salida_str"] == "22:00"
    assert resultado["fin_str"] == "02:00"
    assert resultado["cruza_dia_anterior"] is True
    
def test_nocturnidad_interseccion():
    # Turno 18:00 a 04:00 (10 horas totales, 6 horas nocturnas)
    fecha_hoy = date(2026, 3, 5)
    totales, min_noct, dec_noct = RrhhEngine.calc_nocturnidad("18:00", "04:00", fecha_hoy)
    
    assert totales == 600 # 10h
    assert min_noct == 360 # 6h (22 a 24) + (00 a 06) = 2h + 4h
    assert dec_noct == 6.00

def test_nocturnidad_borde_fuera():
    # 21:00 a 22:00 -> 0 horas nocturnas
    t, m, d = RrhhEngine.calc_nocturnidad("21:00", "22:00", date(2026, 3, 5))
    assert t == 60
    assert m == 0
    assert d == 0.00
    
def test_aldi_trayecto_unificador():
    res = AldiEngine.generar_texto_trayecto_aldi(["AL GEMESI", "ALZIRA", "", None], "SAGUNTO")
    assert res == "AL GEMESI, ALZIRA Y SAGUNTO"
    
def test_aldi_trayecto_sin_tiendas():
    res = AldiEngine.generar_texto_trayecto_aldi([])
    assert res == "SAGUNTO"
