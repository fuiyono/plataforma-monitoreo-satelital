"""
Utilidades para crear mapas interactivos con Folium
"""
import folium
from folium import plugins
import pandas as pd
from typing import Optional, List, Dict


def create_base_map(center_lat: float = 23.6345, center_lon: float = -102.5528, zoom: int = 5) -> folium.Map:
    """
    Crea un mapa base centrado en México
    
    Args:
        center_lat: Latitud central
        center_lon: Longitud central
        zoom: Nivel de zoom inicial
    
    Returns:
        Mapa de Folium
    """
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles='OpenStreetMap'
    )
    
    # Agregar múltiples capas de mapas
    folium.TileLayer('CartoDB positron', name='Claro').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='Oscuro').add_to(m)
    folium.TileLayer('Stamen Terrain', name='Terreno').add_to(m)
    
    # Agregar control de capas
    folium.LayerControl().add_to(m)
    
    return m


def add_fire_markers(
    map_obj: folium.Map,
    df: pd.DataFrame,
    confidence_filter: Optional[str] = None
) -> folium.Map:
    """
    Agrega marcadores de incendios al mapa
    
    Args:
        map_obj: Mapa de Folium
        df: DataFrame con datos de incendios
        confidence_filter: Filtrar por confianza ('high', 'nominal', 'low')
    
    Returns:
        Mapa con marcadores agregados
    """
    if df.empty:
        return map_obj
    
    # Filtrar por confianza si se especifica
    if confidence_filter and "confidence" in df.columns:
        df = df[df["confidence"] == confidence_filter]
    
    # Crear grupos de marcadores por confianza
    high_group = folium.FeatureGroup(name='Alta Confianza')
    nominal_group = folium.FeatureGroup(name='Confianza Normal')
    low_group = folium.FeatureGroup(name='Baja Confianza')
    
    for idx, row in df.iterrows():
        lat = row.get("lat") or row.get("latitude")
        lon = row.get("lon") or row.get("longitude")
        
        if pd.isna(lat) or pd.isna(lon):
            continue
        
        # Información del popup
        brightness = row.get("brightness", "N/A")
        date = row.get("date", "N/A")
        confidence = row.get("confidence", "nominal")
        satellite = row.get("satellite", "N/A")
        
        popup_html = f"""
        <div style="width: 200px;">
            <h4>🔥 Incendio Detectado</h4>
            <p><b>Fecha:</b> {date}</p>
            <p><b>Brillo:</b> {brightness} K</p>
            <p><b>Confianza:</b> {confidence}</p>
            <p><b>Satélite:</b> {satellite}</p>
        </div>
        """
        
        # Color según confianza
        if confidence == "high":
            color = "red"
            icon = "fire"
            group = high_group
        elif confidence == "low":
            color = "orange"
            icon = "info-sign"
            group = low_group
        else:
            color = "darkred"
            icon = "fire"
            group = nominal_group
        
        # Crear marcador
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(color=color, icon=icon, prefix='glyphicon'),
            tooltip=f"Incendio - {date}"
        ).add_to(group)
    
    # Agregar grupos al mapa
    high_group.add_to(map_obj)
    nominal_group.add_to(map_obj)
    low_group.add_to(map_obj)
    
    return map_obj


def add_heatmap(map_obj: folium.Map, df: pd.DataFrame) -> folium.Map:
    """
    Agrega un heatmap de incendios al mapa
    
    Args:
        map_obj: Mapa de Folium
        df: DataFrame con datos de incendios
    
    Returns:
        Mapa con heatmap agregado
    """
    if df.empty:
        return map_obj
    
    # Preparar datos para el heatmap
    heat_data = []
    for idx, row in df.iterrows():
        lat = row.get("lat") or row.get("latitude")
        lon = row.get("lon") or row.get("longitude")
        brightness = row.get("brightness", 300)
        
        if not pd.isna(lat) and not pd.isna(lon):
            heat_data.append([lat, lon, float(brightness)])
    
    if heat_data:
        plugins.HeatMap(
            heat_data,
            name='Heatmap de Incendios',
            min_opacity=0.2,
            max_zoom=18,
            radius=15,
            blur=15,
            gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'}
        ).add_to(map_obj)
    
    return map_obj


def create_fire_map(
    df: pd.DataFrame,
    center_lat: float = 23.6345,
    center_lon: float = -102.5528,
    zoom: int = 5,
    show_heatmap: bool = True,
    confidence_filter: Optional[str] = None
) -> folium.Map:
    """
    Crea un mapa completo con incendios
    
    Args:
        df: DataFrame con datos de incendios
        center_lat: Latitud central
        center_lon: Longitud central
        zoom: Nivel de zoom
        show_heatmap: Mostrar heatmap
        confidence_filter: Filtrar por confianza
    
    Returns:
        Mapa completo de Folium
    """
    # Crear mapa base
    m = create_base_map(center_lat, center_lon, zoom)
    
    # Agregar marcadores
    m = add_fire_markers(m, df, confidence_filter)
    
    # Agregar heatmap si se solicita
    if show_heatmap:
        m = add_heatmap(m, df)
    
    # Agregar fullscreen
    plugins.Fullscreen().add_to(m)
    
    return m

