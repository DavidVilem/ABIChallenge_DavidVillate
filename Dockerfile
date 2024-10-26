# Usar una imagen base de Python
FROM python:3.8-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos necesarios para la aplicación
COPY . /app

# Instalar las dependencias en requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto que la aplicación usa (e.g., 8000 para FastAPI)
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]