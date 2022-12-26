#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd ${SCRIPT_DIR}

BRANCH=$(git rev-parse --abbrev-ref HEAD)
TARGET="gui_stable"

LOG=${SCRIPT_DIR}/start.log
VENV=${SCRIPT_DIR}/env

rm -f ${LOG}
if [[ "$BRANCH" != "$TARGET" ]]; then
    git checkout gui_stable > ${LOG} 2>&1 || exit 1
fi

# Pull and overwrite everything local
git fetch --all > ${LOG} 2>&1 || exit 2
git reset --hard origin/gui_stable > ${LOG} 2>&1 || exit 3

if [ ! -d $VENV ] ; then
    python3 -m venv ${VENV} > ${LOG} 2>&1
fi

source ${VENV}/bin/activate > ${LOG} 2>&1

# https://stackoverflow.com/questions/23475502/update-a-virtualenv-to-match-requirements-txt
env/bin/python -m pip freeze | grep -v -f requirements.txt - | xargs env/bin/python -m pip uninstall -y > ${LOG} 2>&1
env/bin/python -m pip install -r requirements.txt > ${LOG} 2>&1

# Run the app
env/bin/python ./gui_tests.py > ${LOG} 2>&1
