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
        self.title_style = ParagraphStyle("CustomTitle", parent=self.styles["Heading1"], fontSize=20, textColor=colors.HexColor("#1f77b4"), spaceAfter=20, alignment=TA_CENTER, fontName="Helvetica-Bold")
