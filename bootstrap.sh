#!/bin/sh
virtualenv --clear .
./bin/pip install setuptools==7.0
./bin/pip install zc.buildout==2.2.5
./bin/pip install nose==1.3.4
