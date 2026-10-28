#!/bin/bash
# worker.sh を launchd(com.nakamura.macdirect、KeepAlive)に登録する。受け手のMacのターミナルで1回だけ実行する。
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
CLAUDE="$(command -v claude)"; [ -n "$CLAUDE" ] || { echo "claude が見つかりません"; exit 1; }
P="$HOME/Library/LaunchAgents/com.nakamura.macdirect.plist"
mkdir -p "$HOME/MacDirect"
cat > "$P" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key><string>com.nakamura.macdirect</string>
	<key>ProgramArguments</key><array><string>/bin/bash</string><string>$HERE/worker.sh</string></array>
	<key>EnvironmentVariables</key><dict>
		<key>PATH</key><string>$(dirname "$CLAUDE"):/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
		<key>CLAUDE_BIN</key><string>$CLAUDE</string>
	</dict>
	<key>RunAtLoad</key><true/>
	<key>KeepAlive</key><true/>
	<key>StandardOutPath</key><string>$HOME/MacDirect/stdout.log</string>
	<key>StandardErrorPath</key><string>$HOME/MacDirect/stderr.log</string>
</dict>
</plist>
EOF
launchctl bootout gui/$(id -u)/com.nakamura.macdirect 2>/dev/null || true
launchctl bootstrap gui/$(id -u) "$P"
launchctl print gui/$(id -u)/com.nakamura.macdirect | grep -E "state =|pid ="
