#!/bin/bash

# Install venv
apt install jupyter-core

# Upgrade pip
pip install --upgrade pip

# Install Jupyter Notebook
pip install jupyter

# Install ipykernel
pip install ipykernel

# Save the current environment as a Jupyter kernel
python -m ipykernel install --user --name=venv --display-name "Python (venv)"

# Start Jupyter Notebook
python -m notebook
