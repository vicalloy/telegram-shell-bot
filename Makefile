pyenv:
	#pip install pipenv --upgrade
	#pipenv --python 3
	pipenv shell
	pipenv install -d --skip-lock

run:
	python bot.py

isort:
	isort --recursive ./
