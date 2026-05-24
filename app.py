import streamlit as st
import pandas as pd

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Recursos Ayuda Andalucía", page_icon="🧭", layout="centered")

# --- 2. ESTILOS VISUALES (BLINDADOS CONTRA MODO OSCURO ANDROID) ---
st.markdown("""
    <style>
    /* 1. Forzar fondo general claro siempre */
    .stApp {
        background-color: #f9f9f9 !important;
    }
    
    /* 2. Forzar que los textos nativos de Streamlit no se vuelvan blancos invisibles */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp p, .stApp label, .stApp span, .stApp small {
        color: #2C3E50 !important;
    }
    
    /* Evitar letras blancas en botones de radio y campos de texto */
    div[data-testid="stRadio"] label, input {
        color: #2C3E50 !important;
    }
    
    /* 3. Asegurar scroll vertical correcto en pantallas de móviles Android */
    .main .block-container {
        max-width: 100% !important;
        overflow-y: auto !important;
    }

    /* 4. PARCHE ESPECÍFICO PARA EL RECUADRO DE PROVINCIA (st.selectbox) */
    /* Fuerza a que el fondo de la caja del selector sea blanco y su borde gris */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #2C3E50 !important;
        border-color: #cccccc !important;
    }
    
    /* Fuerza a que TODO el texto interno del selector sea oscuro */
    div[data-testid="stSelectbox"] * {
        color: #2C3E50 !important;
    }
    
    /* Blindaje para la lista de opciones que se despliega al hacer clic */
    div[data-baseweb="menu"] *, div[role="listbox"] * {
        background-color: #ffffff !important;
        color: #2C3E50 !important;
    }

    /* 5. Estilos blindados para las Tarjetas de Recursos */
    .stApp .card {
        background-color: white !important; 
        padding: 20px; 
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        margin-bottom: 15px;
        border-left: 6px solid #F4D03F !important;
    }
    
    /* Asegurar que el texto base dentro de la tarjeta sea oscuro */
    .stApp .card, .stApp .card div, .stApp .card b {
        color: #2C3E50 !important;
    }
    
    .stApp .titulo {color: #2C3E50 !important; font-size: 1.2rem; font-weight: bold; margin-bottom: 5px;}
    .stApp .subtitulo {font-size: 0.9rem; color: #666 !important; margin-bottom: 10px; font-style: italic;}
    .stApp .dato {font-size: 0.95rem; margin-bottom: 5px; color: #444 !important;}
    .stApp .info-extra {font-size: 0.85rem; color: #555 !important; margin-top: 10px; padding-top: 10px; border-top: 1px dashed #eee;}
    .stApp .info-extra b {color: #2C3E50 !important;}
    
    /* Blindaje de etiquetas (Tags) para que mantengan su fondo y su texto BLANCO */
    .stApp .tag {
        font-size: 0.75rem; 
        color: #ffffff !important; 
        padding: 2px 8px; 
        border-radius: 4px; 
        display: inline-block; 
        margin-right: 5px; 
        margin-bottom: 5px;
        font-weight: bold !important;
    }
    .stApp .tag-nacional {background-color: #2c3e50 !important;} 
    .stApp .tag-andalucia {background-color: #007A33 !important;} 
    .stApp .tag-local {background-color: #27ae60 !important;} 
    .stApp .tag-online {background-color: #8e44ad !important;} 
    
    .stApp .card a {color: #3498db !important; text-decoration: none; font-weight: bold;}
    .stApp .card a:hover {text-decoration: underline;}

    /* Clases de aislamiento para bloques internos de la tarjeta */
    .stApp .contacto-box {
        background-color: #f0f2f6 !important; 
        padding: 10px; 
        border-radius: 8px;
        margin-top: 5px;
    }
    .stApp .contacto-box div, .stApp .contacto-box b, .stApp .contacto-box a, .stApp .contacto-box small, .stApp .contacto-box i {
        color: #2C3E50 !important;
    }
    
    .stApp .dirigido-box {
        margin-top: 10px; 
        font-size: 0.8rem; 
        color: #555 !important;
    }
    .stApp .dirigido-box b {
        color: #2C3E50 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. CARGAR DATOS ---
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv("recursos.csv", sep=";", encoding='utf-8')
    except:
        try:
            df = pd.read_csv("recursos.csv", sep=";", encoding='latin-1')
        except:
            st.error("⚠️ Error crítico: No puedo leer el archivo recursos.csv. Verifica que esté subido a GitHub.")
            st.stop()
    
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip().replace(['nan', 'None', '_', '-'], '')

    if 'Provincia' in df.columns:
        df['Provincia'] = df['Provincia'].apply(lambda x: x.split('/')[0].strip() if '/' in x else x)

    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al procesar los datos: {e}")
    st.stop()

# --- 4. INTERFAZ DE USUARIO ---
st.title("🧭 Recursos Ayuda Andalucía")
st.markdown("##### Encuentra ayuda especializada en prevención y duelo por suicidio.")

opciones_perfil = [
    "🆘 Tengo pensamientos suicidas / He intentado suicidarme",
    "👫 Busco ayuda para un menor o un joven",
    "👥 Población general",
    "🚑 Profesionales sanitarios y primeros intervinientes",
    "🎗️ He perdido a un ser querido por suicidio"
]

col1, col2 = st.columns(2)

with col1:
    perfil_usuario = st.radio("¿Cuál es tu situación?", opciones_perfil)

with col2:
    provincias_disponibles = sorted([
        p for p in df['Provincia'].unique() 
        if p not in ["Nacional", "Online", "Todas", ""]
    ])
    provincia_seleccionada = st.selectbox("Selecciona tu Provincia:", provincias_disponibles)

localidad = st.text_input("Escribe tu localidad (Opcional):", placeholder="Ej: Bailén, Motril...")

# --- 5. LÓGICA DE FILTRADO ---
criterio_geografico = (
    (df['Provincia'] == provincia_seleccionada) | 
    (df['Provincia'].str.lower() == 'nacional') | 
    (df['Provincia'].str.lower() == 'online') | 
    (df['Provincia'].str.lower() == 'todas')
)
df_filtrado = df[criterio_geografico].copy()

def buscar_keywords(texto_fila, keywords):
    texto_fila = texto_fila.lower()
    return any(k in texto_fila for k in keywords)

if "🆘" in perfil_usuario:
    keywords = ['sobreviviente', 'población general', 'conducta suicida', 'personas con conducta']
    filtro_perfil = df_filtrado['Dirigido a'].apply(lambda x: buscar_keywords(x, keywords))
elif "👫" in perfil_usuario:
    keywords = ['menor', 'jóvenes', 'joven', 'adolescen', 'estudiante', 'infantil', 'población general']
    filtro_perfil = df_filtrado['Dirigido a'].apply(lambda x: buscar_keywords(x, keywords))
elif "👥" in perfil_usuario:
    keywords = ['población general']
    filtro_perfil = df_filtrado['Dirigido a'].apply(lambda x: buscar_keywords(x, keywords))
elif "🚑" in perfil_usuario:
    keywords = ['profesional', 'sanitario', 'interviniente', 'población general']
    filtro_perfil = df_filtrado['Dirigido a'].apply(lambda x: buscar_keywords(x, keywords))
elif "🎗️" in perfil_usuario:
    keywords = ['superviviente', 'duelo', 'familia', 'allegad']
    filtro_perfil = df_filtrado['Dirigido a'].apply(lambda x: buscar_keywords(x, keywords))
else:
    filtro_perfil = [True] * len(df_filtrado)

df_filtrado = df_filtrado[filtro_perfil]

if localidad:
    criterio_localidad = (
        df_filtrado['Localidad / Ámbito'].str.contains(localidad, case=False, na=False) |
        (df_filtrado['Provincia'].str.lower() == 'nacional') |
        (df_filtrado['Provincia'].str.lower() == 'online') |
        (df_filtrado['Provincia'].str.lower() == 'todas')
    )
    df_filtrado = df_filtrado[criterio_localidad]

# --- 6. ORDENAR RESULTADOS ---
def calcular_orden(row):
    nombre = str(row['Nombre del recurso']).lower()
    prov_recurso = row['Provincia'].lower()
    ambito = str(row['Localidad / Ámbito']).lower()
    prov_usuario = provincia_seleccionada.lower()
    
    if "🆘" in perfil_usuario:
        if "061" in nombre or "112" in nombre or "024" in nombre:
            return -10 
        if "salud responde" in nombre:
            return -5
    if "👫" in perfil_usuario:
        if "anar" in nombre:
            return -10
    if localidad and localidad.lower() in ambito: 
        return 0
    if prov_recurso == prov_usuario:
        return 1
    if prov_recurso == 'todas':
        return 2
    if prov_recurso == 'nacional':
        return 3
    if prov_recurso == 'online':
        return 4
        
    return 5

df_filtrado['orden'] = df_filtrado.apply(calcular_orden, axis=1)
df_filtrado = df_filtrado.sort_values(by='orden')
df_final = df_filtrado.drop_duplicates(subset=['Nombre del recurso'])

# --- 7. MOSTRAR RESULTADOS ---
st.write(f"Mostrando **{len(df_final)}** recursos para: **{provincia_seleccionada}**")
st.markdown("---")

if df_final.empty:
    st.warning("No se encontraron recursos con estos filtros.")
else:
    for _, row in df_final.iterrows():
        nombre = row['Nombre del recurso']
        tipo = row['Tipo de recurso']
        desc = row['Descripción clara del recurso']
        prov = row['Provincia']
        ambito = row['Localidad / Ámbito']
        dirigido = row['Dirigido a']
        tel = row['Teléfono(s) de contacto']
        web = row['Web']
        email = row['Email']
        modalidad = row.get('Modalidad', '')
        horario = row.get('Horario de atención', '')
        atencion = row.get('Tipo de atención', '')
        coste = row.get('Coste', '')
        
        if prov.lower() == 'nacional':
            icono, lbl_class, lbl_text = "🇪🇸", "tag-nacional", "NACIONAL"
        elif prov.lower() == 'online':
            icono, lbl_class, lbl_text = "🌐", "tag-online", "ONLINE / REDES"
        elif prov.lower() == 'todas' or "andaluc" in ambito.lower():
            icono, lbl_class, lbl_text = "🟢", "tag-andalucia", "ANDALUCÍA"
        else:
            icono, lbl_class, lbl_text = "📍", "tag-local", f"{prov} - {ambito}"

        # --- BLOQUE DE CONTACTO ---
        html_contacto = ""
        if isinstance(tel, str) and len(tel) > 2:
            lista_tels = [t.strip() for t in tel.split(",")]
            enlaces = []
            for t in lista_tels:
                t_limpio = t.replace(" ", "")
                enlaces.append(f'<a href="tel:{t_limpio}">{t}</a>')
            html_contacto += f'<div class="dato">📞 <b>Tel:</b> {" / ".join(enlaces)}</div>'

        if isinstance(web, str) and len(web) > 4:
            url = web if web.startswith('http') else f'https://{web}'
            html_contacto += f'<div class="dato">🌐 <b>Web:</b> <a href="{url}" target="_blank">Visitar sitio</a></div>'
        
        if isinstance(email, str) and "@" in email:
            html_contacto += f'<div class="dato">📧 <b>Email:</b> <a href="mailto:{email}">{email}</a></div>'

        # --- BLOQUE DE INFORMACIÓN EXTRA ---
        html_extra = ""
        if isinstance(modalidad, str) and len(modalidad) > 1:
            html_extra += f'💻 <b>Modalidad:</b> {modalidad} <br>'
        if isinstance(horario, str) and len(horario) > 1:
            html_extra += f'🕒 <b>Horario:</b> {horario} <br>'
        if isinstance(atencion, str) and len(atencion) > 1:
            html_extra += f'🤝 <b>Atención:</b> {atencion} <br>'
        if isinstance(coste, str) and len(coste) > 1:
            html_extra += f'💶 <b>Coste:</b> {coste}'
            
        div_extra = f'<div class="info-extra">{html_extra}</div>' if html_extra else ""

        # Montaje de la tarjeta
        st.markdown(f"""
        <div class="card">
            <div class="titulo">{icono} {nombre}</div>
            <div class="subtitulo">{tipo}</div>
            <div><span class="tag {lbl_class}">{lbl_text}</span></div>
            <div style="margin-top: 10px; margin-bottom: 10px; color: #2C3E50 !important;">{desc}</div>
            <div class="contacto-box">
                {html_contacto if html_contacto else "<small><i>Consultar web para más detalles</i></small>"}
            </div>
            <div class="dirigido-box">
                <b>Dirigido a:</b> {dirigido}
            </div>
            {div_extra}
        </div>
        """, unsafe_allow_html=True)

# --- PIE DE PÁGINA (CON ACTUALIZACIÓN DE MAYO DE 2026) ---
st.divider()
c1, c2, c3 = st.columns([1, 8, 1])
with c2:
    st.markdown("<div style='text-align: center; color: #555;'>Creado por <b>Susana de Castro García</b></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #555; font-size: 0.9rem;'>Enfermera de emergencias prehospitalarias (Jaén) | Enero 2026 (Última actualización: Mayo 2026)</div>", unsafe_allow_html=True)
    st.write("")
    st.info("""
    **🛡️ REGISTRO DE PROPIEDAD INTELECTUAL (Safe Creative)** Código de inscripción: **2301254360025**
    **⚖️ LICENCIA DE USO** [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es)
    """)
    st.caption("Nota: Los derechos de propiedad intelectual de los recursos externos pertenecen a sus respectivos organismos.")
