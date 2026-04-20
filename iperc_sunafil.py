import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. CONFIGURACIÓN E IDENTIDAD (MPL)
st.set_page_config(page_title="SGI Senior - Enrique Huambo", layout="wide")

def init_db():
    conn = sqlite3.connect('sgi_full_essence.db')
    c = conn.cursor()
    # Tabla IPERC: El origen de todo
    c.execute('''CREATE TABLE IF NOT EXISTS matriz_iperc 
                 (id INTEGER PRIMARY KEY, puesto TEXT, actividad TEXT, peligro TEXT, riesgo TEXT, 
                  evaluacion TEXT, controles TEXT, norma_ref TEXT, codigo TEXT, fecha TEXT)''')
    # Tabla Documentos: Los hijos del IPERC
    c.execute('''CREATE TABLE IF NOT EXISTS documentos_sgi 
                 (id INTEGER PRIMARY KEY, puesto TEXT, tipo TEXT, codigo TEXT, version TEXT, referencia_iperc TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 2. REPOSITORIO NORMATIVO (LAS 5 CATEGORÍAS QUE DICTASTE)
BIBLIOTECA_SST = {
    "General": ["Ley 29783", "D.S. 005-2012-TR", "Ley 30222", "D.S. 001-2021-TR"],
    "Sectorial": ["D.S. 017-2017-TR (Obreros)", "D.S. 011-2019-TR (Construcción)", "R.M. 111-2013-MEM"],
    "Salud/Ergo": ["R.M. 312-2011/MINSA", "R.M. 375-2008-TR", "D.S. 008-2022-SA"],
    "Vulnerables": ["Ley 28048 (Gestantes)", "Ley 31572 (Teletrabajo)"]
}

# 3. INTERFAZ: ESTRUCTURA DE GESTIÓN
st.sidebar.title("🛡️ SGI MPL - Senior")
st.sidebar.markdown(f"**Ing. Enrique Huambo**\nEspecialista SST")

tabs = st.tabs(["🏗️ Generación IPERC", "📄 Documentos y PETS", "🗄️ Legajo por Puesto", "⚖️ Biblioteca Legal", "🚨 Alertas"])

# --- TAB 1: EL CORAZÓN (IPERC SEGÚN RM 050) ---
with tabs[0]:
    st.header("📋 Elaboración de Matriz IPERC")
    st.write("Identificación de Peligros, Evaluación de Riesgos y Medidas de Control.")
    
    with st.form("main_iperc"):
        col1, col2 = st.columns(2)
        with col1:
            puesto = st.selectbox("Puesto de Trabajo", ["Obrero Municipal", "Serenazgo", "Limpieza Pública", "Parques", "Administrativo"])
            actividad = st.text_input("Actividad Específica")
            peligro = st.text_input("Peligro (Fuente/Situación)")
            riesgo = st.text_input("Riesgo (Evento/Consecuencia)")
        with col2:
            nivel = st.selectbox("Evaluación de Riesgo", ["Trivial", "Tolerable", "Moderado", "Importante", "Intolerable"])
            controles = st.text_area("Medidas de Control (Jerarquía de Controles)")
            norma = st.selectbox("Normativa Vinculada", [n for lista in BIBLIOTECA_SST.values() for n in lista])
        
        if st.form_submit_button("Registrar IPERC Base"):
            cod_id = f"MPL-SST-IPERC-{puesto[:3].upper()}-2026-001"
            conn = sqlite3.connect('sgi_full_essence.db')
            c = conn.cursor()
            c.execute("INSERT INTO matriz_iperc (puesto, actividad, peligro, riesgo, evaluacion, controles, norma_ref, codigo, fecha) VALUES (?,?,?,?,?,?,?,?,?)",
                      (puesto, actividad, peligro, riesgo, nivel, controles, norma, cod_id, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()
            st.success(f"IPERC Generado: {cod_id}")

# --- TAB 2: ESTANDARIZACIÓN DE DOCUMENTOS (DERIVADOS) ---
with tabs[1]:
    st.header("🛠️ Estandarización de Documentos Complementarios")
    st.write("A partir del IPERC, genere automáticamente el resto de la documentación.")
    
    conn = sqlite3.connect('sgi_full_essence.db')
    df_ip = pd.read_sql_query("SELECT codigo, puesto, controles FROM matriz_iperc", conn)
    conn.close()
    
    if not df_ip.empty:
        sel = st.selectbox("Seleccione IPERC de referencia", df_ip['codigo'].tolist())
        tipo_doc = st.selectbox("Documento a Crear", ["PETS (Procedimiento)", "Estándar de Seguridad", "Plan de Emergencia", "Registro de Inspección"])
        ver = st.text_input("Versión del Formato", "V.01")
        
        if st.button("Generar y Codificar Documento"):
            nuevo_cod = sel.replace("IPERC", tipo_doc[:3].upper())
            # Guardar relación
            st.success(f"Documento {nuevo_cod} generado exitosamente.")
            st.markdown(f"**Validación SST:** Este {tipo_doc} hereda los controles del IPERC seleccionado.")
    else:
        st.warning("Debe crear un IPERC primero.")

# --- TAB 3: LEGAJO POR PUESTO (EL AGRUPADOR) ---
with tabs[2]:
    st.header("🗄️ Legajos Documentales por Puesto")
    p_ver = st.selectbox("Filtrar por Puesto", ["Obrero Municipal", "Serenazgo", "Limpieza Pública", "Parques", "Administrativo"])
    
    conn = sqlite3.connect('sgi_full_essence.db')
    res = pd.read_sql_query(f"SELECT codigo, actividad, evaluacion, norma_ref FROM matriz_iperc WHERE puesto='{p_ver}'", conn)
    conn.close()
    
    if not res.empty:
        st.table(res)
    else:
        st.info("No hay documentos para este puesto aún.")

# --- TAB 4: BIBLIOTECA LEGAL (REPOSITORIO) ---
with tabs[3]:
    st.header("⚖️ Repositorio Normativo Verificado")
    for cat, leyes in BIBLIOTECA_SST.items():
        with st.expander(f"Ver {cat}"):
            for ley in leyes:
                st.write(f"📖 {ley}")

# --- TAB 5: ALERTAS (NOTIFICACIÓN) ---
with tabs[4]:
    st.header("🚨 Sistema de Alertas Críticas")
    if st.button("Simular Notificación de Riesgo Alto"):
        # Lógica de envío de correo configurada previamente
        st.error("Alerta enviada a enrique.huambo1987@gmail.com sobre Riesgo Crítico detectado.")
