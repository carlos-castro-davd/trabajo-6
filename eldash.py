# Importamos las librerias mínimas necesarias
import os
from os import name
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
#import base64
import plotly.io as pio
from joblib import load
import subprocess
import sys
subprocess.call([sys.executable, '-m', 'pip', 'install', '{0}=={1}'.format("pyarrow", "6.0.1")])

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
print("Cargando parquet...")
#df = pd.read_parquet("partitioned/").drop(columns=['partition'])
df = pd.read_csv("partitioned/mini.csv").drop(columns=['partition'])
print("Parquet cargado!!")

app = dash.Dash()
server = app.server
#app.config.suppress_callback_exceptions = True
app.css.append_css({'external_url': '/assets/style.css'})
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

diccionario_resultdos = {
    'modelo_1':{
        'nombre':'Isolation Forest',
        'TP':355,
        'FP':42156,
        'TN':457188,
        'FN':301,
    },
    'modelo_2':{
        'nombre':'SM + Logistic Regression',
        'TP':2055,
        'FP':27277,
        'TN':663260,
        'FN':11,
    },
    'modelo_3':{
        'nombre':'PCA + Gradient Boosting Classifier',
        'TP':427,
        'FP':364,
        'TN':951411,
        'FN':399,
    },
    'modelo_4':{
        'nombre':'XGBoost',
        'TP':688,
        'FP':11,
        'TN':951764,
        'FN':138,
    },
    'modelo_5':{
        'nombre':'SM + Random Forest',
        'TP':814,
        'FP':89,
        'TN':951686,
        'FN':12,
    }
}

averages = (pd.DataFrame([[1.781970e+05,8.328287e+05,855970.228109,1.101421e+06,1.224926e+06],
                         [1.467967e+06,1.649668e+06,192392.631836,5.442496e+05,1.279708e+06]
                        ], columns=['amount','oldbalanceOrg','newbalanceOrig','oldbalanceDest','newbalanceDest'])
                        .transpose()
                        .reset_index()
                        .rename(
                            columns={0:"notFraud",1:"isFraud"}
                        )
           )

df_m = pd.DataFrame(diccionario_resultdos).transpose()
df_m['accuracy']  = (df_m.TP + df_m.TN)/(df_m.TP + df_m.TN + df_m.FP + df_m.FN)
df_m['recall']    = (df_m.TP)/(df_m.TP + df_m.FN)
df_m['precision'] = (df_m.TP)/(df_m.TP + df_m.FP)

