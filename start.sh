#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd ${SCRIPT_DIR}
BRANCH=$(git rev-parse --abbrev-ref HEAD)
TARGET="gui_stable"
LOG=start.log
rm -f ${LOG}
if [[ "$BRANCH" != "$TARGET" ]]; then
    git checkout gui_stable \
    || echo "Couldn't checkout the branch" > ${LOG}
fi

# Pull and overwrite everything local
git fetch --all
git reset --hard origin/gui_stable

# Run the app
python3 ./gui_tests.py > ${LOG}
