import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Recursos Ayuda Andalucía", page_icon="🎗️", layout="centered")

# --- ESTILOS VISUALES ---
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
        font-size: 0.75rem; color: #fff; background-color: #7f8c8d; 
        padding: 2px 8px; border-radius: 4px; display: inline-block; margin-bottom: 5px;
    }
    .etiqueta-local {
        font-size: 0.75rem; color: #fff; background-color: #27ae60; 
        padding: 2px 8px; border-radius: 4px; display: inline-block; margin-bottom: 5px;
    }
    a {color: #3498db; text-decoration: none; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# --- CARGAR Y LIMPIAR DATOS ---
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
    
    # 1. Limpieza de espacios en nombres de columnas
    df.columns = df.columns.str.strip()
    
    # 2. Limpieza de columnas de texto (quita espacios al principio y final)
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()

    # 3. CORRECCIÓN DE PROVINCIAS (Esto arregla el desplegable)
    # Si pone "Granada / Andalucía", se queda solo con "Granada"
    if 'Provincia' in df.columns:
        df['Provincia'] = df['Provincia'].apply(lambda x: x.split('/')[0].strip() if '/' in x else x)

    return df

try:
    df = cargar_datos()
except:
    st.stop()

# --- INTERFAZ ---

st.title("🎗️ Recursos Andalucía")
st.markdown("##### Encuentra ayuda especializada en prevención y duelo por suicidio.")

# DEFINIR PERFILES (Lenguaje humano)
mapa_perfiles = {
    "🆘 Tengo pensamientos suicidas (Ayuda propia)": ["Sobreviviente", "Propia", "Prevención", "Conducta"],
    "🖤 He perdido a un ser querido (Duelo)": ["Superviviente", "Familiares", "Duelo", "Allegados"],
    "🧸 Busco ayuda para un menor o joven": ["Jóvenes", "Menores", "Estudiantes", "Adolescentes", "Infantil"],
    "🤝 Preocupado por alguien (Entorno)": ["Familiares", "Allegados", "Entorno", "Amistades"]
}

col1, col2 = st.columns(2)

with col1:
    opcion_usuario = st.radio("¿Cuál es tu situación?", list(mapa_perfiles.keys()))
    palabras_clave = mapa_perfiles[opcion_usuario]

with col2:
    # Selector de provincia (Ahora saldrá limpio sin duplicados)
    lista_provincias = sorted([p for p in df['Provincia'].unique() if p != "Nacional"])
    provincia = st.selectbox("Selecciona tu Provincia:", lista_provincias)

# Búsqueda por localidad
localidad = st.text_input("Escribe tu localidad (Opcional):", placeholder="Ej: Bailén, Motril...")

# --- MOTORES DE FILTRADO ---

# 1. Filtro por Perfil
if 'Dirigido a' in df.columns:
    df_filtro = df[df['Dirigido a'].fillna("").apply(lambda x: any(k.lower() in str(x).lower() for k in palabras_clave))]
else:
    df_filtro = df

# 2. Filtro Geográfico Básico (Provincia + Nacional)
df_final = df_filtro[(df_filtro['Provincia'] == provincia) | (df_filtro['Provincia'] == 'Nacional')]

# 3. FILTRO DE LOCALIDAD ESTRICTO (Tu corrección)
# Si el usuario escribe algo, SOLO mostramos lo que coincida (o lo Nacional)
# Eliminamos recursos de otros pueblos de la misma provincia.
if localidad:
    # Buscamos coincidencias (ignorando mayúsculas/minúsculas)
    coincide_localidad = df_final['Localidad / Ámbito'].str.contains(localidad, case=False, na=False)
    es_nacional = df_final['Provincia'] == 'Nacional'
    
    # Nos quedamos solo con: Coincidencias exactas O Nacionales
    df_final = df_final[coincide_localidad | es_nacional]

# --- LIMPIEZA FINAL ---
# Eliminar duplicados exactos de nombre
df_final = df_final.drop_duplicates(subset=['Nombre del recurso'], keep='first')

# Ordenar: Primero Locales (Prioridad 0) -> Luego Nacionales (Prioridad 1)
def calcular_orden(row):
    # Si es Nacional, al final
    if row['Provincia'] == 'Nacional':
        return 1
    # Si es de la provincia (o localidad buscada), primero
    return 0

df_final['orden'] = df_final.apply(calcular_orden, axis=1)
df_final = df_final.sort_values(by='orden')

# --- MOSTRAR RESULTADOS ---
st.markdown("---")

if df_final.empty:
    st.warning(f"No se han encontrado recursos en '{localidad}' para este perfil. Prueba a borrar la localidad para ver los recursos provinciales.")
else:
    for _, row in df_final.iterrows():
        
        # Iconos y etiquetas
        es_hospital = "Hospital" in str(row['Nombre del recurso'])
        icono = "🏥" if es_hospital else "❤️"
        
        es_nacional = row['Provincia'] == 'Nacional'
        if es_nacional:
            etiqueta = "<span class='etiqueta-nacional'>🌍 ÁMBITO NACIONAL</span>"
        else:
            etiqueta = f"<span class='etiqueta-local'>📍 {row['Localidad / Ámbito']}</span>"
        
        # Datos
        nombre = row['Nombre del recurso']
        tel = str(row['Teléfono(s) de contacto']).replace("nan", "No disponible")
        desc = str(row['Descripción clara del recurso'])
        modalidad = str(row.get('Modalidad', '')) # .get evita errores si falta la columna
        
        # Tarjeta HTML
        st.markdown(f"""
        <div class="card">
            <div class="titulo">{icono} {nombre}</div>
            <div>{etiqueta}</div>
            <div class="dato" style="margin-top:8px;">📞 <b>Teléfono:</b> <a href="tel:{tel}">{tel}</a></div>
            <div class="dato">ℹ️ {desc}</div>
            <div class="dato" style="font-size: 0.85rem; color: #666;"><i>{modalidad}</i></div>
        </div>
        """, unsafe_allow_html=True)

# Firma
st.markdown("<br><center><small>Recurso informativo de prevención y posvención del suicidio en Andalucía</small></center>", unsafe_allow_html=True)
