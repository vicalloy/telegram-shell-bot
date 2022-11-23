run:
	python bot.py

pyenv:
	poetry install
	poetry shell

init-pre-commit:
	pre-commit install
	pre-commit run --all-files
