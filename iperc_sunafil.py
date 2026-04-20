import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

st.set_page_config(page_title="SGI Expert - Compliance Perú", layout="wide")

# ==========================================
# 1. MOTOR DE BASE DE DATOS RELACIONAL (SQL)
# ==========================================
def init_db():
    conn = sqlite3.connect('sgi_expert.db')
    c = conn.cursor()
    # Tabla de Usuarios
    c.execute('CREATE TABLE IF NOT EXISTS usuarios (username TEXT, password TEXT, rol TEXT)')
    # Insertar usuarios por defecto si la tabla está vacía
    c.execute('SELECT count(*) FROM usuarios')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO usuarios VALUES ('admin', 'admin123', 'Especialista SST')")
        c.execute("INSERT INTO usuarios VALUES ('medico', 'medico123', 'Médico Ocupacional')")
        c.execute("INSERT INTO usuarios VALUES ('auditor', 'auditor123', 'Auditor SUNAFIL')")
    
    # Tabla de Historial IPERC
    c.execute('''CREATE TABLE IF NOT EXISTS iperc 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa TEXT, puesto TEXT, tarea TEXT, 
                 peligro TEXT, riesgo TEXT, nivel TEXT, norma TEXT, medidas TEXT, fecha TEXT)''')
    
    # Tabla de Plan Anual
    c.execute('''CREATE TABLE IF NOT EXISTS plan_anual 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, empresa TEXT, puesto TEXT, tipo TEXT, tema TEXT)''')
    
    conn.commit()
    conn.close()

# Inicializar la base de datos al arrancar
init_db()

# Funciones de persistencia
def guardar_iperc_db(empresa, puesto, tarea, peligro, riesgo, nivel, norma, medidas):
    conn = sqlite3.connect('sgi_expert.db')
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO iperc (empresa, puesto, tarea, peligro, riesgo, nivel, norma, medidas, fecha) VALUES (?,?,?,?,?,?,?,?,?)",
              (empresa, puesto, tarea, peligro, riesgo, nivel, norma, medidas, fecha_actual))
    conn.commit()
    conn.close()

def guardar_plan_db(empresa, puesto, tipo, tema):
    conn = sqlite3.connect('sgi_expert.db')
    c = conn.cursor()
    c.execute("INSERT INTO plan_anual (empresa, puesto, tipo, tema) VALUES (?,?,?,?)", (empresa, puesto, tipo, tema))
    conn.commit()
    conn.close()

