SHELL := /bin/bash

.SHELLFLAGS = -e -o pipefail -c
.ONESHELL:
.PHONY: run-unit-tests-locally run-webhook-int-tests-locally run-github-int-tests-locally

run-unit-tests-locally:
	act push -W .github/workflows/unit_tests.yaml -P ubuntu-latest=prafdin-ubuntu:hacked-act-latest --pull=false

run-webhook-int-tests-locally:
	act workflow_dispatch -e integration_tests_payload.json --secret-file integration_tests.secrets -W .github/workflows/integration_tests.yaml -P ubuntu-latest=prafdin-ubuntu:hacked-act-latest --pull=false

run-github-int-tests-locally:
	act workflow_dispatch -e github_integration_tests_payload.json --secret-file integration_tests.secrets -W .github/workflows/integration_tests.yaml -P ubuntu-latest=prafdin-ubuntu:hacked-act-latest --pull=false

run-docker-int-tests-locally:
	act workflow_dispatch -e docker_integration_tests_payload.json --secret-file integration_tests.secrets -W .github/workflows/integration_tests.yaml -P ubuntu-latest=prafdin-ubuntu:hacked-act-latest --pull=false

run-compose-int-tests-locally:
	act workflow_dispatch -e compose_integration_tests_payload.json --secret-file integration_tests.secrets -W .github/workflows/integration_tests.yaml -P ubuntu-latest=prafdin-ubuntu:hacked-act-latest --pull=false