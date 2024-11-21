import numpy as np
import pandas as pd
import zipfile
import plotly.express as px
import matplotlib.pyplot as plt
import requests
from io import BytesIO
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from my_plots import *
import streamlit as st

@st.cache_data
def load_name_data():
    names_file = 'https://www.ssa.gov/oact/babynames/names.zip'
    response = requests.get(names_file)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        dfs = []
        files = [file for file in z.namelist() if file.endswith('.txt')]
        for file in files:
            with z.open(file) as f:
                df = pd.read_csv(f, header=None)
                df.columns = ['name','sex','count']
                df['year'] = int(file[3:7])
                dfs.append(df)
        data = pd.concat(dfs, ignore_index=True)
    data['pct'] = data['count'] / data.groupby(['year', 'sex'])['count'].transform('sum')
    return data

@st.cache_data
def ohw(df):
    nunique_year = df.groupby(['name', 'sex'])['year'].nunique()
    one_hit_wonders = nunique_year[nunique_year == 1].index
    one_hit_wonder_data = df.set_index(['name', 'sex']).loc[one_hit_wonders].reset_index()
    return one_hit_wonder_data

data = load_name_data()
ohw_data = ohw(data)



st.title('Streamlit App for Social Security Names')

with st.sidebar:
    input_name = st.text_input('Enter a name:', 'Mary')
    year_input = st.slider("Year", min_value=1880, max_value=2023, value=2000)
    n_names = st.radio('Numer of names per sex:', [3,5,7])

    mens_color = st.color_picker("Pick A Color for the Men's graph", "#00f900")
    st.write("The current color for men is", mens_color)
    womens_color = st.color_picker("Pick A Color for the Women's graph", "#00f900")
    st.write("The current color for women is", womens_color)

tab1, tab2 = st.tabs(['Names', 'Year'])

with tab1:
    custom_color_map = {
        'M': mens_color,
        'F': womens_color
    }

    name_data = data[data['name']==input_name].copy()
    #fig = px.line(name_data, x='year', y='count', color='sex', color_discrete_map=custom_color_map,)
    #st.plotly_chart(fig)

    fig_trend = name_trend_plot(data, mens_color, womens_color, input_name)
    st.plotly_chart(fig_trend)

with tab2:
    fig_year = top_names_plot(data, mens_color, womens_color, n=n_names, year=year_input)
    st.plotly_chart(fig_year)

    st.write('Unique Names Table')
    output_table = unique_names_summary(data, year_input)
    st.dataframe(output_table)

