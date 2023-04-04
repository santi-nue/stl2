import datetime as dt
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import random
import string
import warnings
warnings.filterwarnings('ignore')
import os
import glob
import gc
import requests
from bs4 import BeautifulSoup
from lxml import etree
import time
import re
from io import BytesIO

streamlit_style = """
<style>

.stSelectbox > div[data-baseweb="select"] > div {
    border-radius: 20px;
}

section[data-testid="stFileUploadDropzone"] {
    border-radius: 40px;
}

button {
    border-radius: 20px !important;
    background-color: #B72A4A !important;
    color: #ffffff !important;
    text-align: center !important;
    transition: 0.5s;
    border-color: transparent !important; 
}

button[kind="primary"] {
    width: 100%;
}

.stDownloadButton > button {
    width: 100%;
}

button:hover {
    background-color: #414243 !important;
    transform: scale(1.05);
}

button:active {
    background-color: #414243 !important;
    transform: scale(1.05);
}

div[data-baseweb="popover"] {
    border-radius: 20px;
    transition: 0.5s;
}

div[data-baseweb="popover"] > div {
    border-radius: 20px;
}

div[data-baseweb="popover"] > div > div > ul {
    border-radius: 20px;
}

.stTextInput > div {
    border-radius: 20px;
}

.stNumberInput > div > div[data-baseweb="input"] {
    border-radius: 20px;
}

thead tr th:first-child {display:none}
tbody th {display:none}

.stAlert > div {
    border-radius: 40px;
}

</style>
"""
st.markdown(streamlit_style, unsafe_allow_html=True)

if 'ws_flag' not in st.session_state:
    st.session_state['ws_flag'] = False

def convert_df_2_csv(df):
    try:
        return df.to_csv().encode('UTF-8-SIG')
    except:
        return df.to_csv().encode('ISO-8859-1')
    
def convert_df_2_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Resultados del scraping')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def preview(url_preview):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}
        response = requests.get(url_preview, headers=headers) #timeout=None
        soup = BeautifulSoup(response.content, 'html.parser')
        lxml_soup = etree.HTML(str(soup))
        for j in range(0,number_of_columns):
            st.write('Columna ', j, ': ', names_of_columns[j])
            st.write('Resultado ', j, ': ', lxml_soup.xpath(xpath_of_columns[j])[0])
    except:
        for j in range(0,number_of_columns):
            st.write('Resultado ', j, ': ¡Error!')

def webscraping():
    my_bar = st.progress(0)
    # Variables del contador
    contador = 1
    longitud = len(iaItemListWithLink)
    contador_porcentaje = contador/longitud * 100
    start_time = time.time()

    for i in names_of_columns:
        iaItemListWithLink[i] = ''

    for i in iaItemListWithLink.ItemUPC:
        try:
            # Funciones del scraping
            url = iaItemListWithLink['Links'][iaItemListWithLink['ItemUPC']==i].values[0]
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}
            response = requests.get(url, headers=headers) #timeout=None
            soup = BeautifulSoup(response.content, 'html.parser')
            lxml_soup = etree.HTML(str(soup))
            for j in range(0,number_of_columns):
                results.append([])
                try:
                    results[i].append(lxml_soup.xpath(xpath_of_columns[j])[0])
                except:
                    results[i].append('')
                iaItemListWithLink[names_of_columns[j]][iaItemListWithLink['ItemUPC']==i] = results[i][j]
        except:
            for j in range(0,number_of_columns):
                results.append([])
                try:
                    results[i].append(lxml_soup.xpath(xpath_of_columns[j])[0])
                except:
                    results[i].append('')
                iaItemListWithLink[names_of_columns[j]][iaItemListWithLink['ItemUPC']==i] = results[i][j]
        # Funciones del contador
        time_of_exec = round(time.time(),0) - round(start_time,0)
        remaining_time = ((longitud-contador)*time_of_exec)/contador
        my_bar.progress(int(round(contador_porcentaje, 1)), text=str(contador) + ' de ' + str(longitud) + '   |   ' + str(round(contador_porcentaje, 1)) + '%' + '   |   ' + 'tiempo restante: ' + str(dt.timedelta(seconds=round(remaining_time,0))))
        contador = contador + 1
        contador_porcentaje = contador/longitud * 100
    st.write('\n')
    st.success('¡Webscraping terminado!')
    st.write('\n')

