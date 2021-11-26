# Importamos las librerias mínimas necesarias
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash
#import dash_core_components as dcc
#import dash_html_components as html
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import logging
from plotly.subplots import make_subplots
import plotly.express as px
import base64
import plotly.io as pio

# naming a layout theme for future reference
pio.templates["google"] = go.layout.Template(
    layout_colorway=['#4285F4', '#DB4437', '#F4B400', '#0F9D58',
                     '#185ABC', '#B31412', '#EA8600', '#137333',
                     '#d2e3fc', '#ceead6']
)

# setting Google color palette as default
pio.templates.default = "google"

# Para este Dash, vamos a seleccionar un fichero de datos y realizar un dashboard descriptivo
# sobre un conjunto de datos

#df = pd.read_csv("StudentsPerformance.csv")
df = pd.read_parquet("partitioned/").drop(columns=['partition'])

app = dash.Dash()
server = app.server

#app.config.suppress_callback_exceptions = True
app.css.append_css({'external_url': '/resources/style.css'})
#app.server.static_folder = 'static'

logging.getLogger('werkzeug').setLevel(logging.INFO)

diccionario_terminos = {
    'Total Transferido'  :'amount',
    'Balance Old Origen' :'oldbalanceOrg',
    'Balance New Origen' :'newbalanceOrig',
    'Balance Old Destino':'oldbalanceDest',
    'Balance New Destino':'newbalanceDest',
    'Cambio en Origen'   :'cambioOrigen',
    'Cambio en Destino'  :'cambioDestino'
}
diccionario_color_tipos = {
    'CASH_OUT':'Con Fraude',
    'CASH_IN' :'Sin Fraude',
    'TRANSFER':'Con Fraude',
    'PAYMENT' :'Sin Fraude',
    'DEBIT'   :'Sin Fraude',
    None:'red'
}

#encoded_image = base64.b64encode(open('assets/search.svg', 'rb').read()).decode()

app.layout = html.Div([
    html.Div(
        [
            html.H1( # Primera fila
                children = [
                    'Detección de Fraudes'
                    #"""
                ],
                id = "titulo",
                style = {  # Aquí aplico todo lo que necesite de CSS
                    "text-align": "center", # Alineo el texto al centro
                    "font-size": "50px",
                    "-webkit-text-fill-color": "transparent",
                    "text-fill-color": "transparent",
                    "-webkit-background-clip": "text",
                    "background-clip": "text",
                    "background-image": "linear-gradient(90deg,#58d68d,#f4d03f,#ec7063)"
                }
            )
        ],
        style={
            "width":'600px',
            "margin":"auto",
        }
    ),
    html.Div(
        dcc.Tabs(id="tabs-styled-with-props", value='tab-1', children=[
            dcc.Tab(label='Exploratorio', value='tab-1'),
            dcc.Tab(label='Resultados modelo', value='tab-2'),
            dcc.Tab(label='Consumición del modelo', value='tab-3')
        ], colors={
            "primary": "#58d68d",
            #"background": "#f7dc6f",
        }),
        style={
            "font-weight": "bold",
            "font-size":"30px",
            "background-image": "linear-gradient(90deg,#58d68d,#f4d03f,#ec7063)",
            "color":"#323232",
        }
    ),
    html.Div(id='tabs-content-props', style={"width":"95%","margin":"auto"})
],
    style={
        "font-family":'"Century Gothic", CenturyGothic, Geneva, AppleGothic, sans-serif',
        "background-color": "#323232",
        "color":"white",
    }
)

@app.callback(Output('tabs-content-props', 'children'),
              Input('tabs-styled-with-props', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H2('Análisis exploratorio'),
            html.Div([
                html.H3(
                    children = [
                        "Naturaleza de las operaciones"
                    ],
                    id = "titulo_1",
                    style = {
                        "display": "block",
                        "text-align": "center"
                    }
                ),
                html.P("Seleccionar Distribución:"),
                dcc.RadioItems(
                    id='tipoBoxplot', 
                    options=[{'value': x, 'label': x} 
                            for x in ['Total Transferido', 'Balance Old Origen','Balance New Origen','Balance Old Destino','Balance New Destino','Cambio en Origen', 'Cambio en Destino']],
                    value='Total Transferido', 
                    labelStyle={'display': 'inline-block'}
                ),
                dcc.Graph(id="box-plot"),
            ],
            style={
                    "width": "50%",
                    "height": "800px",
                    "text-align": "center",
                    "display": "inline-block",
                    "float":"left",
                    #"border-style": "ridge",
                    #"border-color": "fuchsia"
                }
            ),
            
        ],
        style = {
            "width": "100%",
            "height": "1000px",
            "text-align": "center",
            "display": "inline-block"
        },
    )
    elif tab == 'tab-2':
        return html.Div([
            html.H3('dsad Resultados modelo')
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Esto es la Consumición del modelo')
        ])

# BOX PLOT
@app.callback(
    Output("box-plot", "figure"), 
    [Input("tipoBoxplot", "value")])
def generate_chart(x):
    data = df.sample(40000)
    data = data[data[diccionario_terminos[x]] != 0]
    fig = px.box(data, x=diccionario_terminos[x], y='type', color='isFraud', points="all", log_x=True, color_discrete_sequence=['#58d68d','#FFC300'],
                    labels={
                        "type": "Tipo de Transacción Realizada",
                        diccionario_terminos[x]: x,
                        "isFraud":"Presencia de Fraude",
                    }
                 )
    #fig.update(layout_showlegend=False)
    fig.update_layout(title='Boxplot Tipos de Transacciones', height=700, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font_color='white', 
                      #title_font_color='white',legend_font_color='white',
                      #legend_title_font_color='white',
                      )
    return fig

# OTROS

if __name__ == '__main__':
    app.run_server()
