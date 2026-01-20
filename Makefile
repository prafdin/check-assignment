SHELL := /bin/bash

.SHELLFLAGS = -e -o pipefail -c
.ONESHELL:
.PHONY: run-unit-tests-locally run-int-tests-locally

run-unit-tests-locally:
	act push -W .github/workflows/unit_tests.yaml -P ubuntu-latest=prafdin-ubuntu:hacked-act-latest --pull=false

run-int-tests-locally:
	act workflow_dispatch -e integration_tests_payload.json --secret-file integration_tests.secrets -W .github/workflows/integration_tests.yaml -P ubuntu-latest=prafdin-ubuntu:hacked-act-latest --pull=false