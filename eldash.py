# Importamos las librerias mínimas necesarias
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import logging
from plotly.subplots import make_subplots

# Para este Dash, vamos a seleccionar un fichero de datos y realizar un dashboard descriptivo
# sobre un conjunto de datos

df = pd.read_csv("StudentsPerformance.csv")

# Crear opciones para las razas
races = df["race/ethnicity"].unique().tolist()
races.sort()
options_dropdown_race = []
for race in races:
    options_dropdown_race.append({'label': race, 'value': race})

# Crear opciones para las asignaturas
subjects = ["math score", "reading score", "writing score"]
options_dropdown_subjects = []
for subject in subjects:
    options_dropdown_subjects.append({'label': subject.split()[0].capitalize(), 'value': subject})

# Crear opciones para las variables categóricas

cols_checklist = ["gender","race/ethnicity","parental level of education", "lunch", "test preparation course"]

options_checklist = []
for col in cols_checklist:
    options_checklist.append({'value': col, 'label': col})

app = dash.Dash()
server = app.server

#app.config.suppress_callback_exceptions = True

logging.getLogger('werkzeug').setLevel(logging.INFO)


app.layout = html.Div([
    html.H1( # Primera fila
            children = [
                "Introducción a Dash"
            ],
            id = "titulo",
            style = {  # Aquí aplico todo lo que necesite de CSS
                "text-align": "center", # Alineo el texto al centro
                "color": "lightsteelblue", # Cambio el color de la fuente, se puede usar codigo hexagesimal
                "font-family": "Arial", # Cambio el tipo de fuente
                "backgroundColor": "darkslategray", # Cambio el color del fondo
                "text-decoration": "underline" # Subrayar el texto
            }
    ),

    dcc.Tabs(id="tabs-styled-with-props", value='tab-1', children=[
        dcc.Tab(label='Exploratorio', value='tab-1'),
        dcc.Tab(label='Resultados modelo', value='tab-2'),
        dcc.Tab(label='Consumición del modelo', value='tab-3')
    ], colors={
        "border": "white",
        "primary": "gold",
        "background": "cornsilk"
    }),
    html.Div(id='tabs-content-props')
])

@app.callback(Output('tabs-content-props', 'children'),
              Input('tabs-styled-with-props', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H2('Análisis exploratorio'),
            html.Div([
                html.H3(
                    children = [
                        "Primer grupo a comparar"
                    ],
                    id = "primer_grupo",
                    style = {
                        "display": "block",
                        "text-align": "center"
                    }
                ),
                dcc.Dropdown(
                    options = options_dropdown_race,
                    placeholder = "Selecciona una raza",
                    id = "dropdown_race",
                    style = {
                        "display": "block",
                        "width": "300px",
                        "margin-left": "10px"
                    }
                ),
                dcc.Dropdown(
                    options = options_dropdown_subjects,
                    placeholder = "Selecciona una asignatura",
                    id = "dropdown_subject",
                    style = {
                        "display": "block",
                        "width": "300px",
                        "margin-left": "10px"
                    }
                ),
                dcc.Graph(
                    id = "dropdown_figure",
                    style = {
                        "display": "none"
                    }
                )
            ],
            style={
                    "width": "50%",
                    "height": "575px",
                    "text-align": "center",
                    "display": "inline-block",
                    "float":"left",
                    "border-style": "ridge",
                    "border-color": "fuchsia"
                }
            ),
            
        ],
        style = {
            "width": "100%",
            "height": "575px",
            "text-align": "center",
            "display": "inline-block",
            "border-style": "ridge",
            "border-color": "black"
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

@app.callback(
    Output("dropdown_figure", "figure"),
    Output("dropdown_figure", "style"),
    Input("dropdown_race", "value"),
    Input("dropdown_subject",'value')
)
def figure_dropdown(dropdown_race_value,dropdown_subject_value):

    subject_dict = {
        "math score": "Math",
        "reading score": "Reading",
        "writing score": "Writing"
    }

    if dropdown_race_value and dropdown_subject_value:
        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x = df[df["race/ethnicity"] == dropdown_race_value][dropdown_subject_value],
                xbins=dict(
                    start= 0,
                    end= 100,
                    size=5,
                ),
                marker_color = "firebrick"
            )
        )
        fig.update_layout(
            title = f"Notas obtenidas en la asignatura {subject_dict[dropdown_subject_value]} de la raza {dropdown_race_value}",
            xaxis_title = "Puntuación",
            yaxis_title = "Frecuencia",
            bargap = 0.1
        )
        return (fig,{"display":"block"})
    else:
        return (go.Figure(data = [], layout = {}), {"display": "none"})

