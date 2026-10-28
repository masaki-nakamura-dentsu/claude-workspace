#!/bin/bash
[ -f "$HOME/.zshenv" ] && source "$HOME/.zshenv" >/dev/null 2>&1
export PATH="$HOME/.npm-global/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$DIR/webhook_autofix.py"
