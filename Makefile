pyenv:
	#pip install pipenv --upgrade
	#pipenv --python 3
	pipenv install -d --skip-lock
	pipenv shell

run:
	python bot.py

isort:
	isort --recursive ./
