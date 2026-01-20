import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Recursos Ayuda Andalucía", page_icon="🎗️", layout="centered")

# --- ESTILOS VISUALES (Bonito y limpio) ---
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
    .etiqueta-nacional {
        font-size: 0.8rem; color: #fff; background-color: #95a5a6; 
        padding: 2px 8px; border-radius: 4px; display: inline-block;
    }
    .etiqueta-local {
        font-size: 0.8rem; color: #fff; background-color: #27ae60; 
        padding: 2px 8px; border-radius: 4px; display: inline-block;
    }
    a {color: #3498db; text-decoration: none; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# --- CARGAR DATOS ---
@st.cache_data
def cargar_datos():
    try:
        # Intentamos leer con punto y coma (Excel español)
        df = pd.read_csv("recursos.csv", sep=";", encoding='utf-8')
    except:
        try:
            df = pd.read_csv("recursos.csv", sep=";", encoding='latin-1')
        except:
            st.error("⚠️ Error crítico: No puedo leer el archivo. Verifica que sea CSV delimitado por punto y coma.")
            st.stop()
    
    # Limpieza de espacios invisibles
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()
            
    return df

try:
    df = cargar_datos()
except:
    st.stop()

# --- INTERFAZ DE USUARIO ---

st.title("🎗️ Recursos Andalucía")
st.markdown("##### Encuentra ayuda especializada en prevención y duelo por suicidio.")

# 1. DEFINIR PERFILES (Aquí está la magia de las palabras sencillas)
# La clave es lo que ve el usuario, la lista son las palabras que busca en tu Excel
mapa_perfiles = {
    "🆘 Tengo pensamientos suicidas (Ayuda propia)": ["Sobreviviente", "Propia", "Prevención", "Conducta"],
    "🖤 He perdido a un ser querido (Duelo)": ["Superviviente", "Familiares", "Duelo", "Allegados"],
    "🧸 Busco ayuda para un menor o joven": ["Jóvenes", "Menores", "Estudiantes", "Adolescentes", "Infantil"],
    "🤝 Preocupado por alguien (Entorno)": ["Familiares", "Allegados", "Entorno", "Amistades"]
}

col1, col2 = st.columns(2)

with col1:
    # Selector con frases humanas
    opcion_usuario = st.radio("¿Cuál es tu situación?", list(mapa_perfiles.keys()))
    palabras_clave = mapa_perfiles[opcion_usuario]

with col2:
    # Selector de provincia inteligente
    lista_provincias = sorted([p for p in df['Provincia'].unique() if p != "Nacional"])
    provincia = st.selectbox("Selecciona tu Provincia:", lista_provincias)

# Búsqueda por localidad
localidad = st.text_input("Escribe tu localidad (Opcional):", placeholder="Ej: Motril, Utrera, Linares...")

# --- MOTORES DE FILTRADO ---

# 1. Filtro por Perfil (Busca las palabras clave en la columna 'Dirigido a')
if 'Dirigido a' in df.columns:
    # Esta función busca si ALGUNA de las palabras clave está en la descripción del recurso
    df_filtro = df[df['Dirigido a'].fillna("").apply(lambda x: any(k.lower() in str(x).lower() for k in palabras_clave))]
else:
    df_filtro = df

# 2. Filtro Geográfico (Provincia elegida + Nacionales)
df_final = df_filtro[(df_filtro['Provincia'] == provincia) | (df_filtro['Provincia'] == 'Nacional')]

# --- LIMPIEZA Y ORDEN ---

# 1. Eliminar duplicados exactos de nombre
df_final = df_final.drop_duplicates(subset=['Nombre del recurso'], keep='first')

# 2. Orden Inteligente (Localidad > Provincia > Nacional)
def calcular_prioridad(row):
    # Si coincide la localidad escrita -> Prioridad 0 (Máxima)
    if localidad and localidad.lower() in str(row['Localidad / Ámbito']).lower():
        return 0
    # Si es recurso provincial -> Prioridad 1
    if row['Provincia'] == provincia:
        return 1
    # Si es Nacional -> Prioridad 2 (Última)
    return 2

df_final['ranking'] = df_final.apply(calcular_prioridad, axis=1)
df_final = df_final.sort_values(by='ranking')

# --- MOSTRAR RESULTADOS ---
st.markdown("---")

if df_final.empty:
    st.warning(f"No hemos encontrado recursos específicos para este perfil en {provincia}. Por favor, consulta los recursos nacionales o llama al 024.")
else:
    count = 0
    for _, row in df_final.iterrows():
        count += 1
        
        # Iconos y etiquetas
        es_hospital = "Hospital" in str(row['Nombre del recurso'])
        icono = "🏥" if es_hospital else "❤️"
        
        es_nacional = row['Provincia'] == 'Nacional'
        etiqueta = f"<span class='etiqueta-nacional'>🌍 ÁMBITO NACIONAL</span>" if es_nacional else f"<span class='etiqueta-local'>📍 {row['Localidad / Ámbito']}</span>"
        
        # Datos
        nombre = row['Nombre del recurso']
        tel = str(row['Teléfono(s) de contacto']).replace("nan", "No disponible")
        desc = str(row['Descripción clara del recurso'])
        
        # Tarjeta HTML
        st.markdown(f"""
        <div class="card">
            <div class="titulo">{icono} {nombre}</div>
            <div style="margin: 8px 0;">{etiqueta}</div>
            <div class="dato">📞 <b>Teléfono:</b> <a href="tel:{tel}">{tel}</a></div>
            <div class="dato">ℹ️ {desc}</div>
        </div>
        """, unsafe_allow_html=True)
