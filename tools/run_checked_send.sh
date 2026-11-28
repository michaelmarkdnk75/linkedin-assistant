#!/bin/sh
# usage: run_checked_send.sh <html> "<subject>" ID1 ID2 ...  -> runs mail_preflight.py (button check + visible-button + media-promise guards) (no Make since 21/11-2026, section 52).
# Exit 0 = HTML is OK: now send it yourself with mcp__Gmail__send_message (htmlBody only) to michaelmarkdnk@gmail.com.
H="$1"; S="$2"; shift 2
python3 -I /mnt/project-files/linkedin-stats/tools/mail_preflight.py "$H" "$@" || { echo "BUTTON CHECK FAILED - DO NOT SEND"; exit 1; }
echo "CHECK OK. Now send with Gmail send_message (htmlBody only), subject: $S"
