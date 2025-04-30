import streamlit as st
from datetime import date
from plots import *





#Layout da Página
st.set_page_config(page_title="Comparação de Ações", layout="wide", page_icon="📊")


#Configuração da barra lateral
with st.sidebar:
    st.subheader("**Comparação de Ações**", help="Página de comparação de ações",anchor="sidebar")
    #st.markdown(":blue[**Configurações das Visualizações**]", help="Selecione as empresas e o intervalo\
    #            \n de datas que gostaria de visualizar")
    st.markdown(":blue[**Selecione o tipo de Análise**]", help="Escolha abaixo o tipo de análise")
    with st.expander("**Seleção da Visualização**"):
        tipo = st.radio(":blue[Selecione o tipo de visualização]", ("Gráficos de Velas", 
                                    "Tendência de Preço", "Variação", "Volume de Negociações", "Bandas de Bollinger"), 
                        index=0, help="Selecione o tipo de gráfico que gostaria de visualizar")
            
    with st.expander("**Seleção de empresas e datas**", expanded=True):
        empresas = ["Tesla", "General Motors", "Ford", "Toyota", "Volkswagen", "BYD"] #Lista de empresas disponibilizadas para análise
        empresa_selecionada = st.selectbox("Selecione a primeira empresa que gostaria de comparar ", empresas, index=0)
        empresa_selecionada_2 = st.selectbox("Selecione a segunda empresa que gostaria de comparar", empresas, index=1)
        data_inicio = st.date_input("Insira a data Inicial", date(2025, 3,26))        
        data_final = st.date_input("Insira a data Final", date.today()) 
    visualizar = st.button("Visualizar")

