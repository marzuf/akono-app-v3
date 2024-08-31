import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import dash_bootstrap_components as dbc

# Exemple de données
df = pd.DataFrame({
    'Date': pd.date_range(start='1/1/2020', periods=10),
    'A': [1, 3, 2, 4, 3, 5, 4, 6, 5, 7],
    'B': [2, 4, 1, 3, 5, 7, 3, 4, 6, 8]
})

# Initialisation de l'application avec Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Graph(
        id='evotimeTimeDB-graph',
        style={'cursor': 'pointer'},
        config={'scrollZoom': True},
        figure={
            'data': [
                go.Scatter(
                    x=df['Date'],
                    y=df['A'],
                    mode='lines+markers',
                    name='A'
                ),
                go.Scatter(
                    x=df['Date'],
                    y=df['B'],
                    mode='lines+markers',
                    name='B'
                )
            ],
            'layout': go.Layout(title='Test Graph')
        }
    ),
    dbc.Modal(
        [
            dbc.ModalHeader("Graph Full Screen"),
            dbc.ModalBody(
                dcc.Graph(
                    id='modal-graph',
                    config={'scrollZoom': True},
                    figure={
                        'data': [
                            go.Scatter(
                                x=df['Date'],
                                y=df['A'],
                                mode='lines+markers',
                                name='A'
                            ),
                            go.Scatter(
                                x=df['Date'],
                                y=df['B'],
                                mode='lines+markers',
                                name='B'
                            )
                        ],
                        'layout': go.Layout(title='Enlarged Graph', height=600)
                    }
                )
            ),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-modal", className="ml-auto")
            ),
        ],
        id="evotime-modal-graph",
        size="xl",
        is_open=False,
    )
])

# Callback pour gérer l'ouverture et la fermeture de la modale
@app.callback(
    Output('evotime-modal-graph', 'is_open'),
    [Input('evotimeTimeDB-graph', 'clickData'),
     Input('close-modal', 'n_clicks')],
    [State('evotime-modal-graph', 'is_open')]
)
def toggle_modal(clickData, n_clicks, is_open):
    ctx = dash.callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]['prop_id']
        if prop_id == 'evotimeTimeDB-graph.clickData' and clickData:
            return True  # Ouvre la modale
        elif prop_id == 'close-modal.n_clicks':
            return False  # Ferme la modale

    return is_open  # Ne change rien si aucun événement n'est détecté

if __name__ == '__main__':
    app.run_server(debug=True)