common_dropdown_style = {
                            'color':'#121212',
                            'background-color': '#FFFFFF',
                            #"background-image": "linear-gradient(90deg,#82e0aa,#f9e79f)",
                            'width':'200px',
                            'margin':'auto',
                            'margin-bottom':'10px',
                            'margin-top':'5px',
                            "font-size": "20px",
                            "border-radius":"0px",
                            "border-width": "0px 0px 4px 0px",
                            "border-color": "#58d68d",
                            "font-weight": "bold",
                            #"padding-top":"10px"
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
            dcc.Tab(label='Análisis exploratorio', value='tab-1'),
            dcc.Tab(label='Modelos', value='tab-2'),
            dcc.Tab(label='Predicción', value='tab-3')
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
                dcc.Dropdown(
                    id='tipoBoxplot', 
                    options=[{'value': x, 'label': x} 
                            for x in ['Total Transferido', 'Balance Old Origen','Balance New Origen','Balance Old Destino','Balance New Destino','Cambio en Origen', 'Cambio en Destino']],
                    value='Total Transferido', 
                    style={
                        'color':'#121212',
                        'background-color': '#FFFFFF',
                        #"background-image": "linear-gradient(90deg,#82e0aa,#f9e79f)",
                        'width':'400px',
                        'margin':'auto',
                        'margin-bottom':'10px',
                        'margin-top':'10px',
                        "font-size": "20px",
                        "border-radius":"0px",
                        "border-width": "0px 0px 4px 0px",
                        "border-color": "#58d68d",
                        "font-weight": "bold",
                        #"padding-top":"10px"
                    }
                ),
                dcc.Graph(id="box-plot", style={'display':'none'}),
            ],
            style={
                    "width": "50%",
                    "height": "950px",
                    "text-align": "center",
                    "display": "inline-block",
                    "float":"left",
                    #"border-style": "ridge",
                    #"border-color": "fuchsia"
                }
            ),
            html.Div([
                html.H3(
                    children = [
                        "Relación entre cuentas"
                    ],
                    id = "titulo_2",
                    style = {
                        "display": "block",
                        "text-align": "center"
                    }
                ),
                html.P("Seleccionar Tipo de Operación:"),
                dcc.RadioItems(
                    id='tipoOperacion', 
                    options=[{'value': x, 'label': x} 
                            for x in df.type.unique().tolist()[:6]],
                    value='TRANSFER', 
                    labelStyle={'display': 'inline-block'}
                ),
                html.Div([
                    html.H3(
                        id="percentage",
                        style={'display': 'none'}
                    )
                    ],
                    style={
                        "width":"400px",
                        "height":"50px",
                        "margin":"auto"
                    }
                ),
                dcc.Graph(id="exploratory-scatters", style={'display':'none'}),
            ],
            style={
                    "width": "50%",
                    "height": "950px",
                    "text-align": "center",
                    "display": "inline-block",
                    "float":"left",
                    #"border-style": "ridge",
                    #"border-color": "fuchsia"
                }
            ),
            html.Div(
                children=[' '],
                style={
                    "width":"100%",
                    "height":"50px",
                    "display":"inline-block"
                }
            ),
            html.Div([
                html.H3(
                    children = [
                        "Tiempo de Transacciones"
                    ],
                    id = "titulo_3",
                    style = {
                        "display": "block",
                        "text-align": "center"
                    }
                ),
                html.Div([
                    html.P("Seleccionar Tipos de Operaciones:"),
                    dcc.Checklist(
                        id="time-scatters-checklist",
                        options=[
                            {'label': 'PAYMENT', 'value': 'PAYMENT'},
                            {'label': 'TRANSFER', 'value': 'TRANSFER'},
                            {'label': 'DEBIT', 'value': 'DEBIT'},
                            {'label': 'CASH_OUT', 'value': 'CASH_OUT'},
                            {'label': 'CASH_IN', 'value': 'CASH_IN'}
                        ],
                        value=['TRANSFER', 'CASH_OUT']
                    ),
                    ],
                    style={
                        "width":"50%",
                        "display":"inline-block"
                    }
                ),
                html.Div([
                    html.P("Seleccionar Regular o Fraude:"),
                    dcc.Checklist(
                        id="time-scatters-fraud",
                        options=[
                            {'label': 'Fraude', 'value': 1},
                            {'label': 'Regular', 'value': 0},
                        ],
                        value=[0]
                    ),
                    ],
                    style={
                        "width":"50%",
                        "display":"inline-block"
                    }
                ),
                dcc.Graph(id="time-scatters", style={'display':'none'}),
            ],
            style={
                    "width": "50%",
                    "height": "950px",
                    "text-align": "center",
                    "display": "inline-block",
                    "float":"left",
                    #"border-style": "ridge",
                    #"border-color": "fuchsia"
                }
            ),
            html.Div([
                html.H3(
                    children = [
                        "Distribuciones según Tipología y Estado Fraudulento"
                    ],
                    id = "titulo_4",
                    style = {
                        "display": "block",
                        "text-align": "center"
                    }
                ),
                html.Div([
                    html.P("Seleccionar Tipos de Operaciones:"),
                    dcc.Checklist(
                        id="histogram-checklist",
                        options=[
                            {'label': 'TRANSFER', 'value': 'TRANSFER'},
                            {'label': 'CASH_OUT', 'value': 'CASH_OUT'}
                        ],
                        value=['TRANSFER']
                    ),
                    ],
                    style={
                        "width":"100%",
                        "display":"inline-block"
                    }
                ),
                html.P("Rango de valores:"),
                dcc.RangeSlider(
                    id='hist-amount-slider',
                    min=df.amount.min(),
                    max=df.amount.max(),
                    step=10000,
                    marks={
                        0: {'label': '0', 'style': {'color': '#58d68d'}},
                        5000000: {'label': '5M', 'style': {'color': '#f7dc6f'}},
                        10000000: {'label': '10M', 'style': {'color': '#f5b041'}},
                        30000000: {'label': '30M', 'style': {'color': ' #dc7633'}},
                        70000000: {'label': '70M', 'style': {'color': '#ec7063'}}
                    },
                    value=[100, 20000000]
                ),
                dcc.Graph(id="histogram-fraud", style={'display':'none'}),
            ],
            style={
                    "width": "50%",
                    "height": "950px",
                    "text-align": "center",
                    "display": "inline-block",
                    "float":"left",
                    #"border-style": "ridge",
                    #"border-color": "fuchsia"
                }
            ),
            html.Div(
                children=[' '],
                style={
                    "height":"100px",
                    "display":"block"
                }
            ),
            html.H3(
                '© Juan Blazquez & Juan Sánchez-Blanco',
                style={
                    "text-align":"right",
                }
            )
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
                #html.H3('Resultados de los modelos entrenados'),
                html.Div([
                    dcc.Dropdown(
                        id='selector-modelo', 
                        options=[
                            {'value': "modelo_1", 'label': "Isolation Forest"},
                            {'value': "modelo_2", 'label': "Regresión Logística"},
                            {'value': "modelo_3", 'label': "Gradient Boosting Classifier"},
                            {'value': "modelo_4", 'label': "XGBoost"},
                            {'value': "modelo_5", 'label': "Random Forest Classifier"}
                        ],
                        value='modelo_1', 
                        style={
                            'color':'#121212',
                            'background-color': '#FFFFFF',
                            #"background-image": "linear-gradient(90deg,#82e0aa,#f9e79f)",
                            'width':'600px',
                            'margin':'auto',
                            'margin-bottom':'50px',
                            'margin-top':'50px',
                            "font-size": "30px",
                            "border-radius":"0px",
                            "border-width": "0px 0px 4px 0px",
                            "border-color": "#58d68d",
                            "font-weight": "bold",
                            #"padding-top":"10px"
                        }
                    ),
                ], style={"margin-bottom":"40px"}),
                html.Div([
                    html.Div([
                                dcc.Graph(id="matriz-confu", style={'display':'none'}),
                            ],
                            style={
                                "width":"50%",
                                "display":"inline-block"
                            }
                        ),
                    html.Div([
                        html.Div(["Accuracy: 99.9861 %"],
                            id = "accuracy-label",
                            style={'display':'none'}
                        ),
                        html.Div(["Precision: 90.1439 %"],
                            id="prec-label",
                            style={'display':'none'}
                        ),
                        html.Div(["Recall: 98.5472 %"],
                            id="recall-label",
                            style={'display':'none'}
                        ),
                        ],
                        style={
                            "width":"50%",
                            "margin":"auto",
                            "font-weight": "bold",
                            "margin-bottom":"40px",
                            "display":"inline-block",
                            "vertical-align":"middle",
                            "margin-top": "-470px",
                        }
                    ),
                ],style={
                    "width":"80%",
                    "margin":"auto"
                }),
                html.Div([
                    html.Div([
                            dcc.Graph(id="bar-chart1", style={'display':'none'}),
                            dcc.Graph(id="bar-chart2", style={'display':'none'}),
                            dcc.Graph(id="bar-chart3", style={'display':'none'}),
                        ],
                        style={
                            "width":"100%",
                            "display":"inline-block"
                        }
                    )
                ], style={"width":"95%"}),
                html.Div(
                    children=[' '],
                    style={
                        "height":"100px",
                        "display":"block"
                    }
                ),
                html.H3(
                    '© Juan Blazquez & Juan Sánchez-Blanco',
                    style={
                        "text-align":"right",
                    }
                )
            ],
            style = {
                "width": "100%",
                "height": "1000px",
                "text-align": "center",
                "display": "inline-block",
                "margin-bottom":"200px",
            },
        )
    elif tab == 'tab-3':
            return html.Div([
                html.H2('Predicción de Fraude - Random Forest Classifier'),
                html.Div([
                        html.Div(
                            children=[
                                html.P("Tipo de Operación:", style={"font-size":"20px"}),
                                dcc.Dropdown(
                                    id='input_tipo_operacion', 
                                    options=[
                                            {'value': "PAYMENT",  'label': "Payment"}, 
                                            {'value': "CASH_IN",  'label': "Cash In"},
                                            {'value': "CASH_OUT", 'label': "Cash Out"},
                                            {'value': "TRANSFER", 'label': "Transfer"},
                                            {'value': "DEBIT",    'label': "Debit"}
                                        ],
                                    value="PAYMENT", 
                                    style=common_dropdown_style
                                    #labelStyle={'display': 'block'}
                                ),
                                html.P("Step:", style={"font-size":"20px"}),
                                dcc.Slider(
                                    id='step-slider',
                                    min=1,
                                    max=750,
                                    step=1,
                                    marks={
                                        0: '0',
                                        150: '150',
                                        300: '300',
                                        450: '450',
                                        600: '600',
                                        750: '750',
                                    },
                                    value=250,
                                ),
                                html.Div(id='step-output-container'),

                                html.P("Amount:", style={"font-size":"20px"}),
                                dcc.Input(
                                    id="input_amount",
                                    type="number",
                                    min=0,
                                    max=10e7,
                                    placeholder="$ Amount",
                                    value="10000000",
                                    style=common_dropdown_style
                                ),
                                html.Div(['Valor máximo: 100M'],id='amount-output-container', style={"color":"#878787"}),

                                html.P("Old balance origen:", style={"font-size":"20px"}),
                                dcc.Input(
                                    id="input_oldbalanceorigen",
                                    type="number",
                                    min=0,
                                    max=6e7,
                                    placeholder="$ Balance",
                                    value="10000000",
                                    style=common_dropdown_style
                                ),
                                html.Div(['Valor máximo: 60M'],id='oldbalanceorigen-output-container', style={"color":"#878787"}),

                                html.P("New balance origen:", style={"font-size":"20px"}),
                                dcc.Input(
                                    id="input_newbalanceorigen",
                                    type="number",
                                    min=0,
                                    max=5e7,
                                    placeholder="$ Balance",
                                    value="8000000",
                                    style=common_dropdown_style
                                ),
                                html.Div(['Valor máximo: 50M'],id='newbalanceorigen-output-container', style={"color":"#878787"}),

                                html.P("Old balance destino:", style={"font-size":"20px"}),
                                dcc.Input(
                                    id="input_oldbalancedestino",
                                    type="number",
                                    min=0,
                                    max=4e8,
                                    placeholder="$ Balance",
                                    value="100000",
                                    style=common_dropdown_style
                                ),
                                html.Div(['Valor máximo: 400M'],id='oldbalancedestino-output-container', style={"color":"#878787"}),

                                html.P("New balance destino:", style={"font-size":"20px"}),
                                dcc.Input(
                                    id="input_newbalancedestino",
                                    type="number",
                                    min=0,
                                    max=4e8,
                                    placeholder="$ Balance",
                                    value="2100000",
                                    style=common_dropdown_style
                                ),
                                html.Div(['Valor máximo: 400M'],id='newbalancedestino-output-container', style={"color":"#878787"}),

                                html.P("Flag de Fraude:", style={"font-size":"20px"}),
                                dcc.RadioItems(
                                    id='input_flag_fraude', 
                                    options=[{'value': 0, 'label': "False"}, {'value': 1, 'label': "True"}],
                                    value=0, 
                                    labelStyle={'display': 'inline-block'}
                                ),
                                
                            ],
                            style={
                                "display":"inline-block",
                                "float":"left",
                                "width":"30%",
                            }
                        ),
                        html.Div(
                            children=[
                                html.Div(" ", id="modelo_output"),
                                html.Div(" ", id="modelo_res"),
                                html.Div(" ", id="modelo_prob"),
                                html.Div(
                                    children=[
                                        dcc.Graph(id="polar-chart1", style={'display':'none'}),
                                        dcc.Graph(id="polar-chart2", style={'display':'none'}),
                                        dcc.Graph(id="polar-chart3", style={'display':'none'}),
                                    ],
                                    style={
                                        "display":"inline-block",
                                        "float":"left",
                                        "margin-top":"50px",
                                        "width":"100%",
                                    }
                                )
                            ],
                            id="modelo_block",
                            style={
                                "display":"inline-block",
                                "float":"left",
                                "margin-top":"100px",
                                "width":"70%",
                            }
                        )
                    ],
                    style={
                        "display":"block",
                        "width":"95%"
                    }
                )
            ],
            style = {
                "width": "100%",
                "height": "1000px",
                "text-align": "center",
                "display": "inline-block",
            },
        )

