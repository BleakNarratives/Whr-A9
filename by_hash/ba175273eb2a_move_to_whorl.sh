#!/bin/bash
# WHORL Migration Script
# Moves hardened verifier and event loop to the final WHORL directory.

TARGET_DIR="/storage/emulated/0/RootBase/Whorl/src"

echo "🚀 Migrating WHORL components..."

# Move Verifier
mv /storage/ED7B-AD5A/root_2026/whr_verifier.py "$TARGET_DIR/"
echo "✅ whr_verifier.py moved to $TARGET_DIR"

# Move Event Loop Manager
mv /storage/ED7B-AD5A/root_2026/event_loop_manager.py "$TARGET_DIR/"
echo "✅ event_loop_manager.py moved to $TARGET_DIR"

echo "🎯 Migration complete."
