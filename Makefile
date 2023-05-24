check-config:
	docker-compose -f docker-compose-local.yml config

check-logs:
	docker-compose -f docker-compose-local.yml logs



build:
	docker-compose -f docker-compose-local.yml up --build -d --remove-orphans

build-postgres:
	docker-compose -f docker-compose-local.yml up --build -d --remove-orphans postgres_report

build-redis:
	docker-compose -f docker-compose-local.yml up --build -d --remove-orphans redis_report

build-api:
	docker-compose -f docker-compose-local.yml up --build -d --remove-orphans api_report

up:
	docker-compose -f docker-compose-local.yml up -d

restart:
	docker-compose -f docker-compose-local.yml restart

down:
	docker-compose -f docker-compose-local.yml down

down-v:
	docker-compose -f docker-compose-local.yml down -v



pipinstall:
	docker-compose -f docker-compose-local.yml run --rm api_report pip install -r requirements.txt

piplist:
	docker-compose -f docker-compose-local.yml run --rm api_report pip list

exec-postgres:
	docker-compose -f docker-compose-local.yml exec postgres_report psql --username=report --dbname=report

backup:
	docker-compose -f docker-compose-local.yml exec postgres_report backup

check-backups:
	docker-compose -f docker-compose-local.yml exec postgres_report backups



inspect-postgres-data:
	docker volume inspect local_postgres_data

inspect-postgres-ip:
	docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgres_report

inspect-api-ip:
	docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' api_report

inspect-postgres-backups:
	docker volume inspect local_postgres_data_backups

inspect_static:
	docker volume inspect static_volume

test:
	pytest --tb=short