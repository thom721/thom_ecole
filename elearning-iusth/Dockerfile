FROM python:3.10-slim-bookworm

WORKDIR /srv/elearning-iusth

RUN apt-get update && apt-get install -y --no-install-recommends default-libmysqlclient-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt ./app/requirements.txt
RUN pip install --no-cache-dir -r app/requirements.txt

COPY app ./app
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