# POLAR CALLBACK
# MODEL CALLBACK
@app.callback(
    Output('polar-chart1', 'figure'),
    Output('polar-chart1', 'style'),
    Output('polar-chart2', 'figure'),
    Output('polar-chart2', 'style'),
    [
        Input('input_amount', 'value'),
        Input('input_oldbalanceorigen', 'value'),
        Input('input_newbalanceorigen', 'value'),
        Input('input_oldbalancedestino', 'value'),
        Input('input_newbalancedestino', 'value')
    ])
def plot_polar_charts(amount,oldborig,newborig,oldbdest,newbdest):
    fig1 = go.Figure(data=[go.Scatterpolar(
                name="Legal",
                mode = "lines",
                r = averages["notFraud"],
                theta = ['Amount','Old Balance Origen','New Balance Origen','Old Balance Destino', 'New Balance Destino'],
                fill = "toself",
                fillcolor = "#58d68d",
                marker_color="#fad7a0",
                marker_line_color="#f39c12",
                opacity = 0.4,
            ),
            go.Scatterpolar(
                name="Actual",
                mode = "lines",
                r = [int(amount)+1,int(oldborig)+1,int(newborig)+1,int(oldbdest)+1,int(newbdest)+1],
                theta = ['Amount','Old Balance Origen','New Balance Origen','Old Balance Destino', 'New Balance Destino'],
                fill = "toself",
                fillcolor = "#f4d03f",
                marker_color="#fad7a0",
                marker_line_color="#f39c12",
                opacity = 0.4,
            )
            ])
    fig1.update_layout(title=f'Spider Plot Media de No Fraude', height=500, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font_color='white', polar = dict(radialaxis_type = "log")
                      )
    fig1.update_traces(line_color = "#323232")
    fig1.update_polars(bgcolor='rgba(0,0,0,0)')
    fig2 = go.Figure(data=[go.Scatterpolar(
                name="Fraude",
                mode = "lines",
                r = averages["isFraud"],
                theta = ['Amount','Old Balance Origen','New Balance Origen','Old Balance Destino', 'New Balance Destino'],
                fill = "toself",
                fillcolor = "#ec7063",
                marker_color="#f5b7b1",
                marker_line_color="#ec7063",
                opacity = 0.4,
            ),
            go.Scatterpolar(
                name="Actual",
                mode = "lines",
                r = [int(amount)+1,int(oldborig)+1,int(newborig)+1,int(oldbdest)+1,int(newbdest)+1],
                theta = ['Amount','Old Balance Origen','New Balance Origen','Old Balance Destino', 'New Balance Destino'],
                fill = "toself",
                fillcolor = "#f4d03f",
                marker_color="#fad7a0",
                marker_line_color="#f39c12",
                opacity = 0.4,
            )])
    fig2.update_layout(title=f'Spider Plot Media de Fraude', height=500, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font_color='white', polar = dict(radialaxis_type = "log")
                      )
    fig2.update_traces(line_color = "#323232")
    fig2.update_polars(bgcolor='rgba(0,0,0,0)')
    
    unified_style = {
        "display":"inline-block",
        "float":"left",
        "width":"50%"
    }
    return fig1,unified_style, fig2,unified_style

