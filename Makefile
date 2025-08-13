.PHONY: help run build test migrate seed lint format clean

help: ## Mostra esta ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

run: ## Executa o projeto com Docker Compose
	docker compose up --build

build: ## Constrói as imagens Docker
	docker compose build

test: ## Executa testes
	docker compose exec api pytest -v

test-coverage: ## Executa testes com cobertura
	docker compose exec api pytest --cov=. --cov-report=html

migrate: ## Executa migrações do banco
	docker compose exec api python manage.py migrate

makemigrations: ## Cria novas migrações
	docker compose exec api python manage.py makemigrations

seed: ## Carrega dados de seed
	docker compose exec api python manage.py loaddata seed.json

superuser: ## Cria superusuário
	docker compose exec api python manage.py createsuperuser

shell: ## Abre shell do Django
	docker compose exec api python manage.py shell

lint: ## Executa linting
	docker compose exec api flake8 .
	docker compose exec web npm run lint

format: ## Formata código
	docker compose exec api black .
	docker compose exec api isort .
	docker compose exec web npm run format

clean: ## Limpa containers e volumes
	docker compose down -v
	docker system prune -f

logs: ## Mostra logs em tempo real
	docker compose logs -f

restart: ## Reinicia serviços
	docker compose restart

status: ## Status dos serviços
	docker compose ps
