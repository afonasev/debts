FROM python:3.7.2-alpine3.9

LABEL Maintainer='Evgeniy Afonasev <ea.afonasev@gmail.com>'
LABEL Description='Debts management server'

RUN addgroup -S app && adduser -S -G app app

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_CACHE_DIR=off
ENV PYTHONDONTWRITEBYTECODE=true
ENV PYTHONFAULTHANDLER=true
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=true

RUN apk add --no-cache --update gcc libffi-dev musl-dev make postgresql-dev && \
    pip install poetry uvicorn

COPY ./docker/entrypoint.sh ./docker/server/start.sh /
COPY pyproject.toml poetry.lock /

ARG ENVIRONMENT
ENV ENVIRONMENT=${ENVIRONMENT}

RUN poetry config settings.virtualenvs.create false \
    && poetry install $(test "$ENVIRONMENT" != "dev" && echo "--no-dev") --no-interaction --no-ansi

WORKDIR /app
COPY ./server /app/server

EXPOSE 8000

USER app
CMD ["sh", "/start.sh"]
ENTRYPOINT ["sh", "/entrypoint.sh"]