# MODEL CALLBACK
@app.callback(
    Output('modelo_output', 'children'),
    Output('modelo_output', 'style'),
    Output('modelo_res', 'children'),
    Output('modelo_res',    'style'),    
    Output('modelo_prob', 'children'),
    Output('modelo_prob',    'style'),
    #Output('modelo_block',  'style')
    [
        Input('input_tipo_operacion', 'value'),
        Input('step-slider', 'value'),
        Input('input_amount', 'value'),
        Input('input_oldbalanceorigen', 'value'),
        Input('input_newbalanceorigen', 'value'),
        Input('input_oldbalancedestino', 'value'),
        Input('input_newbalancedestino', 'value'),
        Input('input_flag_fraude', 'value')
    ])
def prediccion_modelos(operacion,step,amount,oldborig,newborig,oldbdest,newbdest,flag):
    newstyle={
        "display":"block",
        "width":"30%",
        "margin":"auto",
        "text-align":"center",
        "font-size": "80px",
        "-webkit-text-fill-color": "transparent",
        "text-fill-color": "transparent",
        "-webkit-background-clip": "text",
        "background-clip": "text",
        "font-weight": "bold",
    }
    text_style = {
        "display":"block",
        "width":"80%",
        "font-size": "40px",
        "margin":"auto",
        "color":"#878787"
    }
    block_style = {
        "display":"inline-block",
        "width":"70%",
        "vertical-align":"top",
        "height":"500px",
    }
    modelo = load('random_forest_sm_final.joblib')

    df_pred=pd.DataFrame(index=range(1))
    df_pred['step']=int(step)
    df_pred['amount']=float(amount)
    df_pred['oldbalanceOrg']=float(oldborig)
    df_pred['newbalanceOrig']=float(newborig)
    df_pred['oldbalanceDest']=float(oldbdest)
    df_pred['newbalanceDest']=float(newbdest)
    df_pred['isFlaggedFraud']=int(flag)
    df_pred['CASH_IN']=0
    df_pred['CASH_OUT']=0
    df_pred['DEBIT']=0
    df_pred['PAYMENT']=0
    df_pred['TRANSFER']=0
    df_pred['diffOrigen'] = df_pred['newbalanceOrig'] - df_pred['oldbalanceOrg']
    df_pred['diffDestino'] = df_pred['newbalanceDest'] - df_pred['oldbalanceDest']
    df_pred['cambioOrigen'] = (df_pred['diffOrigen'] + 0.01)/(df_pred['oldbalanceOrg'] + 1e3)
    df_pred['cambioDestino'] = (df_pred['diffDestino'] + 0.01)/(df_pred['oldbalanceDest'] + 1e3)
    df_pred[operacion] = 1
    #print(df)
    result = modelo.predict(df_pred)
    probs  = modelo.predict_proba(df_pred)[0]
    if result == 1:
        isfraud = "FRAUDE"
        newstyle["background-image"] = "linear-gradient(90deg,#eb984e,#ec7063)"
    else: 
        isfraud = "LEGAL"
        newstyle["background-image"] = "linear-gradient(90deg,#82e0aa,#f9e79f)"
    string_salida = f'La transacción {operacion}, de ${amount} es:'
    string_probs = f"Legal support: {probs[0]}% Fraud support: {probs[1]}%"
    probs_style = newstyle.copy()
    probs_style["font-weight"]=400
    probs_style["font-size"]="40px"
    return string_salida, text_style, isfraud, newstyle, string_probs, probs_style #, block_style

