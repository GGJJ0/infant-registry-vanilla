# 1. Usamos una versión ligera de Python 3.11
FROM python:3.11-slim

# 2. Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiamos solo el archivo de requerimientos primero
# Esto ayuda a que Docker no reinstale todo si solo cambias una línea de CSS
COPY requirements.txt .

# 4. Instalamos Flask y las librerías necesarias
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiamos el resto de los archivos del proyecto (src, ui, etc.)
COPY . .

# 6. Informamos que la app corre en el puerto 8080
EXPOSE 8080

# 7. Comando para arrancar el servidor
CMD ["python", "src/main.py"]