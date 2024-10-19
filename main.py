# Importando as bibliotecas
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date, timedelta
from PIL import Image
import base64
from io import BytesIO


# functions to load data
@st.cache_data
def carregar_dados(empresas, dt_inicio, dt_fim):
    texto_tickers = " ".join(empresas)
    dados_acao = yf.Tickers(texto_tickers)
    cotacoes_acao = dados_acao.history(
        period="1d", start=dt_inicio, end=dt_fim)
    # print(cotacoes_acao)
    cotacoes_acao = cotacoes_acao["Close"]
    return cotacoes_acao

# Load stocks' list


@st.cache_data
def carregar_todas_acoes():
    local_arquivo = 'tickers.csv'
    base_acoes = pd.read_csv(local_arquivo, sep=";", encoding='ISO-8859-1')
    base_acoes = base_acoes[base_acoes['flg_carrega_site'] == 1]
    todas_acoes = list(base_acoes["Codigo"])
    todas_acoes = [item + ".SA" for item in todas_acoes]
    return todas_acoes

# Função para converter imagem para base64


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Função para alterar o idioma


def change_language(lang):
    st.session_state.language = lang

# -------------------- END OF FUNCTIONS ------------------


if 'language' not in st.session_state:
    st.session_state.language = 'pt'  # setting portuguese as default language

# Configura as datas
data_inicio = "2021-01-01"

# Obter a data de ontem
data_fim = date.today() - timedelta(days=1)

# Chama a ação
acoes = carregar_todas_acoes()
dados = carregar_dados(acoes, data_inicio, data_fim)

# Alterar o texto com base no idioma selecionado
if st.session_state.language == 'en':
    st.write("""
         # Stock Price
         The chart below represents the evolution of stock prices over the years

         """)  # markdown
else:
    st.write("""
         # App Preço das Ações 
         O gráfico abaixo representa a evolução do preço das ações ao longo dos anos

         """)  # markdown


# interface do streamlit
st.sidebar.header("Filtros")


if st.session_state.language == 'en':
    text_filter = "Choose the stocks to view"
    text_period = "Select the period"
else:
    text_filter = "Escolha as ações para visualizar"
    text_period = "Selecione o período"

# Filtro das acoes
lista_acoes = st.sidebar.multiselect(
    text_filter, dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) == 1:
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica: "Close"})

# filtro de datas
data_inicio = dados.index.min().to_pydatetime()
data_fim = dados.index.max().to_pydatetime()
intervalo_data = st.sidebar.slider(text_period,
                                   min_value=data_inicio,
                                   max_value=data_fim,
                                   value=(data_inicio, data_fim))

dados = dados.loc[intervalo_data[0]:intervalo_data[1]]

# Load flag´s
usa_flag = image_to_base64('images/usa_flag.png')
brazil_flag = image_to_base64('images/brazil_flag.png')

# Exibir as imagens das bandeiras como botões
# if st.sidebar.button("🇺🇸", key="usa"):
#    change_language('en')
# if st.sidebar.button("🇧🇷", key="brazil"):
#    change_language('pt')

st.sidebar.markdown(f"""
    <p>&nbsp;</p> <p>&nbsp;</p> <p>&nbsp;</p>
                    """, unsafe_allow_html=True)

# Exibir as bandeiras e botões alinhados
col1, col2 = st.sidebar.columns(2)

with col1:
    # Imagem para inglês
    st.image(f"data:image/png;base64,{usa_flag}", width=40)
    if st.button("EN", key="usa"):
        change_language('en')


with col2:
    # Imagem para português
    st.image(f"data:image/png;base64,{brazil_flag}", width=40)
    if st.button("PT", key="brazil"):
        change_language('pt')


# Exibir a imagem da bandeira com tooltip e ação de clique
# st.sidebar.markdown(f"""
#   <p>&nbsp;</p>
#    <div style="text-align: center;">
#        <img src="data:image/png;base64,{usa_flag}" width="50" title="Click to English" onclick="change_language('en');" style="cursor: pointer;">
#        <img src="data:image/png;base64,{brazil_flag}" width="50" title="Clique para português" onclick="change_language('pt');" style="cursor: pointer;">
#    </div>
#    """, unsafe_allow_html=True)


# grafico
st.line_chart(dados)

texto_performance_ativos = ""


# Montando texto para performance de ação
if len(lista_acoes) == 0:
    lista_acoes = list(dados.columns)
elif len(lista_acoes) == 1:
    dados = dados.rename(columns={"Close": acao_unica})

for acao in lista_acoes:
    performance_ativo = dados[acao].iloc[-1] / dados[acao].iloc[0] - 1
    performance_ativo = float(performance_ativo)
    # print(performance_ativo)
    if performance_ativo > 0:
        texto_performance_ativos = texto_performance_ativos + \
            f"  \n{acao}: :green[{performance_ativo:.1%}]"
    elif performance_ativo < 0:
        texto_performance_ativos = texto_performance_ativos + \
            f"  \n{acao}: :red[{performance_ativo:.1%}]"
    else:
        texto_performance_ativos = texto_performance_ativos + \
            f"  \n{acao}: {performance_ativo:.1%}"

if st.session_state.language == 'en':
    st.write(f"""
         ### Asset Performance
         This was the performance of each asset during the selected period:

        {texto_performance_ativos}
         """)  # markdown
else:
    st.write(f"""
         ### Performance dos Ativos
         Essa foi a performance de cada ativo no período selecionado:

        {texto_performance_ativos}
         """)  # markdown
