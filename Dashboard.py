import streamlit as st
import requests 
import pandas as pd
import plotly.express as px

st.set_page_config(layout= 'wide')

def formataNumero(valor, prefixo = ''):
    for unidade in ['', 'mil']: #Um loop que percorre a lista, se o valor for menor que 1000, ele retorna o valor com a primeira unidade da lista, caso contrário, o valor é dividido por 1000 e o loop volta e retorna o valor com a unidade mil.
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'  #Na segunda iteração, o valor já terá sido dividido por mil
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões' #Nessa linha, se nenhuma das duas condições anteriores forem atendidas, o valor já terá sido dividido por 1000 duas vezes.    

st.title("DASHBOARD DE VENDAS :shopping_trolley:")

url = 'https://labdados.com/produtos' #Url da base de dados
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)
if regiao == 'Brasil':
    regiao = '' #Padrão 
    
todosAnos = st.sidebar.checkbox('Dados de todo o período', value = True) #Vaue = True pois ele estará marcado por padrão
if todosAnos: #Se a checkbox estiver marcada
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)
       
queryString = {'regiao': regiao.lower(), 'ano': ano}
response = requests.get(url,params=queryString)
dados = pd.DataFrame.from_dict(response.json()) #Trasforma a resposta em json e coloca em um dataframe
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra' ], format = '%d/%m/%Y')

filtroVendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtroVendedores:
    dados = dados[dados['Vendedor'].isin(filtroVendedores)]                                   

#Tabelas
#Tabela_aba1--
receitaEstados = dados.groupby('Local da compra')[['Preço']].sum() #Agrupa pelo local da compra e soma a tabela de preço 
receitaEstados = dados.drop_duplicates(subset= 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receitaEstados, left_on= 'Local da compra', right_index= True).sort_values('Preço', ascending= False)
#Remove duplicatas → Mantém apenas um registro por 'Local da compra', garantindo que cada local tenha apenas uma coordenada (lat, lon).
#Faz um merge → Junta essas informações com a soma das vendas (Preço) que foi calculada antes com groupby().
#Ordena os dados → Do maior para o menor preço.

receitaMensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'M'))['Preço'].sum().reset_index() #Soma as vendas de cada mês
receitaMensal['Ano'] = receitaMensal['Data da Compra'].dt.year 
receitaMensal['Mes'] = receitaMensal['Data da Compra'].dt.month_name() 

receitaCategorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

#Tabela_aba2--
quantidadeEstado = dados.groupby('Local da compra')['Produto'].count()
quantidadeEstado = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(quantidadeEstado, left_on= 'Local da compra', right_index=True).sort_values('Produto',ascending=False)

quantidadeMensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'M'))['Produto'].count().reset_index()
quantidadeMensal['Ano'] = quantidadeMensal['Data da Compra'].dt.year
quantidadeMensal['Mes'] = quantidadeMensal['Data da Compra'].dt.month_name()

quantidadeCategoria = dados.groupby('Categoria do Produto')['Produto'].count().sort_values(ascending=False)

#Tabela_aba3--
vendedores = dados.groupby('Vendedor')['Preço'].agg(['sum', 'count'])



#Gráficos
#Gráficos aba1
figMapaReceita = px.scatter_geo(receitaEstados,
                                lat = 'lat',
                                lon = 'lon',
                                scope = 'south america',
                                size = 'Preço',
                                template = 'seaborn',
                                hover_name= 'Local da compra', 
                                hover_data= {'lat': False, 'lon': False},
                                title = 'Receita por estado'
                                )

figReceitaMensal = px.line(receitaMensal,
                           x = 'Mes',
                           y = 'Preço',
                           markers = True,
                           range_y=(0,receitaMensal.max()),
                           color = 'Ano',
                           line_dash = 'Ano',
                           title = 'Receita mensal'
                           )
figReceitaMensal.update_layout(yaxis_title = 'Receita')


figReceitaEstados = px.bar(receitaEstados.head(), #Mostra os 5 primeiros estados com maior receia
                           x = 'Local da compra',
                           y = 'Preço',
                           text_auto=True, #Coloca o valor em cima de cada coluna
                           title = 'Top estados (receita)'
                           ) 
