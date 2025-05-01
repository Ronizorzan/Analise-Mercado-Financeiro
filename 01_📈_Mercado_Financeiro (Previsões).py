import streamlit as st
import pandas as pd
from datetime import date
from plots import *
from joblib import load
from tensorflow.keras.models import load_model
from sklearn.metrics import root_mean_squared_error




#Layout da Página
st.set_page_config(page_title="Análise de Mercado Financeiro", layout="wide", page_icon="📊")


#Configuração da barra lateral
with st.sidebar:    
    st.subheader("**Análises Financeiras e Previsões**", help="Página de Análises Financeiras \
             \n e Previsão das Ações da Tesla")
    st.markdown(":blue[**Configurações das Visualizações**]", help="Selecione a empresa e o intervalo\
                \n de datas que gostaria de visualizar")
    with st.expander("**Seleção de empresas e datas**"):
        empresas = ["Tesla", "General Motors", "Ford", "Toyota", "Volkswagen", "BYD"] #Lista de empresas disponibilizadas para análise
        empresa_selecionada = st.selectbox("Selecione a empresa que gostaria de analisar", empresas, index=0)
        data_inicio = st.date_input("Insira a data Inicial", date(2025, 3,26))        
        data_final = st.date_input("Insira a data Final", date.today())                
    st.markdown(":blue[**Selecione o tipo de Análise**]", help="Escolha abaixo entre previsão e análise")
    with st.expander("Seleção das Visualizações", expanded=True):
        tipo = st.radio("Análise ou previsão de Ações", ["Análise", "Previsão"])
        horizonte_previsao = st.number_input("Quantos dias gostaria de Prever?", min_value=1, max_value=30, value=6, help="Valor Máximo de 15 dias")
    processar = st.button("Processar")            
