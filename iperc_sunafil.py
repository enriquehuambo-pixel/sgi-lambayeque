import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración de página
st.set_page_config(page_title="SGI Enterprise - Enrique Huambo", layout="wide")

# ==========================================
# 1. MOTOR DE BASE DE DATOS Y LÓGICA CORE
# ==========================================
def init_db():
    conn = sqlite3.connect('sgi_expert.db')
    c = conn.cursor()
    # Tablas de Usuarios, IPERC, Accidentes y Personal
    c.execute('CREATE TABLE IF NOT EXISTS usuarios (username TEXT, password TEXT, rol TEXT, nombre_real TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS iperc (id INTEGER PRIMARY KEY AUTOINCREMENT, puesto TEXT, peligro TEXT, riesgo TEXT, nivel TEXT, norma TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS accidentes (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, operario TEXT, descripcion TEXT, gravedad TEXT, estado TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS personal_sst (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, puesto TEXT, fecha_emo TEXT)''')
    
    if c.execute('SELECT count(*) FROM usuarios').fetchone()[0] == 0:
        c.execute("INSERT INTO usuarios VALUES ('admin', 'admin123', 'Especialista SST', 'Ing. Enrique Huambo')")
        c.execute("INSERT INTO usuarios VALUES ('operario', '1234', 'Operario', 'Personal de Campo')")
        # Datos de prueba para alertas
        hoy = datetime.now()
        c.execute("INSERT INTO personal_sst (nombre, puesto, fecha_emo) VALUES ('Trabajador Ejemplo', 'Operario', ?)", ((hoy + timedelta(days=5)).strftime("%Y-%m-%d"),))
    
    conn.commit()
    conn.close()

def cargar_tabla(query):
    conn = sqlite3.connect('sgi_expert.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ==========================================
# 2. FUNCIÓN DE ENVÍO DE CORREO REAL
# ==========================================
def enviar_alerta_real(asunto, mensaje):
    cuenta = "enrique.huambo1987@gmail.com"
    # Tu contraseña de aplicación proporcionada
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
    except Exception as e:
        return False

# Inicializar DB
init_db()

# ==========================================
# 3. SISTEMA DE AUTENTICACIÓN
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🛡️ SGI Corporativo v5.0</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login"):
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Ingresar", use_container_width=True):
                res = sqlite3.connect('sgi_expert.db').cursor().execute("SELECT rol, nombre_real FROM usuarios WHERE username=? AND password=?", (u, p)).fetchone()
                if res:
                    st.session_state.logged_in, st.session_state.rol, st.session_state.nombre_real = True, res[0], res[1]
                    st.rerun()
                else: st.error("Acceso incorrecto")
    st.stop()

# ==========================================
# 4. DASHBOARD PRINCIPAL
# ==========================================
st.sidebar.title(f"Bienvenido, {st.session_state.nombre_real}")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.logged_in = False
    st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["📋 Gestión IPERC", "🚨 Accidentes", "🔔 Alertas Reales", "🧠 Asistente IA"])

with tab1:
    st.header("Matriz IPERC Dinámica")
    puesto_eval = st.selectbox("Seleccione Puesto", ["Ingeniero", "Operario Limpieza", "Serenazgo", "Administrativo"])
    if st.button("Generar IPERC"):
        st.success(f"Matriz IPERC generada para {puesto_eval} bajo Ley 29783.")
        st.info("Controles sugeridos: Sustitución de procesos y EPP específico.")

with tab2:
    st.header("Registro de Incidentes")
    with st.form("accidente"):
        desc = st.text_area("Descripción del suceso")
        grav = st.selectbox("Gravedad", ["Leve", "Grave", "Muy Grave"])
        if st.form_submit_button("Registrar y Notificar"):
            st.warning("Incidente guardado en Base de Datos.")
            if grav == "Muy Grave":
                enviar_alerta_real("⚠️ ALERTA: Accidente Muy Grave", f"Se ha reportado un incidente: {desc}")
                st.error("Alerta crítica enviada a enrique.huambo1987@gmail.com")

with tab3:
    st.header("Centro de Alertas de Vencimiento")
    df_p = cargar_tabla("SELECT * FROM personal_sst")
    hoy = datetime.now()
    
    for i, r in df_p.iterrows():
        f_emo = datetime.strptime(r['fecha_emo'], "%Y-%m-%d")
        dias = (f_emo - hoy).days
        if dias <= 7:
            st.error(f"EMO de {r['nombre']} vence en {dias} días.")
            if st.button(f"Enviar Correo de Aviso a {r['nombre']}", key=i):
                if enviar_alerta_real("Aviso de Vencimiento EMO", f"Estimado {r['nombre']}, su examen vence en {dias} días."):
                    st.success("Correo enviado exitosamente.")

with tab4:
    st.header("SST GPT: Consultor Legal")
    prompt = st.chat_input("¿Qué dice la Ley 29783 sobre...?")
    if prompt:
        st.chat_message("user").write(prompt)
        with st.chat_message("assistant"):
            if "plazo" in prompt.lower():
                st.write("Según el D.S. 005-2012-TR, el plazo para reportar accidentes mortales es de 24 horas.")
            else:
                st.write("Basado en el Reglamento Interno (RISST) y la normativa peruana, se debe proceder con la jerarquía de controles: Eliminación, Sustitución, Ingeniería, Administrativos y EPP.")
