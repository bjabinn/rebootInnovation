"""Data loader module"""
import pandas as pd
import os
from openpyxl import load_workbook


class DataLoader:
    """Clase para cargar y validar los datos de practicas desde CSV."""
    
    def __init__(self, file_path='data/template_evaluacion.csv'):
        self.file_path = file_path
    
    def load_practices(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"No se encontro el archivo: {self.file_path}")
        
        # skip_blank_lines=True ignora lineas vacias automaticamente
        df = pd.read_csv(self.file_path, skip_blank_lines=True)
        
        # Eliminar filas completamente vacias
        df = df.dropna(how='all')
        
        # Eliminar filas donde Practica esta vacia (ayuda a separar dimensiones visualmente)
        df = df.dropna(subset=['Practica'])
        
        # Resetear indices despues de eliminar filas
        df = df.reset_index(drop=True)
        
        required_columns = ['Dimension', 'Practica', 'Peso', 'Basico_Max', 'Medio_Max', 'Avanzado_Max']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Faltan las siguientes columnas: {', '.join(missing_columns)}")
        
        df = df.rename(columns={
            'Basico_Max': 'Limite_Basico',
            'Medio_Max': 'Limite_Medio',
            'Avanzado_Max': 'Limite_Avanzado'
        })
        
        try:
            df['Peso'] = pd.to_numeric(df['Peso'])
            df['Limite_Basico'] = pd.to_numeric(df['Limite_Basico'])
            df['Limite_Medio'] = pd.to_numeric(df['Limite_Medio'])
            df['Limite_Avanzado'] = pd.to_numeric(df['Limite_Avanzado'])
        except ValueError as e:
            raise ValueError(f"Error al convertir valores numericos: {str(e)}")
        
        return df
    
    @staticmethod
    def get_excel_sheets(excel_file):
        """
        Obtiene la lista de pestañas disponibles en un archivo Excel.
        
        Args:
            excel_file: Archivo Excel (BytesIO o ruta)
            
        Returns:
            Lista de nombres de pestañas
        """
        try:
            # Cargar el workbook
            wb = load_workbook(excel_file, read_only=True, data_only=True)
            sheet_names = wb.sheetnames
            wb.close()
            return sheet_names
        except Exception as e:
            raise ValueError(f"Error al leer pestañas del Excel: {str(e)}")
    
    @staticmethod
    def load_from_excel(excel_file, sheet_name):
        """
        Carga datos desde un archivo Excel siguiendo la estructura:
        - Columna B: Dimensión (desde fila 3)
        - Columna C: Práctica (desde fila 3)
        - Columna E: % Cumplimiento / Peso (desde fila 3)
        - Columna F: Básico Max (desde fila 3)
        - Columna G: Medio Max (desde fila 3)
        - Columna H: Avanzado Max (desde fila 3)
        
        El proceso termina al encontrar la primera celda vacía en la columna B.
        
        Args:
            excel_file: Archivo Excel (BytesIO o ruta)
            sheet_name: Nombre de la pestaña a leer
            
        Returns:
            DataFrame con los datos procesados
        """
        try:
            # Leer el Excel especificando la pestaña
            # Estructura del Excel:
            # - Fila 1: Vacía
            # - Fila 2: Cabecera
            # - Fila 3: Primer dato (índice 0 en pandas)
            # skiprows=1 salta solo la fila 1 (vacía)
            # Como usamos names=[...], la fila 2 (cabecera) también se ignora
            SKIP_ROWS = 1
            df = pd.read_excel(
                excel_file,
                sheet_name=sheet_name,
                skiprows=SKIP_ROWS,
                usecols="B,C,E,F,G,H,L",  # Columnas B, C, E, F, G, H, L
                names=['Dimension', 'Practica', 'Valor_Evaluado', 'Limite_Basico', 'Limite_Medio', 'Limite_Avanzado', 'Peso']
            )
            
            # IMPORTANTE: Guardar el número de fila original ANTES de cualquier filtrado
            # Con skiprows=1, saltamos la fila 1 (vacía), y la fila 2 (cabecera) se ignora por names=[]
            # Índice 0 de pandas = Fila 3 de Excel (primer dato)
            # Índice 1 de pandas = Fila 4 de Excel (segundo dato)
            # Fórmula: _excel_row = índice_pandas + SKIP_ROWS + 2
            # Ejemplo: índice 0 → 0 + 1 + 2 = 3 ✅
            df['_excel_row'] = df.index + SKIP_ROWS + 2
            
            # Buscar la primera fila donde la columna B (Dimensión) está vacía
            # Este es el criterio de parada: cuando encontramos una celda vacía, terminamos
            first_empty_idx = None
            for idx in df.index:
                dimension_value = df.loc[idx, 'Dimension']
                # Verificar si está vacío (NaN, None, o string vacío)
                if pd.isna(dimension_value) or str(dimension_value).strip() == '':
                    first_empty_idx = idx
                    break
            
            # Si encontramos una celda vacía, cortar el DataFrame hasta ahí (sin incluir esa fila)
            if first_empty_idx is not None:
                df = df.loc[:first_empty_idx-1].copy()
            
            # Resetear índices (pero mantenemos _excel_row)
            df = df.reset_index(drop=True)
            
            # Validación básica
            if len(df) == 0:
                raise ValueError("No se encontraron datos válidos en el Excel")
            
            # Convertir columnas numéricas
            numeric_columns = ['Peso', 'Limite_Basico', 'Limite_Medio', 'Limite_Avanzado']
            
            for col in numeric_columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception as e:
                    raise ValueError(f"Error al convertir columna '{col}' a numérico: {str(e)}")
            
            # Convertir Peso de formato decimal a porcentaje si es necesario
            # Si los valores están entre 0 y 1, multiplicar por 100
            if (df['Peso'] <= 1.0).all() and (df['Peso'] > 0).any():
                df['Peso'] = df['Peso'] * 100
            
            # Validar que no haya NaN en columnas numéricas después de conversión
            # Mensaje mejorado: mostrar cada fila UNA SOLA VEZ con las columnas que tienen error
            error_details = []
            seen_rows = set()
            
            for col in numeric_columns:
                nan_mask = df[col].isna()
                if nan_mask.any():
                    problem_rows = df[nan_mask].index.tolist()
                    for idx in problem_rows:
                        seen_rows.add(idx)
                    
                    # Mapear nombre de columna al nombre de columna Excel
                    col_map = {
                        'Peso': 'L',
                        'Limite_Basico': 'F',
                        'Limite_Medio': 'G',
                        'Limite_Avanzado': 'H'
                    }
                    error_details.append(col_map[col])
            
            if error_details:
                # Mostrar información de las filas problemáticas UNA SOLA VEZ
                row_info = []
                for idx in sorted(seen_rows):
                    dimension = df.loc[idx, 'Dimension']
                    practica = df.loc[idx, 'Practica']
                    excel_row = df.loc[idx, '_excel_row']
                    row_info.append(f"Fila {excel_row}:")
                    row_info.append(f"  - Columna B (Dimensión): '{dimension}'")
                    row_info.append(f"  - Columna C (Práctica): '{practica}'")
                    row_info.append(f"  - Columnas vacías o no numéricas: {', '.join(error_details)}")
                    row_info.append("")
                
                error_msg = "❌ Valores vacíos o no numéricos detectados:\n\n" + "\n".join(row_info)
                raise ValueError(error_msg)
            
            # Validar rangos
            if (df['Peso'] < 0).any() or (df['Peso'] > 100).any():
                raise ValueError("Los valores de Peso deben estar entre 0 y 100")
            
            if (df['Limite_Basico'] < 0).any() or (df['Limite_Basico'] > 100).any():
                raise ValueError("Los valores de Límite Básico deben estar entre 0 y 100")
            
            if (df['Limite_Medio'] < 0).any() or (df['Limite_Medio'] > 100).any():
                raise ValueError("Los valores de Límite Medio deben estar entre 0 y 100")
            
            if (df['Limite_Avanzado'] < 0).any() or (df['Limite_Avanzado'] > 100).any():
                raise ValueError("Los valores de Límite Avanzado deben estar entre 0 y 100")
            
            # Validar que Básico <= Medio < Avanzado (según nuevo criterio sin solapes)
            # Básico: 0 <= x < LímiteBasico
            # Medio: LímiteBasico <= x <= LímiteMedio
            # Avanzado: LímiteMedio < x <= LímiteAvanzado
            invalid_limits = (
                (df['Limite_Basico'] > df['Limite_Medio']) |
                (df['Limite_Medio'] >= df['Limite_Avanzado'])
            )
            if invalid_limits.any():
                problem_rows = df[invalid_limits]
                error_details = []
                for idx, row in problem_rows.iterrows():
                    excel_row = int(row['_excel_row'])
                    error_details.append(
                        f"Fila {excel_row} - {row['Practica']}:\n"
                        f"  Límite Básico (F): {row['Limite_Basico']}\n"
                        f"  Límite Medio (G): {row['Limite_Medio']}\n"
                        f"  Límite Avanzado (H): {row['Limite_Avanzado']}"
                    )
                raise ValueError(
                    f"❌ Los límites deben cumplir: Básico <= Medio < Avanzado\n\n"
                    f"Problemas encontrados:\n" + "\n\n".join(error_details)
                )
            
            # Validar que los pesos sumen 100 por dimensión
            peso_por_dimension = df.groupby('Dimension')['Peso'].sum()
            dimensiones_incorrectas = peso_por_dimension[abs(peso_por_dimension - 100) > 0.1]
            if len(dimensiones_incorrectas) > 0:
                # Crear mensaje detallado mostrando cada dimensión
                error_details = []
                for dimension, suma in dimensiones_incorrectas.items():
                    dim_practices = df[df['Dimension'] == dimension]
                    error_details.append(f"\n📊 Dimensión: {dimension}")
                    error_details.append(f"   Suma actual: {suma}% (debería ser 100%)")
                    error_details.append(f"   Prácticas:")
                    for idx, row in dim_practices.iterrows():
                        excel_row = int(row['_excel_row'])
                        error_details.append(f"      - Fila {excel_row}: {row['Practica']} → Peso: {row['Peso']}%")
                
                raise ValueError(
                    f"❌ Los pesos deben sumar 100% por dimensión.\n" + 
                    "\n".join(error_details) + 
                    f"\n\n💡 Sugerencia: Verifica que los valores en la columna L (Peso) sumen exactamente 100 por cada dimensión."
                )
            
            # Eliminar la columna auxiliar antes de devolver
            df = df.drop(columns=['_excel_row'])
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error al cargar datos desde Excel: {str(e)}")
