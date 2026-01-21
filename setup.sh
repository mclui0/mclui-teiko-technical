#!/usr/bin/env bash
# Setup file to create venv and install dependencies
set -e

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py  # run main program setup in venv
streamlit run dashboard.py --server.runOnSave=true  # run dashboard: http://localhost:8501

