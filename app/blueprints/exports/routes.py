from flask import send_file, request, flash, redirect, url_for
from flask_login import login_required
from . import bp
from app.services.pdf_generator import PdfGenerator
from app.models.operaciones import PlanificacionDia
from app.models.rrhh import JornadaEmpleado

@bp.route('/pdf/chofer/<int:plan_id>')
@login_required
def pdf_chofer(plan_id):
    pdf_buffer = PdfGenerator.generar_hoja_chofer(plan_id)
    if not pdf_buffer:
        flash("No se pudo generar el PDF", "error")
        return redirect(url_for('viajes.index'))
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Plan_Valin_{plan_id}.pdf",
        mimetype='application/pdf'
    )

@bp.route('/excel/horario/<int:plan_id>')
@login_required
def excel_horario(plan_id):
    import pandas as pd
    import io

    plan = PlanificacionDia.query.get_or_404(plan_id)
    jornadas = JornadaEmpleado.query.filter_by(planificacion_id=plan_id).all()
    
    data = []
    for j in jornadas:
        data.append({
            'FECHA': plan.fecha_operativa,
            'CONDUCTOR': j.conductor.alias,
            'DNI': j.conductor.dni,
            'INICIO': j.hora_inicio_real,
            'FIN': j.hora_fin_real,
            'TIPO': j.tipo_normalizado_interno,
            'H. NOCTURNAS': j.horas_nocturnas_dec,
            'DIETA': 'SI' if j.dieta else 'NO',
            'PERNOCTA': 'SI' if j.pernocta else 'NO'
        })
        
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='HORARIO')
        
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name=f"Horario_Valin_{plan.fecha_operativa}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
