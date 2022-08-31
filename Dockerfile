FROM python:3.10-bullseye
RUN apt-get update && apt-get install -y supervisor cron postgresql
RUN mkdir -p /var/log/supervisor
COPY  supervisord.conf /etc/supervisor/conf.d/supervisord.conf
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install
RUN playwright install-deps
COPY . .

# needs to be set else Celery gives an error (because docker runs commands inside container as root)
ENV C_FORCE_ROOT=1
EXPOSE 8000
CMD ["/usr/bin/supervisord"]