def cargar_tabla(query):
    conn = sqlite3.connect('sgi_expert.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ==========================================
# 2. SISTEMA DE AUTENTICACIÓN Y ROLES (LOGIN)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.rol = ""
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🔒 Acceso al SGI Corporativo</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        st.write("Ingrese sus credenciales para acceder al sistema:")
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Iniciar Sesión")
        
        if submit:
            conn = sqlite3.connect('sgi_expert.db')
            c = conn.cursor()
            c.execute("SELECT rol FROM usuarios WHERE username=? AND password=?", (user, pwd))
            resultado = c.fetchone()
            conn.close()
            
            if resultado:
                st.session_state.logged_in = True
                st.session_state.rol = resultado[0]
                st.session_state.username = user
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos.")
    st.stop() # Detiene la ejecución aquí si no está logueado

# ==========================================
# 3. INTERFAZ PRINCIPAL DEL SISTEMA (LOGUEADO)
# ==========================================
def calcular_nivel(valor):
    if valor >= 25: return "IT"
    if valor >= 17: return "IM"
    if valor >= 9:  return "MO"
    if valor >= 5:  return "TO"
    return "TR"

st.sidebar.markdown(f"### 👤 Usuario: {st.session_state.username}")
st.sidebar.info(f"**Rol:** {st.session_state.rol}")
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🛡️ SGI 360: Operaciones, Base de Datos y Cumplimiento")

# Filtro de seguridad por Rol
is_admin = st.session_state.rol == "Especialista SST"

st.markdown("### 📝 Datos de la Entidad")
col_h1, col_h2 = st.columns(2)
empresa = col_h1.text_input("Razón Social", value="Municipalidad Provincial de Lambayeque", disabled=not is_admin)
sector = col_h2.selectbox("Sector Económico", ["Obreros Municipales (D.S. 017-2017-TR)", "General / Administrativo (Ley 29783)"], disabled=not is_admin)

# 4. SISTEMA DE PESTAÑAS (MÓDULOS)
tab1, tab2, tab3, tab4 = st.tabs(["👤 1. Generador IPERC", "📚 2. Plan Anual (DB)", "⚖️ 3. Matriz Legal (DB)", "📊 4. Dashboard de Control"])

# --- MÓDULO 1: GENERACIÓN (Solo para Especialista SST) ---
with tab1:
    if is_admin:
        st.info("Al procesar el IPERC, los datos se guardarán permanentemente en la Base de Datos SQL (sgi_expert.db).")
        col_i1, col_i2, col_i3 = st.columns(3)
        puesto_ind = col_i1.text_input("Puesto a evaluar", value="Operario de Aseo")
        actividad_ind = col_i2.text_input("Actividad", value="Limpieza")
        expuestos_ind = col_i3.number_input("Expuestos", min_value=1, value=60)

        if st.button("🚀 Procesar IPERC y Guardar en BD"):
            # Simulación de los peligros principales para el MVP
            datos_peligros = [
                {"TAREA": "Labores a la intemperie", "P": "Radiación solar y calor.", "R": "Estrés térmico.", "L": "Ley 30102", "S": 2, "M": "Bloqueador FPS 50+, pausas activas.", "CAP": "Prevención de estrés térmico.", "DOC": "Registro de entrega de EPP."},
                {"TAREA": "Manipulación de Cargas", "P": "Levantamiento manual.", "R": "Sobreesfuerzo biomecánico.", "L": "R.M. 375-2008-TR", "S": 2, "M": "Higiene postural.", "CAP": "Higiene postural.", "DOC": "Evaluación Ergonómica."},
                {"TAREA": "Dinámica laboral", "P": "Insinuaciones sexuales no deseadas.", "R": "Hostigamiento Sexual.", "L": "Ley N° 27942", "S": 3, "M": "Canales de denuncia.", "CAP": "Prevención del Hostigamiento Sexual.", "DOC": "Actas del Comité."}
            ]
            
            # Índices fijos para demostración
            idx_a, idx_b, idx_c, idx_d = 3, 2, 1, 3
            ip_inicial = idx_a + idx_b + idx_c + idx_d
            
            for d in datos_peligros:
                r_ini = ip_inicial * d["S"]
                n_ini = calcular_nivel(r_ini)
                
                # 1. Guardar en SQL: Tabla IPERC
                guardar_iperc_db(empresa, puesto_ind, d["TAREA"], d["P"], d["R"], n_ini, d["L"], d["M"])
                # 2. Guardar en SQL: Tabla Plan Anual
                guardar_plan_db(empresa, puesto_ind, "Capacitación", d["CAP"])
                guardar_plan_db(empresa, puesto_ind, "Documento/Registro", d["DOC"])

            st.success(f"✅ ¡IPERC de {puesto_ind} guardado permanentemente en la Base de Datos!")
    else:
        st.error("⛔ Acceso Denegado: Su rol de '{}' no tiene permisos para generar nuevas matrices. Diríjase a las pestañas de Plan Anual o Matriz Legal para auditar.".format(st.session_state.rol))

# --- MÓDULO 2 y 3: LECTURA DESDE LA BASE DE DATOS (Todos los roles) ---
with tab2:
    st.markdown("### 📚 Plan Anual Documentario y de Capacitaciones (Consultado desde SQL)")
    df_plan = cargar_tabla(f"SELECT puesto, tipo, tema FROM plan_anual WHERE empresa='{empresa}'")
    if not df_plan.empty:
        df_plan = df_plan.drop_duplicates().reset_index(drop=True)
        st.dataframe(df_plan, use_container_width=True)
    else:
        st.warning("La base de datos está vacía para esta entidad.")

with tab3:
    st.markdown("### ⚖️ Matriz de Trazabilidad Legal (Consultado desde SQL)")
    df_legal = cargar_tabla(f"SELECT norma, peligro, medidas, nivel FROM iperc WHERE empresa='{empresa}'")
    if not df_legal.empty:
        df_legal = df_legal.drop_duplicates(subset=['norma', 'peligro']).reset_index(drop=True)
        df_legal['ESTADO (Auditoría)'] = "En Proceso"
        st.dataframe(df_legal, use_container_width=True)
    else:
        st.warning("Aún no hay normativas registradas en la base de datos.")

# --- MÓDULO 4: DASHBOARD (Solo Lectura interactiva) ---
with tab4:
    st.markdown("### 📊 Panel de Control y Nivel de Cumplimiento")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("#### 📁 Documentos de Gestión Maestros")
        doc_1 = st.checkbox("Plan Anual de Seguridad y Salud en el Trabajo (PASST) Aprobado", disabled=not is_admin)
        doc_2 = st.checkbox("Plan Anual de Capacitaciones (PAC) Aprobado", disabled=not is_admin)
        doc_3 = st.checkbox("Política de Seguridad y Salud en el Trabajo (Firmada)", disabled=not is_admin)
    with col_d2:
        st.markdown("#### ⚙️ Auditoría de la Base de Datos")
        total_ipercs = cargar_tabla("SELECT COUNT(DISTINCT puesto) FROM iperc").iloc[0,0]
        st.metric(label="Puestos de Trabajo Evaluados y Guardados", value=total_ipercs)
        
        total_leyes = len(df_legal) if not df_legal.empty else 0
        st.metric(label="Normativas Legales en Trazabilidad", value=total_leyes)    
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
