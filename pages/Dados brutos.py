import streamlit as st
import requests 
import pandas as pd
import plotly.express as px
import time

@st.cache_data
def converteCSV(df):
    return df.to_csv(index = False).encode('utf-8')

def mensagemSucesso():
    sucesso = st.success('Arquivo baixado com sucesso!')
    time.sleep(5)
    sucesso.empty()

st.title('DADOS BRUTOS')
url = 'https://labdados.com/produtos'
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns)) #O terçeiro parâmetro é o padrão, no caso o padrão são todas as colunas como opções iniciais

st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Os produtos', dados['Produto'].unique(), dados['Produto'].unique())
    
with st.sidebar.expander('Categoria do produto'):
    categoriaProdutos = st.multiselect('Categoria de produtos', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())
        
with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço',0, 5000, (0, 5000))
    
with st.sidebar.expander('Frete do produto'):
    frete = st.slider('Selecione o valor do frete', 0, 500, (0, 500))
    
with st.sidebar.expander('Data da compra'):
    dataCompra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))

with st.sidebar.expander('Vendedor do produto'):
    vendedor = st.multiselect('Selecione o vendedor', dados['Vendedor'].unique(), dados['Vendedor'].unique())   
    
with st.sidebar.expander("Local da Compra"):
    localCompra = st.multiselect('Selecione o local da compra', dados['Local da compra'].unique(), dados['Local da compra'].unique()) 

with st.sidebar.expander('Avaliação da Compra'):
    avaliacaoCompra = st.slider('Escolha a avaliação da compra', 0, 3, (0, 3))

with st.sidebar.expander('Tipos de Pagamento'):
    tipoPagamento = st.multiselect('Escolha a forma de pagamento', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())

query = ''' 
Produto in @produtos  and \
`Categoria do Produto` in @categoriaProdutos and \
@preco[0] <= Preço <= @preco[1] and \
@frete[0] <= Frete <= @frete[1] and \
@dataCompra[0] <= `Data da Compra` <= @dataCompra[1] and \
Vendedor in @vendedor and \
`Local da compra` in @localCompra and \
@avaliacaoCompra[0] <= `Avaliação da compra` <= @avaliacaoCompra[1] and \
`Tipo de pagamento` in @tipoPagamento
''' 
#Na variávei produtos(@produtos) será selecionado apenas os itens selecionados no multiselect. | O query é da biblioteca pandas.
    #Quando é um slider, pega a variável do preço mínimo(preco[0]) e o preço máximo(preco[1]) e verifica se a coluna Data de comrpa está dentro do intervalo
    #No cado do date é a msm coisa
    #A crase é usada quando o nome da coluna tem crase
    #Isso se aplica as demais situações
    
dadosFiltrados = dados.query(query)
dadosFiltrados = dadosFiltrados[colunas]
st.dataframe(dadosFiltrados)

st.markdown(f'A tabela possui :blue[{dadosFiltrados.shape[0]}] linhas e :blue[{dadosFiltrados.shape[1]}] colunas')
st.markdown('Escreva um nome para o arquivo')
coluna1,coluna2 = st.columns(2)
with coluna1:
    nomeArquivo = st.text_input('', label_visibility='collapsed', value =  'dados')
    nomeArquivo += '.csv'
with coluna2:
    st.download_button('Fazer o download da tabela em csv', data = converteCSV(dadosFiltrados), file_name= nomeArquivo, mime = 'text/csv', on_click=mensagemSucesso)
