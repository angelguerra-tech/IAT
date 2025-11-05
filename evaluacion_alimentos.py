import pandas as pd
import streamlit as st
from PIL import Image
import hmac
import psutil
import gc



########################### PARA CONTRASEÑAS ####################################
#Para liberar memoria
def liberar_memoria():
    gc.collect()  # Forzar la recolección de basura
    st.write(f"Memoria después de liberar: {get_memory_usage():.2f} MB")

def reset_memory():
    if 'categorias_df' in st.session_state:
        del st.session_state['categorias_df']
    gc.collect()  # Recolectar basura después del reinicio

# Configuración de los usuarios con sus hashes
def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Usuario", key="username")
            st.text_input("Contraseña", type="password", key="password")
            st.form_submit_button("Ingresar", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            st.session_state['is_logged_in'] = True  # Estado de sesión iniciada
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()

    if "password_correct" in st.session_state:
        st.error("Contraseña o usuario incorrecto")
    return False

def logout():
    keys_to_delete = ["is_logged_in", "password_correct"]
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.clear()
    st.rerun()


# Verificar si el usuario ya está autenticado
if 'salida' not in st.session_state:
    st.session_state['salida']=False

# Cargar la imagen del logo
logo = Image.open("logo.png")
logo_2 = Image.open("logo_2.png")

if 'is_logged_in' not in st.session_state or not st.session_state['is_logged_in']:

    # Aplicar configuración de página estándar si no está logueado
    st.set_page_config(layout="centered")

    st.markdown("""
    <style>
    [data-testid="stApp"] {
        background: #F4F7FD;
    }
    [data-testid="stForm"] { /* Apuntar directamente al formulario */
        background-color: #ffffff; /* Cambiar el color de fondo del formulario */
        border-radius: 10px; /* Bordes redondeados */
        border: 2px solid #ccc; /* Borde del formulario */
        padding: 20px; /* Espaciado interno del formulario */
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); /* Sombra para dar efecto elevado */
    }
    </style>
    """, unsafe_allow_html=True)
        
    # Crear columnas para el diseño de la página de login
    col1, col2, col3 = st.columns([5, 8, 2], vertical_alignment="center")
    
    with col2:
        st.image(logo_2, width=200)

    #with col2:
    st.markdown("""
    <div style="text-align: center; font-size: 30px;">
        <strong><em>Instrumento de Análisis Técnico <br> Unidad de Registro de Alimentos y Bebidas <br> IAT-URAB</em></strong>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

#if 'is_logged_in' in st.session_state and st.session_state['is_logged_in']:
else:

    if st.session_state['salida']:
        logout()

    #####################  Página ##############################
    #Configura que cubra todo el ancho de la pagina
    st.set_page_config(layout="wide")

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


    # Crear columnas
    col1, col2,col3 = st.columns([2, 8, 2],vertical_alignment="center")  # Ajusta las proporciones según sea necesario
    # Usar la segunda columna para poner el logo a la derecha
    with col1:
        st.image(logo, width=250) 
        if st.button("❌",type='primary', help="Cerrar Sesión"):
            reset_memory()
            logout()

    with col2:
        st.markdown("""
        <div style="text-align: center; font-size: 36px;">
            <strong><em>Superintendencia de Regulación Sanitaria, Unidad de Registro de Alimentos y Bebidas</em></strong>
        </div>
        """, unsafe_allow_html=True)


    st.markdown("""
    <div style="text-align: center; font-size: 32px;">
        <strong><em>Instrumento de Análisis Técnico - Alimentos</em></strong>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown("""
    <div style="text-align: left; font-size: 17px; color: #636280">
        <strong>Seleccione la categoría de alimento que desea evaluar, correspondiente a la solicitud de registro sanitario. 
                Para poder visualizar el descriptor de cada categoría hacer clic en la flecha a la derecha del nombre de la categoría.
        <br>
        Al ubicar el cursor sobre la categoría de alimento se visualiza el grupo de alimentos del RTCA 67.04.50:17 Alimentos.
                Criterios microbiológicos para la inocuidad de alimentos, correspondiente.
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    #@st.cache_data
    def load_data(ruta_excel):
    # Cargar el archivo Excel y devolverlo
        return pd.read_excel(ruta_excel, sheet_name='Vinculación de CA', keep_default_na=False, na_values='')

    # Cargar los datos solo una vez y almacenarlos en caché
    ruta_excel = 'Matriz.xlsx'
    categorias_df = load_data(ruta_excel)


    #Carga categorias
    #categorias_df = pd.read_excel(ruta_excel, sheet_name='Vinculación de CA', keep_default_na=False, na_values='')


    categorias_df['CATEGORIA'] = categorias_df['CATEGORIA'].astype(str)

    # Tomando las categorias unicas
    categorias_df = categorias_df.drop_duplicates(subset=['CATEGORIA']).copy()


    # Definir una función para cambiar el estado y manejar la lógica en un solo lugar
    def toggle_description(key):
        # Toggle the visibility state
        st.session_state[key] = not st.session_state.get(key, False)

    a=1  #Para cambiar paginas de cada categoria


    # Creación de botones y áreas desplegables
    for i, row in categorias_df.iterrows():
        cat_key = f"expand_{row['CATEGORIA']}"
        
        # Usar columnas para alinear botones en el centro y más cerca uno del otro
        #spacer1, col1, col2, spacer2 = st.columns([0.8, 0.8, 0.2, 1])
        spacer1, col1, col2, spacer2 = st.columns([0.4, 1, 0.1, 0.4], vertical_alignment="center")


        if col1.button(f"▪ {row['CATEGORIA']}", key=f"cat_btn_{cat_key}",help=f"Grupo RTCA: {row['Grupo RTCA']}", use_container_width=True):
            st.session_state['categoria_main'] = row['CATEGORIA'] #PRUEBA PARA UNA SOLA PAGINA DE CATEGORIAS
            #st.switch_page(f"pages/categoria_{a}.py")
            st.switch_page(f"pages/CATEGORIAS.py")
            

        if col2.button("▼", key=f"btn_{cat_key}"): 
            toggle_description(cat_key)

        # Mostrar la descripción justo debajo de ambos botones si está activada
        if st.session_state.get(cat_key, False):
            spacer1, desc_col, spacer2 = st.columns([0.1, 1, 0.1])
            with desc_col:
                st.write(f"**{'Descriptor categoría de alimento, según CXS 192-1995 Norma General del Codex Alimentarius para los Aditivos Alimentarios:'}**")
                st.write(row['Descriptor_codex'])
                st.write("")
                st.write(f"**{'Descriptor grupo de alimento, según RTCA 60.04.50.17 Alimentos. Criterios Microbiológicos para la Inocuidad de Alimentos:'}**")
                st.write(row['Descriptor_rtca'])

        a+=1

# Función para obtener el uso de memoria
def get_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)  # Memoria en MB

# Monitoreo en la página principal
#st.write(f"Uso de memoria actual: {get_memory_usage():.2f} MB")

if not check_password():
    st.stop()

