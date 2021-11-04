run:
	python bot.py

pyenv:
	#pip install pipenv --upgrade
	#pipenv --python 3
	pipenv install -d --skip-lock
	pipenv shell

pre-commit-init:
	pre-commit install
	pre-commit run --all-files

isort:
	isort --recursive ./

flake8:
	flake8 ./

black:
	black ./
