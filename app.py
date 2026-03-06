import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import time
from src.data_loader import DataLoader
from src.calculator import Calculator
from src.visualizer import Visualizer
from src.pdf_generator import PDFGenerator

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
st.title("Evaluación Reboot - Innovación")

# CSS para el campo de texto con fondo gris
st.markdown("""
    <style>    
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 545px;
        max-width: 545px;
    }
    /* Estilo para el input de nombre de equipo */            
    div[data-testid="stTextInput"] input {
        background-color: #f0f2f6 !important;
        border: 1px solid #d0d0d0 !important;
    }
    div[data-testid="stTextInput"] input:focus {
        background-color: #e8eaf0 !important;
        border: 1px solid #4f8bf9 !important;
    }            
    </style>            
""", unsafe_allow_html=True)

# Subtítulo con nombre de equipo (basado en pestaña seleccionada)
col1, col2, col3 = st.columns([0.5, 2, 1.5])
with col1:
    st.markdown("### Equipo:")
with col2:
    # Mostrar el nombre de la pestaña seleccionada como nombre del equipo
    if 'sheet_selector' in st.session_state and st.session_state['sheet_selector']:
        team_name = st.session_state['sheet_selector']
        st.session_state['team_name'] = team_name
        st.markdown(f"### {team_name}")  # Color normal
    else:
        # Texto en gris cuando no hay datos cargados
        st.markdown("<h3 style='color: #999999; font-style: italic;'>Sin datos cargados</h3>", unsafe_allow_html=True)
with col3:
    pass  # Columna vacía para equilibrar

st.markdown("---")

