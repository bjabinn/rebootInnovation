"""Data loader module"""
import pandas as pd
import os


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
