#importar bibliotecas
import streamlit as st
import pandas as pd
import plotly.express as px

#--Configuração da página:Definir título e layout--
st.set_page_config(
    page_title="Dashboard Vendas de Chocolates",
    page_icon=":chocolate_bar:",
    layout='wide',
)

#--Carregar os dados--
vendas_df = pd.read_csv("dados-vendas-chocolate.csv")

##--Conversão tipo de dados da coluna Data--
vendas_df['Data'] = pd.to_datetime(vendas_df['Data'])

#--Cores países--
cores_paises = {
    'Australia': '#FFB300',     
    'UK': '#1E3A8A',            
    'India': '#F57C00',          
    'USA': '#1565C0',           
    'Canada': '#C62828',         
    'New Zealand': '#2E7D32'     
}

#--Barra lateral--
st.sidebar.header("Filtros")

#--Filtro Ano--
anos_min = int(vendas_df['Ano'].min())
anos_max = int(vendas_df['Ano'].max())

anos_selecionados = st.sidebar.select_slider(
    "Ano",
    options=list(range(anos_min, anos_max + 1)),
    value=(anos_min, anos_max)
)

#--Filtro Mês--
mes_min = int(vendas_df['Mes'].min())
mes_max = int(vendas_df['Mes'].max())

meses_selecionados = st.sidebar.select_slider(
    "Mês",
    options=list(range(mes_min, mes_max + 1)),
    value=(mes_min, mes_max)
)

#--Filtro País--
paises_disponiveis = sorted(vendas_df['País'].unique())

with st.sidebar.expander("País", expanded=True):
    
    todos_paises = st.checkbox( "Selecione todos", value=True)
    
    if todos_paises:
        paises_selecionados = st.multiselect(
            "",
            paises_disponiveis,
            default=paises_disponiveis
        )
    else:
        paises_selecionados = st.multiselect(
            "",
            paises_disponiveis
        )    
        
#--Filtro Produto--
with st.sidebar.expander("Produto", expanded=False):

    produtos_filtrados = (
        vendas_df[vendas_df['País'].isin(paises_selecionados)]
        ['Produto']
        .unique()
    )

    todos_produtos = st.checkbox("Selecionar todos os produtos", value=True)

    if todos_produtos:
        produtos_selecionados = st.multiselect(
            "",
            sorted(produtos_filtrados),
            default=sorted(produtos_filtrados)
        )
    else:
        produtos_selecionados = st.multiselect(
            "",
            sorted(produtos_filtrados)
        )

#--Filtragem do DataFrame: Com base da barra lateral--
df_filtrado = vendas_df[
    (vendas_df['Ano'].between(anos_selecionados[0], anos_selecionados[1])) &
    (vendas_df['Mes'].between(meses_selecionados[0], meses_selecionados[1])) &
    (vendas_df['País'].isin(paises_selecionados)) &
    (vendas_df['Produto'].isin(produtos_selecionados))
]

#--Conteúdo Principal--
st.title("Análise de Dados da Venda de Chocolates")
st.markdown("Explore os dados sobre a venda de chocolates em alguns paises e utilize o filtro a esquerda.")

#--Métricas principais (KPIs)--
st.subheader("Métricas gerais")

#--Valor tottal--
valor_total = df_filtrado['Valor'].sum() if not df_filtrado.empty else 0

#--Valor Médio--
valor_medio = df_filtrado['Valor'].mean() if not df_filtrado.empty else 0
    
#--Caixas enviadas--
total_caixas = df_filtrado['Caixas Enviadas'].sum() if not df_filtrado.empty else 0    

#--Ticket médio--
if not df_filtrado.empty and total_caixas > 0:
    ticket_medio = valor_total / total_caixas
else:
    ticket_medio = 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Valor médio", f"${valor_medio:,.0f}")
col2.metric("Faturamento Total", f"${valor_total:,.0f}")
col3.metric("Caixas enviadas", f"{total_caixas:,.0f}")
col4.metric("Ticket médio", f"${ticket_medio:,.0f}")

st.markdown("---")

