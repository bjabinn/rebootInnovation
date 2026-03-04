"""Calculator module for team evaluation"""


class Calculator:
    """Clase para calcular las puntuaciones por dimension y practica."""
    
    def __init__(self, df_practices, evaluation_values):
        self.df_practices = df_practices
        self.evaluation_values = evaluation_values
    
    def calculate_all(self):
        results = {'dimensions': {}, 'detail': {}}
        
        for dimension in self.df_practices['Dimension'].unique():
            dim_practices = self.df_practices[self.df_practices['Dimension'] == dimension]
            dimension_score = 0
            detail_practices = {}
            
            for _, practice in dim_practices.iterrows():
                practice_name = practice['Practica']
                practice_value = self.evaluation_values.get(practice_name, 0)
                weight = practice['Peso']
                contribution = (weight * practice_value) / 100
                dimension_score += contribution
                
                # Criterio sin solapes:
                # Básico: 0 <= x < LímiteBasico
                # Medio: LímiteBasico <= x <= LímiteMedio
                # Avanzado: LímiteMedio < x <= LímiteAvanzado
                if practice_value < practice['Limite_Basico']:
                    level = 'Basico'
                elif practice_value <= practice['Limite_Medio']:
                    level = 'Medio'
                elif practice_value <= practice['Limite_Avanzado']:
                    level = 'Avanzado'
                else:
                    level = 'Excelente'
                
                detail_practices[practice_name] = {
                    'peso': weight,
                    'valor_evaluado': practice_value,
                    'contribucion': contribution,
                    'nivel': level
                }
            
            results['dimensions'][dimension] = dimension_score
            results['detail'][dimension] = detail_practices
        
        return results
