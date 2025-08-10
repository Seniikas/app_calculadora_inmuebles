# estimadora_propiedades.py
import streamlit as st
import pandas as pd
import pickle
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Estimadora de Propiedades",
    page_icon="🏠",
    layout="wide"
)

# Título principal con logo
col_logo, col_titulo = st.columns([1, 3])

with col_logo:
    st.image("LOGO-COLOR2.png", width=200)

with col_titulo:
    st.title("🏠 Estimadora de Valor de Propiedades")

st.markdown("---")

# Cargar el modelo entrenado
@st.cache_resource
def cargar_modelo():
    try:
        with open('random_forest_model3.pkl', 'rb') as f:
            modelo = pickle.load(f)
        return modelo
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo del modelo. Asegúrate de que 'modelo_comprimido2.pkl' esté en la carpeta")
        return None

# Cargar diccionario de barrios
@st.cache_resource
def cargar_barrios():
    try:
        with open('barrios_por_zona.pkl', 'rb') as f:
            barrios_por_zona = pickle.load(f)
        return barrios_por_zona
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo de barrios. Ejecuta primero 'generar_diccionario_barrios.py'")
        return {}

# Cargar opciones de tipos de propiedad (ARCHIVO LIGERO)
@st.cache_resource
def cargar_tipos_propiedad():
    try:
        # Opción 1: JSON (más ligero)
        import json
        with open('tipos_propiedad.json', 'r', encoding='utf-8') as f:
            tipos_propiedad = json.load(f)
        return tipos_propiedad
        
        # Opción 2: CSV simple
        # df_tipos = pd.read_csv("tipos_propiedad.csv")
        # return sorted(df_tipos['property_type'].unique())
        
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo de tipos de propiedad. Ejecuta 'generar_tipos_propiedad.py'")
        return []

# Cargar datos
modelo = cargar_modelo()
barrios_por_zona = cargar_barrios()
tipos_propiedad = cargar_tipos_propiedad()

if modelo is None or not barrios_por_zona or not tipos_propiedad:
    st.stop()

# Crear la interfaz
st.header("📋 Ingresa los datos de la propiedad")

# Crear dos columnas para organizar mejor la interfaz
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Ubicación")
    
    # Selector de zona
    zona = st.selectbox(
        "Zona:",
        options=sorted(barrios_por_zona.keys()),
        help="Selecciona la zona de la propiedad"
    )
    
    # Selector de barrio (dependiente de la zona)
    if zona in barrios_por_zona:
        barrio = st.selectbox(
            "Barrio:",
            options=barrios_por_zona[zona],
            help="Selecciona el barrio de la propiedad"
        )
    else:
        barrio = st.selectbox("Barrio:", options=[])
    
    # Tipo de propiedad
    tipo_propiedad = st.selectbox(
        "Tipo de Propiedad:",
        options=tipos_propiedad,
        help="Selecciona el tipo de propiedad"
    )

with col2:
    st.subheader("🏗️ Características")
    
    # Superficie total
    superficie_total = st.number_input(
        "Superficie Total (m²):",
        min_value=1.0,
        max_value=10000.0,
        value=100.0,
        step=1.0,
        help="Superficie total del terreno"
    )
    
    # Superficie cubierta (CORREGIDO - sin validación automática)
    superficie_cubierta = st.number_input(
        "Superficie Cubierta (m²):",
        min_value=1.0,
        max_value=10000.0,
        value=80.0,
        step=1.0,
        help="Superficie cubierta construida"
    )
    
    # Validación manual
    if superficie_cubierta > superficie_total:
        st.warning("⚠️ La superficie cubierta no puede ser mayor que la superficie total.")
    
    # Ambientes
    ambientes = st.number_input(
        "Ambientes:",
        min_value=1,
        max_value=20,
        value=3,
        step=1,
        help="Número total de ambientes"
    )
    
    # Habitaciones
    habitaciones = st.number_input(
        "Habitaciones:",
        min_value=0,
        max_value=ambientes,
        value=2,
        step=1,
        help="Número de habitaciones"
    )
    
    # Baños
    banos = st.number_input(
        "Baños:",
        min_value=1,
        max_value=10,
        value=1,
        step=1,
        help="Número de baños"
    )

# Botón de predicción
st.markdown("---")
col_prediccion = st.columns([1, 2, 1])
with col_prediccion[1]:
    if st.button("🔍 Calcular Precio", type="primary", use_container_width=True):
        try:
            # Crear DataFrame con los datos ingresados
            datos_propiedad = pd.DataFrame({
                'surface_total': [superficie_total],
                'surface_covered': [superficie_cubierta],
                'rooms': [ambientes],
                'bedrooms': [habitaciones],
                'bathrooms': [banos],
                'l2': [zona],
                'l3': [barrio],
                'property_type': [tipo_propiedad]
            })
            
            # Hacer predicción
            precio_predicho = modelo.predict(datos_propiedad)[0]
            
            # Mostrar resultado
            st.markdown("---")
            st.success("✅ Predicción completada")
            
            # Crear métricas visuales
            col_metric1, col_metric2, col_metric3 = st.columns(3)
            
            with col_metric1:
                st.metric(
                    label="💰 Precio Estimado",
                    value=f"${precio_predicho:,.0f}",
                    delta=None
                )
            
            with col_metric2:
                precio_m2 = precio_predicho / superficie_cubierta
                st.metric(
                    label="📐 Precio por m²",
                    value=f"${precio_m2:,.0f}",
                    delta=None
                )
            
            with col_metric3:
                if superficie_total != superficie_cubierta:
                    precio_m2_total = precio_predicho / superficie_total
                    st.metric(
                        label="📐 Precio por m² (total)",
                        value=f"${precio_m2_total:,.0f}",
                        delta=None
                    )
            
            # Información adicional
            st.info(f"""
            **Información de la propiedad:**
            - Zona: {zona}
            - Barrio: {barrio}
            - Tipo: {tipo_propiedad}
            - Superficie total: {superficie_total} m²
            - Superficie cubierta: {superficie_cubierta} m²
            - Ambientes: {ambientes}
            - Habitaciones: {habitaciones}
            - Baños: {banos}
            """)
            
        except Exception as e:
            st.error(f"❌ Error al realizar la predicción: {str(e)}")

# Información adicional
st.markdown("---")
with st.expander("ℹ️ Información sobre el modelo"):
    st.write("""
    **Sobre el modelo:**
    - Algoritmo: Random Forest Regressor
    - Features utilizadas: Superficie, ambientes, ubicación y tipo de propiedad
    - Dataset: Propiedades de Buenos Aires (sin outliers)
    - Métrica de evaluación: RMSE y MAE
    
    **Nota:** Esta es una estimación basada en datos históricos. 
    El precio real puede variar según condiciones específicas del mercado.
    """)

# Footer
st.markdown("---")

st.markdown("*Desarrollado con Streamlit y Machine Learning*") 


