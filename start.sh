#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd ${SCRIPT_DIR}
BRANCH=$(git rev-parse --abbrev-ref HEAD)
TARGET="gui_stable"
LOG=start.log
rm -f ${LOG}
if [[ "$BRANCH" != "$TARGET" ]]; then
    git checkout gui_stable > ${LOG} 2>&1 || exit 1
fi

# Pull and overwrite everything local
git fetch --all > ${LOG} 2>&1 || exit 2
git reset --hard origin/gui_stable > ${LOG} 2>&1 || exit 3

# Run the app
python3 ./gui_tests.py > ${LOG} 2>&1
