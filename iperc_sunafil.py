import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. BASE DE DATOS DE GESTIÓN DOCUMENTAL
def init_db():
    conn = sqlite3.connect('sgi_lambayeque.db')
    c = conn.cursor()
    # Tabla para documentos generados (IPERC, Planes, etc)
    c.execute('''CREATE TABLE IF NOT EXISTS documentos_sgi 
                 (id INTEGER PRIMARY KEY, puesto TEXT, tipo TEXT, codigo TEXT, version TEXT, fecha TEXT, contenido TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 2. REPOSITORIO DE NORMATIVA PARA ESTANDARIZACIÓN
LIBRERIA_LEGAL = {
    "IPERC": "Ley 29783 Art. 57 / D.S. 005-2012-TR Art. 77",
    "Plan de Emergencia": "Ley 29783 Art. 25 / D.S. 005-2012-TR Art. 83",
    "Procedimiento (PETS)": "D.S. 017-2017-TR (Obreros Municipales)",
    "Registros": "R.M. 050-2013-TR (Formatos Referenciales)"
}

# 3. INTERFAZ OPERATIVA
st.set_page_config(page_title="SGI MPL - Enrique Huambo", layout="wide")
st.title("🛡️ Sistema de Gestión Integrado - MPL")

tabs = st.tabs(["📝 Generador de Documentos", "📂 Legajo por Puesto", "⚖️ Repositorio Legal", "🚨 Operatividad Diaria"])

# --- TAB 1: GENERACIÓN Y ESTANDARIZACIÓN (Aquí está lo que buscas) ---
with tabs[0]:
    st.header("🛠️ Fábrica de Documentos Estandarizados")
    col_a, col_b = st.columns(2)
    
    with col_a:
        puesto_target = st.selectbox("Puesto de Trabajo", ["Limpieza Pública", "Serenazgo", "Parques y Jardines", "Administrativo"])
        tipo_doc = st.selectbox("Tipo de Documento a Generar", ["IPERC", "Procedimiento (PETS)", "Plan de Emergencia", "Registro de Inspección"])
        version = st.text_input("Versión", "V.01")
        
    with col_b:
        # Lógica de Codificación Automática
        prefijo = "MPL-SST"
        abrevia = tipo_doc[:3].upper()
        codigo_aut = f"{prefijo}-{abrevia}-{puesto_target[:3].upper()}-2026-001"
        st.info(f"**Código Sugerido:** {codigo_aut}")
        norma_cita = LIBRERIA_LEGAL.get(tipo_doc, "Ley 29783")
        st.write(f"**Base Legal Aplicada:** {norma_cita}")

    if st.button("Generar y Archivar en el Legajo"):
        # Guardar en Base de Datos
        conn = sqlite3.connect('sgi_lambayeque.db')
        c = conn.cursor()
        c.execute("INSERT INTO documentos_sgi (puesto, tipo, codigo, version, fecha, contenido) VALUES (?,?,?,?,?,?)",
                  (puesto_target, tipo_doc, codigo_aut, version, datetime.now().strftime("%Y-%m-%d"), f"Documento estándar para {puesto_target}"))
        conn.commit()
        conn.close()
        st.success(f"¡Documento {codigo_aut} creado y archivado exitosamente!")

# --- TAB 2: AGRUPACIÓN POR PUESTO ---
with tabs[1]:
    st.header("🗄️ Expediente Documental Agrupado")
    filtro = st.selectbox("Ver documentos de:", ["Limpieza Pública", "Serenazgo", "Parques y Jardines", "Administrativo"])
    
    # Consulta a la DB
    conn = sqlite3.connect('sgi_lambayeque.db')
    df_docs = pd.read_sql_query(f"SELECT tipo, codigo, version, fecha FROM documentos_sgi WHERE puesto='{filtro}'", conn)
    conn.close()
    
    if not df_docs.empty:
        st.table(df_docs)
    else:
        st.warning("Aún no hay documentos generados para este puesto.")

# --- TAB 3: REPOSITORIO LEGAL ---
with tabs[2]:
    st.header("📚 Biblioteca Normativa Verificada")
    st.write("Consulta rápida de las leyes que sustentan tu SGI.")
    # (Aquí va el listado de las 5 categorías que me diste anteriormente)
    st.markdown("- **Ley 29783:** Norma Matriz de SST.")
    st.markdown("- **D.S. 017-2017-TR:** Seguridad para Obreros Municipales.")

# --- TAB 4: OPERATIVIDAD (ATS Y ACCIDENTES) ---
with tabs[3]:
    st.header("🚨 Gestión en Campo")
    # Formularios de ATS y Reporte de Accidentes con envío de correo
    st.write("Use esta pestaña para firmas digitales y reportes inmediatos.")
