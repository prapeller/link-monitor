checkconfig:
	docker-compose -f local.yml config

build:
	docker-compose -f local.yml up --build -d --remove-orphans

checklogs:
	docker-compose -f local.yml logs

inspect_postgres:
	docker volume inspect local_postgres_data

inspect_postgres_ip:
	docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgres

inspect_api_ip:
	docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' api

inspect_postgres_backups:
	docker volume inspect local_postgres_data_backups

inspect_static:
	docker volume inspect static_volume

up:
	docker-compose -f local.yml up -d

restart:
	docker-compose -f local.yml restart

pipinstalllocal:
	docker-compose -f local.yml run --rm api pip install -r requirements.txt

piplist:
	docker-compose -f local.yml run --rm api pip list

backup:
	docker-compose -f local.yml exec postgres backup

checkbackups:
	docker-compose -f local.yml exec postgres backups

down:
	docker-compose -f local.yml down

down-v:
	docker-compose -f local.yml down -v

report_db:
	docker-compose -f local.yml exec postgres psql --username=report --dbname=report

generatekey:
	python -c 'import secrets; print(secrets.token_urlsafe(38))'

test:
	pytest --tb=short