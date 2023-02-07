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

st.set_page_config(page_title='Visão Entregadores', page_icon='🛵', layout='wide')

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
st.header('Marketplace - Visão Entregadores 🛵')

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
# Criando as tabs
# ========================================================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial'] )

with tab1:
    with st.container():
        st.title('Overhall Metrics')

        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            #st.subheader('Maior idade')
            maior_idade = df1['Delivery_person_Age'].max()
            col1.metric('Maior idade:', value = maior_idade) # Pesquisar sobre metrics no streamlit, não é obrigatório escrever value

        with col2:
            #st.subheader('Menor idade')
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric('Menor idade:', value = menor_idade)
        
        with col3:
            #st.subheader('Melhor condição de veículos')
            melhor_condicao = df1['Vehicle_condition'].max()
            col3.metric('Melhor condição:', value = melhor_condicao)
        
        with col4:
            #st.subheader('Pior condição de veículos')
            pior_condicao = df1['Vehicle_condition'].min()
            col4.metric('Pior condição:', value = pior_condicao)

    with st.container(): # construindo um container ainda dentro da Tab1
        st.markdown("""___""")
        st.title('Avaliações')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliações médias por entregador')
            avaliacao_media_entregador = (df1.loc[:, ['Delivery_person_Ratings','Delivery_person_ID']]
                                        .groupby('Delivery_person_ID').mean().reset_index())
            st.dataframe(avaliacao_media_entregador)
        
        with col2:
            st.markdown('##### Avaliações médias por trânsito')
            avaliacao_media_por_transito = (df1.loc[:, ['ID','Delivery_person_Ratings','Road_traffic_density']]
                                            .groupby(['Road_traffic_density']).agg({'Delivery_person_Ratings':['mean','std']}))
            

            # Mudando o nome das colunas
            avaliacao_media_por_transito.columns = ['delivery_mean','delivery_std']

            # Resetando o index
            avaliacao_media_por_transito.reset_index()

            # Plotando o dataframe
            st.dataframe(avaliacao_media_por_transito)

            
            st.markdown('##### Avaliações médias por clima')            
            avaliacao_media_clima = (df1.loc[:, ['Delivery_person_Ratings','Weatherconditions']]
                                    .groupby('Weatherconditions').agg({'Delivery_person_Ratings':['mean','std']}))

            # Mudança do nome das colunas:
            avaliacao_media_clima.cloumns = ['delivery_mean','delivery_std']

            # reset do index
            avaliacao_media_clima = avaliacao_media_clima.reset_index()
            
            st.dataframe(avaliacao_media_clima)

    
    with st.container(): 
        st.markdown("""___""")
        st.title('Velocidade de Entrega')

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('##### Top entregadores mais rápidos')

        df2 = (df1.loc[:, ['Delivery_person_ID','City','Time_taken(min)']]
                .groupby(['City','Delivery_person_ID']).min().sort_values(['City','Time_taken(min)'], ascending=True).reset_index())
                
        df_aux1 = df2.loc[df2['City'] == 'Metropolitian', :]
        df_aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
        df_aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

        df3 = pd.concat([df_aux1,df_aux2,df_aux3]).reset_index()
        st.dataframe(df3)

    with col2:
        st.markdown('##### Top entregadores mais lentos')

        df2 = (df1.loc[:, ['Delivery_person_ID','City','Time_taken(min)']]
                .groupby(['City','Delivery_person_ID']).min().sort_values(['City','Time_taken(min)'], ascending=False).reset_index())
        df_aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
        df_aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
        df_aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

        df3 = pd.concat([df_aux1,df_aux2,df_aux3]).reset_index()

        st.dataframe(df3)
