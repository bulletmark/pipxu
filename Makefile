NAME = $(shell basename $(CURDIR))
PYFILES = $(wildcard */*.py */*/*.py)

check::
	ruff check $(PYFILES)
	mypy $(PYFILES)
	pyright $(PYFILES)
	vermin -vv --exclude --exclude tomllib \
		--no-tips -i $(PYFILES)
	shellcheck $(NAME)-bootstrap

upload:: build
	twine upload dist/*

build::
	rm -rf dist
	python3 -m build --sdist --wheel

doc::
	update-readme-usage -A

format::
	ruff check --select I --fix $(PYFILES) && ruff format $(PYFILES)

clean::
	@rm -vrf *.egg-info build/ dist/ __pycache__/ \
	    */__pycache__ */*/__pycache__
