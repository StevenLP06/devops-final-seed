.PHONY: install test lint security audit all

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	flake8 src/ tests/

security:
	bandit -r src/ --severity-level medium

audit:
	pip-audit -r requirements.txt

all: lint security audit test
