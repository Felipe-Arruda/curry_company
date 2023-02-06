import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon= '🍲🧡'
)

# img_path = 'C:/Users/felipe.souza/repos/FTC/dataset/images/'
image = Image.open('img1.png' )
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company') # A quantidade de # determina o tamanho da fonte
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""") # Cria uma linha

st.write("# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
    ### Como utilizar o Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    Visão Restaurante:
        - indicadores semanais de crescimento dos restaurantes.
    ### Ask for Help
    - Call me on discord: Felipe Arruda#9488
    """
)

