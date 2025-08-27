.DEFAULT_GOAL:=all
all: lint test sbom
lint:
	flake8
test:
	pytest -q
sbom:
	python tools/sbom_gen.py && python tools/sbom_sign.py artifacts/sbom/sbom.json