@app.callback(
    Output("dropdown_figure_2", "figure"),
    Output("dropdown_figure_2", "style"),
    Input("dropdown_race_2", "value"),
    Input("dropdown_subject_2",'value')
)
def figure_dropdown_2(dropdown_race_value,dropdown_subject_value):

    subject_dict = {
        "math score": "Math",
        "reading score": "Reading",
        "writing score": "Writing"
    }

    if dropdown_race_value and dropdown_subject_value:
        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x = df[df["race/ethnicity"] == dropdown_race_value][dropdown_subject_value],
                xbins=dict(
                    start= 0,
                    end= 100,
                    size=5,
                ),
                marker_color = "steelblue"
            )
        )
        fig.update_layout(
            title = f"Notas obtenidas en la asignatura {subject_dict[dropdown_subject_value]} de la raza {dropdown_race_value}",
            xaxis_title = "Puntuación",
            yaxis_title = "Frecuencia",
            bargap = 0.1
        )
        return (fig,{"display":"block"})
    else:
        return (go.Figure(data = [], layout = {}), {"display": "none"})

@app.callback(
    Output("pie_charts", "figure"),
    Output("pie_charts", "style"),
    Input("boton_cat", "n_clicks"),
    State("checklist_cat", "value"),
)
def checklist_callback(n_clicks,checklist_value):
    print(checklist_value)

    if (checklist_value is None) or (checklist_value == []):
        return (go.Figure(data = [], layout = {}), {"display":"none"})
    else:
        print(checklist_value)
        fig = make_subplots(
            rows=1,
            cols=len(checklist_value),
            specs = [[{'type':'domain'}]*len(checklist_value)]
        )

        for col in checklist_value:
            level_count = pd.DataFrame(df[col].value_counts()).reset_index().rename(columns = {"index": col, col: "count"})
            fig.add_trace(
                go.Pie(
                    labels = level_count[col],
                    values = level_count["count"],
                    textinfo = 'label+percent',
                    insidetextorientation = 'radial',
                    textposition = 'inside',
                    sort = False,
                    showlegend = False,
                    hole = 0.5,
                    name = col
                ),
                row = 1,
                col = checklist_value.index(col) + 1
            )

        fig.update_traces(textfont_size=12)
        return (fig,{"display": "block"})


if __name__ == '__main__':
    app.run_server()

#     children=[
#             html.H3(
#                 children=[
#                     "Segundo grupo a comparar"
#                 ],
#                 id="segundo_grupo",
#                 style={
#                     "display": "block",
#                     "text-align": "center"
#                 }
#             ),
#             dcc.Dropdown(
#                 options=options_dropdown_race,
#                 placeholder="Selecciona una raza",
#                 id="dropdown_race_2",
#                 style={
#                     "display": "block",
#                     "width": "300px",
#                     "margin-left": "10px"
#                 }
#             ),
#             dcc.Dropdown(
#                 options=options_dropdown_subjects,
#                 placeholder="Selecciona una asignatura",
#                 id="dropdown_subject_2",
#                 style={
#                     "display": "block",
#                     "width": "300px",
#                     "margin-left": "10px"
#                 }
#             ),
#             dcc.Graph(
#                 id="dropdown_figure_2",
#                 style={
#                     "display": "none"
#                 }
#             )
#     ],
#         style={
#             "width": "700px",
#             "height": "575px",
#             "display": "inline-block",
#             "margin-left": "20px",
#             "border-style": "ridge",
#             "border-color": "black"
#     },
# )
# ],
