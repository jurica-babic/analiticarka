import glob
import fnmatch
import pathlib
import os
import json
# ZA LE WEB DIO:
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


DATA_FILENAME_PATTERN = 'part-*'
DATA_FOLDER = 'data/'
pathname = DATA_FOLDER + DATA_FILENAME_PATTERN

input_files = glob.glob(pathname)

print(input_files)

for filepath in input_files:
    with open(filepath, 'r') as f:
        lines = f.readlines()
        for line in lines:
            record = json.loads(line)
            print(record['name'])

# LE HACK:
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    dcc.Input(id='my-id', value='Dash App', type='text'),
    html.Div(id='my-div')
])


@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='my-id', component_property='value')]
)
def update_output_div(input_value):
    return 'You\'ve entered "{}"'.format(input_value)


if __name__ == '__main__':
    app.run_server()



