test:
	pytest
	flake8 src
	mypy src

testfull:
	make test
	tox
