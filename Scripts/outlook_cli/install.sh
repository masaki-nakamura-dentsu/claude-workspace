#!/usr/bin/env bash
# Sets up `outlook` (Outlook Web CLI) on a new Mac.
# The code lives in this Dropbox folder (synced across Macs); this script
# just wires up ~/Scripts and ~/.local/bin symlinks on the local Mac.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p ~/Scripts ~/.local/bin

if [ -e ~/Scripts/outlook_cli ] && [ ! -L ~/Scripts/outlook_cli ]; then
  echo "~/Scripts/outlook_cli already exists and is not a symlink — not overwriting. Check it manually." >&2
  exit 1
fi
ln -sf "$SCRIPT_DIR" ~/Scripts/outlook_cli
ln -sf ~/Scripts/outlook_cli/outlook ~/.local/bin/outlook

if ! grep -q '\.local/bin' ~/.zshrc 2>/dev/null; then
  echo 'export PATH="$PATH:'"$HOME"'/.local/bin"' >> ~/.zshrc
  echo "Added ~/.local/bin to PATH in ~/.zshrc (open a new shell to pick it up)."
fi

if [ ! -d "$HOME/.local/share/claude-playwright/node_modules/playwright" ]; then
  echo "警告: ~/.local/share/claude-playwright/node_modules/playwright が見つかりません。" >&2
  echo "先に claude_playwright_setup メモリの手順でPlaywright環境をこのMacにも導入してください。" >&2
fi

echo "Done. Symlinks:"
ls -la ~/Scripts/outlook_cli ~/.local/bin/outlook

cat <<'EOF'

Next steps (can't be done from a script):
1. Confirm the shared bot browser for this Mac is running (see memory
   shared_bot_browser.md for the port/profile — d14461 = port 9226).
   If lib.js still points at ICPTokyo2022's port 9227 / timetree-bot
   profile, edit ~/Scripts/outlook_cli/lib.js's PORT/PROFILE_DIR to match
   this Mac's actual shared browser before first use.
2. Run `outlook login` once. On ICPTokyo2022 this needed zero interactive
   steps (existing Teams SSO session in the same browser profile carried
   over silently) — it may or may not on this Mac. If it prompts for
   SSO/MFA, complete it in the opened browser window, then re-run
   `outlook login` to confirm.
3. `outlook list` to confirm the inbox is readable.

Full command reference, known gotchas, and DOM-selector notes: memory
outlook_cli.md (synced via Dropbox, should already be visible here).
EOF
