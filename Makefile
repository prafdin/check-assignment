SHELL := /bin/bash

.SHELLFLAGS = -e -o pipefail -c
.ONESHELL:
.PHONY: run-int-tests-locally

run-int-tests-locally:
	act workflow_dispatch -e integration_tests_payload.json --secret-file integration_tests.secrets -W .github/workflows/integration_tests.yaml