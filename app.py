import streamlit as st
import pandas as pd

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
# Cambio de logo: Ahora es una mano tendida (🤝)
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
    .titulo {color: #2C3E50; font-size: 1.2rem; font-weight: bold;}
    .dato {font-size: 0.95rem; margin-bottom: 5px; color: #444;}
    
    /* Etiquetas visuales para ámbito */
    .etiqueta-nacional {
        font-size: 0.75rem; color: #fff; background-color: #2c3e50; /* Negro/Gris oscuro */
        padding: 2px 8px; border-radius: 4px; display: inline-block; margin-bottom: 5px;
    }
    .etiqueta-andalucia {
        font-size: 0.75rem; color: #fff; background-color: #007A33; /* Verde Andalucía */
        padding: 2px 8px; border-radius: 4px; display: inline-block; margin-bottom: 5px;
    }
    .etiqueta-local {
        font-size: 0.75rem; color: #fff; background-color: #27ae60; /* Verde claro */
        padding: 2px 8px; border-radius: 4px; display: inline-block; margin-bottom: 5px;
    }
    
    a {color: #3498db; text-decoration: none; font-weight: bold;}
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
            st.error("⚠️ Error crítico: No puedo leer el archivo recursos.csv.")
            st.stop()
    
    # Limpieza de datos
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()

    # Corrección Provincias (Granada / Andalucía -> Granada)
    if 'Provincia' in df.columns:
        df['Provincia'] = df['Provincia'].apply(lambda x: x.split('/')[0].strip() if '/' in x else x)

    return df

try:
    df = cargar_datos()
except:
    st.stop()

# --- 4. INTERFAZ DE USUARIO ---

st.title("🤝 Recursos Ayuda Andalucía")
st.markdown("##### Encuentra ayuda especializada en prevención y duelo por suicidio.")

# DEFINIR PERFILES (Nuevos textos e iconos solicitados)
mapa_perfiles = {
    "🤝 Tengo pensamientos suicidas/He intentado suicidarme": ["Sobreviviente", "Propia", "Prevención", "Conducta"],
    "🎗️ He perdido a un ser querido por suicidio": ["Superviviente", "Familiares", "Duelo", "Allegados"],
    "🧸 Busco ayuda para un menor o un joven": ["Jóvenes", "Menores", "Estudiantes", "Adolescentes", "Infantil"],
    "🏘️ Estoy preocupado por alguien conocido en relación al suicidio": ["Familiares", "Allegados", "Entorno", "Amistades"]
}

col1, col2 = st.columns(2)

with col1:
    opcion_usuario = st.radio("¿Cuál es tu situación?", list(mapa_perfiles.keys()))
    palabras_clave = mapa_perfiles[opcion_usuario]

with col2:
    lista_provincias = sorted([p for p in df['Provincia'].unique() if p != "Nacional"])
    provincia = st.selectbox("Selecciona tu Provincia:", lista_provincias)

# Búsqueda localidad
localidad = st.text_input("Escribe tu localidad (Opcional):", placeholder="Ej: Bailén, Motril...")

# --- 5. FILTRADO ---

# Filtro Perfil
if 'Dirigido a' in df.columns:
    df_filtro = df[df['Dirigido a'].fillna("").apply(lambda x: any(k.lower() in str(x).lower() for k in palabras_clave))]
else:
    df_filtro = df

# Filtro Geográfico
df_final = df_filtro[(df_filtro['Provincia'] == provincia) | (df_filtro['Provincia'] == 'Nacional')]

# Filtro Localidad Estricto
if localidad:
    coincide_localidad = df_final['Localidad / Ámbito'].str.contains(localidad, case=False, na=False)
    es_nacional = df_final['Provincia'] == 'Nacional'
    df_final = df_final[coincide_localidad | es_nacional]

# --- 6. LIMPIEZA Y ORDEN ---
df_final = df_final.drop_duplicates(subset=['Nombre del recurso'], keep='first')

def calcular_orden(row):
    if row['Provincia'] == 'Nacional': return 2
    if localidad and localidad.lower() in str(row['Localidad / Ámbito']).lower(): return 0
    return 1

df_final['orden'] = df_final.apply(calcular_orden, axis=1)
df_final = df_final.sort_values(by='orden')

# --- 7. MOSTRAR RESULTADOS (Con nuevos iconos geográficos) ---
st.markdown("---")

if df_final.empty:
    st.warning(f"No se han encontrado recursos específicos en '{localidad}'. Prueba a borrar la localidad.")
else:
    for _, row in df_final.iterrows():
        
        # --- LÓGICA DE ICONOS GEOGRÁFICOS ---
        es_nacional = row['Provincia'] == 'Nacional'
        es_hospital = "Hospital" in str(row['Nombre del recurso'])
        
        # Detectamos si es ámbito Andalucía (A veces viene en Localidad)
        ambito_andalucia = "Andalucía" in str(row['Localidad / Ámbito']) or "Autonómico" in str(row['Localidad / Ámbito'])

        if es_nacional:
            icono_mapa = "🇪🇸"  # Mapa/Bandera España
            etiqueta_texto = "ÁMBITO NACIONAL"
            clase_css = "etiqueta-nacional"
        elif ambito_andalucia:
            icono_mapa = "🟢"  # Círculo Verde (Simula mapa Andalucía)
            etiqueta_texto = "ÁMBITO ANDALUCÍA"
            clase_css = "etiqueta-andalucia"
        else:
            icono_mapa = "📍"  # Chincheta verde (Simula mapa local relleno)
            etiqueta_texto = f"{row['Localidad / Ámbito']}"
            clase_css = "etiqueta-local"
        
        # Si es hospital, añadimos la cruz al nombre para no perder esa info
        nombre_mostrar = f"🏥 {row['Nombre del recurso']}" if es_hospital else row['Nombre del recurso']

        # Datos
        tel = str(row['Teléfono(s) de contacto']).replace("nan", "No disponible")
        desc = str(row['Descripción clara del recurso'])
        
        # Tarjeta HTML
        st.markdown(f"""
        <div class="card">
            <div class="titulo">{icono_mapa} {nombre_mostrar}</div>
            <div style="margin: 5px 0;"><span class="{clase_css}">{etiqueta_texto}</span></div>
            <div class="dato">📞 <b>Teléfono:</b> <a href="tel:{tel}">{tel}</a></div>
            <div class="dato">ℹ️ {desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><center><small>Recurso informativo de prevención y posvención del suicidio en Andalucía</small></center>", unsafe_allow_html=True)
