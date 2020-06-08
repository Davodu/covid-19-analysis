import pandas as pd
import numpy as np

import dash
dash.__version__
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State

import plotly.graph_objects as go

import os
print(os.getcwd())
df_input_large=pd.read_csv('data/processed/COVID_final_set.csv',sep=';')


#Styling
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#figure
layout={
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }
            }
fig = go.Figure(layout=layout)

app.layout = html.Div(
    className='row', 
    style={'backgroundColor': colors['background'],
            'padding': 10,
    },

children= [
    html.H1(
    children='Applied Data Science on COVID-19 data',
    style={
            'textAlign': 'center',
            'color': colors['text'],

        }
    ),
    
    html.Label('Select a country to view current covid trends',
    style={
        'textAlign': 'left',
        'color': colors['text']
    }),
    dcc.Dropdown(
        id='country_drop_down',
        options=[ {'label': each,'value':each} for each in df_input_large['country'].unique()],
        value=['US', 'Nigeria','Italy'], # which are pre-selected
        multi=True
    ),

    html.Label(
        'Select current timeline of confirmed COVID-19 cases or view doubling time statistics',
        style={
        'textAlign': 'left',
        'color': colors['text']
    }),

    dcc.Dropdown(
    style={
        'width': '50%'
    },
    id='doubling_time',
    options=[
        {'label': 'Timeline Confirmed ', 'value': 'confirmed'},
        {'label': 'Timeline Confirmed Filtered', 'value': 'confirmed_filtered'},
        {'label': 'Timeline Doubling Rate', 'value': 'confirmed_dr'},
        {'label': 'Timeline Doubling Rate Filtered', 'value': 'confirmed_filtered_dr'},
    ],
    value='confirmed',
    multi=False
    ),

    dcc.Graph(figure=fig,
     id='main_window_slope',
     style={
        'width': '100%', 
        'display': 'inline-block',
        'color': colors['text']
    })
])



@app.callback(
    Output('main_window_slope', 'figure'),
    [Input('country_drop_down', 'value'),
    Input('doubling_time', 'value')])
def update_figure(country_list,show_doubling):
    if 'doubling_rate' in show_doubling:
        my_yaxis={'type':"log",
               'title':'Approximated doubling rate over 3 days (larger numbers are better #stayathome)'
              }
    else:
        my_yaxis={'type':"log",
                  'title':'Confirmed infected people (source johns hopkins csse, log-scale)'
              }


    traces = []
    for each in country_list:

        df_plot=df_input_large[df_input_large['country']==each]

        if show_doubling=='doubling_rate_filtered':
            df_plot=df_plot[['state','country','confirmed','confirmed_filtered','confirmed_dr','confirmed_filtered_dr','date']].groupby(['country','date']).agg(np.mean).reset_index()
        else:
            df_plot=df_plot[['state','country','confirmed','confirmed_filtered','confirmed_dr','confirmed_filtered_dr','date']].groupby(['country','date']).agg(np.sum).reset_index()
       #print(show_doubling)


        traces.append(dict(x=df_plot.date,
                                y=df_plot[show_doubling],
                                mode='markers+lines',
                                opacity=0.9,
                                name=each
                        )
                )

    return {
            'data': traces,
            'layout': dict (
                width=1280,
                height=720,

                xaxis={'title':'Timeline',
                        'tickangle':-45,
                        'nticks':20,
                        'tickfont':dict(size=14,color="#7f7f7f"),
                      },

                yaxis=my_yaxis
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)