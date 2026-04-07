#!/bin/bash
set -o errexit

ruff check sercol/ tests/

echo 'Passes ruff check'
