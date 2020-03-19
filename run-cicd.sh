#!/usr/bin/env bash


while true; do
  echo "git pull"
  git pull
  pip3 install -r requirements.txt
  echo "Run main.py"
  python3 main.py
  sleep 3600
done
