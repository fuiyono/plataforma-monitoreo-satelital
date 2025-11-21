# Guía de Despliegue - Plataforma de Monitoreo Satelital

## Opciones de Hosting

### 🆓 Opción 1: Streamlit Cloud (Recomendado - GRATIS)

**Ventajas:**
- ✅ Completamente gratuito
- ✅ Despliegue automático desde GitHub
- ✅ SSL/HTTPS incluido
- ✅ Actualizaciones automáticas
- ✅ Muy fácil de configurar

**Pasos:**

1. **Subir código a GitHub:**
```bash
cd /Users/carlosernestomillan/Projects/plataforma-monitoreo-satelital
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/plataforma-monitoreo-satelital.git
git push -u origin main
```

2. **Conectar con Streamlit Cloud:**
   - Ve a https://share.streamlit.io
   - Inicia sesión con GitHub
   - Click en "New app"
   - Selecciona tu repositorio
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Deploy"

3. **Configurar subdominio:**
   - En Streamlit Cloud, ve a Settings → Custom domain
   - Agrega: `satelital.geotecmatica.cloud`
   - Configura DNS en tu proveedor:
     ```
     Tipo: CNAME
     Nombre: satelital
     Valor: share.streamlit.io
     ```

**Límites:**
- CPU limitado (suficiente para esta app)
- Memoria: 1GB
- Sin base de datos persistente

---

### 💰 Opción 2: VPS (DigitalOcean, Linode, Vultr)

**Ventajas:**
- ✅ Control total
- ✅ Más recursos
- ✅ Puedes instalar bases de datos
- ✅ Costo: $5-12/mes

**Pasos:**

1. **Crear VPS:**
   - DigitalOcean: https://www.digitalocean.com
   - Selecciona: Ubuntu 22.04 LTS
   - Plan: $6/mes (1GB RAM) o $12/mes (2GB RAM)

2. **Configurar servidor:**
```bash
# Conectarse al servidor
ssh root@TU_IP_SERVIDOR

# Actualizar sistema
apt update && apt upgrade -y

# Instalar Python y dependencias
apt install -y python3 python3-pip python3-venv nginx

# Instalar Streamlit
pip3 install streamlit

# Crear usuario para la app
adduser streamlit
usermod -aG sudo streamlit
su - streamlit

# Clonar repositorio
git clone https://github.com/TU_USUARIO/plataforma-monitoreo-satelital.git
cd plataforma-monitoreo-satelital

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Crear servicio systemd:**
```bash
sudo nano /etc/systemd/system/streamlit.service
```

Contenido:
```ini
[Unit]
Description=Streamlit App
After=network.target

[Service]
Type=simple
User=streamlit
WorkingDirectory=/home/streamlit/plataforma-monitoreo-satelital
Environment="PATH=/home/streamlit/plataforma-monitoreo-satelital/venv/bin"
ExecStart=/home/streamlit/plataforma-monitoreo-satelital/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

4. **Iniciar servicio:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl start streamlit
```

5. **Configurar Nginx como reverse proxy:**
```bash
sudo nano /etc/nginx/sites-available/satelital
```

Contenido:
```nginx
server {
    listen 80;
    server_name satelital.geotecmatica.cloud;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

6. **Habilitar sitio y SSL:**
```bash
sudo ln -s /etc/nginx/sites-available/satelital /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Instalar Certbot para SSL
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d satelital.geotecmatica.cloud
```

---

### 🐳 Opción 3: Docker + Servidor

**Ventajas:**
- ✅ Fácil de desplegar
- ✅ Aislado del sistema
- ✅ Fácil de actualizar

**Crear Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Desplegar:**
```bash
docker build -t satelital-app .
docker run -d -p 8501:8501 --name satelital --restart always satelital-app
```

---

### ☁️ Opción 4: AWS/GCP/Azure

**AWS:**
- **EC2**: Similar a VPS ($5-20/mes)
- **Elastic Beanstalk**: Más fácil, auto-scaling
- **ECS/Fargate**: Contenedores Docker

**GCP:**
- **Compute Engine**: Similar a EC2
- **Cloud Run**: Serverless con contenedores (muy económico)
- **App Engine**: Plataforma gestionada

**Azure:**
- **App Service**: Fácil despliegue
- **Container Instances**: Contenedores simples

---

### 🚀 Opción 5: Railway / Render (Fácil)

**Railway:**
- ✅ Gratis para empezar
- ✅ Despliegue desde GitHub
- ✅ SSL automático
- ✅ Muy fácil

**Render:**
- ✅ Plan gratuito disponible
- ✅ Auto-deploy desde GitHub
- ✅ SSL incluido

**Pasos para desplegar en Render:**

1. **Preparar el repositorio:**
   - Asegúrate de que todos los archivos estén en GitHub
   - El archivo `render.yaml` ya está incluido en el proyecto

2. **Crear cuenta en Render:**
   - Ve a https://render.com
   - Regístrate o inicia sesión con GitHub

3. **Crear nuevo Web Service:**
   - En el dashboard, click en "New +" → "Web Service"
   - Conecta tu repositorio de GitHub: `fuiyono/plataforma-monitoreo-satelital`
   - O usa el archivo `render.yaml` para configuración automática:
     - Click en "New +" → "Blueprint"
     - Conecta el repositorio
     - Render detectará automáticamente el `render.yaml`

4. **Configuración manual (si no usas render.yaml):**
   - **Name:** `plataforma-monitoreo-satelital`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
   - **Plan:** Free (o el plan que prefieras)

5. **Variables de entorno (opcional):**
   - Si necesitas una API key de NASA FIRMS, agrega:
     - Key: `NASA_FIRMS_API_KEY`
     - Value: `tu_api_key` (si la tienes)

6. **Desplegar:**
   - Click en "Create Web Service"
   - Render comenzará a construir y desplegar tu aplicación
   - El proceso toma 5-10 minutos la primera vez

7. **Configurar dominio personalizado (opcional):**
   - En Settings → Custom Domain
   - Agrega: `satelital.geotecmatica.cloud`
   - Configura el DNS según las instrucciones de Render

**Notas importantes:**
- El plan gratuito puede "dormir" después de 15 minutos de inactividad
- La primera carga después de dormir puede tardar ~30 segundos
- Para evitar el sleep, considera el plan Starter ($7/mes)
- Render asigna automáticamente un puerto a través de `$PORT`

---

## Recomendación por Caso de Uso

### Para empezar rápido (GRATIS):
**Streamlit Cloud** - 5 minutos de setup

### Para producción profesional:
**VPS (DigitalOcean)** - $6-12/mes, control total

### Para escalar fácilmente:
**GCP Cloud Run** - Paga por uso, auto-scaling

### Para máxima simplicidad:
**Railway** - Despliegue en 1 click

---

## Configuración DNS

Para cualquier opción, necesitas configurar:

```
Tipo: A (para IP) o CNAME (para dominio)
Nombre: satelital
Valor: IP del servidor o dominio del hosting
TTL: 3600
```

---

## Monitoreo y Mantenimiento

### Logs:
```bash
# Streamlit Cloud: Ver en dashboard
# VPS: 
sudo journalctl -u streamlit -f
```

### Reiniciar servicio:
```bash
sudo systemctl restart streamlit
```

### Actualizar aplicación:
```bash
cd plataforma-monitoreo-satelital
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart streamlit
```

