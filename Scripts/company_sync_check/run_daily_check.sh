#!/bin/bash
export PATH="$HOME/.npm-global/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

PROJECT_DIR=$(ls -d "$HOME"/*Dropbox*/中村正樹 2>/dev/null | head -1)
cd "$PROJECT_DIR" || exit 1

PROMPT_FILE="$HOME/CompanySyncCheck/daily_check_prompt.md"

claude -p "$(cat "$PROMPT_FILE")" \
  --allowedTools "Bash Read Glob Grep PushNotification"
