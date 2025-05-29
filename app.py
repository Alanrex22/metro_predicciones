import pandas as pd
import numpy as np
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

# Leer las bases
afluencia_df = pd.read_csv("afluencia_mensual_predicha.csv")
proporcion_df = pd.read_csv("proporcion_estacion.csv")

# Preprocesamiento
afluencia_df['Mes'] = afluencia_df['Mes'].astype(str)
proporcion_df['Estacion'] = proporcion_df['Estacion'].str.lower()

# App Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Layout visual
app.layout = dbc.Container([
    html.Img(src='assets/logo_metro.png', style={'height': '80px'}),
    html.H1("🔮 Predicción de Afluencia en el Metro CDMX", className="text-center text-warning mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Mes (YYYY-MM):"),
            dcc.Input(id='input_mes', type='text', placeholder='2026-02', className='form-control')
        ], width=6),

        dbc.Col([
            dbc.Label("Estación:"),
            dcc.Input(id='input_estacion', type='text', placeholder='Ej. Balderas', className='form-control')
        ], width=6),
    ]),

    html.Br(),
    html.Div(id='salida', className="fs-4 text-center text-primary")
])

# Lógica del callback
@app.callback(
    Output('salida', 'children'),
    Input('input_mes', 'value'),
    Input('input_estacion', 'value')
)
def predecir_afluencia(mes, estacion):
    if not mes or not estacion:
        return "⛔ Por favor, completa ambos campos."

    estacion = estacion.strip().lower()
    fila_mes = afluencia_df[afluencia_df['Mes'] == mes]
    fila_est = proporcion_df[proporcion_df['Estacion'] == estacion]

    if not fila_mes.empty and not fila_est.empty:
        total_mes = fila_mes['Pasajeros_Totales'].values[0]
        proporcion = fila_est['Proporcion_Promedio'].values[0]
        estimado = int(total_mes * proporcion)
        return f"📍 En {mes}, se estiman aproximadamente {estimado:,} pasajeros en {estacion.title()}."
    else:
        return "❌ No se encontró ese mes o estación en los datos."

# Ejecutar servidor
if __name__ == '__main__':
    app.run_server(debug=True)
