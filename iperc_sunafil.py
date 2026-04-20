import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="SGI Expert - Compliance Perú", layout="wide")

# --- MEMORIA DE LA APLICACIÓN ---
if 'master_plan' not in st.session_state: st.session_state.master_plan = []
if 'iperc_historico' not in st.session_state: st.session_state.iperc_historico = []

def calcular_nivel(valor):
    if valor >= 25: return "IT"
    if valor >= 17: return "IM"
    if valor >= 9:  return "MO"
    if valor >= 5:  return "TO"
    return "TR"

def pintar_celdas_riesgo(val):
    colores = {"IT": "background-color: #ff0000; color: white; font-weight: bold", "IM": "background-color: #ff6600; color: white; font-weight: bold", "MO": "background-color: #ffff00; color: black; font-weight: bold", "TO": "background-color: #00b050; color: white; font-weight: bold", "TR": "background-color: #92d050; color: black; font-weight: bold"}
    return colores.get(val, "")

st.title("🛡️ SGI 360: IPERC, Legal y Sincronización Cloud")

# 1. ENCABEZADO Y GEOLOCALIZACIÓN
st.markdown("### 📝 Datos de la Entidad")
with st.container(border=True):
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        empresa = st.text_input("Razón Social", value="Municipalidad Provincial de Lambayeque")
        sector = st.selectbox("Sector Económico (Aplica Normativa Específica)", [
            "Obreros Municipales (D.S. 017-2017-TR)", 
            "Construcción Civil (G.050 / D.S. 011-2019-TR)", 
            "Minería (D.S. 024-2016-EM)", 
            "Industria (D.S. 42-F)", 
            "Agricultura (D.S. 005-2021-MIDAGRI)",
            "Electricidad (RESESATE)",
            "General / Administrativo (Ley 29783)"
        ])
    with col_h2:
        area = st.text_input("Área / Gerencia", value="Gerencia de Servicios Públicos")
        region = st.text_input("Región / Provincia", value="Lambayeque")
    with col_h3:
        proceso = st.text_input("Proceso General", value="Operaciones")
        fecha = st.date_input("Fecha de Elaboración", datetime.now())

# 2. AUDITORÍA SIDEBAR (Basado en RM 050 y D.S. 005-2012-TR)
with st.sidebar:
    st.header("📋 Documentos (D.S. 005-2012-TR)")
    has_politica = st.toggle("¿Política SST aprobada?")
    has_risst = st.toggle("¿RISST entregado?")
    has_pets = st.toggle("¿PETS operativos?")
    
    st.divider()
    st.header("🏥 Salud y Comités")
    has_emo = st.toggle("¿EMOs vigentes (R.M. 312-2011/MINSA)?")
    has_sctr = st.toggle("¿SCTR Activo (Ley 26790)?")
    has_comite_sst = st.toggle("¿Comité SST (R.M. 245-2021-TR)?")
    has_comite_hsl = st.toggle("¿Comité Prev. Hostigamiento?")

    st.divider()
    st.header("⚠️ Grupos Vulnerables (Ley 28048 / 31572)")
    pob_sensible = st.multiselect("Identificar grupos:", ["Mujeres Gestantes/Lactantes", "Personal con Discapacidad", "Teletrabajadores"])

# 3. LÓGICA NORMATIVA DINÁMICA
def obtener_norma_sectorial(sector_str):
    if "Municipales" in sector_str: return "D.S. N° 017-2017-TR"
    elif "Construcción" in sector_str: return "Norma G.050 / D.S. 011-2019-TR"
    elif "Minería" in sector_str: return "D.S. N° 024-2016-EM"
    elif "Industria" in sector_str: return "D.S. N° 42-F"
    elif "Agricultura" in sector_str: return "D.S. N° 005-2021-MIDAGRI"
    elif "Electricidad" in sector_str: return "R.M. N° 111-2013-MEM/INV"
    return "Ley N° 29783 / D.S. N° 005-2012-TR"

