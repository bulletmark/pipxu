#!/bin/sh
# Install this utility in a temporary virtual environment to then
# run itself to install itself.
# M.Blakeney, Mar 2024.
trap 'rm -rf $VENV' EXIT
VENV=$(mktemp -d)
python3 -m venv $VENV
$VENV/bin/pip install pipxu
$VENV/bin/pipxu install -f pipxu
