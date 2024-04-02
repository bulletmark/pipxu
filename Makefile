NAME = $(shell basename $(CURDIR))
PYNAME = $(subst -,_,$(NAME))

check:
	ruff check $(NAME)
	flake8 $(NAME)
	mypy $(NAME)
	pyright $(NAME)
	vermin -vv --exclude importlib.metadata --exclude tomllib \
		--no-tips -i $(NAME)/*.py $(NAME)/*/*.py
	shellcheck $(NAME)-bootstrap

upload: build
	twine upload dist/*

build:
	rm -rf dist
	python3 -m build

doc:
	update-readme-usage -a

clean:
	@rm -vrf *.egg-info build/ dist/ __pycache__/ \
	    */__pycache__ */*/__pycache__
