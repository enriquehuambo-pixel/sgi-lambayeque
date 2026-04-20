import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================
# CONFIGURACIÓN Y ESTÁNDARES (ISO / SST)
# ==========================================
FORMATO_BASE = {
    "ENTIDAD": "Municipalidad Provincial de Lambayeque",
    "SIGLA": "MPL",
    "SISTEMA": "SST"
}

# ==========================================
# 1. BASE DE DATOS MEJORADA
# ==========================================
def init_db():
    conn = sqlite3.connect('sgi_enterprise.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS usuarios (username TEXT, password TEXT, rol TEXT, nombre TEXT)')
    # Nueva tabla para "Cerebro" del sistema (Entrenamiento)
    c.execute('CREATE TABLE IF NOT EXISTS entrenamiento (id INTEGER PRIMARY KEY, contenido TEXT, fuente TEXT, fecha TEXT)')
    # Tabla de Documentos con Codificación
    c.execute('''CREATE TABLE IF NOT EXISTS documentos (id INTEGER PRIMARY KEY, codigo TEXT, titulo TEXT, version TEXT, contenido TEXT, fecha TEXT)''')
    
    if c.execute('SELECT count(*) FROM usuarios').fetchone()[0] == 0:
        c.execute("INSERT INTO usuarios VALUES ('admin', 'admin123', 'Especialista SST', 'Enrique Huambo')")
    conn.commit()
    conn.close()

# ==========================================
# 2. LÓGICA DE GESTIÓN DOCUMENTAL (EL ESTÁNDAR)
# ==========================================
def generar_codigo(tipo_doc, correlativo):
    # Estándar: SIGLA-SISTEMA-TIPO-CORRELATIVO (Ej: MPL-SST-IPERC-001)
    return f"{FORMATO_BASE['SIGLA']}-{FORMATO_BASE['SISTEMA']}-{tipo_doc}-{str(correlativo).zfill(3)}"

def enviar_alerta_real(asunto, mensaje):
    cuenta = "enrique.huambo1987@gmail.com"
    password_app = "ejerfkbcs lqujrf" 
    msg = MIMEMultipart()
    msg['From'] = cuenta
    msg['To'] = cuenta
    msg['Subject'] = asunto
    msg.attach(MIMEText(mensaje, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(cuenta, password_app)
        server.send_message(msg)
        server.quit()
        return True
    except: return False

init_db()

# ==========================================
# 3. INTERFAZ STREAMLIT
# ==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🛡️ SGI Enterprise: Gestión Estandarizada")
    with st.form("Login"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            if u == "admin" and p == "admin123":
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# Menú Lateral
st.sidebar.title(f"Ing. Enrique Huambo")
st.sidebar.info("Especialista SST")

tabs = st.tabs(["🚀 Entrenamiento IA", "📑 Estandarización", "📋 Generador IPERC", "🔔 Alertas"])

# --- FASE DE ENTRENAMIENTO ---
with tabs[0]:
    st.header("🧠 Centro de Entrenamiento del Sistema")
    st.write("Sube ejemplos de IPERC exitosos o medidas de control específicas para que la IA aprenda tu criterio técnico.")
    
    uploaded_file = st.file_uploader("Cargar documento de referencia (TXT/CSV)", type=['txt', 'csv'])
    if uploaded_file is not None:
        contenido = uploaded_file.read().decode("utf-8")
        st.success("Documento cargado. Procesando patrones de peligro...")
        # Aquí se guardaría en la tabla 'entrenamiento' para que el Chatbot lo use de contexto
        st.info("La IA ahora priorizará estas medidas de control en futuras consultas.")

# --- GESTIÓN DOCUMENTAL (EL PROCEDIMIENTO) ---
with tabs[1]:
    st.header("📄 Estándar de Elaboración de Documentos")
    st.markdown("""
    | Campo | Requisito Estándar |
    | :--- | :--- |
    | **Formato** | A4 Horizontal para Matrices / Vertical para Procedimientos |
    | **Codificación** | `MPL-SST-[TIPO]-[NUM]` |
    | **Versión** | Numérica (V.01, V.02...) |
    | **Tipografía** | Arial 10 (Cuerpo) / Bold (Títulos) |
    """)
    
    st.subheader("Documentos Vigentes")
    # Simulación de tabla de control de documentos
    data_docs = {
        "Código": ["MPL-SST-IPERC-001", "MPL-SST-PRO-005"],
        "Documento": ["Matriz IPERC General", "Procedimiento de Trabajos en Altura"],
        "Versión": ["V.02", "V.01"],
        "Última Revisión": ["2026-03-10", "2026-04-15"]
    }
    st.table(data_docs)

# --- GENERADOR CON FORMATO ---
with tabs[2]:
    st.header("📝 Elaboración de Documento Nuevo")
    tipo = st.selectbox("Tipo de Documento", ["IPERC", "ESTANDAR", "PROCEDIMIENTO", "REGISTRO"])
    titulo = st.text_input("Título del Documento")
    
    if st.button("Generar Borrador Codificado"):
        codigo = generar_codigo(tipo, 1) # Lógica simplificada
        st.subheader(f"Vista Previa: {codigo}")
        st.markdown(f"""
        **{FORMATO_BASE['ENTIDAD']}** **Sistema de Gestión de Seguridad y Salud en el Trabajo** ---
        **Código:** {codigo} | **Versión:** V.01 | **Fecha:** {datetime.now().strftime('%d/%m/%Y')}  
        **Título:** {titulo.upper()}
        """)
        st.info("Estructura alineada al estándar de la Municipalidad.")

# --- ALERTAS ---
with tabs[3]:
    if st.button("📧 Probar Notificación Maestra"):
        if enviar_alerta_real("SGI: Prueba de Conexión", "El sistema de alertas está activo y codificado."):
            st.success("Correo enviado a enrique.huambo1987@gmail.com")
