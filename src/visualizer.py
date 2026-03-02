"""Visualizer module"""
import plotly.graph_objects as go


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
