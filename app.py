import streamlit as st
import pandas as pd

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Recursos Ayuda Andalucía", page_icon="🧭", layout="centered")

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
        df = pd.read_csv("recursos.csv", sep=";", encoding='utf-8')
    except:
        try:
            df = pd.read_csv("recursos.csv", sep=";", encoding='latin-1')
        except:
            st.error("⚠️ Error crítico: No puedo leer el archivo recursos.csv. Verifica que esté subido.")
            st.stop()
    
    # Limpieza básica
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip().replace('nan', '')

    # Normalizar Provincia
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

# --- DEFINICIÓN DE PERFILES ---
opciones_perfil = [
    "🆘 Tengo pensamientos suicidas / He intentado suicidarme",
    "👫 Busco ayuda para un menor o un joven",
    "👥 Población general",
    "🧑‍⚕️ Profesionales sanitarios y primeros intervinientes",
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

# Búsqueda localidad
localidad = st.text_input("Escribe tu localidad (Opcional):", placeholder="Ej: Bailén, Motril...")

# --- 5. LÓGICA DE FILTRADO ---

# PASO 1: FILTRO GEOGRÁFICO
criterio_geografico = (
    (df['Provincia'] == provincia_seleccionada) | 
    (df['Provincia'].str.lower() == 'nacional') | 
    (df['Provincia'].str.lower() == 'online') | 
    (df['Provincia'].str.lower() == 'todas')
)
df_filtrado = df[criterio_geografico].copy()

# PASO 2: FILTRO POR PERFIL
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

elif "🧑‍⚕️" in perfil_usuario:
    keywords = ['profesional', 'sanitario', 'interviniente', 'población general']
    filtro_perfil = df_filtrado['Dirigido a'].apply(lambda x: buscar_keywords(x, keywords))

elif "🎗️" in perfil_usuario:
    keywords = ['superviviente', 'duelo', 'familia', 'allegad']
    filtro_perfil = df_filtrado['Dirigido a'].apply(lambda x: buscar_keywords(x, keywords))

else:
    filtro_perfil = [True] * len(df_filtrado)

df_filtrado = df_filtrado[filtro_perfil]

# PASO 3: FILTRO LOCALIDAD
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
    
    # A. LÓGICA ESPECIAL PARA GRUPO SOS
    if "🆘" in perfil_usuario:
        if "061" in nombre or "112" in nombre or "024" in nombre:
            return -10 
        if "salud responde" in nombre:
            return -5

    # B. LÓGICA DE ORDEN GEOGRÁFICO
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
        
        # Iconos
        if prov.lower() == 'nacional':
            icono, lbl_class, lbl_text = "🇪🇸", "tag-nacional", "NACIONAL"
        elif prov.lower() == 'online':
            icono, lbl_class, lbl_text = "🌐", "tag-online", "ONLINE / REDES"
        elif prov.lower() == 'todas' or "andaluc" in ambito.lower():
            icono, lbl_class, lbl_text = "🟢", "tag-andalucia", "ANDALUCÍA"
        else:
            icono, lbl_class, lbl_text = "📍", "tag-local", f"{prov} - {ambito}"

        # Contacto HTML
        html_contacto = ""
        if tel and len(tel) > 2:
            html_contacto += f'<div class="dato">📞 <b>Tel:</b> <a href="tel:{tel}">{tel}</a></div>'
        if web and len(web) > 4:
            link_web = web if web.startswith('http') else f'https://{web}'
            html_contacto += f'<div class="dato">🌐 <b>Web:</b> <a href="{link_web}" target="_blank">Visitar sitio</a></div>'
        if email and "@" in email:
            html_contacto += f'<div class="dato">📧 <b>Email:</b> <a href="mailto:{email}">{email}</a></div>'

        st.markdown(f"""
        <div class="card">
            <div class="titulo">{icono} {nombre}</div>
            <div class="subtitulo">{tipo}</div>
            <div><span class="tag {lbl_class}">{lbl_text}</span></div>
            <div style="margin-top: 10px; margin-bottom: 10px;">{desc}</div>
            <div style="background-color: #f0f2f6; padding: 10px; border-radius: 8px;">
                {html_contacto if html_contacto else "<small><i>Consultar web para más detalles</i></small>"}
            </div>
            <div style="margin-top:5px; font-size:0.8rem; color:#888;">
                <b>Dirigido a:</b> {dirigido}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
#      PIE DE PÁGINA (VERSIÓN NATIVA)
# ==========================================
st.divider() # Línea separadora visual

# Usamos columnas para centrar un poco el contenido
col_izq, col_centro, col_der = st.columns([1, 8, 1])

with col_centro:
    # 1. Título y Autoría
    st.markdown(
        "<h4 style='text-align: center; color: #555;'>Recursos de prevención y posvención del suicidio</h4>", 
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='text-align: center;'>Creado por <b>Susana de Castro García</b><br>Enfermera de emergencias (Jaén) | Enero 2026</div>", 
        unsafe_allow_html=True
    )
    st.write("") # Espacio en blanco

    # 2. Caja de Licencias (Usamos st.info que crea un recuadro azul/gris automático)
    with st.info("🛡️ **Información de Propiedad Intelectual y Licencia**"):
        st.markdown("**Registro Safe Creative:**")
        st.code("2301254360025", language="text") # Muestra el número destacado
        
        st.markdown("---") # Pequeña separación
        
        st.markdown("⚖️ **Licencia de uso:**")
        st.markdown("[**CC BY-NC-SA 4.0**](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es) (Creative Commons)")
        st.caption("✅ Se permite compartir citando autoría. | 🚫 Prohibido uso comercial.")

    # 3. Descargo de responsabilidad final
    st.caption(
        "Nota: Los derechos de propiedad intelectual de los recursos externos enlazados "
        "pertenecen a sus respectivos organismos. Esta herramienta es un directorio facilitador."
    )
