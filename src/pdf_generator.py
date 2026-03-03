"""PDF Generator""" 
from reportlab.lib.pagesizes import landscape, A4 
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak 
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch 
from reportlab.lib import colors 
import io 
from datetime import datetime
from src.visualizer import MatplotlibVisualizer


class PDFGenerator:  
    def __init__(self):  
        self.styles = getSampleStyleSheet()
        self.mpl_visualizer = MatplotlibVisualizer()
    
    def generate_report(self, results, team_name, visualizer, df_practices):  
        buffer = io.BytesIO()  
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=landscape(A4), 
            rightMargin=30, 
            leftMargin=30, 
            topMargin=40, 
            bottomMargin=30
        )  
        story = [] 
        
        # Título
        title = Paragraph(
            f"Evaluacion Reboot - Innovacion - {team_name}", 
            self.styles["Title"]
        )  
        story.append(title)  
        story.append(Spacer(1, 0.3*inch)) 
        
        # Gráfico global usando matplotlib
        try:
            img_bytes = self.mpl_visualizer.create_global_chart_image(results, width=12, height=8)
            img = Image(io.BytesIO(img_bytes), width=6*inch, height=4*inch)  
            story.append(img)
        except Exception as e:
            error_text = Paragraph(
                f"Error al generar gráfico global: {str(e)}", 
                self.styles["Normal"]
            )
            story.append(error_text)
        
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
        
        # Página 2: Gráficos por dimensión en grid 2x2
        story.append(PageBreak())
        story.append(Paragraph("Detalle por Dimension", self.styles["Heading2"]))
        story.append(Spacer(1, 0.2*inch))
        
        dims = list(results["dimensions"].keys())
        for i in range(0, len(dims), 2):
            row = []
            for j in range(2):
                if i+j < len(dims):
                    try:
                        img_bytes = self.mpl_visualizer.create_dimension_chart_image(
                            results, 
                            dims[i+j], 
                            width=8, 
                            height=6
                        )
                        row.append(Image(io.BytesIO(img_bytes), width=3.5*inch, height=2.5*inch))
                    except Exception as e:
                        error_text = Paragraph(
                            f"Error en {dims[i+j]}: {str(e)}", 
                            self.styles["Normal"]
                        )
                        story.append(error_text)
            
            if len(row) == 2:
                t = Table([row], colWidths=[3.7*inch, 3.7*inch])
                story.append(t)
            elif len(row) == 1:
                story.append(row[0])
            story.append(Spacer(1, 0.15*inch))
        
        doc.build(story)
        buffer.seek(0)  
        return buffer.getvalue()