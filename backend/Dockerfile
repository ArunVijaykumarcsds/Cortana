FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENV=production \
    PYTHONPATH=/app/backend
WORKDIR /app
COPY backend/ /app/backend/
COPY backend/entrypoint.sh /app/entrypoint.sh
COPY models/ /app/models/
COPY fusion/ /app/fusion/
COPY rules/ /app/rules/
COPY evaluation/ /app/evaluation/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
RUN useradd --create-home --uid 10001 cortana && chmod +x /app/entrypoint.sh && chown -R cortana:cortana /app
USER cortana
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/api/v1/health', timeout=3)"
ENTRYPOINT ["/app/entrypoint.sh"]
