# Usamos una imagen ligera de Python
FROM python:3.11-slim

# Establecemos el directorio de trabajo principal
WORKDIR /app

# Copiamos los requisitos primero para optimizar el build
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# COPIAMOS TODO EL CONTENIDO (src, ui, data) al contenedor
# Esto garantiza que /app/ui y /app/src existan internamente
COPY . .

# Exponemos el puerto que configuramos en Flask
EXPOSE 8080

# Ejecutamos el servidor indicando la ruta exacta
CMD ["python", "src/main.py"]