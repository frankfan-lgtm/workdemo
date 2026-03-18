#!/bin/bash
# ClawTeam Setup Script
# Installs ClawTeam from source

set -e

echo "==> Cloning ClawTeam..."
if [ ! -d "ClawTeam" ]; then
    git clone https://github.com/HKUDS/ClawTeam.git
fi

echo "==> Installing ClawTeam..."
cd ClawTeam
pip3 install -e .

echo "==> Verifying installation..."
clawteam --version

echo "==> Done! ClawTeam is ready to use."
echo ""
echo "Quick start:"
echo "  clawteam team spawn-team my-team -d 'My first team' -n leader"
echo "  clawteam spawn --team my-team --agent-name alice --task 'Do something cool'"
echo "  clawteam board attach my-team"
