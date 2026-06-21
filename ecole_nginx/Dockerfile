FROM python:3.10-slim

# Dépendances système requises par WeasyPrint (génération de PDF) sur Linux.
# Sur Windows, ces mêmes libs sont fournies via le dossier gtk_runtime/ embarqué
# (voir setup_weasyprint_dlls() dans app/main.py) — rien n'est changé côté Windows.
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-cffi \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libffi-dev \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/ecole_nginx

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 9001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9001"]
