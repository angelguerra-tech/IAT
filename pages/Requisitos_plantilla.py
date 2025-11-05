import pandas as pd
import streamlit as st
from docx import Document
import io
from PIL import Image

# Asegurarse de que el diccionario de observaciones está inicializado
if 'observaciones_por_normativa' not in st.session_state:
    st.session_state['observaciones_por_normativa'] = {}

# Funciones para manejar observaciones
def agregar_observacion(norma, requisito, cumplimiento, observacion):
    if norma not in st.session_state['observaciones_por_normativa']:
        st.session_state['observaciones_por_normativa'][norma] = {}
    st.session_state['observaciones_por_normativa'][norma][requisito] = {
        'cumplimiento': cumplimiento,
        'observacion': observacion
    }

def eliminar_observacion(norma, requisito):
    if norma in st.session_state['observaciones_por_normativa']:
        if requisito in st.session_state['observaciones_por_normativa'][norma]:
            del st.session_state['observaciones_por_normativa'][norma][requisito]

# Función para cambiar de normativa
def cambiar_normativa(norma):
    st.session_state['current_norma'] = norma


def clear_input_states():
    # Lista para almacenar las claves que se van a eliminar
    keys_to_delete = []

    # Buscar claves que deben ser eliminadas
    for key in st.session_state.keys():
        if key.startswith('indice_') or key.startswith('input_'):
            keys_to_delete.append(key)
    
    # Eliminar también 'observaciones_por_normativa' si es necesario
    if 'observaciones_por_normativa' in st.session_state:
        keys_to_delete.append('observaciones_por_normativa')
    
    # Eliminar las claves seleccionadas
    for key in keys_to_delete:
        del st.session_state[key]

def clear_specific_keys():
    # Identificar claves específicas que contienen los valores del textarea
    text_area_keys = [key for key in st.session_state.keys() if key.startswith('input_') or key.startswith('obs_')]
    # Reiniciar estas claves
    for key in text_area_keys:
        st.session_state[key] = ""

    # Reiniciar también los índices de los selectboxes si es necesario
    selectbox_keys = [key for key in st.session_state.keys() if key.startswith('indice_')]
    for key in selectbox_keys:
        st.session_state[key] = 0  # o el índice default que prefieras
####################################################################


#Configura que cubra todo el ancho de la pagina
st.set_page_config(layout="wide")


st.markdown("""
<style>
[data-testid="stSidebarContent"] {
    background: #F4F7FD;
}
button.st-emotion-cache-1mcbg9u e16zdaao0 {
    background-color: #FFFFFF !important; /* Fondo blanco */
}
div.st-emotion-cache-1jicfl2 {
    background-color: white; /* Establece el fondo a blanco */
}
[data-testid="stBaseButton-secondary"] {
    background: #436ab2 !important;
    color: white !important;  /* Asegura que el color del texto sea blanco */
    border: 2px solid #436ab2 !important;  /* Asegura el color del borde */
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
div[data-testid="stButton"] > button {
    display: block;
    margin: 0 auto;  /* Centra el botón horizontalmente */
}
div[data-testid="stDownloadButton"] > button {
    display: block;
    margin: 0 auto;  /* Centra el botón horizontalmente */
}             
[data-testid="stBaseButton-primary"] {
    background-color: #81d4fa; /* Celeste claro */
    color: black; /* Texto blanco para contraste */
    border: 2px solid #81d4fa; /* Borde del mismo color */
    text-align: center;
}
[data-testid="bstBaseButton-primary"]:hover {
    background-color: #4fc3f7; /* Celeste más oscuro para el hover */
    color: black;
    border-color: #29b6f6; /* Borde un poco más oscuro en hover */
    text-align: center;
}
[data-testid="stLinkButton"] { 
    width: 100%; /* Asegura que tome todo el ancho disponible */
    text-align: right; /* Alinea el contenido a la derecha */
}
[data-testid="stLinkButton"]>a {
    background-color: #4dd0e1; /* Un turquesa claro */
    color: white; /* Texto blanco */
    border: 2px solid #4dd0e1; /* Borde del mismo color */
    padding: 8px 16px; /* Añade algo de relleno */
    border-radius: 5px; /* Bordes redondeados */
}
[data-testid="stLinkButton"]>a:hover {
    background-color: #26c6da; /* Turquesa más oscuro para el hover */
    border-color: #00acc1; /* Borde más oscuro en hover */
}
</style>
""", unsafe_allow_html=True)

