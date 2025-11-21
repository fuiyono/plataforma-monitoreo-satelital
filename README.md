# Plataforma de Monitoreo Satelital
## Sistema de alerta temprana para incendios forestales

Dashboard interactivo para visualización y monitoreo de incendios forestales utilizando datos satelitales de NASA FIRMS.

**URL**: https://satelital.geotecmatica.cloud

## Características

- 🗺️ Visualización interactiva de incendios en tiempo casi real
- 📊 Análisis de tendencias temporales
- 🔍 Filtros por fecha, región y confianza
- 📈 Gráficos de estadísticas
- 🌍 Múltiples capas de mapas (Satélite, Calles, Terreno)

## Stack Tecnológico

- **Frontend**: Streamlit
- **Visualización**: Folium, Plotly
- **Datos**: NASA FIRMS API
- **Mapas**: OpenStreetMap, CartoDB

## Instalación

```bash
# Clonar el repositorio
git clone <tu-repo>
cd plataforma-monitoreo-satelital

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
streamlit run app.py
```

## Estructura del Proyecto

```
plataforma-monitoreo-satelital/
├── app.py                 # Aplicación principal Streamlit
├── utils/
│   ├── data_fetcher.py    # Conexión con NASA FIRMS API
│   ├── map_utils.py       # Utilidades para mapas
│   └── visualizations.py  # Gráficos y visualizaciones
├── requirements.txt
├── README.md
└── .gitignore
```

## Uso

1. La aplicación se conecta automáticamente a la API de NASA FIRMS
2. Selecciona la región y fecha de interés
3. Visualiza los incendios detectados en el mapa interactivo
4. Explora las estadísticas y tendencias

## Despliegue

### Opción 1: Streamlit Cloud (Recomendado)
1. Sube el código a GitHub
2. Conecta con Streamlit Cloud
3. Configura el subdominio en tu DNS

### Opción 2: Servidor Propio
```bash
# Con Docker
docker build -t satelital-app .
docker run -p 8501:8501 satelital-app

# O directamente
streamlit run app.py --server.port 8501
```

## Licencia

MIT

# plataforma-monitoreo-satelital
