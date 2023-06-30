start:
	flask --app example --debug run
lint:
	flake8 /home/spacewalrus/prog/hexlet-flask-example/example.py
	flake8 /home/spacewalrus/prog/hexlet-flask-example/validator.py