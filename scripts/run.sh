#!/bin/bash

bin='./.venv/bin'
flask="$bin"'/flask'
pip="$bin"'/pip'

"$pip" install -r requirements.txt
"$flask" db upgrade
"$flask" run