#--Análise visuais com Plotly--
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        df_pais = (
            df_filtrado
            .groupby('País', as_index=False)['Valor']
            .sum()
            .sort_values(by='Valor', ascending=False)
            .reset_index(drop=True)
        )

        df_pais['Valor_milhoes'] = df_pais['Valor'] / 1_000_000
        
        fig = px.bar(
            df_pais,
            x='País',
            y='Valor_milhoes',
            title='Faturamento por País',
            color='País',
            color_discrete_map=cores_paises,
            labels={
                'Valor_milhoes':'Faturamento (R$ milhões)',
                'País': 'País'
            },
            hover_data={
                'Valor_milhoes': ':.2f',
                'Valor': ':.2f'
            }
        )

        fig.update_yaxes(tickformat=',.2f')
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico.")
        
with col_graf2:
    if not df_filtrado.empty:        
        df_produto = (
            df_filtrado
            .groupby('Produto', as_index=False)['Valor']
            .sum()
            .sort_values(by='Valor', ascending=False)
            .reset_index(drop=True)
        )

        df_produto['Valor_milhoes'] = df_produto['Valor'] / 1_000_000
        
        cores_produtos = {
            'Chocolate Amargo': '#4E342E',
            'Chocolate Ao Leite': '#6D4C41',
            'Chocolate Branco': '#F5F5DC',
            'Chocolate Meio Amargo': '#5D4037'
        }
        
        fig = px.bar(
            df_produto,
            x='Produto',
            y='Valor_milhoes',
            title='Faturamento por Produto',
            color='Produto',
            color_discrete_map=cores_produtos,
            
            labels={
                'Produto':'Produto',
                'Valor_milhoes':'Faturamento (R$ milhões)'
            },
            hover_data={
                'Valor_milhoes':':.2f',
                'Valor':':.2f'
            }   
        )
        
        fig.update_yaxes(tickformat=',.2f')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico.")
            
col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        df_mes = (
            df_filtrado
            .groupby(df_filtrado['Data']
            .dt.to_period('M'))['Valor']
            .sum()
            .reset_index()
        )

        df_mes['Data'] = df_mes['Data'].dt.to_timestamp()

        fig = px.line(
            df_mes,
            x='Data',
            y='Valor',
            title='Evolução do faturamento ao longo do tempo',
            labels={
                'Valor':'Faturamento (R$)'
            }
        )

        fig.update_yaxes(tickformat=',.0f')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico.")
        
with col_graf4:
    if not df_filtrado.empty:
        df_caixas = (
            df_filtrado
            .groupby('País', as_index=False)['Caixas Enviadas']
            .sum()
            .sort_values(by='Caixas Enviadas', ascending=False)
            .reset_index(drop=True)
        )
        
        fig = px.bar(
            df_caixas,
            x='País',
            y='Caixas Enviadas',
            title='Total de Caixas Enviadas por País',
            color='País',
            color_discrete_map=cores_paises
        )
                
        st.plotly_chart(fig, use_container_width=True)
    else:
       st.warning("Nenhum dado disponível para exibir o gráfico.")
       
col_graf5, = st.columns(1)

with col_graf5:
    if not df_filtrado.empty:
        df_scatter = (
            df_filtrado
            .groupby('País', as_index=False)
            .agg({
                'Caixas Enviadas': 'mean',
                'Valor': 'mean'
            })
        )
        
        fig = px.scatter(
            df_scatter,
            x='Caixas Enviadas',
            y='Valor',
            color='País',
            size='Valor',
            title='Valor Médio x Caixas Enviadas (por País)',
            color_discrete_map=cores_paises,
            labels={
               'Caixas Enviadas': 'Caixas Enviadas (média)',
               'Valor': 'Valor Médio (R$)'
            }
        )

        fig.update_yaxes(tickformat=',.0f')
        st.plotly_chart(fig, use_container_width=True)
    else:
       st.warning("Nenhum dado disponível para exibir o gráfico.")
       
st.markdown("---")

#--Tabela de Dados Detalhada--
st.header("Dados Detalhados")
st.dataframe(df_filtrado)
