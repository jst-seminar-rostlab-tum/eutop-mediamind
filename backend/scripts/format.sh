#!/bin/bash

echo  "black"
black app
echo "isort"
isort app
echo -n "flake8"
flake8 app

