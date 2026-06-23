FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9004

# 9004 : port attendu par le Nginx hôte en prod (proxy_pass
# http://127.0.0.1:9004/), voir infini-software/deploy/nginx-infini-software.cloud.conf
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9004"]
