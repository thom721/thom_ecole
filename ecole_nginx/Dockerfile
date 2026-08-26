FROM python:3.10-slim-bookworm

# Debian bookworm figée (pas "slim" seul, qui dérive vers la version Debian
# courante — ex. trixie début 2026, où libgdk-pixbuf2.0-0 ci-dessous n'existe
# plus sous ce nom et casse le build). bookworm est la version où ces noms de
# paquets sont valides.
#
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
# uvicorn[standard]==0.38.0 : mêmes extras que le "uvicorn" déjà épinglé dans
# requirements.txt (0.38.0), pour ne pas dériver de version en réinstallant.
RUN pip install --no-cache-dir "gunicorn" "uvicorn[standard]==0.38.0"

COPY app ./app

# Dossier de logs — monté sur l'hôte par docker-compose.web.yml (./logs),
# même pattern que /opt/post/fastapi déjà en prod sur ce serveur.
RUN mkdir -p /srv/ecole_nginx/logs

EXPOSE 9001

CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:9001", \
     "--timeout", "120", \
     "--access-logfile", "/srv/ecole_nginx/logs/access.log", \
     "--error-logfile", "/srv/ecole_nginx/logs/error.log"]
