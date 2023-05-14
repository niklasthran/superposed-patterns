#! /bin/bash

echo $'\nChecking for Python ...'
if ! hash python; then
    echo $'\nPython is not installed on this system.\n'
    exit 1
fi

sleep 1

echo 'Setting up virtual environment for experiments ...'
python -m venv ./experiment-env

sleep 1

echo 'Activating environment ...'
source experiment-env/bin/activate

sleep 1

echo $'Installing requirements ...\n'
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo $'\nDone. Environment is ready to use!\n'
