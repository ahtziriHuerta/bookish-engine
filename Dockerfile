FROM python:3.11

# Instala dependencias del sistema necesarias para WeasyPrint
RUN apt-get update && apt-get install -y \
    build-essential \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copia todo el código del proyecto
COPY . .

# Instala dependencias Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Archivos estáticos de Django
RUN python manage.py collectstatic --noinput

# Puerto y arranque
EXPOSE 8000
CMD ["gunicorn", "proyecto.wsgi:application", "--bind", "0.0.0.0:8000"]
