import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import random

st.set_page_config(page_title="SGI Expert - Fase 2 (Operaciones)", layout="wide")

# ==========================================
# 1. MOTOR DE BASE DE DATOS RELACIONAL (SQL)
# ==========================================
def init_db():
    conn = sqlite3.connect('sgi_expert.db')
    c = conn.cursor()
    # Tabla de Usuarios
    c.execute('CREATE TABLE IF NOT EXISTS usuarios (username TEXT, password TEXT, rol TEXT, nombre_real TEXT)')
    
    c.execute('SELECT count(*) FROM usuarios')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO usuarios VALUES ('admin', 'admin123', 'Especialista SST', 'Ing. Enrique')")
        c.execute("INSERT INTO usuarios VALUES ('medico', 'medico123', 'Médico Ocupacional', 'Dr. Vera')")
        c.execute("INSERT INTO usuarios VALUES ('auditor', 'auditor123', 'Auditor SUNAFIL', 'Inspector')")
        # NUEVO USUARIO DE CAMPO
        c.execute("INSERT INTO usuarios VALUES ('operario', '1234', 'Operario de Campo', 'Juan Pérez (Conductor)')")
    
    c.execute('''CREATE TABLE IF NOT EXISTS iperc 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa TEXT, puesto TEXT, tarea TEXT, 
                 peligro TEXT, riesgo TEXT, nivel TEXT, norma TEXT, medidas TEXT, fecha TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS plan_anual 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa TEXT, puesto TEXT, tipo TEXT, tema TEXT)''')
    
    # NUEVA TABLA: ATS DIGITAL FIRMADO EN CAMPO
    c.execute('''CREATE TABLE IF NOT EXISTS ats_digital 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, operario TEXT, puesto TEXT, epp_completos TEXT, 
                 latitud TEXT, longitud TEXT, firma_hash TEXT, fecha_hora TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

def cargar_tabla(query):
    conn = sqlite3.connect('sgi_expert.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def guardar_ats_digital(operario, puesto, epp_completos, lat, lon, firma):
    conn = sqlite3.connect('sgi_expert.db')
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO ats_digital (operario, puesto, epp_completos, latitud, longitud, firma_hash, fecha_hora) VALUES (?,?,?,?,?,?,?)",
              (operario, puesto, str(epp_completos), lat, lon, firma, fecha_actual))
    conn.commit()
    conn.close()

# ==========================================
# 2. SISTEMA DE AUTENTICACIÓN
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.rol = ""
    st.session_state.username = ""
    st.session_state.nombre_real = ""

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🔒 Acceso al SGI Corporativo</h1>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.info("💡 **Prueba de Roles:**\n* **Admin:** `admin` / `admin123` \n* **Operario de campo:** `operario` / `1234`")
            with st.form("login_form"):
                user = st.text_input("Usuario")
                pwd = st.text_input("Contraseña", type="password")
                submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)
                
                if submit:
                    conn = sqlite3.connect('sgi_expert.db')
                    c = conn.cursor()
                    c.execute("SELECT rol, nombre_real FROM usuarios WHERE username=? AND password=?", (user, pwd))
                    resultado = c.fetchone()
                    conn.close()
                    
                    if resultado:
                        st.session_state.logged_in = True
                        st.session_state.rol = resultado[0]
                        st.session_state.username = user
                        st.session_state.nombre_real = resultado[1]
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas.")
    st.stop()

# ==========================================
# 3. INTERFACES SEGÚN EL ROL
# ==========================================
st.sidebar.markdown(f"### 👤 {st.session_state.nombre_real}")
st.sidebar.info(f"**Rol:** {st.session_state.rol}")
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.logged_in = False
    st.rerun()

is_admin = st.session_state.rol == "Especialista SST"

# ---------------------------------------------------------
# INTERFAZ MÓVIL: SOLO PARA OPERARIOS DE CAMPO
# ---------------------------------------------------------
if st.session_state.rol == "Operario de Campo":
    st.markdown("## 📱 Portal de Operaciones en Campo")
    st.warning("Debe completar su ATS y firmar antes de iniciar su ruta.")
    
    st.markdown("### 1. Lectura de Peligros (Resumen IPERC)")
    st.info("Puesto: **Conductor de Compactadora**\n* Riesgo principal: Atropello, Ruido, Riesgo Biológico.\n* Controles: Manejo a la defensiva, uso de EPP completo.")
    
    st.markdown("### 2. Check de EPPs Obligatorios")
    epp_casco = st.checkbox("👷 Casco de Seguridad")
    epp_chaleco = st.checkbox("🦺 Chaleco Reflectivo")
    epp_guantes = st.checkbox("🧤 Guantes de Badana/Nitrilo")
    epp_zapatos = st.checkbox("🥾 Zapatos de Seguridad (Antideslizantes)")
    
    st.markdown("### 3. Sello de Geolocalización (GPS)")
    if 'gps_capturado' not in st.session_state:
        st.session_state.gps_capturado = False
        st.session_state.lat = ""
        st.session_state.lon = ""

    if st.button("📍 Capturar mi ubicación actual (GPS)"):
        # Simulador de captura GPS (Lambayeque)
        st.session_state.lat = f"-6.7{random.randint(100, 999)}"
        st.session_state.lon = f"-79.9{random.randint(100, 999)}"
        st.session_state.gps_capturado = True
    
    if st.session_state.gps_capturado:
        st.success(f"GPS Capturado: Lat {st.session_state.lat}, Lon {st.session_state.lon}")
    
    st.markdown("### 4. Firma Digital")
    firma_digital = st.text_input("Escriba su DNI para firmar digitalmente:")
    declaracion = st.checkbox("Declaro bajo juramento que me encuentro en buenas condiciones de salud, he revisado mis EPPs y he comprendido los riesgos de mi labor hoy.")
    
    if st.button("✅ Firmar ATS e Iniciar Turno", use_container_width=True, type="primary"):
        if epp_casco and epp_chaleco and epp_guantes and epp_zapatos and firma_digital and declaracion and st.session_state.gps_capturado:
            guardar_ats_digital(st.session_state.nombre_real, "Conductor de Compactadora", "Completos", st.session_state.lat, st.session_state.lon, firma_digital)
            st.balloons()
            st.success("¡ATS firmado y enviado a la base de datos! Puede iniciar su turno con seguridad.")
        else:
            st.error("Debe marcar todos los EPPs, capturar su GPS, ingresar su DNI y aceptar la declaración jurada.")

# ---------------------------------------------------------
# INTERFAZ DE ESCRITORIO: PARA INGENIEROS / MÉDICOS / AUDITORES
# ---------------------------------------------------------
else:
    st.title("🛡️ SGI 360: Panel de Mando Corporativo")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📱 1. Control de Campo (ATS en Vivo)", 
        "👤 2. Generador IPERC", 
        "📚 3. Plan Anual", 
        "⚖️ 4. Matriz Legal"
    ])

    # --- NUEVO MÓDULO: CONTROL DE CAMPO EN VIVO ---
    with tab1:
        st.markdown("### 📡 Monitoreo de Inicio de Jornada en Tiempo Real")
        st.info("Aquí puede verificar qué trabajadores ya firmaron su Análisis de Trabajo Seguro (ATS) desde sus celulares, junto con su sello de tiempo y ubicación GPS exacta.")
        
        df_ats = cargar_tabla("SELECT fecha_hora, operario, puesto, epp_completos, latitud, longitud, firma_hash as dni_firma FROM ats_digital ORDER BY id DESC")
        
        if not df_ats.empty:
            st.dataframe(df_ats, use_container_width=True)
            
            # Botón de exportación rápida para auditoría
            csv_ats = df_ats.to_csv(sep=';', index=False).encode('utf-8-sig')
            st.download_button("📥 Exportar Registro de ATS Diario (Excel)", data=csv_ats, file_name=f"Registro_ATS_Diario.csv", mime='text/csv')
        else:
            st.warning("Aún no hay registros de trabajadores iniciando turno hoy.")

    # --- MÓDULO IPERC ---
    with tab2:
        if is_admin:
            st.info("Módulo restringido para el Especialista SST.")
            puesto_ind = st.text_input("Puesto a evaluar", value="Operario de Aseo")
            if st.button("🚀 Procesar IPERC Básico"):
                st.success("IPERC procesado (Simulado para acortar código en esta demostración). Revisa el Plan Anual.")
        else:
            st.error("⛔ Acceso Denegado: Su rol no permite generar matrices.")

    # --- MÓDULOS DE DB ---
    with tab3:
        st.markdown("### 📚 Plan Anual (Desde Base de Datos)")
        df_plan = cargar_tabla("SELECT * FROM plan_anual")
        st.dataframe(df_plan, use_container_width=True)

    with tab4:
        st.markdown("### ⚖️ Matriz de Trazabilidad Legal")
        df_legal = cargar_tabla("SELECT norma, peligro, medidas FROM iperc")
        st.dataframe(df_legal, use_container_width=True)
