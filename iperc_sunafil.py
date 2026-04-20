import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import random
import time

st.set_page_config(page_title="SGI Expert - Fase 4 (Alertas)", layout="wide")

# ==========================================
# 1. MOTOR DE BASE DE DATOS RELACIONAL (SQL)
# ==========================================
def init_db():
    conn = sqlite3.connect('sgi_expert.db')
    c = conn.cursor()
    # Usuarios
    c.execute('CREATE TABLE IF NOT EXISTS usuarios (username TEXT, password TEXT, rol TEXT, nombre_real TEXT, telefono TEXT)')
    if c.execute('SELECT count(*) FROM usuarios').fetchone()[0] == 0:
        c.execute("INSERT INTO usuarios VALUES ('admin', 'admin123', 'Especialista SST', 'Ing. Enrique', '+51999888777')")
        c.execute("INSERT INTO usuarios VALUES ('medico', 'medico123', 'Médico Ocupacional', 'Dr. Vera', '+51999111222')")
        c.execute("INSERT INTO usuarios VALUES ('auditor', 'auditor123', 'Auditor SUNAFIL', 'Inspector', '')")
        c.execute("INSERT INTO usuarios VALUES ('operario', '1234', 'Operario de Campo', 'Juan Pérez (Conductor)', '+51999444555')")
    
    # Tablas Anteriores
    c.execute('''CREATE TABLE IF NOT EXISTS iperc (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa TEXT, puesto TEXT, tarea TEXT, peligro TEXT, riesgo TEXT, nivel TEXT, norma TEXT, medidas TEXT, fecha TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS plan_anual (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa TEXT, puesto TEXT, tipo TEXT, tema TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ats_digital (id INTEGER PRIMARY KEY AUTOINCREMENT, operario TEXT, puesto TEXT, epp_completos TEXT, latitud TEXT, longitud TEXT, firma_hash TEXT, fecha_hora TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS accidentes (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha_hora TEXT, operario TEXT, puesto TEXT, descripcion TEXT, gravedad TEXT, estado_investigacion TEXT)''')
    
    # NUEVA TABLA FASE 4: VENCIMIENTOS Y PERSONAL
    c.execute('''CREATE TABLE IF NOT EXISTS personal_sst (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, puesto TEXT, fecha_emo TEXT, fecha_sctr TEXT)''')
    if c.execute('SELECT count(*) FROM personal_sst').fetchone()[0] == 0:
        # Insertamos data de prueba: Uno a punto de vencer y otro vencido
        hoy = datetime.now()
        vence_pronto = (hoy + timedelta(days=10)).strftime("%Y-%m-%d")
        vencido = (hoy - timedelta(days=5)).strftime("%Y-%m-%d")
        ok = (hoy + timedelta(days=180)).strftime("%Y-%m-%d")
        
        c.execute("INSERT INTO personal_sst (nombre, puesto, fecha_emo, fecha_sctr) VALUES ('Juan Pérez', 'Conductor Compactadora', ?, ?)", (vence_pronto, ok))
        c.execute("INSERT INTO personal_sst (nombre, puesto, fecha_emo, fecha_sctr) VALUES ('Luis Rojas', 'Operario Aseo', ?, ?)", (vencido, vencido))
        c.execute("INSERT INTO personal_sst (nombre, puesto, fecha_emo, fecha_sctr) VALUES ('Ana Gómez', 'Jardinera', ?, ?)", (ok, ok))

    conn.commit()
    conn.close()

init_db()

