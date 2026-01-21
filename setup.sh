#!/usr/bin/env bash
set -e

python -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python main.py