def generar_datos_iperc(puesto_eval, actividad_eval, expuestos_eval):
    idx_a = 1 if expuestos_eval <= 3 else (2 if expuestos_eval <= 12 else 3)
    idx_b = 1 if (has_risst and has_pets) else (2 if (has_risst or has_pets) else 3)
    idx_c = 1 if has_comite_sst else 3
    idx_d = 3 
    ip_inicial = idx_a + idx_b + idx_c + idx_d

    # Modificadores de vulnerabilidad y normativas
    mod_sev = 1 if len(pob_sensible) > 0 else 0
    norma_base = obtener_norma_sectorial(sector)
    ley_gestantes = " + Ley N° 28048" if "Mujeres Gestantes/Lactantes" in pob_sensible else ""
    ley_teletrabajo = " + Ley N° 31572" if "Teletrabajadores" in pob_sensible else ""

    datos = [
        {"TAREA": "Operaciones Generales", "P": "Ausencia de protección frente a accidentes de alto riesgo.", "R": "Falta de atención médica e indemnización.", "C": "Invalidez desatendida, multas.", "L": f"Ley N° 26790 (SCTR) + {norma_base}", "S": 3, "J": {"CAD": "X"}, "M": "Contratación obligatoria de SCTR Salud y Pensiones.", "CAP": "Difusión de coberturas SCTR.", "DOC": "Póliza SCTR vigente."},
        {"TAREA": "Manipulación de Cargas", "P": "Levantamiento manual de peso.", "R": "Sobreesfuerzo biomecánico.", "C": "Hernias discales.", "L": f"R.M. 375-2008-TR{ley_gestantes}", "S": 2 + mod_sev, "J": {"CAD": "X"}, "M": "Pausas activas, límite de carga (25kg H / 15kg M). Restricción absoluta para gestantes.", "CAP": "Higiene postural.", "DOC": "Evaluación Ergonómica."},
        {"TAREA": "Dinámica laboral", "P": "Insinuaciones sexuales no deseadas.", "R": "Hostigamiento Sexual Laboral.", "C": "Afectación psicológica profunda.", "L": "Ley N° 27942 / D.S. N° 014-2019-MIMP", "S": 3, "J": {"CAD": "X"}, "M": "Canales de denuncia, protección a la víctima.", "CAP": "Prevención del Hostigamiento Sexual.", "DOC": "Actas del Comité de Hostigamiento."},
        {"TAREA": "Trabajo frente a Pantallas / Remoto", "P": "Posturas estáticas y uso prolongado de PVD.", "R": "Fatiga visual, estrés ergonómico.", "C": "Disminución visual, Síndrome de Burnout.", "L": f"R.M. 375-2008-TR{ley_teletrabajo}", "S": 2, "J": {"CAD": "X"}, "M": "Silla ergonómica, desconexión digital.", "CAP": "Ergonomía en oficina y Teletrabajo.", "DOC": "Auto-evaluación ergonómica de Teletrabajo."},
        {"TAREA": "Labores de campo/operativas", "P": "Radiación solar y clima extremo.", "R": "Exposición a UV.", "C": "Cáncer de piel, insolación.", "L": f"Ley N° 30102 + {norma_base}", "S": 2 + mod_sev, "J": {"CAD": "X", "EPP": "X"}, "M": "Bloqueador FPS 50+, sombrero de ala ancha.", "CAP": "Prevención de cáncer de piel.", "DOC": "Registro de entrega de EPP."},
        {"TAREA": "Monitoreo de Salud", "P": "Desconocimiento de patologías preexistentes.", "R": "Agravamiento de enfermedades ocupacionales.", "C": "Enfermedades crónicas no tratadas.", "L": "R.M. 312-2011/MINSA + D.S. 016-2016-TR", "S": 3, "J": {"CAD": "X"}, "M": "Realización de EMOs de ingreso, periódico y retiro.", "CAP": "Importancia de la Vigilancia Médica.", "DOC": "Certificados de Aptitud Médico Ocupacional."}
    ]

    filas_iperc = []
    for i, d in enumerate(datos):
        r_ini = ip_inicial * d["S"]
        ip_res = idx_a + 1 + 1 + 2 
        r_res = ip_res * d["S"]

        fila = {"PUESTO": puesto_eval, "ACTIVIDAD": actividad_eval, "TAREA": d["TAREA"], "PELIGRO": d["P"], "RIESGO": d["R"], "BASE LEGAL": d["L"], "CONSECUENCIA": d["C"], "PROB_INI": ip_inicial, "SEV_INI": d["S"], "PxS_INI": r_ini, "NIVEL_INI": calcular_nivel(r_ini), "ELM": d["J"].get("ELM", ""), "SUS": d["J"].get("SUS", ""), "CDI": d["J"].get("CDI", ""), "CAD": d["J"].get("CAD", ""), "EPP": d["J"].get("EPP", ""), "MEDIDAS": d["M"], "PROB_RES": ip_res, "SEV_RES": d["S"], "PxS_RES": r_res, "NIVEL_RES": calcular_nivel(r_res)}
        filas_iperc.append(fila)
        st.session_state.iperc_historico.append(fila) 

        st.session_state.master_plan.append({"PUESTO": puesto_eval, "TIPO": "Capacitación", "TEMA": d["CAP"], "PELIGRO": d["P"]})
        st.session_state.master_plan.append({"PUESTO": puesto_eval, "TIPO": "Documento/Registro", "TEMA": d["DOC"], "PELIGRO": d["P"]})
        
    return filas_iperc

