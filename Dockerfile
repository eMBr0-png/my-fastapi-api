FROM python:3.14.7-slim

WORKDIR /app

ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-interaction

COPY . .

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD poetry run uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
