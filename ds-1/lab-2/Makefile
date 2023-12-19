# Targets
.PHONY: run clean

run:
	@echo "Postgresql up..."
	docker compose -f docker-compose.yml up --build --detach
	@echo "Starting Flask server..."
	python3 src/app.py

clean:
	@echo "Cleaning up..."
	docker-compose -f docker/docker-compose.yml down
	# Add any additional cleanup tasks if needed