if processar:
    try:
        dados = Gerador_de_graficos(data_inicio, data_final, empresa_selecionada)          
    
    except yf.YFRateLimitError:
        
        dados = baixar_dados(data_inicio , data_final)           
    else:
        dados, medias_moveis, variacao_perc = dados.Gerador_de_calculos()            
        grafico_velas = Grafico_velas(dados) #Gráfico de Velas já vem com todos os cálculos e customizações efetivados

        #Atualização dos eixos e títulos
        grafico_medias_moveis = Grafico_linhas_tendencia(medias_moveis, True ) #Gráfico de Médias Móveis    
        grafico_medias_moveis.update_layout(title="Identifique a tendência", xaxis_title="Data", yaxis_title="Valor das Ações", 
                                                yaxis=(dict(titlefont=dict(size=17), tickformat=",.2f")))
        grafico_medias_moveis.update_traces(text="Data", textposition="top right", hovertemplate="Valor das Ações: %{y}<br>Data: %{x}")    
        
        #Atualização dos Eixos e títulos
        grafico_variacao = Grafico_linhas_tendencia(variacao_perc, legenda="Sem variação")  #Gráfico de Variação Percentual 
        grafico_variacao.update_layout(title="Descubra a Variação Percentual", 
                                    yaxis_title="Variação Percentual", yaxis=dict(titlefont=dict(size=16), tickformat=",.2f"))
        grafico_variacao.update_traces( hovertemplate="Variação Percentual: %{y}%<br>Data: %{x} ", 
                                    line=dict(color="#07B8FB", width=2))
        grafico_variacao.add_hline(y=0, line_color="white", line_width=1.5, line_dash="dash")
                
        #Atualização dos Eixos e títulos
        grafico_volume = Grafico_barras(dados, "Volume de Negociações")  #Gráfico de Volume               
        grafico_volume.update_layout(title="Identifique períodos de maior atividade no mercado", yaxis_title="Volume de Negociações",
                                    xaxis=dict(type="category"), yaxis=dict(titlefont=dict(size=16), tickformat=",.0f"))
        grafico_volume.update_traces(text="Volume de Negociações", textposition="none", hovertemplate="Volume de Negociações: %{y}<br>Data: %{x}")
        
        grafico_boolinger = Grafico_bollinger(dados)    
        
        st.title(f"Análise das Ações da {empresa_selecionada} ") 
        tab1, tab2, tab3 = st.tabs(["Gráfico de Velas", "Análise Estatística", "Análise de Compras e Vendas"])     
    with tab1:              #Exibição do Gráfico de Velas
            st.header("Gráfico de Velas", divider="green")
            st.plotly_chart(grafico_velas, use_container_width=True)  
            st.markdown(":green[***Descrição:***]  *Este painel apresenta uma análise visual detalhada dos valores das ações ao longo do período selecionado, \
                         utilizando gráficos de velas altamente intuitivos. Cada vela encapsula informações cruciais do mercado: valores de abertura, fechamento, \
                        máximos e mínimos, proporcionando um panorama completo das oscilações diárias. Além disso, o gráfico identifica os dias de maior impacto  \
                        positivo e negativo, permitindo uma análise estratégica. Ferramentas interativas, como zoom e filtros avançados, garantem uma experiência \
                        personalizada e imersiva. Este recurso é ideal para acompanhar tendências, projetar estratégias e tomar decisões informadas no mercado financeiro.*")
                  
            
    with tab2:   
            st.subheader("Análises Estatísticas", divider="blue")    
            col1, col2 = st.columns(2)
            with col1:                                
                st.plotly_chart(grafico_medias_moveis, use_container_width=True)
                st.markdown(":blue[***Propósito:***] *Este gráfico apresenta o valor das ações ao longo do período de tempo selecionado, usando uma média móvel.\
                    A média móvel suaviza as oscilações diárias nos preços das ações, eliminando 'ruídos' e tornando mais fácil identificar tendências gerais, como aumento, queda ou estabilidade no preço.*")
                st.markdown(":blue[***O que observar?***]")
                st.markdown(":green[**Subidas Constantes:**] *Podem indicar valorização contínua das ações*")
                st.markdown(":orange[**Períodos de Estabilidade:**] *Indicam que o preço não está variando muito, sugerindo equilíbrio*")
                st.markdown(":red[**Quedas Frequentes:**] *Podem sugerir períodos de desvalorização*" )
                    

            with col2:
                 st.plotly_chart(grafico_variacao, use_container_width=True)
                 st.markdown(":blue[***Propósito:***] *Este gráfico calcula o quanto o preço das ações mudou, em termos percentuais, de um dia de fechamento para o outro. \
                             Diferente das variações calculadas dentro de um único dia, como a do gráifco de Velas (valor de abertura versus fechamento),\
                             este gráfico destaca a mudança geral entre dias consecutivos.*")
                 st.markdown(":blue[***O que observar?***]")
                 st.markdown(":green[***Variações Positivas***] *Indicam aumento nas ações em relação ao dia anterior*")
                 st.markdown(":orange[***Mudanças Bruscas***] *Apontam possíveis eventos ou notícias que impactaram o mercado*")
                 st.markdown(":red[***Mudanças Negativas***] *Mostram que o preço das ações caiu em relação ao dia anterior*")

    with tab3:    
        st.subheader("Análises de Volume e Bollinger", divider="blue")
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            st.plotly_chart(grafico_volume, use_container_width=True) 
            st.markdown(":green[***Descrição:***] *Este gráfico mostra a quantidade de ações negociadas diariamente dentro do período selecionado. \
                        Barras mais altas indicam dias em que houve maior movimentação dos investidores, ou seja, quando mais pessoas compraram ou venderam ações. \
                        Isso ajuda a entender quais dias tiveram maior engajamento e atividade no mercado financeiro, destacando os momentos que podem ter \
                        sido influenciados por notícias,eventos econômicos ou decisões empresariais importantes.* ")

        with col2:
            st.plotly_chart(grafico_boolinger, use_container_width=True)
            st.markdown(":green[***Descrição:***] *Este gráfico utiliza três linhas para apresentar a evolução do preço das ações ao longo do período: \
                        o valor de fechamento diário e duas faixas chamadas banda superior e banda inferior. Essas faixas, conhecidas como “Bandas de Bollinger”,\
                        destacam os momentos de maior instabilidade no mercado, onde o preço das ações varia mais do que o normal.\
                        Isso é útil para identificar tendências e períodos de risco ou oportunidade, especialmente para investidores que buscam aproveitar essas oscilações.*")


