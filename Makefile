run:
	python bot.py

pyenv:
	#pip install pipenv --upgrade
	#pipenv --python 3
	pipenv install -d --skip-lock
	pipenv shell

isort:
	isort --recursive ./