figReceitaEstados.update_layout(yaxis_title = 'Receita')


figReceitaCategorias = px.bar(receitaCategorias,
                              text_auto=True,
                              title = 'Receita por categoria'
                              )

figReceitaCategorias.update_layout(yaxis_title = 'Receita')

#Gráficos aba2--
figMapaQuantidade = px.scatter_geo(quantidadeEstado,
                                lat = 'lat',
                                lon = 'lon',
                                scope = 'south america',
                                size = 'Produto',
                                template = 'seaborn',
                                hover_name= 'Local da compra', 
                                hover_data= {'lat': False, 'lon': False},
                                title = 'Quantidade de produtos vendidos por estado'
                                )


figQuantidadeMensal = px.line(quantidadeMensal,
                              x = 'Mes',
                              y = 'Produto',
                              markers = True,
                              range_y=(0,quantidadeMensal.max()),
                              color = 'Ano',
                              line_dash = 'Ano',
                              title = 'Quantidade de vendas mensal'
                              )
figQuantidadeMensal.update_layout(yaxis_title = 'Quantidade de vendas mensal')

figQuantidadeEstados = px.bar(quantidadeEstado.head(),
                              x = 'Local da compra',
                              y = 'Produto',
                              text_auto=True,
                              title= 'Top 5 estados (Quantidade de vendas)'
                              )
figQuantidadeMensal.update_layout(yaxis_title = 'Top 5 estados (Quantidade de vendas)')

figQuantidadeCategoria = px.bar(quantidadeCategoria,
                                text_auto=True,
                                title = 'Quantidade de produto vendido por categoria'
                                )
figQuantidadeCategoria.update_layout(yaxis_title = 'Quantidade de produto vendido por categoria')



##Visualização no Streamlite
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores']) #Cria abas
with aba1: 
    coluna1, coluna2 = st.columns(2) # Cria as variáveis das colunas e indica o número de colunas dentro do parênteses
    with coluna1: #Coloca a métrica dentro da coluna
        st.metric('Receita', formataNumero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(figMapaReceita, use_container_width = True)
        st.plotly_chart(figReceitaEstados, use_container_width = True)
    with coluna2:
        st.metric('Quantidade de vendas', formataNumero(dados.shape[0])) #O shame nos da a quantidade de linhas ou colunas do dataframe. 0 é linha e 1 é coluna
        st.plotly_chart(figReceitaMensal, use_container_width = True)
        st.plotly_chart(figReceitaCategorias, use_container_width = True )
        
with aba2: 
    coluna1, coluna2 = st.columns(2) 
    with coluna1: 
        st.metric('Receita', formataNumero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(figMapaQuantidade, use_container_width = True)
        st.plotly_chart(figQuantidadeEstados, use_container_width = True)
        
        
    with coluna2:
        st.metric('Quantidade de vendas', formataNumero(dados.shape[0]))
        st.plotly_chart(figQuantidadeMensal, use_container_width = True)
        st.plotly_chart(figQuantidadeCategoria, use_container_width = True )
        
         
    

with aba3: 
    qtdVendedores = st.number_input('Quantidade de vendedores', 2, 10, 5) #No mínimo 2 vendedores, no máximo 10, valor padrão é 5
    coluna1, coluna2 = st.columns(2) 
    with coluna1: 
        st.metric('Receita', formataNumero(dados['Preço'].sum(), 'R$'))
        figReceitaVendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtdVendedores),
                                      x = 'sum',
                                      y = vendedores[['sum']].sort_values('sum', ascending=False).head(qtdVendedores).index,
                                      text_auto=True,
                                      title= f'Top {qtdVendedores} vendedores (receita)'
                                      )
        st.plotly_chart(figReceitaVendedores)
        
    with coluna2:
        st.metric('Quantidade de vendas', formataNumero(dados.shape[0])) 
        figVendasVendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtdVendedores),
                                      x = 'count',
                                      y = vendedores[['count']].sort_values('count', ascending=False).head(qtdVendedores).index,
                                      text_auto=True,
                                      title= f'Top {qtdVendedores} vendedores (Quantidade de vendas)'
                                      ) 
        st.plotly_chart(figVendasVendedores)

st.dataframe(dados)
