# just --working-directory . --justfile justfile

default: lint typecheck

lint:
  pylint plover_cycle_translations

typecheck:
  mypy plover_cycle_translations