#Valores para almacenar información del reporte
observaciones_no_cumple = []


#@st.cache_data
def load_data(ruta_excel):
# Cargar el archivo Excel y devolverlo
    return pd.read_excel(ruta_excel, sheet_name=None, keep_default_na=False, na_values='')

# Cargar los datos solo una vez y almacenarlos en caché
ruta_excel = 'Matriz.xlsx'
matriz = load_data(ruta_excel)

# Dataframes
categorias_df = matriz['Vinculación de CA']
reglamentos_df = matriz['Reglamentos Aplicables']
requisitos_df=matriz['REQUISITOS']

# Inicialización del estado al cargar la página
if 'observaciones_por_normativa' not in st.session_state:
    st.session_state['observaciones_por_normativa'] = {}
    
if 'current_norma' not in st.session_state:
    st.session_state['current_norma'] = None


# Cargar la imagen del logo
logo = Image.open("logo_3.png")

#st.sidebar.image(logo, width=150,use_column_width=True)
st.sidebar.image(logo, width=150,use_container_width=True)


space1, col1, col2, space = st.sidebar.columns([4,2,2,4],vertical_alignment="center")  # Ajusta las proporciones según sea necesario
# Usar la segunda columna para poner el logo a la derecha
with space1:
    if st.button("❌",type='primary', help="Cerrar Sesión"):
        st.session_state['salida']=True
        st.switch_page("evaluacion_alimentos.py")
with col1:
    if st.button("🢀",type='primary'):
        clear_specific_keys()
        st.switch_page("pages/CATEGORIAS.py")
with col2:
    if st.button("🏚️",type='primary'):
        clear_specific_keys()
        st.switch_page("evaluacion_alimentos.py")


st.sidebar.title("Regulación aplicable")

# Se selecciona categoría
categoria_seleccionada = st.session_state.get('categoria_seleccionada', None)

if 'categoria_seleccionada' not in st.session_state:
    st.session_state['categoria_seleccionada'] = None

if 'last_categoria_seleccionada' not in st.session_state:
    st.session_state['last_categoria_seleccionada'] = None

# Crear columnas
col1, col2,col3,col4 = st.columns([0.5,0.5,8, 2],vertical_alignment="center")  # Ajusta las proporciones según sea necesario

with col3: 
    if 'categoria_seleccionada' in st.session_state:
        # Utilizar la categoría seleccionada del session_state
        categoria_seleccionada = st.session_state['categoria_seleccionada']
        subgrupo=st.session_state['Subgrupo_rtca']
        Descrip_sub_rtca=st.session_state['Descriptor_subcategoria_rtca']

        st.markdown(f"""
        <div style="text-align: center; font-size: 25px;">
            <strong><em>{categoria_seleccionada}</em></strong>
        </div>
        <div style="text-align: left; font-size: 16px;">
            <strong><em>Subgrupo RTCA: {Descrip_sub_rtca}</em></strong>
        </div>
        """, unsafe_allow_html=True)

