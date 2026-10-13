test:
	python3 -m pytest
run:
	uvicorn app.main:app --reload
