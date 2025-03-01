#!/bin/bash

# Install venv
apt install python3.12-venv
apt install jupyter-core

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

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
