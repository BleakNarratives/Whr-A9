#!/bin/bash
# WHORL Environment Shim
# Standardizes paths across Android Termux and Chromebook Linux containers.

if [ -d "/storage/emulated/0/RootBase/Whorl" ]; then
    # Android/Termux environment
    export WHORL_ROOT="/storage/emulated/0/RootBase/Whorl"
elif [ -d "/home/chronos/user/RootBase/Whorl" ]; then
    # Chromebook/Linux environment
    export WHORL_ROOT="/home/chronos/user/RootBase/Whorl"
else
    # Fallback to current project root
    export WHORL_ROOT="/storage/ED7B-AD5A/root_2026"
fi

export WHORL_SWARM_LOGS="$WHORL_ROOT/Swarm-System/logs"
export WHORL_DATA="$WHORL_ROOT/data"
export WHORL_VERIFIER="$WHORL_ROOT/whr_verifier.py"

echo "🎯 WHORL environment mapped to $WHORL_ROOT"
