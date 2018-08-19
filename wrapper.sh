#!/usr/bin/env bash

# Use pyenv provided framework version of python instead of pipenv (virtualenv) copy.
PYTHON=$(pyenv which python)
export PYTHONHOME=$(pipenv --venv)
exec $PYTHON $1