# MINI CALLBACKS
@app.callback(
    Output('step-output-container', 'children'),
    [Input('step-slider', 'value')])
def update_step_output(value):
    return 'Valor seleccionado: {}'.format(value)

# MODELOS
@app.callback(
    [
    Output("accuracy-label", "children"),
    Output("prec-label","children"),
    Output("recall-label","children"),
    Output("matriz-confu","figure"),
    Output("matriz-confu","style"),
    Output("bar-chart1","figure"),
    Output("bar-chart1","style"),
    Output("bar-chart2","figure"),
    Output("bar-chart2","style"),
    Output("bar-chart3","figure"),
    Output("bar-chart3","style"),
    Output("accuracy-label","style"),
    Output("prec-label","style"),
    Output("recall-label","style"),
    ],
    [Input("selector-modelo", "value")])
def report_modelo(modelo):
    datos_modelo = diccionario_resultdos[modelo]
    accuracy  = 100*(datos_modelo['TP']+datos_modelo['TN'])/(datos_modelo['TP']+datos_modelo['TN']+datos_modelo['FP']+datos_modelo['FN'])
    recall    = 100*datos_modelo['TP']/(datos_modelo['TP'] + datos_modelo['FN'])
    precision = 100*datos_modelo['TP']/(datos_modelo['TP'] + datos_modelo['FP'])

    img_rgb = np.array([[[ 46, 204, 113, 100 ], [ 236, 112, 99, 100 ]],
                    [[ 236, 112, 99, 100 ], [ 46, 204, 113, 100 ]]
                   ], dtype=np.uint8)
    fig = px.imshow(img_rgb)

    fig.add_annotation(x=0, y=0,
            text="<b>TN: "+str(datos_modelo['TN'])+"</b>",
            showarrow=False,
            bordercolor="rgba(0,0,0,0)",
            font=dict(
                family="Century Gothic",
                size=30,
                color="#FFFFFF"
            ),
            borderwidth=2,
            borderpad=10,
            bgcolor="rgba(0,0,0,0)",
            )
    fig.add_annotation(x=1, y=0,
            text="<b>FP: "+str(datos_modelo['FP'])+"</b>",
            showarrow=False,
            bordercolor="rgba(0,0,0,0)",
            font=dict(
                family="Century Gothic",
                size=30,
                color="#FFFFFF"
            ),
            borderwidth=2,
            borderpad=10,
            bgcolor="rgba(0,0,0,0)",
            )
    fig.add_annotation(x=0, y=1,
            text="<b>FN: "+str(datos_modelo['FN'])+"</b>",
            showarrow=False,
            bordercolor="rgba(0,0,0,0)",
            font=dict(
                family="Century Gothic",
                size=30,
                color="#FFFFFF"
            ),
            borderwidth=2,
            borderpad=10,
            bgcolor="rgba(0,0,0,0)",
            )
    fig.add_annotation(x=1, y=1,
            text="<b>TP: "+str(datos_modelo['TP'])+"</b>",
            showarrow=False,
            bordercolor="rgba(0,0,0,0)",
            font=dict(
                family="Century Gothic",
                size=30,
                color="#FFFFFF",
            ),
            borderwidth=2,
            borderpad=10,
            bgcolor="rgba(0,0,0,0)",
            )

    fig.update_layout(title=f'Matriz de Confusión del modelo {datos_modelo["nombre"]}', height=500, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font_color='white', xaxis_showticklabels = False, yaxis_showticklabels = False,
                      yaxis_fixedrange=True, xaxis_fixedrange=True, xaxis_title="Predicted Labels", 
                      yaxis_title="True Labels", xaxis_showgrid = False, yaxis_showgrid = False,  
                      )
    #fig.update_coloraxes(showscale=False)
    text_style = {"width":"20%",
                  "vertical-align":"middle",
                  "display":"inline-block",
                  "margin-left":"3.33%",
                  "margin-right":"3.33%",
                  "text-align":"center",
                  "font-size": "30px",
                  "-webkit-text-fill-color": "transparent",
                  "text-fill-color": "transparent",
                  "-webkit-background-clip": "text",
                  "background-clip": "text",}
    acc_style = text_style.copy()
    acc_style["background-image"]  = "linear-gradient(90deg,#58d68d,#f4d03f)"
    rec_style = text_style.copy()
    rec_style["background-image"]  = "linear-gradient(90deg,#eb984e,#ec7063)"
    prec_style = text_style.copy()
    prec_style["background-image"] = "linear-gradient(90deg,#f4d03f,#eb984e)"
    
    color_seq = ['#abebc6','#f9e79f', '#fad7a0','#f5cba7','#f5b7b1']
    lines_seq = ['#58d68d','#f4d03f', '#f39c12','#e67e22','#ec7063']
    color_seq[df_m.index.get_loc(modelo)] = lines_seq[df_m.index.get_loc(modelo)]
    #lines_seq[df_m.index.get_loc(modelo)] = '#58d68d'

    bar1 = go.Figure(data=[go.Bar(x=df_m['nombre'],
                                  y=df_m['accuracy'])]) #hole=.3, pull=pull)])
    bar2 = go.Figure(data=[go.Bar(x=df_m['nombre'],
                                  y=df_m['recall'])])    #hole=.3, pull=pull)])
    bar3 = go.Figure(data=[go.Bar(x=df_m['nombre'],
                                  y=df_m['precision'])]) #hole=.3, pull=pull)])
    bar1.update_layout(title=f'Accuracy de los modelos', height=750, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font_color='white',
                      )
    bar1.update_traces(marker=dict(color=color_seq, line=dict(color=lines_seq, width=4)))
    bar1.update_yaxes(range=[0.9,1])
    bar2.update_layout(title=f'Recall de los modelos', height=750, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font_color='white'
                      )
    bar2.update_traces(marker=dict(color=color_seq, line=dict(color=lines_seq, width=4)))
    bar2.update_yaxes(range=[0.4,1])
    bar3.update_layout(title=f'Precisión de los modelos', height=750, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font_color='white'
                      )
    bar3.update_traces(marker=dict(color=color_seq, line=dict(color=lines_seq, width=4)))

    unified_style = {'display':'inline-block', 'width':'33%'}

    return f"Accuracy: {round(accuracy,4)} %", f"Precisión: {round(precision,4)} %", f"Recall: {round(recall,4)} %", fig, {'display':'inline-block'}, bar1, unified_style, bar3, unified_style, bar2, unified_style, acc_style, prec_style, rec_style

