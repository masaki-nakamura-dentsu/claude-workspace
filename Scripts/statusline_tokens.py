#!/usr/bin/env python3
"""Claude Code statusLine: shows model, current context tokens, and session cost."""
import json
import os
import sys


def read_lines_reverse(path, chunk_size=8192, max_bytes=2_000_000):
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            pos = f.tell()
            buf = b""
            scanned = 0
            while pos > 0 and scanned < max_bytes:
                read_size = min(chunk_size, pos)
                pos -= read_size
                f.seek(pos)
                chunk = f.read(read_size)
                buf = chunk + buf
                scanned += read_size
                lines = buf.split(b"\n")
                buf = lines[0]
                for line in reversed(lines[1:]):
                    if line.strip():
                        yield line.decode("utf-8", errors="ignore")
            if buf.strip():
                yield buf.decode("utf-8", errors="ignore")
    except FileNotFoundError:
        return


def fmt_tokens(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1000:
        return f"{n / 1000:.1f}K"
    return str(n)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        print("Claude Code")
        return

    model_info = data.get("model") or {}
    model = model_info.get("display_name") or model_info.get("id") or "Claude"

    cost = data.get("cost") or {}
    total_cost = cost.get("total_cost_usd")

    transcript_path = data.get("transcript_path")
    context_tokens = None
    if transcript_path:
        for line in read_lines_reverse(transcript_path):
            try:
                entry = json.loads(line)
            except Exception:
                continue
            if entry.get("type") == "assistant":
                usage = (entry.get("message") or {}).get("usage")
                if usage:
                    context_tokens = (
                        (usage.get("input_tokens") or 0)
                        + (usage.get("cache_creation_input_tokens") or 0)
                        + (usage.get("cache_read_input_tokens") or 0)
                    )
                    break

    parts = [f"\U0001F916 {model}"]
    if context_tokens is not None:
        parts.append(f"\U0001F524 {fmt_tokens(context_tokens)} tok")
    if total_cost is not None:
        parts.append(f"\U0001F4B0 ${total_cost:.2f}")

    print(" | ".join(parts))


if __name__ == "__main__":
    main()