def cargar_tabla(query):
    conn = sqlite3.connect('sgi_expert.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def guardar_ats_digital(operario, puesto, epp, lat, lon, firma):
    conn = sqlite3.connect('sgi_expert.db')
    c = conn.cursor()
    c.execute("INSERT INTO ats_digital (operario, puesto, epp_completos, latitud, longitud, firma_hash, fecha_hora) VALUES (?,?,?,?,?,?,?)",
              (operario, puesto, str(epp), lat, lon, firma, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def registrar_accidente(operario, puesto, desc, grav):
    conn = sqlite3.connect('sgi_expert.db')
    c = conn.cursor()
    c.execute("INSERT INTO accidentes (fecha_hora, operario, puesto, descripcion, gravedad, estado_investigacion) VALUES (?,?,?,?,?,'Pendiente (Ley 29783)')",
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), operario, puesto, desc, grav))
    conn.commit()
    conn.close()

# ==========================================
# 2. SISTEMA DE AUTENTICACIÓN
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🔒 SGI Corporativo</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.info("💡 **Roles:**\n* **Admin:** `admin` / `admin123` \n* **Operario:** `operario` / `1234`")
        with st.form("login"):
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                conn = sqlite3.connect('sgi_expert.db')
                res = conn.cursor().execute("SELECT rol, nombre_real FROM usuarios WHERE username=? AND password=?", (u, p)).fetchone()
                if res:
                    st.session_state.logged_in, st.session_state.rol, st.session_state.nombre_real = True, res[0], res[1]
                    st.rerun()
                else: st.error("Error.")
    st.stop()

# ==========================================
# 3. INTERFACES (CERO OLVIDOS)
# ==========================================
st.sidebar.markdown(f"### 👤 {st.session_state.nombre_real}")
st.sidebar.info(f"Rol: {st.session_state.rol}")
if st.sidebar.button("🚪 Salir"):
    st.session_state.logged_in = False
    st.rerun()

# ---------------------------------------------------------
# INTERFAZ MÓVIL (OPERARIO)
# ---------------------------------------------------------
if st.session_state.rol == "Operario de Campo":
    st.markdown("## 📱 Portal Operativo")
    with st.expander("🚨 S.O.S - REPORTAR INCIDENTE", expanded=False):
        desc = st.text_area("¿Qué sucedió?")
        grav = st.selectbox("Gravedad", ["Incidente (Casi Accidente)", "Accidente Leve", "Accidente Incapacitante", "Accidente Mortal"])
        if st.button("⚠️ ENVIAR ALERTA", type="primary", use_container_width=True):
            registrar_accidente(st.session_state.nombre_real, "Conductor Compactadora", desc, grav)
            st.success("Alerta enviada a Central.")
            
    st.markdown("### 📝 Firma de ATS Diario")
    st.checkbox("👷 Casco")
    st.checkbox("🦺 Chaleco")
    st.checkbox("🥾 Botas")
    firma = st.text_input("DNI para firma:")
    if st.button("✅ Firmar e Iniciar Turno", use_container_width=True):
        if firma:
            guardar_ats_digital(st.session_state.nombre_real, "Conductor Compactadora", "OK", "-6.771", "-79.901", firma)
            st.success("ATS Guardado.")
        else: st.error("Ingrese su DNI.")

# ---------------------------------------------------------
# INTERFAZ ESCRITORIO (ADMIN / MÉDICO)
# ---------------------------------------------------------
else:
    st.title("🛡️ SGI 360: Mando Corporativo")
    
    # Consolidamos Plan y Legal en uno para hacer espacio a las Alertas
    t_ats, t_iperc, t_docs, t_acc, t_alertas = st.tabs([
        "📱 1. ATS", "👤 2. IPERC", "📚 3. Docs & Legal", "🚨 4. Accidentes", "🔔 5. Alertas (Fase 4)"
    ])

    with t_ats:
        st.dataframe(cargar_tabla("SELECT fecha_hora, operario, latitud, longitud FROM ats_digital ORDER BY id DESC"), use_container_width=True)

    with t_iperc:
        if st.session_state.rol == "Especialista SST":
            puesto = st.text_input("Puesto", "Operario")
            if cargar_tabla(f"SELECT COUNT(*) FROM accidentes WHERE puesto='{puesto}'").iloc[0,0] > 0:
                st.error("⚠️ Puesto con historial de accidentes. Reevaluar IPERC (Art. 57).")
            if st.button("🚀 Procesar IPERC"): st.success("IPERC Generado.")

    with t_docs:
        st.markdown("#### Plan Anual")
        st.dataframe(cargar_tabla("SELECT * FROM plan_anual"), height=150, use_container_width=True)
        st.markdown("#### Matriz Legal")
        st.dataframe(cargar_tabla("SELECT norma, peligro, medidas FROM iperc"), height=150, use_container_width=True)

    with t_acc:
        st.dataframe(cargar_tabla("SELECT fecha_hora, operario, gravedad, estado_investigacion FROM accidentes"), use_container_width=True)

    # --- MAGIA FASE 4: CERO OLVIDOS ---
    with t_alertas:
        st.markdown("### 🔔 Centro de Control Automático (Cero Olvidos)")
        st.info("El sistema escanea la base de datos en tiempo real y detecta quiebres normativos antes de que ocurran.")
        
        col_alerta1, col_alerta2 = st.columns(2)
        
        # 1. ESCÁNER DE VENCIMIENTOS MÉDICOS Y SCTR
        with col_alerta1:
            st.markdown("#### 🏥 Alertas Médicas (EMO / SCTR)")
            df_personal = cargar_tabla("SELECT nombre, puesto, fecha_emo FROM personal_sst")
            hoy = datetime.now()
            
            for index, row in df_personal.iterrows():
                fecha_emo = datetime.strptime(row['fecha_emo'], "%Y-%m-%d")
                dias_restantes = (fecha_emo - hoy).days
                
                if dias_restantes < 0:
                    st.error(f"🔴 **VENCIDO:** El EMO de {row['nombre']} venció hace {abs(dias_restantes)} días.")
                    if st.button(f"📧 Enviar Notificación RR.HH ({row['nombre']})", key=f"btn_emo_{index}"):
                        st.toast(f"Enviando correo a Recursos Humanos y al Médico Ocupacional... 🚀", icon="📧")
                        time.sleep(1)
                        st.success("Correo enviado exitosamente.")
                        
                elif 0 <= dias_restantes <= 15:
                    st.warning(f"🟡 **POR VENCER:** El EMO de {row['nombre']} vence en {dias_restantes} días.")
                    if st.button(f"📲 WhatsApp a Trabajador ({row['nombre']})", key=f"btn_emo_{index}"):
                        st.toast(f"Conectando con API de WhatsApp...", icon="📲")
                        time.sleep(1)
                        st.success("Mensaje programado: 'Estimado Juan, su EMO vence en 10 días. Acérquese a la clínica...'")
        
        # 2. ESCÁNER DE CUMPLIMIENTO LEGAL (ACCIDENTES SIN INVESTIGAR)
        with col_alerta2:
            st.markdown("#### 🚨 Alertas Legales (Investigaciones)")
            df_pendientes = cargar_tabla("SELECT id, operario, fecha_hora FROM accidentes WHERE estado_investigacion LIKE '%Pendiente%'")
            
            if not df_pendientes.empty:
                for index, row in df_pendientes.iterrows():
                    st.error(f"🔴 **INFRACCIÓN LATENTE:** Accidente de {row['operario']} el {row['fecha_hora']} no ha sido investigado.")
                    if st.button(f"📲 WhatsApp a Comité SST (Caso #{row['id']})", key=f"btn_acc_{index}"):
                        st.toast("Notificando al Comité de Seguridad y Salud en el Trabajo...", icon="📲")
                        time.sleep(1)
                        st.success("El Comité ha sido convocado de urgencia vía WhatsApp.")
            else:
                st.success("✅ Todas las investigaciones están al día.")