# HISTOGRAMA FRAUDE
@app.callback(
    [Output("histogram-fraud", "figure"),Output("histogram-fraud","style")],
    [Input("histogram-checklist", "value"), Input("hist-amount-slider","value")])
def generate_fraud_histogram(x, range_amount):
    min_am = range_amount[0]
    max_am = range_amount[1]
    df_l = df[df.isFraud == 1].append(df[df.isFraud == 0].sample(1000000))
    data = df_l[(df_l['type'].isin(x)) & (df_l.amount <= max_am) & (df_l.amount >= min_am)]

    fig = px.histogram(data, x='amount', color='isFraud', color_discrete_sequence=['#58d68d','#ec7063'])
    fig.update_layout(title=f'Histogram - Distribución de transacciones según fraude y cantidad.', height=750, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font_color='white', 
                      )
    return fig, {'display':'block'}

#SCATTER STEP
@app.callback(
    [Output("time-scatters", "figure"),Output("time-scatters","style")],
    [Input("time-scatters-checklist", "value"), Input("time-scatters-fraud", "value")])
def generate_step_scatter(x, sel_fraud):
    try:
        data = df[(df['type'].isin(x)) & (df['amount'] != 0) & (df['isFraud'].isin(sel_fraud))].sample(40000)
    except:
        data = df[(df['type'].isin(x)) & (df['amount'] != 0) & (df['isFraud'].isin(sel_fraud))]
    # Para Pintar:
    data['isFraud'] = (data['isFraud'] + 1)*10

    fig = px.scatter(data, x='amount', y='step', color='type', log_x=True, size='isFraud', color_discrete_sequence=['#58d68d','#f4d03f','#ec7063','#a569bd','#3498db'])
    fig.update_layout(title=f'Scatterplot - Distribución de transacciones según el tiempo.', height=850, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font_color='white', 
                      )
    return fig, {'display':'block'}

