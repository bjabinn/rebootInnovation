"""Visualizer module"""
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import io
matplotlib.use('Agg')


class Visualizer:
    """Clase para crear visualizaciones usando Plotly."""
    
    def create_global_chart(self, results):
        """Crea gráfico radar global."""
        dimensions = list(results['dimensions'].keys())
        values = list(results['dimensions'].values())
        dimensions_closed = dimensions + [dimensions[0]]
        values_closed = values + [values[0]]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=dimensions_closed,
            fill='toself',
            name='Puntuación',
            line=dict(color='rgb(0, 123, 255)', width=2),
            fillcolor='rgba(0, 123, 255, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickmode='linear', tick0=0, dtick=20),
                angularaxis=dict(showline=True, showgrid=True, gridcolor='lightgray')
            ),
            showlegend=False,
            title=dict(text="Evaluación Global", x=0.5, xanchor='center', font=dict(size=16)),
            height=500,
            margin=dict(l=80, r=80, t=100, b=80)
        )
        return fig
    
    def create_dimension_chart(self, results, dimension):
        """Crea gráfico radar por dimensión."""
        practices = list(results['detail'][dimension].keys())
        values = [results['detail'][dimension][p]['valor_evaluado'] for p in practices]
        practices_closed = practices + [practices[0]]
        values_closed = values + [values[0]]
        
        dimension_score = results['dimensions'][dimension]
        if dimension_score <= 33:
            title_color, level, line_color = '#dc3545', 'Básico', 'rgb(220, 53, 69)'
        elif dimension_score <= 67:
            title_color, level, line_color = '#ffc107', 'Medio', 'rgb(255, 193, 7)'
        else:
            title_color, level, line_color = '#28a745', 'Avanzado', 'rgb(40, 167, 69)'
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=practices_closed,
            fill='toself',
            line=dict(color=line_color, width=2),
            fillcolor=f'rgba{line_color[3:-1]}, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickmode='linear', tick0=0, dtick=25),
                angularaxis=dict(showline=True, showgrid=True, gridcolor='lightgray')
            ),
            showlegend=False,
            title=dict(text=f"{dimension}<br><sub>{dimension_score:.1f}% - {level}</sub>", 
                      x=0.5, xanchor='center', font=dict(size=14, color=title_color)),
            height=400,
            margin=dict(l=60, r=60, t=80, b=60)
        )
        return fig


class MatplotlibVisualizer:
    """Clase para crear visualizaciones usando matplotlib (para PDF)."""
    
    def create_global_chart_image(self, results, width=12, height=8):
        """Crea gráfico radar global y retorna bytes de la imagen PNG."""
        dimensions = list(results['dimensions'].keys())
        values = list(results['dimensions'].values())
        
        # Número de variables
        num_vars = len(dimensions)
        
        # Calcular ángulos
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        values_plot = values + [values[0]]
        angles += angles[:1]
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(width, height), subplot_kw=dict(projection='polar'))
        
        # Dibujar el gráfico
        ax.plot(angles, values_plot, 'o-', linewidth=2, color='#007bff', label='Puntuación')
        ax.fill(angles, values_plot, alpha=0.25, color='#007bff')
        
        # Configurar etiquetas
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimensions, size=10)
        
        # Configurar límites y grid
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 20, 40, 60, 80, 100])
        ax.set_yticklabels(['0', '20', '40', '60', '80', '100'], size=8)
        ax.grid(True, linestyle='--', alpha=0.5)
        
        # Título
        plt.title('Evaluación Global', size=16, pad=20, weight='bold')
        
        plt.tight_layout()
        
        # Guardar en buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf.getvalue()
    
    def create_dimension_chart_image(self, results, dimension, width=8, height=6):
        """Crea gráfico radar por dimensión y retorna bytes de la imagen PNG."""
        practices = list(results['detail'][dimension].keys())
        values = [results['detail'][dimension][p]['valor_evaluado'] for p in practices]
        
        # Número de variables
        num_vars = len(practices)
        
        # Calcular ángulos
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        values_plot = values + [values[0]]
        angles += angles[:1]
        
        # Determinar color según puntuación
        dimension_score = results['dimensions'][dimension]
        if dimension_score <= 33:
            color_hex, level = '#dc3545', 'Básico'
        elif dimension_score <= 67:
            color_hex, level = '#ffc107', 'Medio'
        else:
            color_hex, level = '#28a745', 'Avanzado'
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(width, height), subplot_kw=dict(projection='polar'))
        
        # Dibujar el gráfico
        ax.plot(angles, values_plot, 'o-', linewidth=2, color=color_hex)
        ax.fill(angles, values_plot, alpha=0.25, color=color_hex)
        
        # Configurar etiquetas (truncar si son muy largas)
        labels_short = [p[:30] + '...' if len(p) > 30 else p for p in practices]
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels_short, size=8)
        
        # Configurar límites y grid
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_yticklabels(['0', '25', '50', '75', '100'], size=7)
        ax.grid(True, linestyle='--', alpha=0.5)
        
        # Título con puntuación y nivel
        plt.title(f'{dimension}\n{dimension_score:.1f}% - {level}', 
                 size=12, pad=15, weight='bold', color=color_hex)
        
        plt.tight_layout()
        
        # Guardar en buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf.getvalue()