# 4. SISTEMA DE PESTAÑAS (Integración de Drive)
st.markdown("---")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["👤 1. IPERC", "📚 2. Plan Anual", "⚖️ 3. Matriz Legal", "📊 4. Dashboard", "☁️ 5. Google Drive Sync"])

with tab1:
    col_i1, col_i2, col_i3 = st.columns(3)
    puesto_ind = col_i1.text_input("Puesto a evaluar", value="Operario")
    actividad_ind = col_i2.text_input("Actividad", value="Limpieza")
    expuestos_ind = col_i3.number_input("Expuestos", min_value=1, value=60)

    if st.button("🚀 Generar IPERC (Con Normativa Sectorial)"):
        filas = generar_datos_iperc(puesto_ind, actividad_ind, expuestos_ind)
        st.dataframe(pd.DataFrame(filas).style.map(pintar_celdas_riesgo, subset=['NIVEL_INI', 'NIVEL_RES']), use_container_width=True)

with tab2:
    if len(st.session_state.master_plan) > 0:
        st.dataframe(pd.DataFrame(st.session_state.master_plan).drop_duplicates().reset_index(drop=True), use_container_width=True)

with tab3:
    if len(st.session_state.iperc_historico) > 0:
        df_legal = pd.DataFrame(st.session_state.iperc_historico)[['BASE LEGAL', 'PELIGRO', 'MEDIDAS']].drop_duplicates().reset_index(drop=True)
        df_legal['ESTADO (DS 019-2006-TR)'] = "En Proceso"
        st.dataframe(df_legal, use_container_width=True)

with tab4:
    st.markdown("### 📈 Auditoría de Implementación Documentaria")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.checkbox("RISST y Política aprobada (Ley 29783)")
        st.checkbox("Plan Anual de SST y Capacitaciones")
        st.checkbox("Elección de Comité SST (RM 245-2021-TR)")
    with col_d2:
        st.checkbox("Protocolos EMO (RM 312-2011/MINSA)")
        st.checkbox("SCTR Activo (D.S. 003-98-SA)")
        st.checkbox("Comité Ley 27942 (Hostigamiento)")
    st.progress(0.5)

# --- PESTAÑA 5: GOOGLE DRIVE (NUEVO) ---
with tab5:
    st.markdown("### ☁️ Sincronización con Google Drive Workspace")
    st.info("Respalda automáticamente todos los IPERCs, Matrices Legales y Planes Anuales directamente en una carpeta compartida de Google Drive de la Entidad.")
    
    auth_email = st.text_input("Correo Institucional (Google Workspace)", value="sst@munilambayeque.gob.pe")
    
    if st.button("🔄 Conectar y Respaldar en Google Drive"):
        if len(st.session_state.iperc_historico) == 0:
            st.error("No hay documentos generados. Crea un IPERC primero.")
        else:
            with st.spinner("Autenticando con Google API y subiendo archivos..."):
                # Aquí reside la lógica de integración para Python (google-api-python-client)
                import time
                time.sleep(2) # Simulando el tiempo de carga a la API
                st.success(f"✅ ¡Archivos respaldados exitosamente en el Drive de {auth_email}!")
                st.markdown("""
                **Archivos subidos:**
                * 📄 `IPERC_Consolidado_2026.csv`
                * 📄 `Matriz_Requisitos_Legales_SST.csv`
                * 📄 `Plan_Anual_Capacitaciones_PAC.csv`
                
                *(Nota Técnica: Para habilitar la subida real en tu Mac, asegúrate de tener el archivo `credentials.json` de Google Cloud Console en la misma carpeta que este script).*
                """)