elif processar and "Previsão":
     st.subheader("Previsão de Ações da Tesla", divider="blue")
     col1, col2 = st.columns([0.55,0.45], gap="medium")
     with col1:
        dados = pd.read_csv("dados_teste.csv")                   
        
        
        grafico_previsoes = Grafico_linhas_previsoes(dados)
        rmse = root_mean_squared_error(dados["Valores Reais"], dados["Previsões"])
        grafico_previsoes.update_layout(xaxis_title=f"Erro do Modelo (RMSE): {rmse:.2f} ", yaxis=dict(titlefont=dict(size=16), tickformat=",.2f"), 
                                        title="Comparação Previsão do Modelo x Valores Reais")
        st.plotly_chart(grafico_previsoes, use_container_width=True)    
        st.markdown(":blue[***Propósito:***] *Previsão de Alta Precisão para Ações da Empresa. Explore um painel inovador que transforma dados em insights financeiros valiosos.\
                Com uma interface que combina praticidade e análise robusta, visualize comparações entre valores reais e previstos, enquanto projeta tendências futuras com base em algoritmos de ponta.\
                Do desempenho histórico às previsões futuras, mergulhe nos gráficos que revelam a verdadeira essência do mercado financeiro.\
                Com indicadores como RMSE, avalie a acurácia e tenha uma idéia concreta da confiabilidade do modelo.*")
        

     with col2:
         modelo = load_model("Modelo_treinado_close.keras")
         scaler = load("scaler_close.joblib")         
         novas_previsoes = Gerador_Previsoes_RN(horizonte_previsao, dados["Valores Reais"], modelo, scaler, 30)
         novas_previsoes_df = pd.DataFrame({"Previsões Futuras": novas_previsoes.flatten()}, 
                                           index=pd.date_range("2025-04-28", periods=len(novas_previsoes), freq="B"))
         grafico_novas_previsoes = Grafico_linhas(novas_previsoes_df, "Previsões Futuras")
         grafico_novas_previsoes.update_layout(xaxis_title="Data", yaxis_title="Valor das Ações", 
                                        yaxis=dict(titlefont=dict(size=16), tickformat=",.2f"), title="Previsões Futuras das Ações da Tesla")
         st.plotly_chart(grafico_novas_previsoes, use_container_width=True)       
         st.markdown(":blue[***Propósito:***] *Este gráfico oferece a opção de gerar previsões futuras permitindo extrapolar além dos dados históricos disponíveis. \
                     Mas observe que essas previsões são obtidas através de uma Rede Neural — que integra Redes Neurais Convolucionais para captar padrões e Redes Neurais Recorrentes para modelar dependências temporais.\
                     É importante ressaltar que, para gerar essas projeções, o modelo utiliza uma estratégia iterativa, ou seja, suas próprias previsões servem de entrada\
                     para estimar eventos subsequentes. Essa abordagem pode levar ao chamado 'Erro Acumulado', que tende a se intensificar à medida que as previsões se estendem para horizontes mais distantes.\
                     Portanto, embora essas previsões utilizem técnicas avançadas e ofereçam uma visão poderosa sobre o futuro, é recomendável utilizá-las\
                     com cautela e sempre considerar análises adicionais para tomar decisões mais embasadas.*")         
     
     

     
        
        
             
              
            

    


    

