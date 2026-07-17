#!/usr/bin/env python3
"""Verify the integrity of a vigil-proxy action log.

Usage:
    python verify_log.py [path/to/vigil_actions.jsonl]

Exit code 0 if the hash chain is intact, 1 if tampering is detected.
"""

import sys

from vigil_proxy.actionlog import verify


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else "vigil_actions.jsonl"
    ok, bad_line, count = verify(path)
    if ok:
        print(f"OK: {count} record(s), hash chain intact ({path})")
        return 0
    print(f"TAMPERING DETECTED: chain breaks at line {bad_line} ({count} valid record(s) before break) ({path})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
