#!/bin/bash
# DataWithEla — Daily auto-publish script
# Runs autopilot to find trends and publish 3 articles

export GEMINI_API_KEY="PASTE_YOUR_KEY_HERE"
export PATH="/opt/anaconda3/bin:/usr/local/bin:/usr/bin:$PATH"

cd /Users/elakumuk/Desktop/elakumuk.github.io

# Log output
python3 autopilot.py 3 >> /Users/elakumuk/Desktop/elakumuk.github.io/autopilot.log 2>&1

echo "$(date): Autopilot run complete" >> /Users/elakumuk/Desktop/elakumuk.github.io/autopilot.log
