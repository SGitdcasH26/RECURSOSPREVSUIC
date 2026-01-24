import streamlit as st
import pandas as pd

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Recursos Ayuda Andalucía", page_icon="🤝", layout="centered")

# --- 2. ESTILOS VISUALES ---
st.markdown("""
    <style>
    .stApp {background-color: #f9f9f9;}
    .card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px;
        border-left: 6px solid #F4D03F;
    }
    .titulo {color: #2C3E50; font-size: 1.2rem; font-weight: bold; margin-bottom: 5px;}
    .subtitulo {font-size: 0.9rem; color: #666; margin-bottom: 10px; font-style: italic;}
    .dato {font-size: 0.95rem; margin-bottom: 5px; color: #444;}
    
    /* Etiquetas visuales */
    .tag {
        font-size: 0.75rem; color: #fff; padding: 2px 8px; border-radius: 4px; 
        display: inline-block; margin-right: 5px; margin-bottom: 5px;
    }
    .tag-nacional {background-color: #2c3e50;} /* Gris oscuro */
    .tag-andalucia {background-color: #007A33;} /* Verde Andalucía */
    .tag-local {background-color: #27ae60;} /* Verde claro */
    .tag-online {background-color: #8e44ad;} /* Morado */
    
    a {color: #3498db; text-decoration: none; font-weight: bold;}
    a:hover {text-decoration: underline;}
    </style>
""", unsafe_allow_html=True)

# --- 3. CARGAR DATOS ---
@st.cache_data
def cargar_datos():
    try:
        # Intentamos leer con separador de punto y coma
        df = pd.read_csv("recursos.csv", sep=";", encoding='utf-8')
    except:
        try:
            df = pd.read_csv("recursos.csv", sep=";", encoding='latin-1')
        except:
            st.error("⚠️ Error crítico: No puedo leer el archivo recursos.csv. Verifica que esté subido.")
            st.stop()
    
    # Limpieza de nombres de columnas
    df.columns = df.columns.str.strip()
    
    # Limpieza de datos (quitar espacios extra y convertir nan a string vacío)
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip().replace('nan', '')

    # Normalizar Provincia (Si pone "Granada / Andalucía", dejar solo "Granada")
    if 'Provincia' in df.columns:
        df['Provincia'] = df['Provincia'].apply(lambda x: x.split('/')[0].strip() if '/' in x else x)

    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al procesar los datos: {e}")
    st.stop()

# --- 4. INTERFAZ DE USUARIO ---

st.title("🤝 Recursos Ayuda Andalucía")
st.markdown("##### Encuentra ayuda especializada en prevención y duelo por suicidio.")

# DEFINIR PERFILES DE USUARIO
opciones_perfil = [
    "🫴 Tengo pensamientos suicidas/He intentado suicidarme",
    "🎗️ He perdido a un ser querido por suicidio",
    "🧸 Busco ayuda para un menor o un joven",
    "🏘️ Estoy preocupado por alguien conocido"
]

col1, col2 = st.columns(2)

with col1:
    perfil_usuario = st.radio("¿Cuál es tu situación?", opciones_perfil)

with col2:
    # Obtenemos lista de provincias reales (excluyendo 'Nacional', 'Online', 'Todas' para el selector)
    provincias_disponibles = sorted([
        p for p in df['Provincia'].unique() 
        if p not in ["Nacional", "Online", "Todas", ""]
    ])
    provincia_seleccionada = st.selectbox("Selecciona tu Provincia:", provincias_disponibles)

# Búsqueda localidad
localidad = st.text_input("Escribe tu localidad (Opcional):", placeholder="Ej: Bailén, Motril...")

# --- 5. LÓGICA DE FILTRADO ---

# PASO 1: FILTRO GEOGRÁFICO (El más importante)
# Incluimos: La provincia elegida + Nacional + Online + Todas (recursos autonómicos genéricos)
criterio_geografico = (
    (df['Provincia'] == provincia_seleccionada) | 
    (df['Provincia'].str.lower() == 'nacional') | 
    (df['Provincia'].str.lower() == 'online') | 
    (df['Provincia'].str.lower() == 'todas')
)
df_filtrado = df[criterio_geografico].copy()

# PASO 2: FILTRO POR PERFIL (Lógica mejorada)
if "preocupado" in perfil_usuario.lower():
    # Muestra recursos para familiares/allegados O población general
    keywords = ['familia', 'allegad', 'entorno', 'amistad', 'compañer', 'población general']
    filtro_perfil = df_filtrado['Dirigido a'].str.lower().apply(lambda x: any(k in x for k in keywords))
    df_filtrado = df_filtrado[filtro_perfil]

elif "menor" in perfil_usuario.lower() or "joven" in perfil_usuario.lower():
    # Muestra recursos específicos de juventud/educación O población general
    keywords = ['jóvenes', 'joven', 'adolescen', 'estudiante', 'educativa', 'menor', 'infantil']
    filtro_perfil = df_filtrado['Dirigido a'].str.lower().apply(lambda x: any(k in x for k in keywords))
    df_filtrado = df_filtrado[filtro_perfil]

