import pandas as pd
import sys
import os

# Path hack to import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.maestros import Vehiculo, Conductor, Granja
from app.utils.local_settings import LocalSettingsManager

def import_excel_data(file_path=None):
    # Try to get path from settings if not provided
    if not file_path:
        settings = LocalSettingsManager.get_settings()
        file_path = settings.get('legacy_excel_path')
    
    if not file_path or not os.path.exists(file_path):
        print(f"Error: No se encuentra el archivo de Excel ({file_path}). Confígurelo en el Dashboard.")
        return

    app = create_app('dev')
    with app.app_context():
        # ... (rest of the logic stays same, just ensuring relative paths inside)
        print(f"Iniciando importación desde: {file_path}")
        
        # 1. VEHÍCULOS
        try:
            df_bases = pd.read_excel(file_path, sheet_name='BASES', usecols="A:C", skiprows=1)
            for _, row in df_bases.iterrows():
                if pd.isna(row.iloc[0]): continue
                cod = str(row.iloc[0]).split('.')[0]
                if not Vehiculo.query.filter_by(codigo_interno=cod).first():
                    db.session.add(Vehiculo(
                        codigo_interno=cod,
                        matricula_tractora=str(row.iloc[1]) if not pd.isna(row.iloc[1]) else '',
                        matricula_semirremolque=str(row.iloc[2]) if not pd.isna(row.iloc[2]) else ''
                    ))
            db.session.commit()
            print("Vehículos OK.")
        except Exception as e: print(f"Error vehículos: {e}")

        # 2. CONDUCTORES
        try:
            df_cond = pd.read_excel(file_path, sheet_name='BASES', usecols="G,H,I", skiprows=1)
            for _, row in df_cond.iterrows():
                alias = str(row.iloc[0]) if not pd.isna(row.iloc[0]) else ''
                if alias and not Conductor.query.filter_by(alias=alias).first():
                    db.session.add(Conductor(
                        alias=alias,
                        codigo_alfabetico=str(row.iloc[1]) if not pd.isna(row.iloc[1]) else '',
                        dni=str(row.iloc[2]) if not pd.isna(row.iloc[2]) else ''
                    ))
            db.session.commit()
            print("Conductores OK.")
        except Exception as e: print(f"Error conductores: {e}")

        # 3. GRANJAS
        try:
            df_granjas = pd.read_excel(file_path, sheet_name='GRANJAS', skiprows=1)
            for _, row in df_granjas.iterrows():
                cod = str(row.iloc[1]).split('.')[0] if not pd.isna(row.iloc[1]) else ''
                if cod and not Granja.query.filter_by(codigo=cod).first():
                    # Default times
                    trayecto = 120; carga = 60
                    try: trayecto = int(row.iloc[6]) if not pd.isna(row.iloc[6]) else 120
                    except: pass
                    try: carga = int(row.iloc[7]) if not pd.isna(row.iloc[7]) else 60
                    except: pass
                    
                    db.session.add(Granja(
                        codigo=cod,
                        nombre_cliente=str(row.iloc[2]) if not pd.isna(row.iloc[2]) else 'DESCONOCIDO',
                        localidad=str(row.iloc[3]) if not pd.isna(row.iloc[3]) else '',
                        tiempo_trayecto_min=trayecto,
                        tiempo_carga_min=carga
                    ))
            db.session.commit()
            print("Granjas OK.")
        except Exception as e: print(f"Error granjas: {e}")

if __name__ == '__main__':
    # No harder paths. Script uses current directory or settings.
    import_excel_data()