st.write("")
st.write("")
st.markdown("""
<div style="text-align: left; font-size: 15px; color: #636280">
    <strong>En esta sección se presenta la regulación aplicable correspondiente a la categoría de alimento en evaluación.<br><br>
    Para acceder a los requisitos correspondientes de cada regulación, hacer click en el reglamento a verificar. <br><br>
    Para evaluar un requisito en específico debe hacer click en ver requisito, esto lo direccionará a la sección específica del reglamento 
            a evaluar.<br><br>
    Una vez verificado el cumplimiento del requisito correspondiente debe seleccionar en el menú desplegable según corresponda 
            (cumple, no cumple, no aplica). En caso de incumplimiento es mandatorio emitir observaciones de acuerdo a la naturaleza 
            del hallazgo.<br><br>
    Al finalizar la verificación de los requisitos correspondientes a la regulación aplicable, hacer click en generar reporte y luego hacer 
            click en descargar. Esto guardará automáticamente en la bandeja de descargas las observaciones resultantes de la observación.<br><br>
    Las observaciones resultantes del IAT deberán colocarse en la sección de observaciones de SISAM.
</strong>
</div>
""", unsafe_allow_html=True)

#Revisa la categoria seleccionada con la anterior
if st.session_state['categoria_seleccionada'] != st.session_state['last_categoria_seleccionada']:
    st.session_state['current_norma'] = None  # Resetear current_norma
    st.session_state['last_categoria_seleccionada'] = st.session_state['categoria_seleccionada']  # Actualizar la última categoría seleccionada


# Mostrar la descripción de la categoría seleccionada y los botones de normas aplicables
if categoria_seleccionada:
    # Filtrar las normas aplicables a la categoría seleccionada
    normas_aplicables = categorias_df[categorias_df['Subcategoria'] == categoria_seleccionada].iloc[0, 8:].dropna().tolist()


if 'current_norma' not in st.session_state:
    st.session_state['current_norma'] = None


for norma in normas_aplicables:
    if st.sidebar.button(norma,use_container_width=True):
        cambiar_normativa(norma)

st.markdown("---")

# Asegurándose de que las definiciones iniciales de session_state están en su lugar
if 'show_selectbox' not in st.session_state:
    st.session_state.show_selectbox = False

if 'selected_fortification' not in st.session_state:
    st.session_state.selected_fortification = None

cumplimiento_guardado=None
observacion_guardada=None

