# just --working-directory . --justfile test/justfile

default: lint typecheck

test:
  pytest --cov --cov-report=term-missing

coverage:
  pytest --cov --cov-report=html
  open htmlcov/index.html

lint:
  pylint plover_cycle_translations

typecheck:
  mypy plover_cycle_translations
