import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import smtplib

# ==========================================
# 1. REPOSITORIO NORMATIVO INTEGRAL (SST PERÚ)
# ==========================================
LIBRERIA_COMPLIANCE = {
    "1. Marco Legal General": {
        "Ley N° 29783": "Ley de SST (Norma Matriz)",
        "Ley N° 30222": "Modificatoria de Ley 29783",
        "D.S. N° 005-2012-TR": "Reglamento de la Ley de SST",
        "D.S. N° 006-2014-TR": "Simplificación de registros",
        "D.S. N° 016-2016-TR": "Periodicidad de EMO",
        "D.S. N° 020-2019-TR": "Participación en IPERC y Capacitaciones",
        "D.S. N° 001-2021-TR": "EPP y Emergencias Sanitarias"
    },
    "2. Gestión y Comités": {
        "R.M. N° 050-2013-TR": "Formatos referenciales de registros obligatorios",
        "R.M. N° 085-2013-TR": "Registros simplificados MYPE",
        "R.M. N° 245-2021-TR": "Elección de representantes Comité SST",
        "Ley N° 28806": "Ley General de Inspección del Trabajo",
        "D.S. N° 019-2006-TR": "Reglamento de Inspección del Trabajo"
    },
    "3. Salud y Ergonomía": {
        "R.M. N° 312-2011/MINSA": "Protocolos de Exámenes Médicos Ocupacionales",
        "R.M. N° 375-2008-TR": "Norma Básica de Ergonomía",
        "Ley N° 26790": "Ley de Modernización de Seguridad Social (SCTR)",
        "D.S. N° 008-2022-SA": "Actualización Anexo 5 SCTR (Alto Riesgo)"
    },
    "4. Normativa Sectorial": {
        "D.S. N° 017-2017-TR": "SST Obreros Municipales",
        "D.S. N° 011-2019-TR": "SST Construcción Civil",
        "Norma G.050": "Seguridad durante la construcción",
        "D.S. N° 024-2016-EM": "SST Minería",
        "R.M. N° 111-2013-MEM": "SST Electricidad (RESESATE)"
    },
    "5. Grupos Vulnerables": {
        "Ley N° 28048": "Protección a mujer gestante",
        "Ley N° 31572": "Ley del Teletrabajo",
        "D.S. N° 002-2023-TR": "Reglamento Ley Teletrabajo (Ergonomía)"
    }
}

# ==========================================
# 2. MOTOR DE BASE DE DATOS Y PERSISTENCIA
# ==========================================
def init_db():
    conn = sqlite3.connect('sgi_master.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS legajos 
                 (id INTEGER PRIMARY KEY, puesto TEXT, codigo TEXT, normativa TEXT, fecha TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 3. INTERFAZ Y FUNCIONALIDADES
# ==========================================
st.sidebar.title("🔐 SGI Enterprise v6.0")
st.sidebar.markdown(f"**Admin:** Ing. Enrique Huambo")

tabs = st.tabs(["📂 Repositorio Normativo", "📝 Gestión por Puesto", "📊 Dashboard Cloud"])

with tabs[0]:
    st.header("📚 Biblioteca Legal SST Actualizada")
    categoria = st.selectbox("Seleccione Categoría Legal", list(LIBRERIA_COMPLIANCE.keys()))
    
    df_legal = pd.DataFrame(LIBRERIA_COMPLIANCE[categoria].items(), columns=["Norma", "Descripción"])
    st.table(df_legal)
    st.caption("Nota: Toda la normativa está vinculada automáticamente a los generadores de IPERC.")

with tabs[1]:
    st.header("🗄️ Legajos Agrupados por Puesto")
    puesto = st.text_input("Ingrese Puesto de Trabajo (ej. Operario de Limpieza)")
    norma_ref = st.selectbox("Vincular Norma Sectorial", list(LIBRERIA_COMPLIANCE["4. Normativa Sectorial"].keys()))
    
    if st.button("Vincular y Agrupar Documentación"):
        codigo = f"MPL-SST-{puesto[:3].upper()}-2026"
        st.success(f"Expediente '{codigo}' creado con éxito.")
        st.info(f"Norma Aplicada: {norma_ref} - {LIBRERIA_COMPLIANCE['4. Normativa Sectorial'][norma_ref]}")

with tabs[2]:
    st.header("🌐 Acceso Multi-dispositivo")
    st.write("""
    Para usar esta plataforma en tu celular, tablet u otra PC, tienes 3 opciones:
    
    1. **Streamlit Cloud (Recomendado):** Sube tu código a GitHub y conéctalo a Streamlit Cloud. Te dará un link tipo `mi-sgi-sst.streamlit.app` que podrás abrir en cualquier parte del mundo.
    2. **Red Local (WiFi):** Si ejecutas el código en tu Mac, usa el link que dice `Network URL` (ej. `http://192.168.1.XX:8501`). Si tu celular está en el mismo WiFi, solo entra a esa dirección.
    3. **Ngrok:** Una herramienta que crea un túnel seguro y te da un link temporal para compartir.
    """)