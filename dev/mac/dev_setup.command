#!/bin/bash

cd "$(dirname "$0")"
cd ..

if [ -d "solstice_dev" ]
then
    rm -r solstice_dev
fi

virtualenv solstice_dev
cd solstice_dev
cd bin
source activate
cd ..
cd ..
cd mac
pip install --no-cache-dir -r dev_requirements.txt