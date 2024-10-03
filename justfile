# just --working-directory . --justfile justfile

default: lint typecheck

lint:
  pylint src

typecheck:
  mypy src
