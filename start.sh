#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd ${SCRIPT_DIR}

BRANCH=$(git rev-parse --abbrev-ref HEAD)
TARGET="gui"

LOG=${SCRIPT_DIR}/start.log
VENV=${SCRIPT_DIR}/env

rm -f ${LOG}
if [[ "$BRANCH" != "$TARGET" ]]; then
    git checkout gui_stable || exit 1
fi

# Pull and overwrite everything local
#git fetch --all > ${LOG} 2>&1 || exit 2
#git reset --hard origin/gui_stable > ${LOG} 2>&1 || exit 3

if [ ! -d $VENV ] ; then
    python3 -m venv ${VENV}
fi

source ${VENV}/bin/activate

pip install -r requirements.txt --upgrade

# Run the app
env/bin/python ./gui_tests.py
