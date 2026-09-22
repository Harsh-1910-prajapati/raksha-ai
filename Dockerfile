# Build from the repo root so the data catalogue is included:
#   gcloud builds submit --tag gcr.io/YOUR_PROJECT/raksha-ai-backend .
#   docker build -t raksha-ai-backend .
FROM python:3.13-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV RAKSHA_DATA_DIR=/app/data
ENV PORT=8080

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend/app /app/app
COPY data /app/data

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8080') + '/health')" || exit 1

CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"
