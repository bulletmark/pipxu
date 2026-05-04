NAME := file_name(justfile_dir())
PYFILES := `echo */*.py */*/*.py`

check:
  ruff check {{PYFILES}}
  ty check {{PYFILES}}
  vermin -vv --no-tips -i {{PYFILES}}
  shellcheck {{NAME}}-bootstrap
  md-link-checker

build:
  rm -rf dist
  uv build

upload: build
	uv-publish

doc:
  update-readme-usage -A

format:
  ruff check --select I --fix {{PYFILES}} && ruff format {{PYFILES}}

clean:
	@rm -vrf uv.lock *.egg-info build/ dist/ __pycache__/ \
	    */__pycache__ */*/__pycache__
