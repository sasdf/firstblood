mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(dir $(mkfile_path))
export PYTHONPATH := $(current_dir):$(PYTHONPATH)

.PHONY: all test

all:
	@echo '[!] Nothing to build. Run `make test` if you want to test the package.'

test:
	coverage run --source firstblood -m unittest discover && \
	coverage report -m