file_extensions = ['CSV', 'Excel']
iaItemListWithLink = None
names_of_columns = []
xpath_of_columns = []
results = [[]]

st.title('Webscraping fácil')
st.write('Solo necesitas un archivo Excel o CSV con una columna de enlaces y una columna de SKU, UPC o simplemente índices (una columns con valores distintos)')
st.subheader('Carga tu archivo de datos')
file_type = st.selectbox(
                'Selecciona el tipo de archivo:',
                file_extensions)
if(file_type=='CSV'):
    uploaded_file = st.file_uploader("Carga tu archivo",label_visibility="hidden")
    if(uploaded_file is not None):
        try:
            try:
                iaItemListWithLink = pd.read_csv(uploaded_file, encoding='UTF-8-SIG')
            except:
                iaItemListWithLink = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
            st.write('Este es el archivo del que se obtendrán los enlaces para el webscraping')
            st.table(iaItemListWithLink.astype('str'))
        except:
            st.error('¡Error!, ¿cargaste un archivo csv?')
if(file_type=='Excel'):
    uploaded_file = st.file_uploader("Carga tu archivo",label_visibility="hidden")
    excel_sheet = st.text_input(label='Escribe el nombre o número de la página que contiene los enlaces', value='')
    if(uploaded_file is not None and excel_sheet!=''):
        try:
            iaItemListWithLink = pd.read_excel(uploaded_file, sheet_name=excel_sheet)
            st.write('Este es el archivo del que se obtendrán los enlaces para el webscraping, si no es lo que esperabas, cambia el nombre de la hoja')
            st.table(iaItemListWithLink.astype('str').head(10))
        except:
            st.error('¡Error! ¿cargaste un archivo excel?')

if(iaItemListWithLink is not None):
    column_of_code = st.text_input(label='Escribe el nombre de la columna que contiene SKU ó UPC', value='')
    column_of_link = st.text_input(label='Escribe el nombre de la columna que contiene los enlaces', value='')
    if(column_of_code != '' and column_of_link!=''):
        iaItemListWithLink = iaItemListWithLink.rename(columns={column_of_code:'ItemUPC', column_of_link:'Links'})
        number_of_columns = st.number_input('¿Cuántos datos quieres obtener?', value=1, step=1)
        for i in range(0,number_of_columns):
            names_of_columns.append(st.text_input(label='Escribe el nombre de la columna '+str(i+1), value=''))
        for i in range(0,number_of_columns):
            xpath_of_columns.append(st.text_input(label='Escribe el xpath de la columna '+str(i+1), value=''))
        if(xpath_of_columns[number_of_columns-1] is not None):
            st.subheader('Vista previa')
            st.write('Estos son los resultados que obtendrás, revisa y corrige en xpath en caso de ser necesario')
            preview(iaItemListWithLink['Links'][iaItemListWithLink['Links'].str.contains(r'\.com')].head(1).values[0])
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            init_ws = st.button('Iniciar', type='primary')
        if init_ws == True:
            st.session_state['ws_flag'] = True
        if st.session_state['ws_flag'] == True:
            st.subheader('Webscraping')
            webscraping()
            st.subheader('Resultados')
            st.table(iaItemListWithLink.head(10))
            csv_file = convert_df_2_csv(iaItemListWithLink)
            excel_file = convert_df_2_excel(iaItemListWithLink)
            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                st.download_button(label="Descargar CSV",
                                    data=csv_file,
                                    file_name='webscraping_'+ re.sub("\.[a-zA-Z]+$", '',uploaded_file.name) +'.csv',
                                    mime='text/csv',)
            with col3:
                st.download_button(label="Descargar excel",
                    data=excel_file,
                    file_name='webscraping_'+ re.sub("\.[a-zA-Z]+$", '',uploaded_file.name) +'.xlsx',
                    mime='application/vnd.ms-excel')

            st.write('Si necesitas hacer un nuevo webscraping, simplemente recarga esta página. Se borrarán los datos anteriores que no hayas descargado')
            
