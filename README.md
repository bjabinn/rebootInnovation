# Sistema de Evaluacion de Equipos

App Streamlit para evaluar equipos.

## Instalacion

pip install -r requirements.txt
streamlit run app.py

## Estructura

- app.py: App principal
- src/: Modulos Python
- data/: CSV con practicas

## Uso

1. Evaluacion: Ajusta sliders
2. Resultados: Ve graficos
3. Datos: Ver estructura

## Calculo

Score = Sum(Peso x Valor) / 100

## CSV Format

Puedes usar lineas en blanco para separar dimensiones visualmente.
El sistema las ignorara automaticamente.

```csv
Dimension,Practica,Peso,Basico_Max,Medio_Max,Avanzado_Max
Estrategia y Gobernanza,Roadmap tecnologico,30,30,60,100
Estrategia y Gobernanza,Gestion stakeholders,40,40,70,100

Adopcion,Onboarding equipos,25,30,65,100
Adopcion,Formacion continua,35,25,60,100
```

NOTA: Las lineas vacias y filas con "Practica" vacia seran ignoradas.