# SCATTER RELATION
@app.callback(
    [Output("exploratory-scatters","figure"),Output("exploratory-scatters","style"), Output("percentage","children"), Output("percentage","style")],
    Input("tipoOperacion","value"))
def generateScatter(x):
    data = df[(df.type == x)] # & (df.oldbalanceOrg != 0) & (df.newbalanceOrig != 0) & (df.oldbalanceDest != 0) & (df.newbalanceDest != 0)]
    data_fraud = data[data.isFraud == 1]
    data_none  = data[data.isFraud == 0].sample(10000)
    percentage = (len(data_fraud)/len(data))*100
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Cuenta de Origen',  'Cuenta de Destino'))
    print()
    fig.add_trace(
        go.Scatter(
            x=data_none['oldbalanceOrg'], y=data_none['newbalanceOrig'],
            mode="markers",
            marker_color='#58d68d',
            name="Regular Origen"
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=data_fraud['oldbalanceOrg'], y=data_fraud['newbalanceOrig'],
            mode="markers",
            marker_color='#ec7063',
            name="Fraude Origen"
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=data_none['oldbalanceDest'], y=data_none['newbalanceDest'],
            mode="markers",
            marker_color='#58d68d',
            name="Regular Destino"
        ),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(
            x=data_fraud['oldbalanceDest'], y=data_fraud['newbalanceDest'],
            mode="markers",
            marker_color='#ec7063',
            name="Fraude Destino"
        ),
        row=1, col=2
    )
    #fig.update_xaxes(type="log")
    #fig.update_yaxes(type="log")
    fig['layout']['xaxis']['title']='Balance Viejo Origen'
    fig['layout']['xaxis2']['title']='Balance Viejo Destino'
    fig['layout']['yaxis']['title']='Balance Nuevo Origen'
    fig['layout']['yaxis2']['title']='Balance Nuevo Destino'
    fig.update_layout(title=f'Scatterplot - Relación entre cuentas ({x})', height=750, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font_color='white', 
                      #title_font_color='white',legend_font_color='white',
                      #legend_title_font_color='white',
                      )
    new_style = {
        "display":"block",
        "font-size":"30px",
        "-webkit-text-fill-color": "transparent",
        "text-fill-color": "transparent",
        "-webkit-background-clip": "text",
        "background-clip": "text",
        "background-image": "linear-gradient(90deg,#f4d03f,#eb984e,#ec7063)"
    }
    return fig, {'display':'block'}, ['Fraude: ' + str(round(percentage,4))+' %'], new_style

# BOX PLOT
@app.callback(
    [Output("box-plot", "figure"),Output("box-plot","style")],
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
    fig.update_layout(title=f'Boxplot - Distribución de {x} según los Tipos de Transacción', height=850, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font_color='white', 
                      #title_font_color='white',legend_font_color='white',
                      #legend_title_font_color='white',
                      )
    return fig, {'display':'block'}

# OTROS

if __name__ == '__main__':
    app.run_server()
