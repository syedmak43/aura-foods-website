FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

RUN python manage.py migrate --run-syncdb && python manage.py seed

EXPOSE 8000

CMD ["sh", "-lc", "gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 aurafoods.wsgi:application"]
