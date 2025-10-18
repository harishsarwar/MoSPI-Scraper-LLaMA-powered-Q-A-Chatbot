
.PHONY: crawl parse etl index run-api run-ui test

crawl:
	python -m scraper.crawl --seed-url $(SEED_URLS)

parse:
	python -m scraper.parse

etl:
	python -m pipeline.run

index:
	python -m pipeline.run

run-api:
	uvicorn rag.api:app --host ${API_HOST} --port ${API_PORT}

run-ui:
	uvicorn webui.fastapi_app:app --host 0.0.0.0 --port ${WEBUI_PORT}

test:
	pytest -q
