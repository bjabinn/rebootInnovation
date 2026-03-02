"""PDF Generator""" 
from reportlab.lib.pagesizes import landscape, A4 
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak 
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle 
from reportlab.lib.units import inch 
from reportlab.lib import colors 
from reportlab.lib.enums import TA_CENTER 
import plotly.io as pio 
import io 
from datetime import datetime
  
class PDFGenerator:  
    def __init__(self):  
        self.styles = getSampleStyleSheet() 
    def generate_report(self, results, team_name, visualizer, df_practices):  
        buffer = io.BytesIO()  
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)  
        story = [] 
        title = Paragraph(f"Evaluacion Reboot - Innovacion - {team_name}", self.styles["Title"])  
        story.append(title)  
        story.append(Spacer(1, 0.3*inch)) 
        fig_global = visualizer.create_global_chart(results)  
        img_bytes = pio.to_image(fig_global, format="png", width=1200, height=800)  
        img = Image(io.BytesIO(img_bytes), width=6*inch, height=4*inch)  
        story.append(img) 
        # Tabla resumen
        story.append(Spacer(1, 0.2*inch))
        data = [['Dimension', 'Puntuacion', 'Nivel']]
        for dim, score in results['dimensions'].items():
            nivel = 'Basico' if score < 33 else 'Medio' if score < 67 else 'Avanzado'
            data.append([dim[:35], f'{score:.1f}%', nivel])
        table = Table(data, colWidths=[4.5*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 11),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.lightgrey])
        ]))
        story.append(table)
        
        # Pagina 2: Graficos por dimension en grid 2x3
        story.append(PageBreak())
        story.append(Paragraph("Detalle por Dimension", self.styles["Heading2"]))
        story.append(Spacer(1, 0.2*inch))
        
        dims = list(results["dimensions"].keys())
        for i in range(0, len(dims), 2):
            row = []
            for j in range(2):
                if i+j < len(dims):
                    fig = visualizer.create_dimension_chart(results, dims[i+j])
                    img_bytes = pio.to_image(fig, format="png", width=800, height=600)
                    row.append(Image(io.BytesIO(img_bytes), width=3.5*inch, height=2.5*inch))
            if len(row) == 2:
                t = Table([row], colWidths=[3.7*inch, 3.7*inch])
                story.append(t)
            elif len(row) == 1:
                story.append(row[0])
            story.append(Spacer(1, 0.15*inch))
        
        doc.build(story)
        buffer.seek(0)  
        return buffer.getvalue() 
