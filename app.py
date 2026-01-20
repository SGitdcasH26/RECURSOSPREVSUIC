import streamlit as st
import pandas as pd

# CONFIGURACIÓN
st.set_page_config(page_title="Recursos Ayuda Andalucía", page_icon="🎗️", layout="centered")

# ESTILOS
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
    a {color: #3498db; text-decoration: none;}
    </style>
""", unsafe_allow_html=True)

# CARGAR DATOS (Corrección para leer punto y coma ;)
@st.cache_data
def cargar_datos():
    try:
        # Probamos con separador ; y codificación utf-8
        return pd.read_csv("recursos.csv", sep=";", encoding='utf-8')
    except:
        # Si falla, probamos con latin-1
        return pd.read_csv("recursos.csv", sep=";", encoding='latin-1')

try:
    df = cargar_datos()
except:
    st.error("⚠️ Error leyendo el archivo. Asegúrate de que se llama recursos.csv")
    st.stop()

# INTERFAZ
st.title("🎗️ Recursos Andalucía")
st.markdown("Herramienta de orientación para prevención y posvención del suicidio.")

col1, col2 = st.columns(2)
with col1:
    perfil = st.radio("¿Tu situación?", ("Soy Superviviente (Duelo)", "Soy Sobreviviente (Prevención)"))
with col2:
    # Selector de provincia
    if 'Provincia' in df.columns:
        provincias = sorted([p for p in df['Provincia'].unique() if p != "Nacional"])
        provincia = st.selectbox("Tu Provincia:", provincias)
    else:
        st.error("No leo la columna 'Provincia'. Revisa el CSV.")
        st.stop()

# Búsqueda opcional
localidad = st.text_input("Tu localidad (Opcional):", placeholder="Ej: Dos Hermanas")

# FILTRADO
palabras_clave = ["Superviviente", "Familiares", "Allegados"] if "Superviviente" in perfil else ["Sobreviviente", "Prevención", "Propia"]

# Filtro 1: Perfil
if 'Dirigido a' in df.columns:
    df_filtro = df[df['Dirigido a'].fillna("").apply(lambda x: any(k.lower() in str(x).lower() for k in palabras_clave))]
else:
    df_filtro = df

# Filtro 2: Provincia + Nacional
df_final = df_filtro[(df_filtro['Provincia'] == provincia) | (df_filtro['Provincia'] == 'Nacional')]

# Ordenar (Localidad > Provincia > Nacional)
if locality_match := df_final['Localidad / Ámbito'].str.contains(localidad, case=False, na=False) if localidad else None:
    df_final = pd.concat([df_final[locality_match], df_final[~locality_match]])
else:
    df_final = df_final.sort_values(by='Provincia', key=lambda x: x == 'Nacional')

# MOSTRAR
st.markdown("---")
if df_final.empty:
    st.warning("No hay resultados exactos. Llama al 024 o 112.")
else:
    for _, row in df_final.iterrows():
        icono = "🏥" if "Hospital" in str(row['Nombre del recurso']) else "🤝"
        tel = str(row['Teléfono(s) de contacto'])
        st.markdown(f"""
        <div class="card">
            <div class="titulo">{icono} {row['Nombre del recurso']}</div>
            <div class="dato">📍 {row['Localidad / Ámbito']} | 📞 <a href="tel:{tel}">{tel}</a></div>
            <div class="dato">{row['Descripción clara del recurso']}</div>
            <div class="dato"><i>{row['Modalidad']} • {row['Coste']}</i></div>
        </div>
        """, unsafe_allow_html=True)
