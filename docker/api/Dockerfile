ARG PYTHON_VERSION=3.10-slim-bullseye
FROM python:${PYTHON_VERSION} as python

FROM python as python-build-stage
ARG BUILD_ENVIRONMENT=local
RUN apt-get update && apt-get install --no-install-recommends -y \
    libpq-dev \
    build-essential
COPY ./requirements.txt .
RUN pip wheel --wheel-dir /usr/src/app/wheels -r requirements.txt

FROM python as python-run-stage
ARG BUILD_ENVIRONMENT=local
ARG APP_HOME=/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}
WORKDIR ${APP_HOME}
RUN apt-get update && apt-get install --no-install-recommends -y  \
    libpq-dev gettext curl postgresql \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

COPY --from=python-build-stage /usr/src/app/wheels /wheels/
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* && rm -rf /wheels/

COPY ./docker/api/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./docker/api/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./docker/api/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./docker/api/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

COPY ./docker/api/celery/beat/start /start-beat
RUN sed -i 's/\r$//g' /start-beat
RUN chmod +x /start-beat

COPY . ${APP_HOME}
ENTRYPOINT ["/entrypoint"]