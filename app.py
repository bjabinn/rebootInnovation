import streamlit as st
import pandas as pd
from src.data_loader import DataLoader
from src.calculator import Calculator
from src.visualizer import Visualizer

# Configuración de la página
st.set_page_config(
    page_title="Evaluación de Equipos de Desarrollo",
    page_icon="📊",
    layout="wide"
)

# CSS para mejorar la impresión
st.markdown("""
    <style>
    @media print {
        /* Ocultar elementos de navegación al imprimir */
        header, footer, .stApp > header, [data-testid="stSidebar"] {
            display: none !important;
        }
        /* Asegurar que los gráficos se vean bien */
        .stPlotlyChart {
            page-break-inside: avoid;
        }
        /* Título para impresión */
        body::before {
            content: "Evaluación Reboot - Innovación";
            font-size: 24px;
            font-weight: bold;
            display: block;
            margin-bottom: 20px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.title("🚀 Evaluación Reboot - Innovación")

# Subtítulo con campo de texto para el nombre del equipo
col1, col2 = st.columns([1, 2])
with col1:
    st.markdown("### Evaluación de prácticas por dimensiones del equipo:")
with col2:
    team_name = st.text_input(
        "Nombre del equipo",
        placeholder="Introduce el nombre del equipo...",
        label_visibility="collapsed",
        key="team_name_input"
    )
    if team_name:
        st.session_state['team_name'] = team_name

st.markdown("---")

# Inicializar el cargador de datos
@st.cache_data
def load_data():
    loader = DataLoader()
    return loader.load_practices()

# Cargar datos
try:
    df_practices = load_data()
    
    # Barra lateral
    with st.sidebar:
        st.subheader("📁 Cargar datos personalizados")
        uploaded_file = st.file_uploader("Subir CSV", type=['csv'])
        if uploaded_file is not None:
            df_practices = pd.read_csv(uploaded_file)
            st.success("Archivo cargado correctamente")
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["📝 Evaluación", "📊 Resultados", "📋 Datos"])
    
    # TAB 1: EVALUACIÓN
    with tab1:
        st.header("Evaluación de Prácticas")
        st.markdown("Selecciona el nivel de cumplimiento (0-100%) para cada práctica:")
        
        # Crear formulario de evaluación
        evaluation_values = {}
        
        # Agrupar por dimensión
        dimensions = df_practices['Dimension'].unique()
        
        for dimension in dimensions:
            # Un único expander por dimensión (colapsado por defecto)
            with st.expander(f"### **{dimension}**", expanded=False):
                practices_dim = df_practices[df_practices['Dimension'] == dimension]
                
                cols = st.columns(2)
                for idx, (_, practice) in enumerate(practices_dim.iterrows()):
                    col_idx = idx % 2
                    with cols[col_idx]:
                        st.markdown(f"**{practice['Practica']}**")
                        st.caption(f"Peso: {practice['Peso']}%")
                        
                        value = st.slider(
                            f"Nivel de cumplimiento",
                            min_value=0,
                            max_value=100,
                            value=0,
                            step=5,
                            key=f"{dimension}_{practice['Practica']}",
                            label_visibility="collapsed"
                        )
                        evaluation_values[practice['Practica']] = value
                        
                        # Mostrar nivel alcanzado
                        if value <= practice['Limite_Basico']:
                            nivel = "🔴 Básico"
                        elif value <= practice['Limite_Medio']:
                            nivel = "🟡 Medio"
                        else:
                            nivel = "🟢 Avanzado"
                        st.caption(f"Nivel: {nivel}")
                
                st.markdown("---")
        
        # Botón para calcular
        if st.button("🔍 Calcular Resultados", type="primary", use_container_width=True):
            # Guardar valores en session_state
            st.session_state['evaluation_values'] = evaluation_values
            st.success("✅ Evaluación guardada. Ve a la pestaña 'Resultados' para ver los gráficos.")
    
    # TAB 2: RESULTADOS
    with tab2:
        if 'evaluation_values' not in st.session_state:
            st.info("👈 Por favor, completa la evaluación en la pestaña 'Evaluación' primero.")
        else:
            st.header("Resultados de la Evaluación")
            
            # Crear calculadora
            calculator = Calculator(df_practices, st.session_state['evaluation_values'])
            results = calculator.calculate_all()
            
            # Mostrar resumen en métricas
            st.subheader("📈 Resumen por Dimensión")
            
            cols = st.columns(len(results['dimensions']))
            for idx, (dim, score) in enumerate(results['dimensions'].items()):
                with cols[idx]:
                    st.metric(
                        label=dim,
                        value=f"{score:.1f}%",
                        delta=None
                    )
            
            st.markdown("---")
            
            # Gráficos
            visualizer = Visualizer()
            
            # Gráfico global
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("🌍 Vista Global")
                fig_global = visualizer.create_global_chart(results)
                st.plotly_chart(fig_global, use_container_width=True)
            
            with col2:
                st.subheader("📊 Puntuación Global")
                # Calcular puntuación global promedio
                global_score = sum(results['dimensions'].values()) / len(results['dimensions'])
                
                # Determinar nivel global
                if global_score < 33:
                    nivel_global = "🔴 Básico"
                    color = "red"
                elif global_score < 67:
                    nivel_global = "🟡 Medio"
                    color = "orange"
                else:
                    nivel_global = "🟢 Avanzado"
                    color = "green"
                
                st.markdown(f"### {global_score:.1f}%")
                st.markdown(f"### {nivel_global}")
                st.progress(global_score / 100)
                
                st.markdown("---")
                st.markdown("**Distribución:**")
                for dim, score in results['dimensions'].items():
                    st.markdown(f"- {dim}: {score:.1f}%")
            
            st.markdown("---")
            
            # Gráficos por dimensión
            st.subheader("📊 Detalle por Dimensión")
            
            dim_cols = st.columns(2)
            for idx, dimension in enumerate(results['dimensions'].keys()):
                col_idx = idx % 2
                with dim_cols[col_idx]:
                    with st.container():
                        fig_dim = visualizer.create_dimension_chart(results, dimension)
                        st.plotly_chart(fig_dim, use_container_width=True)
            
            # Tabla resumen
            st.markdown("---")
            st.subheader("📋 Tabla Resumen Detallada")
            
            # Crear DataFrame de resultados
            summary_data = []
            for dim, dim_result in results['detail'].items():
                for practice, practice_data in dim_result.items():
                    summary_data.append({
                        'Dimensión': dim,
                        'Práctica': practice,
                        'Peso (%)': practice_data['peso'],
                        'Valor Evaluado (%)': practice_data['valor_evaluado'],
                        'Contribución (%)': practice_data['contribucion'],
                        'Nivel': practice_data['nivel']
                    })
            
            df_summary = pd.DataFrame(summary_data)
            
            # Aplicar colores según nivel
            def highlight_level(row):
                if row['Nivel'] == 'Basico':
                    return ['background-color: #ffebee'] * len(row)
                elif row['Nivel'] == 'Medio':
                    return ['background-color: #fff9c4'] * len(row)
                else:
                    return ['background-color: #e8f5e9'] * len(row)
            
            st.dataframe(
                df_summary.style.apply(highlight_level, axis=1),
                use_container_width=True,
                hide_index=True
            )
            
            # Botones de descarga
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                csv = df_summary.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar Resultados (CSV)",
                    data=csv,
                    file_name="resultados_evaluacion.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_btn2:
                # Botón para imprimir en PDF
                if st.button("🖨️ Imprimir / Guardar PDF", use_container_width=True):
                    st.markdown("""
                        <script>
                        window.print();
                        </script>
                    """, unsafe_allow_html=True)
                    st.info("💡 Usa Ctrl+P o selecciona 'Guardar como PDF' en el diálogo de impresión")
    
    # TAB 3: DATOS
    with tab3:
        st.header("📋 Estructura de Datos")
        st.markdown("Vista de las prácticas y dimensiones configuradas:")
        
        # Mostrar datos agrupados
        for dimension in df_practices['Dimension'].unique():
            with st.expander(f"📌 {dimension}"):
                dim_data = df_practices[df_practices['Dimension'] == dimension]
                st.dataframe(
                    dim_data[['Practica', 'Peso', 'Limite_Basico', 'Limite_Medio', 'Limite_Avanzado']],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Verificar que los pesos sumen 100
                total_peso = dim_data['Peso'].sum()
                if abs(total_peso - 100) < 0.01:
                    st.success(f"✅ Los pesos suman {total_peso:.1f}%")
                else:
                    st.warning(f"⚠️ Los pesos suman {total_peso:.1f}% (deberían sumar 100%)")
        
        st.markdown("---")
        st.subheader("📄 Datos completos")
        st.dataframe(df_practices, use_container_width=True)
        
        # Información sobre el formato CSV
        st.markdown("---")
        st.subheader("ℹ️ Formato del CSV")
        st.markdown("""
        **Columnas requeridas:**
        - `Dimension`: Nombre de la dimensión (ej: "Estrategia y Gobernanza")
        - `Practica`: Nombre de la práctica o tarea
        - `Peso`: Peso de la práctica dentro de la dimensión (deben sumar 100% por dimensión)
        - `Limite_Basico`: Valor máximo para considerar nivel Básico
        - `Limite_Medio`: Valor máximo para considerar nivel Medio
        - `Limite_Avanzado`: Valor máximo (normalmente 100) para nivel Avanzado
        
        **Ejemplo:**
        ```
        Dimension,Practica,Peso,Limite_Basico,Limite_Medio,Limite_Avanzado
        Estrategia y Gobernanza,Definición de Objetivos,30,30,60,100
        ```
        """)

except FileNotFoundError:
    st.error("❌ No se encontró el archivo de datos. Por favor, asegúrate de que existe 'data/template_evaluacion.csv'")
    st.info("Puedes crear el archivo manualmente o usar el botón de la barra lateral para subir tu propio CSV.")
except Exception as e:
    st.error(f"❌ Error al cargar los datos: {str(e)}")
    st.exception(e)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p>📊 Sistema de Evaluación de Equipos de Desarrollo | Reboot Innovation</p>
    </div>
    """,
    unsafe_allow_html=True
)
