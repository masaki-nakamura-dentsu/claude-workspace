#!/bin/zsh
# launchd から呼ぶラッパー(.zshenvのTEAMS_WEBHOOK_URLを読み込む)
source ~/.zshenv 2>/dev/null
export PATH="$HOME/.local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
mkdir -p ~/expo_watch_logs
python3 "$(dirname "$0")/expo_watch.py" >> ~/expo_watch_logs/launchd.log 2>&1
