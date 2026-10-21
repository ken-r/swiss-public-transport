db-up:
	docker compose up -d db

db-schema:
	docker compose exec -T db psql -U $$POSTGRES_USER -d $$POSTGRES_DB -v ON_ERROR_STOP=1 --single-transaction -f - < sql/schema.sql
