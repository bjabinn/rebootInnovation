"""PDF Generator""" 
from reportlab.lib.pagesizes import landscape, A4 
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak 
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch 
from reportlab.lib import colors 
from reportlab.lib.enums import TA_CENTER
import io 
from datetime import datetime
from src.visualizer import MatplotlibVisualizer


class PDFGenerator:  
    def __init__(self):  
        self.styles = getSampleStyleSheet()
        self.mpl_visualizer = MatplotlibVisualizer()
        
        # Estilo personalizado para la fecha
        self.date_style = ParagraphStyle(
            'CustomDate',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=10
        )
    
    def _header_footer(self, canvas, doc, team_name, fecha_hora):
        """Función para agregar encabezado y pie de página en página 2"""
        canvas.saveState()
        
        # Solo agregar en página 2 en adelante
        if canvas.getPageNumber() >= 2:
            # Encabezado izquierdo: nombre del proyecto
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(colors.HexColor('#666666'))
            canvas.drawString(15, landscape(A4)[1] - 15, f"Proyecto: {team_name}")
            
            # Encabezado derecho: fecha
            canvas.drawRightString(landscape(A4)[0] - 15, landscape(A4)[1] - 15, f"Fecha: {fecha_hora}")
            
            # Pie de página centro: número de página
            page_num = canvas.getPageNumber()
            canvas.drawCentredString(landscape(A4)[0] / 2.0, 10, f"Página {page_num}")
        
        canvas.restoreState()
    
    def generate_report(self, results, team_name, visualizer, df_practices):  
        buffer = io.BytesIO()  
        
        # Obtener fecha y hora una sola vez
        fecha_hora = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=landscape(A4), 
            rightMargin=15, 
            leftMargin=15, 
            topMargin=25, 
            bottomMargin=20
        )  
        story = [] 
        
        # Título
        title = Paragraph(
            f"Evaluacion Reboot - Innovacion - {team_name}", 
            self.styles["Title"]
        )  
        story.append(title)
        
        # Fecha y hora del informe
        date_para = Paragraph(
            f"Fecha del informe: {fecha_hora}",
            self.date_style
        )
        story.append(date_para)
        story.append(Spacer(1, 0.2*inch)) 
        
        # Gráfico global usando matplotlib (tamaño reducido)
        try:
            img_bytes = self.mpl_visualizer.create_global_chart_image(results, width=10, height=7)
            img = Image(io.BytesIO(img_bytes), width=5*inch, height=3.5*inch)  
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
        
        # Página 2: Gráficos por dimensión (5 gráficas: 3 arriba, 2 abajo)
        story.append(PageBreak())
        story.append(Paragraph("Detalle por Dimension", self.styles["Heading2"]))
        story.append(Spacer(1, 0.1*inch))
        
        dims = list(results["dimensions"].keys())
        
        # Primera fila: 3 gráficas (10% más grandes)
        first_row = []
        for i in range(min(3, len(dims))):
            try:
                img_bytes = self.mpl_visualizer.create_dimension_chart_image(
                    results, 
                    dims[i], 
                    width=7, 
                    height=5
                )
                first_row.append(Image(io.BytesIO(img_bytes), width=3.3*inch, height=2.42*inch))
            except Exception as e:
                error_text = Paragraph(f"Error en {dims[i]}: {str(e)}", self.styles["Normal"])
                story.append(error_text)
        
        if len(first_row) == 3:
            t = Table([first_row], colWidths=[3.4*inch, 3.4*inch, 3.4*inch])
            story.append(t)
            story.append(Spacer(1, 0.1*inch))
        
        # Segunda fila: 2 gráficas (10% más grandes)
        if len(dims) > 3:
            second_row = []
            for i in range(3, min(5, len(dims))):
                try:
                    img_bytes = self.mpl_visualizer.create_dimension_chart_image(
                        results, 
                        dims[i], 
                        width=7, 
                        height=5
                    )
                    second_row.append(Image(io.BytesIO(img_bytes), width=3.3*inch, height=2.42*inch))
                except Exception as e:
                    error_text = Paragraph(f"Error en {dims[i]}: {str(e)}", self.styles["Normal"])
                    story.append(error_text)
            
            if len(second_row) > 0:
                col_widths = [3.4*inch] * len(second_row)
                t = Table([second_row], colWidths=col_widths)
                story.append(t)
        
        # Construir el PDF con la función de encabezado/pie de página
        doc.build(story, onFirstPage=lambda c, d: self._header_footer(c, d, team_name, fecha_hora),
                  onLaterPages=lambda c, d: self._header_footer(c, d, team_name, fecha_hora))
        buffer.seek(0)  
        return buffer.getvalue()