try:    
    dados1 = Gerador_de_graficos(data_inicio, data_final, empresa_selecionada)
    dados2 = Gerador_de_graficos(data_inicio, data_final, empresa_selecionada_2)
    dados1, medias_moveis1, variacao_perc1 = dados1.Gerador_de_calculos()
    dados2, medias_moveis2, variacao_perc2 = dados2.Gerador_de_calculos()
    if empresa_selecionada == empresa_selecionada_2:
            st.error("As empresas selecionadas são iguais, por favor selecione empresas diferentes para comparação", icon="🚨")
    if visualizar and tipo== "Gráficos de Velas":        
        grafico1 = Grafico_velas(dados1)
        grafico2 = Grafico_velas(dados2)        
     
        st.header(f"Comparação entre as ações das empresas - {empresa_selecionada} e {empresa_selecionada_2}", divider="green")           
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div style='font-size: 22px; font-weight: bold'>Ações da Empresa: {empresa_selecionada}", unsafe_allow_html=True)
            st.plotly_chart(grafico1, use_container_width=True)
        with col2:                    
            st.markdown(f"<div style='font-size: 22px; font-weight: bold'>Ações da Empresa: {empresa_selecionada_2}", unsafe_allow_html=True)
            st.plotly_chart(grafico2, use_container_width=True)

        st.markdown("<div style='font-size: 35px; font-weight: bold; color: #026d04'>Identificação de Oportunidades</div>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid #026d04'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 25px; font-weight: bold'>Compare facilmente as oscilações no mercado financeiro.</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 21px; font-weight: serif'>Os dias com maiores variações positivas e negativas \
                    (destacados em verde e vermelho) ajudam a identificar momentos cruciais de compra e venda.\
                    Essas informações são muito valiosas para estratégias de investimento baseadas em dados históricos\
                    e essenciais para investidores que desejam avaliar os potenciais riscos antes de realizar um investimento.</div>", unsafe_allow_html=True) 

    if visualizar and tipo == "Tendência de Preço":
        st.header(f"Comparação da Tendência de Preço das empresas - {empresa_selecionada} e {empresa_selecionada_2}", divider="blue")
        
        col1, col2 = st.columns(2)
        with col1:            
            grafico_medias_moveis = Grafico_linhas_tendencia(medias_moveis1) #Gráfico de Médias Móveis (1ª empresa)
            grafico_medias_moveis.update_layout(title=f"Tendência de preço da empresa: {empresa_selecionada} ",
                                                 xaxis_title="Data", yaxis_title="Valor das Ações", 
                                        yaxis=(dict(titlefont=dict(size=17), tickformat=",.2f")))
            grafico_medias_moveis.update_traces(text="Data",  textposition="middle center", hovertemplate="Valor das Ações: %{y}<br>Data: %{x}")
            st.markdown("<div style='font-size: 22px; font-weight: bold'>Identifique a tendência", unsafe_allow_html=True)                                
            st.plotly_chart(grafico_medias_moveis, use_container_width=True)  

        with col2:
            grafico_medias_moveis2 = Grafico_linhas_tendencia(medias_moveis2 ) #Gráfico de Médias Móveis (2ª empresa)
            grafico_medias_moveis2.update_layout(title=f"Tendência de preço da empresa {empresa_selecionada_2} ",
                                                  xaxis_title="Data", yaxis_title="Valor das Ações", 
                                        yaxis=(dict(titlefont=dict(size=19), tickformat=",.2f")))
            grafico_medias_moveis2.update_traces(text="Data", textposition="middle center", hovertemplate="Valor das Ações: %{y}<br>Data: %{x}")
            st.markdown("<div style='font-size: 22px; font-weight: bold'>Identifique a tendência", unsafe_allow_html=True)
            st.plotly_chart(grafico_medias_moveis2, use_container_width=True)
        st.markdown("<div style='font-size: 35px; font-weight:bold; color: #07B8FB'>Identificação da Tendência</div>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid #07B8FB'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 25px; font-weight: bold'>Identifique e compare facilmente a tendência de preços.</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 20px; font-weight: serif'> Estes gráficos suavizam as oscilações nos preços das ações,\
                     eliminando variações que dificultam a identificação das tendências gerais, como aumento, queda ou estabilidade no preço.\
                     \n Além disso, uma linha de tendência é traçada ajudando a identificar rapidamente a tendência das ações.</div>", unsafe_allow_html=True)
        
        

    if visualizar and tipo == "Variação":
        st.subheader(f"Comparação da Variação de preço das empresas - {empresa_selecionada} e {empresa_selecionada_2}", divider="blue")
        
        col1, col2 = st.columns(2)
        with col1:
            grafico_variacao = Grafico_linhas_values(variacao_perc1) #Gráfico de Variação Percentual (1ª empresa)
            grafico_variacao.update_layout(title=f"Variação Percentual da empresa {empresa_selecionada} ", 
                                yaxis_title="Variação Percentual", 
                                yaxis=dict(titlefont=dict(size=19), tickformat=",.2f"))
            grafico_variacao.update_traces( hovertemplate="Variação Percentual: %{y}%<br>Data: %{x} ")
            grafico_variacao.add_hline(y=0, line_color="white", line_width=1.5, line_dash="dash")
            st.markdown("<div style='font-size: 22px; font-weight: bold'>Identifique a variação percentual", unsafe_allow_html=True)
            st.plotly_chart(grafico_variacao, use_container_width=True)

        with col2:
            grafico_variacao2 = Grafico_linhas_values(variacao_perc2) #Gráfico de Variação Percentual (2ª empresa)
            grafico_variacao2.update_layout(title=f"Variação Percentual da empresa {empresa_selecionada_2}",    
                                yaxis_title="Variação Percentual", yaxis=dict(titlefont=dict(size=17), tickformat=",.2f"))
            grafico_variacao2.update_traces( hovertemplate="Variação Percentual: %{y}%<br>Data: %{x} ")
            grafico_variacao2.add_hline(y=0, line_color="white", line_width=1.5, line_dash="dash")
            st.markdown("<div style='font-size: 22px; font-weight: bold'>Identifique a variação percentual", unsafe_allow_html=True)
            st.plotly_chart(grafico_variacao2, use_container_width=True)  
        st.markdown("<div style='font-size: 35px; font-weight: bold; color: #07B8FB'>Compare facilmente a variação percentual", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid #07B8FB'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 25px; font-weight: bold'>Identifique e compare facilmente a variação percentual.</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 22px; font-weight:serif'>Estes gráficos mostram a variação percentual \
                            das ações ao longo do tempo, ajudando a identificar rapidamente os momentos de picos\
                     e quedas acentuadas no valor das ações.</div>", unsafe_allow_html=True)


    if visualizar and tipo == "Volume de Negociações":
        st.subheader(f"Comparação do Volume de Negociações das empresas - {empresa_selecionada} e {empresa_selecionada_2}", divider="blue")
        
        col1, col2 = st.columns(2)
        with col1:
               #Atualização dos Eixos e títulos
            grafico_volume = Grafico_barras(dados1, "Volume de Negociações")  #Gráfico de Volume (1ª empresa)
            grafico_volume.update_layout(title=f"Identifique períodos de maior atividade na empresa {empresa_selecionada} ", yaxis_title="Volume de Negociações",
                                xaxis=dict(type="category"), yaxis=dict(titlefont=dict(size=17), tickformat=",.0f"))
            grafico_volume.update_traces(text="Volume de Negociações", textposition="none", hovertemplate="Volume de Negociações: %{y}<br>Data: %{x}")
            st.markdown(f"<div style='font-size: 22px; font-weight: bold'>Volume de Negociações da empresa: {empresa_selecionada}", unsafe_allow_html=True)
            st.plotly_chart(grafico_volume, use_container_width=True)

        with col2:
               #Atualização dos Eixos e títulos
            grafico_volume2 = Grafico_barras(dados2, "Volume de Negociações")  #Gráfico de Volume (2ª empresa)
            grafico_volume2.update_layout(title=f"Identifique períodos de maior atividade na empresa {empresa_selecionada_2} ", yaxis_title="Volume de Negociações",
                                        xaxis=dict(type="category"), yaxis=dict(titlefont=dict(size=17), tickformat=",.0f"))
            grafico_volume2.update_traces(text="Volume de Negociações", textposition="none", hovertemplate="Volume de Negociações: %{y}<br>Data: %{x}")
            st.markdown(f"<div style='font-size: 22px; font-weight: bold'>Volume de Negociações da empresa: {empresa_selecionada_2}", unsafe_allow_html=True)
            st.plotly_chart(grafico_volume2, use_container_width=True)              
        st.markdown("<div style='font-size: 35px; font-weight: bold; color: #07B8FB'>Identifique o volume de negociações", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid #07B8FB'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 25px; font-weight: bold'>Identifique e compare facilmente o volume de negociações.</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 22px; font-weight: serif'>Isso ajuda a entender quais dias tiveram maior engajamento e atividade no mercado financeiro,\
                     destacando os momentos que podem ter sido influenciados por notícias,eventos econômicos ou decisões empresariais importantes.\
                    Utilize juntamente com as bandas de bollinger para decisões de investimento mais informadas e confiáveis.</div>", unsafe_allow_html=True)
            
    elif visualizar and tipo == "Bandas de Bollinger":
        st.header(f"Comparação das Bandas de Bollinger das empresas - {empresa_selecionada} e {empresa_selecionada_2}", divider="blue")
        col1, col2 = st.columns(2)
        with col1:
            grafico_bollinger = Grafico_bollinger(dados1) #Gráfico de Bandas de Bollinger (1ª empresa)
            st.markdown(f"<div style='font-size: 22px; font-weight: bold'>Bandas de Bollinger da empresa: {empresa_selecionada}", unsafe_allow_html=True)
            grafico_bollinger.update_layout(title=f"Identifique períodos de maior atividade na empresa {empresa_selecionada} ", yaxis_title="Valor das Ações",
                                xaxis=dict(type="category"), yaxis=dict(titlefont=dict(size=17), tickformat=",.2f"))
            grafico_bollinger.update_traces(text="Valor das Ações", textposition="middle center", hovertemplate="Valor das Ações: %{y}<br>Data: %{x}")
            st.plotly_chart(grafico_bollinger, use_container_width=True)
        with col2:
            bollinger2 = Grafico_bollinger(dados2) #Gráfico de Bandas de Bollinger (2ª empresa)
            st.markdown(f"<div style='font-size: 22px; font-weight: bold'>Bandas de Bollinger da empresa: {empresa_selecionada_2}", unsafe_allow_html=True)
            bollinger2.update_layout(title=f"Identifique períodos de maior atividade na empresa {empresa_selecionada_2} ", yaxis_title="Valor das Ações",
                                xaxis=dict(type="category"), yaxis=dict(titlefont=dict(size=17), tickformat=",.2f"))
            bollinger2.update_traces(text="Valor das Ações", textposition="middle center", hovertemplate="Valor das Ações: %{y}<br>Data: %{x}")
            st.plotly_chart(bollinger2, use_container_width=True)

        st.markdown("<div style='font-size: 35px; font-weight: bold; color: #07B8FB'>Identifique a volatilidade do mercado", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid #07B8FB'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 25px; font-weight: bold'>Identifique e compare facilmente a volatilidade do mercado.</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 22px; font-weight: serif'>As Bandas de Bollinger ajudam a visualizar\
                    a faixa normal dos preços e a identificar quando os valores se afastam dessa faixa. Quando o preço toca \
                    a banda superior ou inferior, isso sinaliza momentos de sobrecompra ou sobrevenda, respectivamente,\
                     servindo como alerta para possíveis reversões ou manutenção de tendências.", unsafe_allow_html=True)

except Exception as erro:
    st.error(f"Ocorreu um erro, por favor, tente novamente.\nErro: {erro}", icon="🚨")
        
        