from pathlib import Path
from datetime import date
import io
import re
import unicodedata

import pandas as pd
import streamlit as st
from docx import Document


# =========================
# Rutas (Streamlit Cloud safe)
# =========================
BASE_DIR = Path(__file__).resolve().parents[1]  # sube de /pages a la raíz del proyecto
RUTA_EXCEL = BASE_DIR / "Matriz.xlsx"
PLANTILLA_DICTAMEN = BASE_DIR / "Dictamen_no_conformidad.docx"


# =========================
# Utilidades
# =========================
def _norm(s: str) -> str:
    """Normaliza texto: lower, strip, sin acentos, separadores a espacios."""
    s = str(s).strip().lower()
    s = "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )
    s = s.replace("_", " ").replace("-", " ")
    s = re.sub(r"\s+", " ", s)
    return s


def _load_catalogos():
    """Carga catálogos desde Matriz.xlsx / hoja Catalogos."""
    df = pd.read_excel(RUTA_EXCEL, sheet_name="Catalogos", keep_default_na=False)

    # mapa normalizado -> nombre real
    colmap = {_norm(c): c for c in df.columns}

    def pick(*cands):
        for c in cands:
            c_norm = _norm(c)
            if c_norm in colmap:
                return colmap[c_norm]
        return None

    # acepta distintas variaciones de encabezado
    col_titulo = pick("titulo", "título")
    col_nombre = pick("nombre del analista", "nombre analista", "analista", "nombre")
    col_cargo = pick("cargo", "puesto")

    if not col_titulo or not col_nombre or not col_cargo:
        st.error(
            "En la hoja 'Catalogos' faltan columnas esperadas. "
            f"Detectadas: {list(df.columns)}"
        )
        st.stop()

    titulos = [x for x in df[col_titulo].astype(str).tolist() if str(x).strip()]
    nombres = [x for x in df[col_nombre].astype(str).tolist() if str(x).strip()]
    cargos = [x for x in df[col_cargo].astype(str).tolist() if str(x).strip()]

    return titulos, nombres, cargos


def _replace_in_paragraph(paragraph, replacements: dict):
    """Reemplaza tags incluso si están partidos en runs."""
    full = "".join(run.text for run in paragraph.runs)
    new = full
    for k, v in replacements.items():
        new = new.replace(k, v)

    if new != full:
        for run in paragraph.runs:
            run.text = ""
        if paragraph.runs:
            paragraph.runs[0].text = new
        else:
            paragraph.add_run(new)


def _replace_everywhere(doc: Document, replacements: dict):
    """Reemplaza en párrafos, tablas, header y footer."""
    for p in doc.paragraphs:
        _replace_in_paragraph(p, replacements)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    _replace_in_paragraph(p, replacements)

    for section in doc.sections:
        for p in section.header.paragraphs:
            _replace_in_paragraph(p, replacements)
        for p in section.footer.paragraphs:
            _replace_in_paragraph(p, replacements)


# =========================
# UI
# =========================
st.set_page_config(layout="wide")
st.title("Generar dictamen (No conformidad)")

# Validación de flujo (trazabilidad)
if not st.session_state.get("reporte_descargado", False):
    st.warning("Primero debes generar y descargar el reporte para mantener trazabilidad.")
    st.stop()

if not st.session_state.get("reporte_tiene_no_cumple", False):
    st.info("No hay incumplimientos. (Por ahora no se genera dictamen).")
    st.stop()

# Validación archivos requeridos
if not RUTA_EXCEL.exists():
    st.error(f"No se encontró el archivo Excel: {RUTA_EXCEL.name} en la raíz del proyecto.")
    st.stop()

if not PLANTILLA_DICTAMEN.exists():
    st.error(f"No se encontró la plantilla: {PLANTILLA_DICTAMEN.name} en la raíz del proyecto.")
    st.stop()

titulos, nombres, cargos = _load_catalogos()

c1, c2 = st.columns(2)
with c1:
    fecha = st.date_input("Fecha", value=date.today())
with c2:
    solicitud = st.text_input("Solicitud", value=st.session_state.get("solicitud", ""))

nombre_producto = st.text_input(
    "Nombre del producto",
    value=st.session_state.get("nombre_producto", "")
)

d1, d2, d3 = st.columns(3)
with d1:
    titulo_sel = st.selectbox("Título", options=titulos)
with d2:
    nombre_sel = st.selectbox("Nombre analista", options=nombres)
with d3:
    cargo_sel = st.selectbox("Cargo", options=cargos)

st.write("")

if st.button("Generar dictamen", type="primary"):
    observaciones = st.session_state.get("dictamen_observaciones", "").strip()
    if not observaciones:
        observaciones = "• (No se encontraron observaciones. Verifica evaluación y generación del reporte.)"

    replacements = {
        "{Fecha}": fecha.strftime("%d/%m/%Y"),
        "{Solicitud}": str(solicitud).strip(),
        "{Nombre del alimento}": str(nombre_producto).strip(),
        "{Título}": str(titulo_sel).strip(),
        "{Nombre}": str(nombre_sel).strip(),
        "{Cargo}": str(cargo_sel).strip(),
        "{Observaciones}": observaciones,
    }

    doc = Document(str(PLANTILLA_DICTAMEN))
    _replace_everywhere(doc, replacements)

    buff = io.BytesIO()
    doc.save(buff)
    buff.seek(0)

    st.success("Dictamen generado.")
    st.download_button(
        "Descargar dictamen",
        data=buff.getvalue(),
        file_name=f"Dictamen_no_conformidad_{solicitud or 's_solicitud'}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

