FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* /app/

RUN uv pip install --system --no-cache .

COPY . /app/

RUN uv run python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:8000", "auth_service.wsgi:application"]