# Cargar datos (solo desde Excel, no hay datos por defecto)
try:
    # Inicializar df_practices como None si no existe
    if 'df_practices' not in st.session_state:
        st.session_state['df_practices'] = None
    
    df_practices = st.session_state['df_practices']
    
    # Barra lateral
    with st.sidebar:
        # Mostrar estado actual
        if df_practices is None:
            st.info("👋 **Bienvenido**\n\nPara comenzar, sube un archivo Excel con la estructura de evaluación.")
        else:
            st.success(f"✅ **Datos cargados**\n\n{len(df_practices)} prácticas en {len(df_practices['Dimension'].unique())} dimensiones")
        
        st.markdown("---")
        
        # Sección de carga de datos
        st.subheader("📁 Cargar Excel")
        st.caption("Estructura: Col B (Dimensión), C (Práctica), E (Evaluación %), F-G-H (Límites), L (Peso %)")
        
        uploaded_excel = st.file_uploader("Selecciona archivo Excel", type=['xlsx', 'xls'], key="excel_uploader")
        
        if uploaded_excel is not None:
            try:
                # Guardar archivo en session_state
                if 'excel_file' not in st.session_state or st.session_state.get('excel_file_name') != uploaded_excel.name:
                    st.session_state['excel_file'] = BytesIO(uploaded_excel.getvalue())
                    st.session_state['excel_file_name'] = uploaded_excel.name
                    st.session_state['excel_sheets'] = None
                    st.session_state['selected_sheet'] = None
                
                # Obtener pestañas disponibles
                if st.session_state['excel_sheets'] is None:
                    st.session_state['excel_file'].seek(0)
                    sheets = DataLoader.get_excel_sheets(st.session_state['excel_file'])
                    st.session_state['excel_sheets'] = sheets
                
                # Selector de pestaña
                selected_sheet = st.selectbox(
                    "Selecciona la pestaña:",
                    options=st.session_state['excel_sheets'],
                    key="sheet_selector"
                )
                
                # Botón para cargar datos
                if st.button("📊 Cargar datos desde Excel", type="primary"):
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔵 BOTÓN PULSADO: Cargar datos desde Excel")
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📄 Pestaña seleccionada: {selected_sheet}")
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📂 Nombre archivo: {st.session_state.get('excel_file_name', 'N/A')}")
                    
                    st.session_state['excel_file'].seek(0)
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 Iniciando carga desde Excel...")
                    
                    df_practices = DataLoader.load_from_excel(st.session_state['excel_file'], selected_sheet)
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Excel cargado: {len(df_practices)} filas, {len(df_practices.columns)} columnas")
                    
                    st.session_state['df_practices'] = df_practices
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 💾 Datos guardados en session_state")
                    
                    # LOG: Verificar si existe columna Valor_Evaluado
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Columnas en df_practices: {df_practices.columns.tolist()}")
                    
                    # Si hay valores evaluados en el Excel, cargarlos en evaluation_values
                    if 'Valor_Evaluado' in df_practices.columns:
                        print("🔍 LOG: Columna 'Valor_Evaluado' encontrada")
                        evaluation_values = {}
                        for _, row in df_practices.iterrows():
                            # Convertir valor a porcentaje si está en decimal
                            valor = row['Valor_Evaluado']
                            if pd.notna(valor):
                                if valor <= 1.0:
                                    valor = valor * 100
                                evaluation_values[row['Practica']] = int(valor)
                                print(f"🔍 LOG: {row['Practica']} = {int(valor)}%")
                        
                        if evaluation_values:
                            st.session_state['loaded_values'] = evaluation_values
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 LOG: Total valores cargados: {len(evaluation_values)}")
                            
                            # SOLUCIÓN DEFINITIVA: Incrementar versión de datos para forzar recreación de sliders con keys nuevas
                            if 'data_version' not in st.session_state:
                                st.session_state['data_version'] = 0
                            st.session_state['data_version'] += 1
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 Versión de datos incrementada a: {st.session_state['data_version']}")
                            
                            # Limpiar keys de sliders y evaluación anteriores
                            keys_to_delete = []
                            dimensions = df_practices['Dimension'].unique().tolist()
                            
                            protected_keys = {
                                'excel_file', 'excel_file_name', 'excel_sheets', 
                                'selected_sheet', 'df_practices', 'loaded_values',
                                'team_name', 'team_name_input', 'excel_uploader', 'sheet_selector',
                                'data_version'
                            }
                            
                            for key in list(st.session_state.keys()):
                                if key not in protected_keys:
                                    if (any(dim in key for dim in dimensions) or 
                                        key.startswith('evaluation') or 
                                        key == 'show_results'):
                                        keys_to_delete.append(key)
                            
                            for key in keys_to_delete:
                                if key in st.session_state:
                                    del st.session_state[key]
                            
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🧹 LOG: {len(keys_to_delete)} keys antiguas eliminadas")
                    else:
                        print("⚠️ LOG: Columna 'Valor_Evaluado' NO encontrada")
                    
                    st.success(f"✅ Datos cargados correctamente desde la pestaña '{selected_sheet}'")
                    time.sleep(1.5)  # Mostrar mensaje durante 1.5 segundos antes de recargar
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error al procesar Excel: {str(e)}")
    
    # Solo mostrar tabs si hay datos cargados
    if df_practices is None:
        # Mensaje de bienvenida cuando no hay datos
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style='text-align: center; padding: 20px 20px;'>
                <h2>👋 Bienvenido a la Evaluación Reboot - Innovación</h2>
                <p style='font-size: 18px; color: #666; margin-top: 20px;'>
                    Para comenzar la evaluación, sube un archivo Excel desde la barra lateral.
                </p>
                <p style='font-size: 16px; color: #888; margin-top: 30px;'>
                    📊 <strong>Estructura del Excel:</strong><br>
                    • Columna B: Dimensión<br>
                    • Columna C: Práctica<br>
                    • Columna E: Evaluación (opcional)<br>
                    • Columnas F, G, H: Límites (Básico, Medio, Avanzado)<br>
                    • Columna L: Peso (%)<br>
                    • Datos desde fila 3
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Mostrar tabs normalmente cuando hay datos
        tab1, tab2, tab3 = st.tabs(["📝 Evaluación", "📊 Resultados", "📋 Datos"])
        
        # TAB 1: EVALUACIÓN
        with tab1:
            st.header("Evaluación de Prácticas por Dimensión")
            
            # Crear formulario de evaluación
            evaluation_values = {}
            
            # Agrupar por dimensión
            dimensions = df_practices['Dimension'].unique()
            
            for dimension in dimensions:
                # Un único expander por dimensión (colapsado por defecto)
                with st.expander(f"**{dimension}**", expanded=False):
                    practices_dim = df_practices[df_practices['Dimension'] == dimension]
                    
                    cols = st.columns(2)
                    for idx, (_, practice) in enumerate(practices_dim.iterrows()):
                        col_idx = idx % 2
                        with cols[col_idx]:
                            st.markdown(f"**{practice['Practica']}**")
                            st.caption(f"Peso: {practice['Peso']}%")
                            
                            # Determinar el valor inicial del slider
                            initial_value = 0
                            if 'loaded_values' in st.session_state and practice['Practica'] in st.session_state['loaded_values']:
                                initial_value = st.session_state['loaded_values'][practice['Practica']]
                                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 LOG Slider: {practice['Practica']} -> inicial={initial_value}")
                            # No loguear cuando no hay valor (reduce ruido en logs)
                            
                            # Usar data_version en la key para forzar recreación de widgets
                            data_ver = st.session_state.get('data_version', 0)
                            value = st.slider(
                                f"Nivel de cumplimiento",
                                min_value=0,
                                max_value=100,
                                value=initial_value,
                                step=5,
                                key=f"{dimension}_{practice['Practica']}_v{data_ver}",
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
            if st.button("🔍 Calcular Resultados", type="primary", width='stretch'):
                with st.spinner("⏳ Guardando evaluación..."):
                    # Guardar valores en session_state
                    st.session_state['evaluation_values'] = evaluation_values
                st.success("✅ Evaluación guardada correctamente")
                st.info("👉 **Ve a la pestaña 'Resultados' arriba para ver el análisis completo**")
    
        # TAB 2: RESULTADOS
        with tab2:
            if 'evaluation_values' not in st.session_state:
                st.info("👈 Por favor, completa la evaluación en la pestaña 'Evaluación' primero.")
            else:
                st.header("Resultados de la Evaluación")
                
                # Crear calculadora y visualizer con spinner
                with st.spinner("⏳ Calculando resultados y generando gráficos..."):
                    calculator = Calculator(df_practices, st.session_state['evaluation_values'])
                    results = calculator.calculate_all()
                    visualizer = Visualizer()
                
                # Mostrar resumen en métricas con botón de PDF
                col_title, col_pdf = st.columns([3, 1])
                with col_title:
                    st.subheader("📈 Resumen por Dimensión")
                with col_pdf:
                    # Botón de PDF en la parte superior
                    try:
                        pdf_gen = PDFGenerator()
                        pdf_bytes = pdf_gen.generate_report(results, st.session_state.get('team_name', 'Equipo'), visualizer, df_practices)
                        st.download_button(
                            label="🖨️ Descargar PDF",
                            data=pdf_bytes,
                            file_name=f"evaluacion_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                            type="primary",
                            width='stretch'
                        )
                    except Exception as e:
                        st.error(f"Error PDF: {str(e)}")
                
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
                
                # Crear DataFrame de resultados con formato
                summary_data = []
                for dim, dim_result in results['detail'].items():
                    for practice, practice_data in dim_result.items():
                        summary_data.append({
                            'Dimensión': dim,
                            'Práctica': practice,
                            'Peso (%)': f"{practice_data['peso']:.2f}",
                            'Valor Evaluado (%)': f"{practice_data['valor_evaluado']:.0f}",
                            'Contribución (%)': f"{practice_data['contribucion']:.2f}"
                        })
                
                df_summary = pd.DataFrame(summary_data)
                
                # Aplicar estilos: centrar columnas numéricas con CSS
                styled_df = df_summary.style.set_properties(**{
                    'text-align': 'center'
                }, subset=['Peso (%)', 'Valor Evaluado (%)', 'Contribución (%)'])\
                .set_table_styles([
                    {'selector': 'th.col1, th.col2, th.col3', 'props': [('text-align', 'center')]}
                ])
                
                st.dataframe(
                    styled_df,
                    width="stretch",
                    hide_index=True
                )
                
                # Botón de descarga CSV
                csv = df_summary.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar Tabla Resumen (CSV)",
                    data=csv,
                    file_name="resultados_evaluacion.csv",
                    mime="text/csv",
                    width='stretch'
                )
    
        # TAB 3: DATOS
        with tab3:
            st.header("📋 Estructura de Datos")
            st.markdown("Vista de las prácticas y dimensiones cargadas desde el Excel:")
            
            # Mostrar datos agrupados
            for dimension in df_practices['Dimension'].unique():
                with st.expander(f"📌 {dimension}"):
                    dim_data = df_practices[df_practices['Dimension'] == dimension]
                    st.dataframe(
                        dim_data[['Practica', 'Peso', 'Limite_Basico', 'Limite_Medio', 'Limite_Avanzado']],
                        width="stretch",
                        hide_index=True
                    )
                    
                    total_peso = dim_data['Peso'].sum()
                    if abs(total_peso - 100) < 0.01:
                        st.success(f"✅ Los pesos suman {total_peso:.1f}%")
                    else:
                        st.warning(f"⚠️ Los pesos suman {total_peso:.1f}% (deberían sumar 100%)")
            
            st.markdown("---")
            st.subheader("📄 Datos completos")
            st.dataframe(df_practices, width="stretch")
            
            st.markdown("---")
            st.subheader("ℹ️ Formato del Excel")
            st.markdown("""
            **Estructura requerida:**
            - Columna B: Dimensión
            - Columna C: Práctica
            - Columna E: Evaluación % (opcional - si existe, se carga automáticamente)
            - Columna F: Límite Básico
            - Columna G: Límite Medio
            - Columna H: Límite Avanzado
            - Columna L: Peso %
            - Datos desde fila 3
            
            💡 **Nota:** El Excel es la única fuente de datos. No se requiere CSV.
            """)

except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.info("💡 Intenta cargar un archivo Excel desde la barra lateral.")

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'><p>📊 Sistema de Evaluación | Reboot Innovation</p></div>", unsafe_allow_html=True)
