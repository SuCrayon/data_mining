#!/bin/bash
echo '===create a new python env==='
# create a new python env named "env"
python -m venv env
echo '===create env successfully==='

# activate the new env
source env/Scripts/activate

echo '===start installing requirement==='
# install requirement
pip install -r requirement.txt

echo 'successful'
