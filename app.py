# ZA WEB APLIKACIJU
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output
# CUSTOM KOD
from dataprocessor import retrieveDataFrame


df = retrieveDataFrame()







# LE HACK:
app = dash.Dash(__name__)
server = app.server

PAGE_SIZE = 20

COLUMNS = ["custom_params.time", "custom_params.timeToSelect", 'custom_params.changeInDistance']

#https://dash.plotly.com/datatable/callbacks
#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')



app.layout = html.Div(
    className="row",
    children=[

        html.Div(children=[
            html.H1(children='Analitičarka'),
            dcc.Dropdown(id='dropdown-userid', options=[
                {'label': i, 'value': i} for i in sorted(df.userid.unique())
                ], multi=True, placeholder='FIltriraj po useru...'),
            dcc.Dropdown(id='dropdown-name', options=[
                {'label': i, 'value': i} for i in sorted(df.name.unique())
                ], multi=True, placeholder='FIltriraj po sceni...'),
            ],
            ),
        html.Div( children =[
            html.H2("Grafovi"),
            html.Span("Grupiraj po:"),
            dcc.Dropdown(id='dropdown-groupby', options=[
                {'label': i, 'value': i} for i in sorted(df.columns)
                ], multi=False, placeholder='Grupiraj po...',
                value = 'name')
            ]            
        ),
        
        html.Br(),
        html.Div(
            id='graphs-placeholder',
            className="five columns"
        ),
        html.H2("Tablica"),
                html.Div(
            
            dash_table.DataTable(
                id='table-paging-with-graph',
                columns=[
                    {"name": i, "id": i} for i in sorted(df.columns)
                ],
                page_current=0,
                page_size=PAGE_SIZE,
                page_action='custom',

                filter_action='custom',
                filter_query='',

                sort_action='custom',
                sort_mode='multi',
                sort_by=[]
            ),
            style={'height': 750, 'overflowY': 'scroll'},
            className='six columns'
        ),
    ]
)

operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]


def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3

def filter_df(filter, userids, names):
    filtering_expressions = filter.split(' && ')
    dff = df
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(str(filter_value), na=False)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]
    if userids:
        dff = dff[dff['userid'].str.contains('|'.join(userids))]
    if names:
        dff = dff[dff['name'].str.contains('|'.join(names))]
    return(dff)


@app.callback(
    Output('table-paging-with-graph', "data"),
    Input('table-paging-with-graph', "page_current"),
    Input('table-paging-with-graph', "page_size"),
    Input('table-paging-with-graph', "sort_by"),
    Input('table-paging-with-graph', "filter_query"),
    Input('dropdown-userid', "value"), 
    Input('dropdown-name', "value")
    )

def update_table(page_current, page_size, sort_by, filter, filter_userid, filter_name):

    dff = filter_df(filter, filter_userid, filter_name)
    
    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )

    return dff.iloc[
        page_current*page_size: (page_current + 1)*page_size
    ].to_dict('records')


@app.callback(
    Output('graphs-placeholder', "children"),
    Input('table-paging-with-graph', "filter_query"),
    Input('dropdown-userid', "value"), 
    Input('dropdown-name', "value"),
    Input('dropdown-groupby', "value"))    
    
def update_graph(filter, filter_userid, filter_name, groupby_option):
    
    dff = filter_df(filter, filter_userid, filter_name)
    print(dff)
    dff = dff.groupby(groupby_option, as_index= False).mean()
    print(dff)

    figs =  [
            dcc.Graph(
                id=column,
                figure={
                    "data": [
                        {
                            "x": dff[groupby_option],
                            "y": dff[column] if column in dff else [],
                            "type": "bar",
                            "marker": {"color": "#0074D9"},
                        }
                    ],
                    "layout": {
                        "title": "Average "+column,
                        "xaxis": {
                            "automargin": True,
                            'title': groupby_option
                            },
                        "yaxis": {
                            "automargin": True,
                            'title': column
                            },
                        "height": 250,
                        "margin": {"t": 50, "l": 10, "r": 10},
                    },
                },
            )
            for column in COLUMNS 
        ]

    return html.Div(
        figs
    )



if __name__ == '__main__':
    app.run_server(debug=True)
    #app.run_server()



