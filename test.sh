#!/bin/bash
set -o errexit

pytest --cov=sercol/ --cov-report=term-missing tests "$@"

