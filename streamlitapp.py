# Importando bibliotecas
import streamlit as st
from streamlit_gsheets import GSheetsConnection
# from unidecode import unidecode
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
import numpy as np
import math

# Usando largura completa da tela
st.set_page_config(layout="wide")

# Criando a conexão
conn = st.connection("gsheets", type=GSheetsConnection)

# Lendo o arquivo
df = conn.read(
    worksheet="resultados",
    usecols=list(range(11))
)

# Dropando linhas nulas
df.dropna(how='all', inplace=True)
# st.dataframe(df)

# Alterando tipo das colunas
df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
df['Data'] = df['Data'].dt.date
df['Tempo'] = df['Tempo'].str.replace(',', '.')
df['Tempo'] = df['Tempo'].astype(float)

# Lista de atletas
atletas = df['Nome'].unique()
atletas.sort()

# Dataframe pra cada atleta
# dataframes_atletas = []
# for atleta in atletas:
#     name = f'df_{unidecode(atleta.replace(" ", "_")).lower()}'
#     globals()[name] = df[df['Nome'] == atleta]
#     dataframes_atletas.append(name)

########## -------------- STREAMLIT APP -------------- ##########

# Imagem banner
imagem_url = "https://drive.google.com/uc?export=view&id=1JP59eNZOFegqtDIclf3KmG0HKGamlI7O"
st.sidebar.image(imagem_url, use_column_width=True)

# SelectboxColumn
atleta = st.sidebar.selectbox('$\sf \large{Atleta}$', atletas)
prova = df[df['Nome']==atleta]['Prova'].unique()
prova.sort()
prova_atleta = st.sidebar.selectbox('$\sf \large{Prova}$', prova)
datas = df[(df['Nome'] == atleta) & (df['Prova'] == prova_atleta)]['Data']
anos = [data.year for data in datas]
ano = list(set(anos))
ano.sort()
ano.insert(0, 'Todos')
ano_atleta = st.sidebar.selectbox('$\sf \large{Ano}$', ano)
if ano_atleta == 'Todos':
    piscina = df[(df['Nome']==atleta)&(df['Prova']==prova_atleta)]['Piscina'].unique()
else:
    piscina = df[(df['Nome']==atleta)&(df['Prova']==prova_atleta)&(df['Data'].dt.year==int(ano_atleta))]['Piscina'].unique()
piscina_atleta = st.sidebar.selectbox('$\sf \large{Piscina}$', piscina, )
st.sidebar.text('\n\nCriado por:\nCarol Yumi e Gui Messias')

# Title, header, subheader
st.title('Natação UFSCar - Análise de resultados')
st.markdown('##')
st.subheader(f'Atleta: {atleta}')
st.subheader(f'Prova: {prova_atleta}')

# Gráfico
if ano_atleta == 'Todos':
    df_atleta = df[(df['Nome']==atleta)&(df['Prova']==prova_atleta)&(df['Piscina']==piscina_atleta)]
else:
    df_atleta = df[(df['Nome']==atleta)&(df['Prova']==prova_atleta)&(df['Piscina']==piscina_atleta)&(df['Data'].dt.year==int(ano_atleta))]
df_atleta = df_atleta.sort_values(by = 'Data')
df_display = df_atleta.rename(columns={'Tempo_str': 'Tempo oficial'})

st.dataframe(df_display[['Data', 'Categoria', 'Tempo oficial', 'Campeonato', 'Colocação', 'Local']], hide_index=True)

# selecionar só o menor tempo de uma data duplicada

df_atleta = df_atleta.groupby(['Data', 'Prova']).agg({'Tempo' : 'min', 'Campeonato' : 'first', 'Local' : 'first'}).reset_index()

tempo_min = df_atleta['Tempo'].min()
tempo_min = math.floor(tempo_min)
tempo_max = df_atleta['Tempo'].max()
tempo_max = math.ceil(tempo_max)
def segundos_para_minutos_segundos_centesimos(segundos):
    minutos = int(segundos // 60)
    segundos_restantes = segundos % 60
    segundos_int = int(segundos_restantes)
    centesimos = int((segundos_restantes - segundos_int) * 100)
    return f"{minutos}:{segundos_int:02d}.{centesimos:02d}"
tempo_min_formatado = segundos_para_minutos_segundos_centesimos(tempo_min)
tempo_max_formatado = segundos_para_minutos_segundos_centesimos(tempo_max)
# num_ticks = 6
num_ticks = tempo_max - tempo_min + 3
valores_de_ticks_y = np.linspace(tempo_min-1, tempo_max+1, num_ticks)
valores_de_ticks_y_formatados = [segundos_para_minutos_segundos_centesimos(val) for val in valores_de_ticks_y]

fig = px.line(df_atleta, x = 'Data', y = 'Tempo', hover_data=['Campeonato', 'Local'])
fig.update_traces(mode="markers+lines", line=dict(color="#DD0000", width=4),
                  marker=dict(size=12),
                  hoverlabel=dict(bordercolor="white", font=dict(size=18)))
fig.update_xaxes(
    title='Data',
    # ticktext=df_atleta['Data'].apply(lambda x: x.strftime('%m/%y')),
    ticktext=df_atleta['Data'].apply(lambda x: x.strftime('%b/%y')),
    # ticktext=df_atleta['Data'],
    tickvals=df_atleta['Data'],
    tickfont = dict(size=18, color='white'), 
    titlefont = dict(size=21, color='white')
)
fig.update_yaxes(
    title='Tempo',
    ticktext=valores_de_ticks_y_formatados, #df_atleta['Tempo_str'],
    tickvals=valores_de_ticks_y, #df_atleta['Tempo'],
    tickfont = dict(size=18, color='white'),
    titlefont = dict(size=21, color='white'),
    showgrid=True, gridcolor='gray', gridwidth=0.5, griddash='dash',
    range=[df_atleta['Tempo'].min() - 0.4, df_atleta['Tempo'].max() + 0.4]
)
fig.update_layout(
    width=1000,
    plot_bgcolor='rgba(255, 255, 255, 0.98)'
)
# fig.add_vline(x=pd.to_datetime('2023-07-01'), line_width=3, line_color="blue") # Início dos treinos com Colombo
st.plotly_chart(fig)