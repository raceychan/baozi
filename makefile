.PHONY: install
install:
	pip install -e .

.PHONY: test
test:
	pytest -sv --cov-report term-missing --cov=baozi tests

# bash: make release VERSION=1.0.1
.PHONY: release
release: test
	git add -A
	git tag -a v$(VERSION) -m "Version $(VERSION)"
	git push origin master --tags

.PHONY: publish
publish: test
	poetry build
	twine upload --skip-existing dist/*

