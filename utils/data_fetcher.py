"""
Módulo para obtener datos de incendios desde NASA FIRMS API
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict


class FIRMSDataFetcher:
    """Clase para obtener datos de la API de NASA FIRMS"""
    
    # URL base de la API de NASA FIRMS
    BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/country/csv"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el fetcher de datos
        
        Args:
            api_key: API key de NASA FIRMS (opcional para datos públicos)
        """
        self.api_key = api_key
    
    def get_fires_by_country(
        self, 
        country: str = "MEX",
        days: int = 7,
        satellite: str = "VIIRS_SNPP"
    ) -> pd.DataFrame:
        """
        Obtiene datos de incendios por país
        
        Args:
            country: Código de país (MEX, USA, etc.)
            days: Número de días hacia atrás
            satellite: Satélite a usar (VIIRS_SNPP, MODIS, etc.)
        
        Returns:
            DataFrame con los datos de incendios
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "country": country,
            "satellite": satellite,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            # Leer CSV desde la respuesta
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            
            if df.empty:
                return pd.DataFrame()
            
            # Renombrar columnas para consistencia
            column_mapping = {
                "latitude": "lat",
                "longitude": "lon",
                "brightness": "brightness",
                "acq_date": "date",
                "acq_time": "time",
                "confidence": "confidence"
            }
            
            # Renombrar solo las columnas que existen
            df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener datos: {e}")
            return pd.DataFrame()
    
    def get_fires_by_region(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        days: int = 7,
        satellite: str = "VIIRS_SNPP"
    ) -> pd.DataFrame:
        """
        Obtiene datos de incendios por región geográfica
        
        Args:
            min_lat, max_lat: Rango de latitud
            min_lon, max_lon: Rango de longitud
            days: Número de días hacia atrás
            satellite: Satélite a usar
        
        Returns:
            DataFrame con los datos de incendios
        """
        # Para regiones, primero obtenemos por país y luego filtramos
        # O podemos usar la API de área si está disponible
        df = self.get_fires_by_country("MEX", days, satellite)
        
        if df.empty:
            return df
        
        # Filtrar por región
        if "lat" in df.columns and "lon" in df.columns:
            mask = (
                (df["lat"] >= min_lat) & (df["lat"] <= max_lat) &
                (df["lon"] >= min_lon) & (df["lon"] <= max_lon)
            )
            return df[mask]
        
        return df


def get_sample_data() -> pd.DataFrame:
    """
    Retorna datos de ejemplo para desarrollo/testing
    """
    import numpy as np
    
    # Generar datos de ejemplo para México
    n_points = 50
    dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
    
    data = {
        "lat": np.random.uniform(14.5, 32.5, n_points),  # Latitud de México
        "lon": np.random.uniform(-118.0, -86.0, n_points),  # Longitud de México
        "brightness": np.random.uniform(300, 500, n_points),
        "confidence": np.random.choice(["nominal", "high", "low"], n_points),
        "date": np.random.choice(dates, n_points),
        "satellite": "VIIRS_SNPP"
    }
    
    return pd.DataFrame(data)

