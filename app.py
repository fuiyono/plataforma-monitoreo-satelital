"""
Plataforma de Monitoreo Satelital
Dashboard interactivo para visualización de incendios forestales
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium

# Importar utilidades
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_fetcher import FIRMSDataFetcher, get_sample_data
from utils.map_utils import create_fire_map
from utils.visualizations import (
    plot_fires_timeline,
    plot_confidence_distribution,
    plot_brightness_distribution,
    create_summary_stats
)

# Configuración de la página
st.set_page_config(
    page_title="Plataforma de Monitoreo Satelital",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🔥 Plataforma de Monitoreo Satelital")
st.markdown("### Sistema de alerta temprana para incendios forestales")
st.markdown("---")

# Sidebar para controles
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Selector de modo
    mode = st.radio(
        "Modo de datos",
        ["Datos en vivo (NASA FIRMS)", "Datos de ejemplo"],
        help="Los datos en vivo requieren conexión a internet"
    )
    
    # Selector de país/región
    country = st.selectbox(
        "País/Región",
        ["MEX", "USA", "CAN", "BRA", "ARG"],
        index=0
    )
    
    # Selector de días
    days = st.slider(
        "Días hacia atrás",
        min_value=1,
        max_value=30,
        value=7,
        help="Número de días de datos históricos a mostrar"
    )
    
    # Filtro de confianza
    confidence_filter = st.selectbox(
        "Filtrar por confianza",
        ["Todos", "Alta", "Normal", "Baja"],
        index=0
    )
    
    # Opciones de visualización
    st.header("📊 Visualización")
    show_heatmap = st.checkbox("Mostrar Heatmap", value=True)
    show_markers = st.checkbox("Mostrar Marcadores", value=True)
    
    st.markdown("---")
    st.markdown("### ℹ️ Información")
    st.info(
        "Esta plataforma utiliza datos de NASA FIRMS para detectar "
        "incendios activos mediante satélites. Los datos se actualizan "
        "varias veces al día."
    )

# Mapeo de confianza
confidence_map = {
    "Todos": None,
    "Alta": "high",
    "Normal": "nominal",
    "Baja": "low"
}

# Cargar datos
@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_fire_data(mode: str, country: str, days: int):
    """Carga datos de incendios"""
    if mode == "Datos en vivo (NASA FIRMS)":
        fetcher = FIRMSDataFetcher()
        df = fetcher.get_fires_by_country(country, days)
        
        if df.empty:
            st.warning("No se pudieron cargar datos en vivo. Mostrando datos de ejemplo.")
            return get_sample_data()
        
        return df
    else:
        return get_sample_data()

# Cargar datos
with st.spinner("Cargando datos de incendios..."):
    df = load_fire_data(mode, country, days)

# Mostrar estadísticas
if not df.empty:
    stats = create_summary_stats(df)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Incendios", stats["total_fires"])
    
    with col2:
        st.metric(
            "Brillo Promedio",
            f"{stats['avg_brightness']:.1f} K" if stats['avg_brightness'] > 0 else "N/A"
        )
    
    with col3:
        st.metric("Alta Confianza", stats["high_confidence"])
    
    with col4:
        st.metric("Rango de Fechas", stats["date_range"][:10] if stats["date_range"] != "N/A" else "N/A")
    
    st.markdown("---")
    
    # Mapa y gráficos en columnas
    col_map, col_charts = st.columns([2, 1])
    
    with col_map:
        st.subheader("🗺️ Mapa de Incendios")
        
        # Calcular centro del mapa basado en los datos
        if not df.empty and "lat" in df.columns and "lon" in df.columns:
            center_lat = df["lat"].mean()
            center_lon = df["lon"].mean()
        else:
            center_lat, center_lon = 23.6345, -102.5528  # Centro de México
        
        # Crear mapa
        fire_map = create_fire_map(
            df,
            center_lat=center_lat,
            center_lon=center_lon,
            zoom=5,
            show_heatmap=show_heatmap,
            confidence_filter=confidence_map[confidence_filter]
        )
        
        # Mostrar mapa
        map_data = st_folium(fire_map, width=700, height=500)
    
    with col_charts:
        st.subheader("📈 Estadísticas")
        
        # Gráfico de confianza
        fig_confidence = plot_confidence_distribution(df)
        st.plotly_chart(fig_confidence, use_container_width=True)
    
    st.markdown("---")
    
    # Gráficos adicionales
    col_timeline, col_brightness = st.columns(2)
    
    with col_timeline:
        st.subheader("📅 Tendencia Temporal")
        fig_timeline = plot_fires_timeline(df)
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    with col_brightness:
        st.subheader("🌡️ Distribución de Brillo")
        fig_brightness = plot_brightness_distribution(df)
        st.plotly_chart(fig_brightness, use_container_width=True)
    
    # Tabla de datos
    with st.expander("📋 Ver Datos Detallados"):
        st.dataframe(df, use_container_width=True)
        
        # Botón de descarga
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"incendios_{country}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

else:
    st.error("No se encontraron datos de incendios para los parámetros seleccionados.")
    st.info("Intenta cambiar el país, el rango de fechas o usar datos de ejemplo.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>Datos proporcionados por <a href='https://firms.modaps.eosdis.nasa.gov/' target='_blank'>NASA FIRMS</a></p>
        <p>Desarrollado con ❤️ usando Streamlit y Folium</p>
    </div>
    """,
    unsafe_allow_html=True
)