elif "perdido" in perfil_usuario.lower():
    # Duelo
    keywords = ['superviviente', 'duelo', 'familia', 'allegad']
    filtro_perfil = df_filtrado['Dirigido a'].str.lower().apply(lambda x: any(k in x for k in keywords))
    df_filtrado = df_filtrado[filtro_perfil]

else:
    # Pensamientos suicidas (Sobrevivientes)
    keywords = ['sobreviviente', 'propia', 'prevención', 'conducta', 'riesgo', 'población general']
    filtro_perfil = df_filtrado['Dirigido a'].str.lower().apply(lambda x: any(k in x for k in keywords))
    df_filtrado = df_filtrado[filtro_perfil]

# PASO 3: FILTRO LOCALIDAD (Opcional)
if localidad:
    # Si escribe localidad, filtramos por nombre de localidad PERO mantenemos los Nacionales/Online
    criterio_localidad = (
        df_filtrado['Localidad / Ámbito'].str.contains(localidad, case=False, na=False) |
        (df_filtrado['Provincia'].str.lower() == 'nacional') |
        (df_filtrado['Provincia'].str.lower() == 'online') |
        (df_filtrado['Provincia'].str.lower() == 'todas')
    )
    df_filtrado = df_filtrado[criterio_localidad]

# --- 6. ORDENAR RESULTADOS ---
# Prioridad: 1. Coincidencia exacta localidad (si hay) -> 2. Provincia seleccionada -> 3. Nacional/Online
def calcular_orden(row):
    p = row['Provincia'].lower()
    l = str(row['Localidad / Ámbito']).lower()
    
    # Si coincide la localidad escrita por el usuario, sale primero (0)
    if localidad and localidad.lower() in l:
        return 0
    # Si es de la provincia seleccionada (y no es 'Todas'), sale segundo (1)
    if p == provincia_seleccionada.lower():
        return 1
    # El resto (Nacional, Online, Todas) sale después (2)
    return 2

df_filtrado['orden'] = df_filtrado.apply(calcular_orden, axis=1)
df_filtrado = df_filtrado.sort_values(by='orden')
df_final = df_filtrado.drop_duplicates(subset=['Nombre del recurso']) # Evitar duplicados visuales

# --- 7. MOSTRAR RESULTADOS ---
st.write(f"Mostrando **{len(df_final)}** recursos para: **{provincia_seleccionada}** (más Nacionales y Online)")
st.markdown("---")

if df_final.empty:
    st.warning("No se encontraron recursos con estos filtros. Prueba a borrar la localidad o cambiar el perfil.")
else:
    for _, row in df_final.iterrows():
        
        # Preparar variables para HTML
        nombre = row['Nombre del recurso']
        tipo = row['Tipo de recurso']
        desc = row['Descripción clara del recurso']
        prov = row['Provincia']
        ambito = row['Localidad / Ámbito']
        
        # Iconos y Etiquetas
        if prov.lower() == 'nacional':
            icono = "🇪🇸"
            lbl_class = "tag-nacional"
            lbl_text = "NACIONAL"
        elif prov.lower() == 'online':
            icono = "🌐"
            lbl_class = "tag-online"
            lbl_text = "ONLINE / REDES"
        elif prov.lower() == 'todas' or "andaluc" in ambito.lower():
            icono = "🟢"
            lbl_class = "tag-andalucia"
            lbl_text = "ANDALUCÍA"
        else:
            icono = "📍"
            lbl_class = "tag-local"
            lbl_text = f"{prov} - {ambito}"

        # Contacto (Teléfono, Web, Email) - Solo si tienen datos
        html_contacto = ""
        
        # Teléfono
        tel = row['Teléfono(s) de contacto']
        if tel and len(tel) > 2:
            html_contacto += f'<div class="dato">📞 <b>Tel:</b> <a href="tel:{tel}">{tel}</a></div>'
        
        # Web
        web = row['Web']
        if web and len(web) > 4:
            # Asegurar que tenga http/https
            link_web = web if web.startswith('http') else f'https://{web}'
            html_contacto += f'<div class="dato">🌐 <b>Web:</b> <a href="{link_web}" target="_blank">Visitar sitio</a></div>'
            
        # Email
        email = row['Email']
        if email and "@" in email:
            html_contacto += f'<div class="dato">📧 <b>Email:</b> <a href="mailto:{email}">{email}</a></div>'

        # Renderizar Tarjeta
        st.markdown(f"""
        <div class="card">
            <div class="titulo">{icono} {nombre}</div>
            <div class="subtitulo">{tipo}</div>
            <div><span class="tag {lbl_class}">{lbl_text}</span></div>
            <div style="margin-top: 10px; margin-bottom: 10px;">{desc}</div>
            <div style="background-color: #f0f2f6; padding: 10px; border-radius: 8px;">
                {html_contacto if html_contacto else "<small><i>Consultar web para más detalles de contacto</i></small>"}
            </div>
            <div style="margin-top:5px; font-size:0.8rem; color:#888;">
                Dirigido a: {row['Dirigido a']}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><center><small>Recurso informativo de prevención y posvención del suicidio en Andalucía</small></center>", unsafe_allow_html=True)
