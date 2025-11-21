"""
Utilidades para crear gráficos y visualizaciones
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional


def plot_fires_timeline(df: pd.DataFrame) -> go.Figure:
    """
    Crea un gráfico de línea temporal de incendios
    
    Args:
        df: DataFrame con datos de incendios
    
    Returns:
        Figura de Plotly
    """
    if df.empty or "date" not in df.columns:
        return go.Figure()
    
    # Agrupar por fecha
    daily_counts = df.groupby("date").size().reset_index(name="count")
    daily_counts["date"] = pd.to_datetime(daily_counts["date"])
    daily_counts = daily_counts.sort_values("date")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_counts["date"],
        y=daily_counts["count"],
        mode='lines+markers',
        name='Incendios Detectados',
        line=dict(color='red', width=2),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Tendencia de Incendios en el Tiempo",
        xaxis_title="Fecha",
        yaxis_title="Número de Incendios",
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


def plot_confidence_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Crea un gráfico de distribución por confianza
    
    Args:
        df: DataFrame con datos de incendios
    
    Returns:
        Figura de Plotly
    """
    if df.empty or "confidence" not in df.columns:
        return go.Figure()
    
    confidence_counts = df["confidence"].value_counts().reset_index()
    confidence_counts.columns = ["confidence", "count"]
    
    # Mapear colores
    color_map = {
        "high": "red",
        "nominal": "orange",
        "low": "yellow"
    }
    
    colors = [color_map.get(c, "gray") for c in confidence_counts["confidence"]]
    
    fig = go.Figure(data=[
        go.Bar(
            x=confidence_counts["confidence"],
            y=confidence_counts["count"],
            marker_color=colors,
            text=confidence_counts["count"],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Distribución por Nivel de Confianza",
        xaxis_title="Confianza",
        yaxis_title="Número de Incendios",
        template='plotly_white'
    )
    
    return fig


def plot_brightness_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Crea un histograma de distribución de brillo
    
    Args:
        df: DataFrame con datos de incendios
    
    Returns:
        Figura de Plotly
    """
    if df.empty or "brightness" not in df.columns:
        return go.Figure()
    
    fig = go.Figure(data=[
        go.Histogram(
            x=df["brightness"],
            nbinsx=30,
            marker_color='red',
            opacity=0.7
        )
    ])
    
    fig.update_layout(
        title="Distribución de Brillo (Temperatura)",
        xaxis_title="Brillo (Kelvin)",
        yaxis_title="Frecuencia",
        template='plotly_white'
    )
    
    return fig


def create_summary_stats(df: pd.DataFrame) -> dict:
    """
    Crea un diccionario con estadísticas resumidas
    
    Args:
        df: DataFrame con datos de incendios
    
    Returns:
        Diccionario con estadísticas
    """
    if df.empty:
        return {
            "total_fires": 0,
            "avg_brightness": 0,
            "high_confidence": 0,
            "date_range": "N/A"
        }
    
    stats = {
        "total_fires": len(df),
        "avg_brightness": df["brightness"].mean() if "brightness" in df.columns else 0,
        "high_confidence": len(df[df["confidence"] == "high"]) if "confidence" in df.columns else 0,
    }
    
    if "date" in df.columns:
        dates = pd.to_datetime(df["date"], errors='coerce')
        if not dates.isna().all():
            stats["date_range"] = f"{dates.min()} a {dates.max()}"
        else:
            stats["date_range"] = "N/A"
    else:
        stats["date_range"] = "N/A"
    
    return stats

