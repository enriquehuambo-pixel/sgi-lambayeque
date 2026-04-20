import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. CONFIGURACIÓN E IDENTIDAD
st.set_page_config(page_title="SGI Senior - Enrique Huambo", layout="wide")

def init_db():
    conn = sqlite3.connect('sgi_esencia_total.db')
    c = conn.cursor()
    # Tabla IPERC Completa (Con Controles Existentes)
    c.execute('''CREATE TABLE IF NOT EXISTS matriz_iperc 
                 (id INTEGER PRIMARY KEY, puesto TEXT, actividad TEXT, peligro TEXT, riesgo TEXT, 
                  consecuencia TEXT, c_ingenieria TEXT, c_admin TEXT, c_epp TEXT, 
                  nivel TEXT, base_legal TEXT, codigo TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 2. LIBRERÍA DE INTELIGENCIA SST (AUTO-GENERACIÓN)
DATOS_INTELIGENTES = {
    "Limpieza Pública": {
        "Actividad": "Recolección de residuos sólidos",
        "Peligro": "Agentes biológicos (bacterias, virus en basura)",
        "Riesgo": "Contacto con residuos contaminados",
        "Consecuencia": "Infecciones, enfermedades infectocontagiosas",
        "Ingenieria": "Compactadoras herméticas",
        "Admin": "Protocolo de higiene, vacunas",
        "EPP": "Guantes de nitrilo reforzado, mascarilla, calzado de seguridad"
    },
    "Serenazgo": {
        "Actividad": "Patrullaje preventivo",
        "Peligro": "Agresión por terceros / Delincuencia",
        "Riesgo": "Exposición a violencia física",
        "Consecuencia": "Contusiones, heridas, traumatismos",
        "Ingenieria": "Cámaras de vigilancia en unidades",
        "Admin": "Capacitación en defensa personal y manejo de crisis",
        "EPP": "Chaleco antibalas, vara de ley, radio comunicación"
    },
    "Obras / Construcción": {
        "Actividad": "Trabajo en altura / Excavación",
        "Peligro": "Caída de personas a distinto nivel",
        "Riesgo": "Pérdida de equilibrio en altura",
        "Consecuencia": "Fracturas, muerte",
        "Ingenieria": "Andamios certificados, líneas de vida fijas",
        "Admin": "Permiso de Trabajo de Alto Riesgo (PETAR)",
        "EPP": "Arnés de cuerpo completo, línea de anclaje con absorbedor"
    }
}

# 3. REPOSITORIO NORMATIVO (CATEGORÍAS REALES)
BIBLIOTECA_SST = {
    "General": ["Ley 29783", "D.S. 005-2012-TR", "Ley 30222", "D.S. 001-2021-TR"],
    "Sectorial": ["D.S. 017-2017-TR (Obreros)", "D.S. 011-2019-TR (Construcción)", "R.M. 375-2008-TR (Ergonomía)"],
    "Vulnerables": ["Ley 28048 (Gestantes)", "Ley 31572 (Teletrabajo)"]
}

# 4. INTERFAZ: ESTRUCTURA DE GESTIÓN
st.sidebar.title("🛡️ SGI MPL - Senior")
st.sidebar.info(f"Admin: Ing. Enrique Huambo\nEspecialista SST")

tabs = st.tabs(["🏗️ Generación de IPERC", "📄 Documentos Derivados", "🗄️ Legajo por Puesto", "⚖️ Repositorio Legal"])

# --- TAB 1: EL MOTOR IPERC (CON COLUMNAS DE CONTROL) ---
with tabs[0]:
    st.header("📋 Matriz IPERC - Identificación y Evaluación")
    
    puesto_sel = st.selectbox("Seleccione el Puesto de Trabajo", list(DATOS_INTELIGENTES.keys()) + ["Administrativo"])
    
    # Auto-llenado basado en la inteligencia del sistema
    default_data = DATOS_INTELIGENTES.get(puesto_sel, {"Actividad": "", "Peligro": "", "Riesgo": "", "Consecuencia": "", "Ingenieria": "", "Admin": "", "EPP": ""})

    with st.form("iperc_full"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📍 Identificación")
            act = st.text_input("Actividad", default_data["Actividad"])
            pel = st.text_input("Peligro", default_data["Peligro"])
            rie = st.text_input("Riesgo", default_data["Riesgo"])
            cons = st.text_input("Consecuencia", default_data["Consecuencia"])
            norma = st.selectbox("Marco Legal Vinculado", [n for lista in BIBLIOTECA_SST.values() for n in lista])

        with col2:
            st.subheader("🛡️ Controles Existentes (Con qué se cuenta)")
            c_ing = st.text_input("Control de Ingeniería", default_data["Ingenieria"])
            c_adm = st.text_input("Control Administrativo", default_data["Admin"])
            c_epp = st.text_input("EPP Específico", default_data["EPP"])
            nivel = st.select_slider("Nivel de Riesgo Residual", options=["Bajo", "Medio", "Alto", "Crítico"])

        if st.form_submit_button("Generar IPERC y Guardar en Legajo"):
            cod_doc = f"MPL-SST-IPERC-{puesto_sel[:3].upper()}-2026-001"
            # Guardar en DB
            conn = sqlite3.connect('sgi_esencia_total.db')
            c = conn.cursor()
            c.execute("""INSERT INTO matriz_iperc 
                         (puesto, actividad, peligro, riesgo, consecuencia, c_ingenieria, c_admin, c_epp, nivel, base_legal, codigo) 
                         VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                      (puesto_sel, act, pel, rie, cons, c_ing, c_adm, c_epp, nivel, norma, cod_doc))
            conn.commit()
            conn.close()
            st.success(f"IPERC Guardado exitosamente con código: {cod_doc}")

# --- TAB 2: DOCUMENTOS DERIVADOS ---
with tabs[1]:
    st.header("📑 Generación de PETS y Planes")
    st.write("El sistema usa los controles del IPERC para proponer el estándar de trabajo.")
    # (Lógica para extraer el IPERC guardado y transformarlo en PETS)

# --- TAB 3: LEGAJO (LA AGRUPACIÓN POR PUESTO) ---
with tabs[2]:
    st.header("🗄️ Expediente Documental por Cargo")
    p_filtro = st.selectbox("Filtrar Legajo", list(DATOS_INTELIGENTES.keys()))
    
    conn = sqlite3.connect('sgi_esencia_total.db')
    df_res = pd.read_sql_query(f"SELECT codigo, actividad, nivel, base_legal FROM matriz_iperc WHERE puesto='{p_filtro}'", conn)
    conn.close()
    
    if not df_res.empty:
        st.table(df_res)
    else:
        st.info("No hay registros para este puesto.")

# --- TAB 4: REPOSITORIO LEGAL ---
with tabs[3]:
    st.header("⚖️ Marco Normativo Peruano")
    for cat, leyes in BIBLIOTECA_SST.items():
        with st.expander(cat):
            for ley in leyes: st.write(f"✅ {ley}")
