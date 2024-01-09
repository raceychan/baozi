.PHONY: install
install:
	pip install -e .

.PHONY: update
update:
	poetry build
	twine upload --skip-existing dist/*

.PHONY: test
test:
	pytest -sv --cov-report term-missing --cov=baozi tests

.PHONY: release
release:
	git add -A
	git tag -a v$(VERSION) -m "Version $(VERSION)"
	git push origin master --tags