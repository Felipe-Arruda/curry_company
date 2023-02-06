# Imports
import pandas as pd
from datetime import datetime
import time
import plotly.express as px
import folium # plotar mapas
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Home', page_icon='📊', layout='wide')

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
st.header('Marketplace - Visão Empresa 🏪')

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

st.header(date_slider)
st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    df1['Road_traffic_density'].unique().tolist(),
    default= df1['Road_traffic_density'].unique().tolist())

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

# ============================================================
# Layout no Streamlit
# ============================================================

# Estou desenvolvendo este layout com base no modelo criado pelo Meigarom no Draw Io, para relembrar devo assistir a última aula do módulo 5
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica' ] ) # Cria abas no página

# O que ficar identado no with, será aplicado somenta à aba criada.
with tab1:

    with st.container(): # O container são os quadrantes onde eu quero plotar algum gráfico ou coluna
        # Order Metric
        st.markdown('# Orders by day 🛵')
        
        cols = ['ID','Order_Date']
        df_aux = df1.loc[:, cols].groupby(['Order_Date']).count().reset_index()
        fig = px.bar( df_aux, x='Order_Date', y='ID')
    
        st.plotly_chart(fig, use_container_width=True)
    
   # Colocando duas colunas na mesma linha
    with st.container():
        col1, col2 = st.columns(2)
       
        with col1:
            st.markdown('## Traffic Order Share')
            cols = ['ID','Road_traffic_density']
            df_aux = df1.loc[:, cols].groupby(['Road_traffic_density']).count().reset_index()

            # Removendo o NaN
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

            # Criar uma coluna de percentual
            df_aux['entregas_percent'] = df_aux['ID'] / df_aux['ID'].sum()
            fig = px.pie(df_aux, values='entregas_percent', names='Road_traffic_density')
            st.plotly_chart(fig, use_container_width=True)


        with col2:
            st.markdown('# Traffic Order City')
            df_aux = df1.loc[:, ['ID','Road_traffic_density', 'City']].groupby(['City','Road_traffic_density']).count().reset_index()

            # Eliminando os NaN

            df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

            fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City') 
            st.plotly_chart(fig, use_container_width=True)
    
with tab2:
    with st.container():
        st.markdown("## Order by week")
        # Criar uma coluna de semana
        df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')# O %U considera o domingo sendo o primeiro dia da semana, o %W considera a segunda.
        # Agora farei o agrupamento
        df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        fig = px.line(df_aux, x='week_of_year', y='ID')

        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("## Order share by week")
        # Quantidade de pedido por semana / Número único de entregadores por semana.
        # vou dividir a consulta em dois aux para facilitar
        df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

        # merge
        df_aux = pd.merge(df_aux01, df_aux02, how='inner')

        # Criando a coluna que trará a quantidade de pedidos por semana / número unico de entregadores
        df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']

        fig = px.line(df_aux, x='week_of_year', y='order_by_delivery')
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown('## Country Map')
    df_aux = df1.loc[:, ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()

    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                 location_info['Delivery_location_longitude']],
                popup=location_info[['City','Road_traffic_density']]).add_to(map)

    folium_static(map, width = 900, height=500)