import pandas as pd
import numpy as np
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

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
    html.H1("🚇 Predicción de Afluencia en el Metro CDMX", className="text-center text-warning mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Mes (YYYY-MM):"),
            dcc.Dropdown(
                id='input_mes',
                options=[{'label': mes, 'value': mes} for mes in sorted(afluencia_df['Mes'].unique())],
                placeholder="Selecciona el mes"
            )
        ], width=6),

        dbc.Col([
            dbc.Label("Estación:"),
            dcc.Dropdown(
                id='input_estacion',
                options=[{'label': est.title(), 'value': est} for est in proporcion_df['Estacion'].unique()],
                placeholder="Selecciona una estación"
            )
        ], width=6),
    ]),

    html.Br(),
    html.Div(id='salida', className="fs-4 text-center text-light bg-dark p-3 rounded"),
    dcc.Graph(id='grafico_afluencia')
], style={'backgroundColor': '#000000', 'color': 'white', 'padding': '20px'})

# Callback con gráfica y predicción
@app.callback(
    Output('salida', 'children'),
    Output('grafico_afluencia', 'figure'),
    Input('input_mes', 'value'),
    Input('input_estacion', 'value')
)
def predecir_afluencia(mes, estacion):
    if not mes or not estacion:
        return "⛔ Por favor, completa ambos campos.", {}

    estacion = estacion.strip().lower()
    fila_mes = afluencia_df[afluencia_df['Mes'] == mes]
    fila_est = proporcion_df[proporcion_df['Estacion'] == estacion]

    if not fila_mes.empty and not fila_est.empty:
        total_mes = fila_mes['Pasajeros_Totales'].values[0]
        proporcion = fila_est['Proporcion_Promedio'].values[0]
        estimado = int(total_mes * proporcion)

        # Crear dataframe para gráfica
        historico = afluencia_df.copy()
        historico['Estimado'] = historico['Pasajeros_Totales'] * proporcion

        fig = px.line(
            historico, x='Mes', y='Estimado',
            title=f"Evolución estimada de afluencia en {estacion.title()}",
            markers=True,
            template="plotly_dark",
            line_shape="spline"
        )
        fig.update_traces(line=dict(color='orange', width=4))
        fig.update_layout(
            xaxis_title='Mes',
            yaxis_title='Pasajeros Estimados',
            font=dict(color='white'),
            plot_bgcolor='#111111',
            paper_bgcolor='#111111'
        )

        texto = f"📍 En {mes}, se estiman aproximadamente <strong>{estimado:,}</strong> pasajeros en <strong>{estacion.title()}</strong>."
        return texto, fig
    else:
        return "❌ No se encontró ese mes o estación en los datos.", {}

# Ejecutar local
if __name__ == '__main__':
    app.run_server(debug=True)
