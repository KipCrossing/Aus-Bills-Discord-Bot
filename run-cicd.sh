#!/usr/bin/env bash


while true; do
  echo "git pull"
  git pull
  echo "Run main.py"
  python3 main.py
  sleep 3600
done
