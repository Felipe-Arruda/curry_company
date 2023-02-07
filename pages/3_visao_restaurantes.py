 # Imports
import pandas as pd
import numpy as np
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
import folium # plotar mapas
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Restaurante', page_icon='🍥', layout='wide')

# Import datasets
df = pd.read_csv('dataset/train.csv')

# Data cleaning
df1 = df.copy()

## removendo os espaços
df1['ID'] = df1['ID'].apply( lambda x: x.strip())
df1['Delivery_person_ID'] = df1['Delivery_person_ID'].apply( lambda x: x.strip())
df1['Weatherconditions'] = df1['Weatherconditions'].apply( lambda x: x.strip())
df1['Road_traffic_density'] = df1['Road_traffic_density'].apply( lambda x: x.strip())
df1['Type_of_order'] = df1['Type_of_order'].apply( lambda x: x.strip())
df1['Type_of_vehicle'] = df1['Type_of_vehicle'].apply( lambda x: x.strip())
df1['Festival'] = df1['Festival'].apply( lambda x: x.strip())
df1['City'] = df1['City'].apply( lambda x: x.strip())
df1['Delivery_person_Age'] = df1['Delivery_person_Age'].apply( lambda x: x.strip())
df1['multiple_deliveries'] = df1['multiple_deliveries'].apply( lambda x: x.strip())
# Removendo NaN
linhas_selecionadas = (df1['City'] != 'NaN')
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN')
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN')
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1['Festival'] != 'NaN')
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN')
df1 = df1.loc[linhas_selecionadas, :].copy()

# Convertendo variáveis
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y')
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

# Limpando a coluna time taken
df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split('(min) ')[1] )
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

# Visão Empresa

# ============================================================
# Barra lateral
# ============================================================
st.header('Marketplace - Visão Restaurantes 🍲')

# img_path = 'C:/Users/felipe.souza/repos/FTC/dataset/images/img1.png'
image = Image.open('img1.png')
st.sidebar.image(image, width=180)

st.sidebar.markdown('# Cury Company') # A quantidade de # determina o tamanho da fonte
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""") # Cria uma linha

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = pd.datetime(2022, 4, 13), # data defaut -> Aqui selecionei a data máxima
    min_value = pd.datetime(2022, 2, 11), # data mínima 
    max_value = pd.datetime(2022, 4, 6),
    format = 'DD-MM-YYY') # Formato da data

#st.header(date_slider)
st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    df1['Road_traffic_density'].unique().tolist(),
    default= df1['Road_traffic_density'].unique().tolist())

st.sidebar.markdown("""___""")

weather_options = st.sidebar.multiselect(
    'Quais as condições climáticas?',
    df1['Weatherconditions'].unique().tolist(),
    default=df1['Weatherconditions'].unique())


st.sidebar.markdown("""___""")
st.sidebar.markdown('## Powered by Felipe Arruda')

# ========================================================================      
# Aplicando os filtros - Eles devem ficar depois da barra lateral.
# ========================================================================

# Aplicando o filtro nas datas
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

linhas_selecionadas = df1['Weatherconditions'].isin(weather_options)
df1 = df1.loc[linhas_selecionadas, :]

# ========================================================================      
# Layout no Streamlit
# ========================================================================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
    with st.container():
        st.markdown('## Overall Metrics')

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            entregadores_unicos = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos', entregadores_unicos)

        with col2:
            cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
            df1['distance'] = df1.loc[:, cols].apply(lambda x: 
                          haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                          (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1 )

            avg_distance = np.round(df1.loc[:, 'distance'].mean(), 2)
            col2.metric('Distância média', avg_distance )

        with col3:
            df_aux = (df1.loc[:, ['Time_taken(min)','Festival']].groupby(['Festival']).agg({'Time_taken(min)':['mean','std']}))
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()

            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'], 2)
            col3.metric('Entrega com festival (min)', df_aux)

        with col4:
            df_aux = (df1.loc[:, ['Time_taken(min)','Festival']].groupby(['Festival']).agg({'Time_taken(min)':['mean','std']}))
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()

            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'], 2)
            col4.metric('STD com festival', df_aux)

        with col5:
            df_aux = (df1.loc[:, ['Time_taken(min)','Festival']].groupby(['Festival']).agg({'Time_taken(min)':['mean','std']}))
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()

            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'], 2)
            col5.metric('Entrega sem festival (min)', df_aux)

        with col6:
            
            df_aux = (df1.loc[:, ['Time_taken(min)','Festival']].groupby(['Festival']).agg({'Time_taken(min)':['mean','std']}))
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()

            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'std_time'], 2)
            col6.metric('STD sem festival', df_aux)

    with st.container():
        st.markdown("""___""")
        st.markdown('## Tempo médio de entrega por região')

        col1, col2 = st.columns(2)

        with col1:
            df_aux = df1.loc[:, ['City','Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']})
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()

            fig = go.Figure()
            fig.add_trace( go.Bar(name='Control',
                            x=df_aux['City'],
                            y=df_aux['avg_time'],
                            error_y=dict(type='data', array=df_aux['std_time']))) # o error Y é o desvio padrão (risquinho em cima da barra)
            fig.update_layout(barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:

            df_aux = df1.loc[:, ['City','Time_taken(min)','Type_of_order']].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']})
            df_aux.columns = ['avg_time','std_time']

            df_aux = df_aux.reset_index()

            st.dataframe(df_aux, use_container_width=True)

    with st.container():
        st.markdown("""___""")
        st.markdown('## Distribuição por tempo')

        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de pizza
            cols = ['Delivery_location_latitude','Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df1['distance'] = (df1.loc[:, cols].apply(lambda x: 
                            haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                            (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1 ))

            avg_distance = df1.loc[:, ['City','distance']].groupby('City').mean().reset_index()
            fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])]) # esse pull é o espacinho que se destaca

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Sunburst                   
            df_aux = df1.loc[:, ['City','Time_taken(min)','Road_traffic_density']].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean','std']})
            df_aux.columns = ['avg_time','std_time']

            df_aux = df_aux.reset_index()

            fig = px.sunburst(df_aux, path=['City','Road_traffic_density'], values='avg_time',
                            color='std_time', color_continuous_scale='RdBu',
                            color_continuous_midpoint=np.average(df_aux['std_time']))

            st.plotly_chart(fig, use_container_width=True)
    
    # with st.container():
        
    #     st.markdown("""___""")
    #     st.markdown('#### Distribuição da distância')  

