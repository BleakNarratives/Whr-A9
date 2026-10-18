#!/bin/bash
# CodeCity-Bench Initialization
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 src/api/telemetry_server.py
