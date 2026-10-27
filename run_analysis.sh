#!/usr/bin/env bash
# Generates before/after reports for Pylint, Bandit and Flake8.
# "before" = the original starter file (first commit); "after" = current file.
set -u
cd "$(dirname "$0")"
mkdir -p reports/before reports/after

FIRST_COMMIT=$(git rev-list --max-parents=0 HEAD)
TMP=$(mktemp -d)
git show "$FIRST_COMMIT:maintenance_system.py" > "$TMP/maintenance_system.py"

(cd "$TMP" && pylint maintenance_system.py) > reports/before/pylint_report.txt
bandit -r "$TMP/maintenance_system.py" > reports/before/bandit_report.txt 2>&1
(cd "$TMP" && flake8 maintenance_system.py) > reports/before/flake8_report.txt

pylint maintenance_system.py > reports/after/pylint_report.txt
bandit -r maintenance_system.py > reports/after/bandit_report.txt 2>&1
flake8 maintenance_system.py > reports/after/flake8_report.txt

rm -rf "$TMP"
grep "rated at" reports/before/pylint_report.txt reports/after/pylint_report.txt
echo "Reports written to reports/before and reports/after"
