# Targets
.PHONY: run clean clean-volumes

run-db:
	@echo "Postgresql up..."
	docker compose -f docker-compose.yml up --build --detach

run-web:
	@echo "Starting Flask server..."
	python3 src/app.py

add-sql:
	@echo "Running SQL file..."
	docker exec -i lab-2-db psql -U user -d lab2 -a < sql/additional_tables.sql


stop:
	@echo "Cleaning up..."
	docker compose -f docker-compose.yml down
	# Add any additional cleanup tasks if needed

clean-volumes:
	@echo "Cleaning up volumes..."
	docker compose -f docker-compose.yml down -v

