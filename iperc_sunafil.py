import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. CONFIGURACIÓN DE IDENTIDAD VISUAL Y ESTÁNDAR
st.set_page_config(page_title="SGI Senior - Enrique Huambo", layout="wide")

# 2. MOTOR DE BASE DE DATOS (REPOSITORIO DE GESTIÓN)
def init_db():
    conn = sqlite3.connect('sgi_sistema_expert.db')
    c = conn.cursor()
    # Tabla Maestra: IPERC (De aquí nace todo)
    c.execute('''CREATE TABLE IF NOT EXISTS matriz_iperc 
                 (id INTEGER PRIMARY KEY, puesto TEXT, actividad TEXT, peligro TEXT, riesgo TEXT, 
                  nivel_riesgo TEXT, medidas_control TEXT, base_legal TEXT, codigo TEXT)''')
    # Tabla de Documentos Derivados (PETS, Planes, Registros)
    c.execute('''CREATE TABLE IF NOT EXISTS documentos_derivados 
                 (id INTEGER PRIMARY KEY, id_iperc_origen INTEGER, tipo TEXT, codigo TEXT, version TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 3. LIBRERÍA NORMATIVA (EL CEREBRO DEL SISTEMA)
# Incluye todas las leyes que me proporcionaste para validar el IPERC
MARCO_LEGAL = {
    "General": ["Ley 29783", "D.S. 005-2012-TR", "Ley 30222", "D.S. 001-2021-TR"],
    "Sectorial": ["D.S. 017-2017-TR (Obreros)", "D.S. 011-2019-TR (Construcción)", "R.M. 111-2013-MEM"],
    "Salud/Ergo": ["R.M. 312-2011/MINSA", "R.M. 375-2008-TR", "D.S. 008-2022-SA"]
}

# 4. INTERFAZ: EL FLUJO DE TRABAJO (WOKFLOW)
st.sidebar.title("🛡️ SGI MPL - Senior")
st.sidebar.info(f"Admin: Ing. Enrique Huambo\nEspecialista SST")

tabs = st.tabs(["🏗️ 1. Creación de IPERC (Base)", "📄 2. Documentos Derivados", "🗄️ 3. Legajo por Puesto", "📚 4. Biblioteca Legal"])

# --- TAB 1: EL CORAZÓN DEL SISTEMA (IPERC) ---
with tabs[0]:
    st.header("📋 Elaboración de Matriz IPERC (RM 050-2013-TR)")
    st.write("Todo el sistema nace aquí. Defina los peligros para generar los controles.")
    
    with st.form("iperc_form"):
        col1, col2 = st.columns(2)
        with col1:
            puesto = st.selectbox("Puesto de Trabajo", ["Obrero Municipal", "Serenazgo", "Limpieza Pública", "Administrativo"])
            actividad = st.text_input("Actividad / Tarea")
            peligro = st.text_input("Peligro Detectado")
            riesgo = st.text_input("Riesgo Asociado")
        with col2:
            nivel = st.select_slider("Nivel de Riesgo", options=["Bajo", "Medio", "Alto", "Crítico"])
            control = st.text_area("Medidas de Control Propuestas")
            norma = st.selectbox("Vincular Marco Legal", MARCO_LEGAL["General"] + MARCO_LEGAL["Sectorial"])
        
        if st.form_submit_button("Generar IPERC y Codificar"):
            cod_iperc = f"MPL-SST-IPERC-{puesto[:3].upper()}-001"
            # Guardar en DB
            conn = sqlite3.connect('sgi_sistema_expert.db')
            c = conn.cursor()
            c.execute("INSERT INTO matriz_iperc (puesto, actividad, peligro, riesgo, nivel_riesgo, medidas_control, base_legal, codigo) VALUES (?,?,?,?,?,?,?,?)",
                      (puesto, actividad, peligro, riesgo, nivel, control, norma, cod_iperc))
            conn.commit()
            conn.close()
            st.success(f"Matriz IPERC creada con éxito. Código: {cod_iperc}")
            st.balloons()

# --- TAB 2: GENERACIÓN DE DERIVADOS (Sincronizado con el IPERC) ---
with tabs[1]:
    st.header("📑 Generador de Documentos Complementarios")
    st.write("Seleccione un IPERC existente para derivar sus procedimientos y planes.")
    
    conn = sqlite3.connect('sgi_sistema_expert.db')
    df_iperc = pd.read_sql_query("SELECT id, codigo, puesto, medidas_control FROM matriz_iperc", conn)
    conn.close()
    
    if not df_iperc.empty:
        sel_iperc = st.selectbox("Seleccionar IPERC de Origen", df_iperc['codigo'].tolist())
        tipo_der = st.selectbox("Documento a Derivar", ["PETS (Procedimiento)", "Estándar de Seguridad", "Plan de Emergencia", "Registro de EPP"])
        
        if st.button("Generar Documento"):
            nuevo_cod = sel_iperc.replace("IPERC", tipo_der[:3].upper())
            st.success(f"Se ha generado el {tipo_der} con el código {nuevo_cod}")
            st.markdown(f"**Estandarización:** Basado en el control '{df_iperc[df_iperc['codigo']==sel_iperc]['medidas_control'].values[0]}'")
    else:
        st.warning("Primero debe crear un IPERC en la pestaña 1.")

# --- TAB 3: LEGAJO POR PUESTO (AGRUPACIÓN) ---
with tabs[2]:
    st.header("🗄️ Expediente Documental por Cargo")
    p_ver = st.selectbox("Ver Legajo de:", ["Obrero Municipal", "Serenazgo", "Limpieza Pública", "Administrativo"])
    
    conn = sqlite3.connect('sgi_sistema_expert.db')
    res = pd.read_sql_query(f"SELECT codigo, actividad, nivel_riesgo, base_legal FROM matriz_iperc WHERE puesto='{p_ver}'", conn)
    conn.close()
    
    if not res.empty:
        st.write(f"### Documentación de {p_ver}")
        st.table(res)
    else:
        st.info("No hay documentos registrados para este puesto.")

# --- TAB 4: BIBLIOTECA LEGAL ---
with tabs[3]:
    st.header("⚖️ Repositorio Normativo Verificado")
    for cat, leyes in MARCO_LEGAL.items():
        with st.expander(f"Ver {cat}"):
            for l in leyes:
                st.write(f"✅ {l}")
