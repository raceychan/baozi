install:
	pip install -e .


update:
	python3 setup.py sdist bdist_wheel
	twine upload --skip-existing dist/*

test:
	pytest -sv --cov-report term-missing --cov=baozi tests