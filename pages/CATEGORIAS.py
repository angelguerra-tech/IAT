import pandas as pd
import streamlit as st
from PIL import Image


#Configura que cubra todo el ancho de la pagina
st.set_page_config(layout="wide")


########################################################

# Verificar si el usuario ya está autenticado
if 'is_logged_in' in st.session_state and st.session_state['is_logged_in']:

    # Estilos personalizados con CSS
    st.markdown("""
    <style>
    [data-testid="stApp"] {
        background: #F4F7FD;
    }
    [data-testid="stBaseButton-secondary"] {
        background: #436ab2 !important;
        color: white !important;  /* Asegura que el color del texto sea blanco */
        border: 2px solid #111e60 !important;  /* Asegura el color del borde */
    }
    [data-testid="stMarkdownContainer"] {
        display: block;
        width: 100%;
        text-align: left;
    }
    button[data-testid="stBaseButton-secondary"]:hover {
        background-color: #FFFFFF !important;
        color: #436ab2 !important;  /* Asegura que el texto cambie a azul oscuro */
        border-color: #436ab2 !important;  /* Asegura que el borde cambie a azul oscuro */
    }  
    [data-testid="stBaseButton-primary"] {
        background-color: #F4F7FD !important;
        border: 2px solid !important;
        text-align: left !important;
        color: black !important;
        font-size: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)


    #Cargar la imagen del logo
    logo = Image.open("logo.png")


    # Crear columnas
    col1, col2,col3 = st.columns([2,8,2],vertical_alignment="center")  # Ajusta las proporciones según sea necesario
    # Usar la segunda columna para poner el logo a la derecha
    with col1:
        st.image(logo, width=250) 
        space1, space2, space3 = st.columns([3,1,6], vertical_alignment="center")
        with space1:
            if st.button("❌",type='primary', help="Cerrar Sesión"):
                st.session_state['salida']=True
                st.switch_page("evaluacion_alimentos.py")
        with space2:
            if st.button("🏚️",type='primary'):
                st.switch_page("evaluacion_alimentos.py")


    with col2:
        st.markdown("""
        <div style="text-align: center; font-size: 36px;">
            <strong><em>Superintendencia de Regulación Sanitaria, Unidad de Registro de Alimentos y Bebidas</em></strong>
        </div>
        """, unsafe_allow_html=True)


    #@st.cache_data
    def load_data(ruta_excel):
    # Cargar el archivo Excel y devolverlo
        return pd.read_excel(ruta_excel, sheet_name='Vinculación de CA', keep_default_na=False, na_values='')

    # Cargar los datos solo una vez y almacenarlos en caché
    ruta_excel = 'Matriz.xlsx'
    categorias_df = load_data(ruta_excel)


    if 'observaciones_por_normativa' in st.session_state:
        del st.session_state['observaciones_por_normativa']

    if 'categoria_main' not in st.session_state:
        st.session_state['categoria_main'] = None

    if 'last_categoria_main' not in st.session_state:
        st.session_state['last_categoria_main'] = None

    if 'categoria_main' in st.session_state:
        # Utilizar la categoría seleccionada del session_state
        categoria_main = st.session_state['categoria_main']

        st.markdown(f"""
        <div style="text-align: center; font-size: 22px;">
            <strong><em>{categoria_main}</em></strong>
        </div>
        """, unsafe_allow_html=True)


    st.write("")

    st.markdown("""
    <div style="text-align: left; font-size: 17px; color: #636280">
        <strong>Seleccione la subcategoría de alimento que desea evaluar, correspondiente a la solicitud de registro sanitario. 
            Para poder visualizar el descriptor de cada subcategoría hacer clic en la flecha a la derecha del nombre de la subcategoría.
        <br>
        <strong>Al ubicar el cursor sobre la subcategoría de alimento se visualiza el subgrupo de alimentos del RTCA 67.04.50:17 Alimentos.
                Criterios microbiológicos para la inocuidad de alimentos, correspondiente.  
    </strong>
    </div> 
    """, unsafe_allow_html=True)
    st.write("")

    # Eliminar duplicados basados en 'CATEGORIA' para obtener una lista de todas las categorías únicas
    categorias_agrupadas = categorias_df['CATEGORIA'].drop_duplicates().reset_index(drop=True)


    indice = categorias_agrupadas[categorias_agrupadas == categoria_main].index.item()


    # Seleccionar la categoría de la lista
    nombre_categoria_n = categorias_agrupadas[indice]

    # Filtrar el DataFrame para incluir solo filas de la categoría detectada
    subcategoria_1_df = categorias_df[categorias_df['CATEGORIA'] == nombre_categoria_n]

    # Tomando las subcategorías únicas para evitar duplicados en los botones
    categoria_1_df = subcategoria_1_df.drop_duplicates(subset=['Subcategoria'])

    categoria_1_df['Subgrupo_rtca'] = categoria_1_df['Subgrupo_rtca'].astype(str)


    # Definir una función para cambiar el estado y manejar la lógica en un solo lugar
    def toggle_description(key):
        # Toggle the visibility state
        st.session_state[key] = not st.session_state.get(key, False)

    # Creación de botones y áreas desplegables
    for i, row in categoria_1_df.iterrows():
        cat_key = f"expand_{row['Subcategoria']}"
        st.session_state['Descriptor_subcategoria_rtca']=row['Descriptor_subcategoria_rtca']
        
        # Usar columnas para alinear botones en el centro y más cerca uno del otro
        spacer1, col1, col2, spacer2 = st.columns([0.6, 1, 0.1, 0.6], vertical_alignment="center")

        if col1.button(row['Subcategoria'], key=f"cat_btn_{cat_key}", help=f"Subgrupo RTCA: {row['Subgrupo_rtca']}",use_container_width=True):
            st.session_state['categoria_seleccionada'] = row['Subcategoria']
            st.session_state['Subgrupo_rtca']=row['Subgrupo_rtca']
            st.switch_page('pages/Requisitos_plantilla.py')

        if col2.button("▼", key=f"btn_{cat_key}"): 
            toggle_description(cat_key)

        # Mostrar la descripción justo debajo de ambos botones si está activada
        if st.session_state.get(cat_key, False):
            spacer1, desc_col, spacer2 = st.columns([0.1, 1, 0.1])
            with desc_col:
                st.write(f"**{'Descriptor subcategoría de alimento, según CXS 192-1995 Norma General del Codex Alimentarius para los Aditivos Alimentarios'}**")
                st.write(row['Descriptor_subcategoria'])
                st.write("")
                st.write(f"**{'Descriptor de subgrupo según RTCA 60.04.50.17 Alimentos. Criterios Microbiológicos para la Inocuidad de Alimentos:'}**")
                st.write(row['Descriptor_subcategoria_rtca'])
                st.session_state['Descriptor_subcategoria_rtca']=row['Descriptor_subcategoria_rtca']