# Desplegar los requisitos de la normativa seleccionada
if 'current_norma' in st.session_state and st.session_state['current_norma']:

    norma = st.session_state['current_norma'].strip() #Quitando espacios en blanco para que puedan coincidir con el listado

    # Crear una tabla editable para los requisitos
    st.markdown(f"""
    <div style="text-align: center; font-size: 22px; color:#005662;">
        <strong><em>{norma}</em></strong>
    </div>
    """, unsafe_allow_html=True)

    reglamentos_df['REGLAMENTO'] = reglamentos_df['REGLAMENTO'].str.strip()
    enlace = reglamentos_df.loc[reglamentos_df['REGLAMENTO'] == norma, 'ENLACE'].iloc[0]


    if norma !="Observaciones Generales":
        st.link_button("VER REGLAMENTO",enlace)

    st.write(f"")
    st.write(f"")

    # Eliminar duplicados basados en 'Normas' para obtener una lista de todas las normativas únicas
    requisitos_df['Normas'] =  requisitos_df['Normas'].str.strip()


    #Para submenú en RTS 67.06.01:13
    norma_forti="RTS 67.06.01:13 Fortificación de alimentos. Especificaciones (azúcar, sal, harina de maíz nixtamalizado y pastas alimenticias)"
    if norma==norma_forti:
        st.session_state.show_selectbox = True

    # Mostrar el selectbox solo si el estado está activo
    if st.session_state.show_selectbox:
        selected = st.sidebar.selectbox(
            "",
            ("Seleccione una opción...", "Azúcar", "Sal", "Harina de maíz nixtamalizado", "Pastas alimenticias"),
            key="fortification_select",placeholder="Seleccione la sección aplicable:",
        )
        st.session_state.selected_fortification = selected
        requisitos = requisitos_df[(requisitos_df['Normas'] == norma) & (requisitos_df['INFO'] == selected)]
    else:
        # Para normativas que no requieren selectbox, mostrar todos los requisitos
        requisitos = requisitos_df[requisitos_df['Normas'] == norma]


    #Colocar nombre de sub normativa
    if st.session_state.selected_fortification:
        st.markdown(f"""
        <div style="text-align: left; font-size: 18px; color:red">
            <strong>{st.session_state.selected_fortification}</strong>
        </div>
        """, unsafe_allow_html=True)

    if 'observaciones_no_cumple' not in st.session_state:
        st.session_state['observaciones_no_cumple'] = []
    

    for index, row in requisitos.iterrows():

        requisito=row['Requisito']

        # Clave única para el índice en el estado de sesión
        indice = f'indice_{norma}_{requisito}'
        obs_key = f"obs_{norma}_{requisito}_{index}"


        if obs_key not in st.session_state:
            st.session_state[obs_key] = ""

        if indice not in st.session_state:
            st.session_state[indice] = 0

        if norma in st.session_state['observaciones_por_normativa']:
            observaciones_norma = st.session_state['observaciones_por_normativa'][norma]
            if requisito in observaciones_norma:
                observacion_guardada = observaciones_norma[requisito].get('observacion', "")
        
        especificacion=f"Sección: {row['Sección']} - {row['Requisito']}"
        obs_dictamen=f"{row['Sección']} - {row['Requisito']}"

        if norma!="Observaciones Generales":
            st.markdown(f"""
            <div style="text-align: left; font-size: 18px;">
                <strong><em>{especificacion}</em></strong>
            </div>
            """, unsafe_allow_html=True)

        observacion_guardada = st.session_state[obs_key]


        if norma=="Observaciones Generales":
            def on_text_area_change(key):
                st.session_state[key] = st.session_state[f"input_{key}"]

            input_key = f"input_{obs_key}"  # Clave única para el input
            observacion=st.text_area("", value=observacion_guardada, key=input_key, on_change=on_text_area_change, args=(obs_key,))
            agregar_observacion(norma, requisito="General", cumplimiento="No cumple", observacion=observacion)
            break

        #Agrega enlaces her codex online
        if norma=="RTCA 67.04.54:18 Alimentos y bebidas procesadas. Aditivos alimentarios" and not pd.isna(row['LINK']) and (row['Sección']=="Cuadro 2" or row['Sección']=="Cuadro 3"):
            st.link_button("Norma Codex",row['LINK'])
        else:
            st.link_button("Ver requisito",row['LINK'])

         # Ajustar el orden de las opciones basado en si se seleccionó una subnormativa
        if st.session_state.selected_fortification and norma == norma_forti:
            opciones_cumple = ('No aplica', 'No cumple', 'Cumple')
        else:
            opciones_cumple = ('Cumple', 'No cumple', 'No aplica')


        cumplimiento = st.selectbox("", opciones_cumple, index=st.session_state[indice], key=f"cumple_{norma}_{index}")


        def on_text_area_change(key):
            st.session_state[key] = st.session_state[f"input_{key}"]

        is_disabled=cumplimiento!="No cumple"
        
        input_key = f"input_{obs_key}"  # Clave única para el input
        observacion=st.text_area("Observaciones", value=observacion_guardada, key=input_key, on_change=on_text_area_change, args=(obs_key,), disabled=is_disabled)
        
        st.session_state[indice] = opciones_cumple.index(cumplimiento)
       

        # Si ya existía una observación previa para este requisito, eliminarla primero
        eliminar_observacion(norma, obs_dictamen)
        
        # Luego guardar la nueva información, ya sea Cumple, No cumple o No aplica
        agregar_observacion(norma, obs_dictamen, cumplimiento, observacion)

        
        #AGREGADO
        if norma=="RTS 67.07.01:22 Mezcla de Crema (Nata) con Aceite o Grasa Vegetal Comestible. Especificaciones" and categoria_seleccionada=="1.4.4 Productos análogos a la nata (crema)":
            break


    # Asegurándose de resetear el selectbox cuando se cambia de normativa
    if 'current_norma' in st.session_state and st.session_state['current_norma'] != norma:
        st.session_state.show_selectbox = False
        st.session_state.selected_fortification = None


