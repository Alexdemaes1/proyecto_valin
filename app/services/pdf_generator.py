import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from app.models.operaciones import PlanificacionDia

class PdfGenerator:
    """Generador de PDFs corporativos para Transportes Valin"""
    
    @staticmethod
    def generar_hoja_chofer(plan_id):
        plan = PlanificacionDia.query.get(plan_id)
        if not plan: return None
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=20)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1, textColor=colors.HexColor("#1C3F78"))
        
        # Header
        elements.append(Paragraph(f"TRANSPORTES VALIN E HIJOS S.A.", title_style))
        elements.append(Paragraph(f"PLANIFICACIÓN DE VIAJES - {plan.fecha_operativa.strftime('%d/%m/%Y')} ({plan.dia_semana})", styles['Heading3']))
        elements.append(Spacer(1, 12))
        
        # Tabla de Viajes Pollo
        data = [['#', 'CAMIÓN', 'CONDUCTOR', 'GRANJA / CLIENTE', 'LLEGADA', 'CARGA', 'SALIDA', 'FIN']]
        for v in plan.viajes:
            data.append([
                v.orden_visual,
                v.vehiculo.codigo_interno if v.vehiculo else '-',
                v.conductor.alias if v.conductor else '-',
                f"{v.granja.codigo} - {v.granja.nombre_cliente}" if v.granja else '-',
                v.hora_llegada_matadero,
                v.hora_carga_granja_calc or '-',
                v.hora_salida_sueca_calc or '-',
                v.hora_fin_jornada_aprox_calc or '-'
            ])
            
        t = Table(data, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#14345F")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F4FC")])
        ]))
        
        elements.append(t)
        doc.build(elements)
        buffer.seek(0)
        return buffer
