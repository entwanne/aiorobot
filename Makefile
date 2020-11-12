build:
	python setup.py sdist bdist_wheel

testpublish:
	python -m twine upload --repository testpypi dist/*

publish:
	python -m twine upload dist/*

.PHONY: build testpublish publish