def generar_reporte():
    # Determinar si usar la plantilla favorable o desfavorable
    tiene_no_cumple = any(
        obs_data['cumplimiento'] == "No cumple"
        for obs_list in st.session_state['observaciones_por_normativa'].values()
        for obs_data in obs_list.values()
    )

    template_path = "Dictamen_desfavorable_2.docx" if tiene_no_cumple else "Dictamen_favorable.docx"

    doc = Document(template_path)

    if tiene_no_cumple:
        # Generar texto de todas las observaciones, enumeradas por normativa
        observaciones_texto = ""
        contador = 1
        for norma, requisitos in st.session_state['observaciones_por_normativa'].items():
            for requisito, obs in requisitos.items():
                if obs['cumplimiento'] == "No cumple":
                    if norma == "Observaciones Generales":
                        observaciones_texto += f"{contador}. Incumplimiento en: {obs['observacion']}.\n"
                    else:
                        observaciones_texto += f"{contador}. Incumplimiento con el numeral {requisito} del Reglamento {norma} en cuanto a: {obs['observacion']}.\n"
                    contador += 1
        
        # Buscar y reemplazar el marcador de posición en el documento
        placeholder = "{Observaciones}"
        for paragraph in doc.paragraphs:
            if placeholder in paragraph.text:
                paragraph.text = paragraph.text.replace(placeholder, observaciones_texto.strip())
        
        # Generar texto para los requisitos que cumplen, agrupados por normativa
        cumplimientos_texto = ""
        normas_con_cumplimientos = {}
        
        # Primero agrupamos todos los requisitos que cumplen por normativa
        for norma, requisitos in st.session_state['observaciones_por_normativa'].items():
            if norma != "Observaciones Generales":
                for requisito, obs in requisitos.items():
                    if obs['cumplimiento'] == "Cumple":
                        if norma not in normas_con_cumplimientos:
                            normas_con_cumplimientos[norma] = []
                        normas_con_cumplimientos[norma].append(requisito)
        
        # Luego generamos el texto con viñetas
        for norma, requisitos_lista in normas_con_cumplimientos.items():
            cumplimientos_texto += f"• {norma}\n"
            for requisito in requisitos_lista:
                cumplimientos_texto += f"  - {requisito}\n"
        
        # Reemplazar el marcador para cumplimientos
        placeholder_cumplimientos = "{Cumplimientos}"
        for paragraph in doc.paragraphs:
            if placeholder_cumplimientos in paragraph.text:
                paragraph.text = paragraph.text.replace(placeholder_cumplimientos, cumplimientos_texto.strip())
        
        # Generar texto para los requisitos que no aplican, agrupados por normativa
        inaplicables_texto = ""
        normas_con_inaplicables = {}
        
        # Primero agrupamos todos los requisitos que no aplican por normativa
        for norma, requisitos in st.session_state['observaciones_por_normativa'].items():
            if norma != "Observaciones Generales":
                for requisito, obs in requisitos.items():
                    if obs['cumplimiento'] == "No aplica":
                        if norma not in normas_con_inaplicables:
                            normas_con_inaplicables[norma] = []
                        normas_con_inaplicables[norma].append(requisito)
        
        # Luego generamos el texto con viñetas
        for norma, requisitos_lista in normas_con_inaplicables.items():
            inaplicables_texto += f"• {norma}\n"
            for requisito in requisitos_lista:
                inaplicables_texto += f"   - {requisito}\n"

        # Reemplazar el marcador para requisitos no aplicables
        placeholder_inaplicables = "{Inaplicables}"
        for paragraph in doc.paragraphs:
            if placeholder_inaplicables in paragraph.text:
                paragraph.text = paragraph.text.replace(placeholder_inaplicables, inaplicables_texto.strip())

    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    del st.session_state['observaciones_por_normativa']
    return output


# Botón para generar y descargar el informe
if st.sidebar.button('Generar reporte',type='primary'):
    output = generar_reporte()
    st.sidebar.download_button("Descargar",
                               output,
                               "Reporte.docx", 
                               "application/vnd.openxmlformats-officedocument.wordprocessingml.document",type='primary')
