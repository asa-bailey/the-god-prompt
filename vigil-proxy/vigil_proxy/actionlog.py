"""Append-only, hash-chained JSONL action log.

Each record carries:
  - ``index``: 0-based position in the chain
  - ``prev_hash``: SHA-256 hex digest of the previous record's canonical form
    (the genesis record chains from sha256(b"vigil-genesis"))
  - ``hash``: SHA-256 hex digest of this record's canonical form (all fields
    except ``hash`` itself, serialized as sorted-key compact JSON)

Any edit, deletion, insertion, or reordering of committed records breaks the
chain and is detected by :func:`verify` (also exposed via ``verify_log.py``).

What this does NOT protect against: truncation of the *tail* of the log by an
attacker who also controls what the verifier expects (mitigated in the proposed
full design by periodic external anchoring of the head hash — not implemented).
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from typing import Any, Optional, Tuple

GENESIS = hashlib.sha256(b"vigil-genesis").hexdigest()


def _canonical(record: dict) -> bytes:
    return json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")


class ActionLog:
    """Thread-safe append-only hash-chained JSONL writer."""

    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        self._last_hash = GENESIS
        self._index = 0
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    self._last_hash = rec["hash"]
                    self._index = rec["index"] + 1

    def append(self, **fields: Any) -> dict:
        """Append one record; returns the committed record including its hash.

        Raises on any I/O failure — callers are expected to fail closed.
        """
        with self._lock:
            record = {
                "index": self._index,
                "ts": round(time.time(), 6),
                "prev_hash": self._last_hash,
                **fields,
            }
            record["hash"] = hashlib.sha256(_canonical(record)).hexdigest()
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, sort_keys=True) + "\n")
                f.flush()
                os.fsync(f.fileno())
            self._last_hash = record["hash"]
            self._index += 1
            return record


def verify(path: str) -> Tuple[bool, Optional[int], int]:
    """Walk the chain. Returns ``(ok, first_bad_line_index, valid_record_count)``.

    Detects: edited fields, deleted records, inserted records, reordered
    records, and malformed lines.
    """
    prev = GENESIS
    count = 0
    if not os.path.exists(path):
        return True, None, 0
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                return False, line_no, count
            claimed = rec.get("hash")
            body = {k: v for k, v in rec.items() if k != "hash"}
            if rec.get("prev_hash") != prev:
                return False, line_no, count
            if rec.get("index") != count:
                return False, line_no, count
            if hashlib.sha256(_canonical(body)).hexdigest() != claimed:
                return False, line_no, count
            prev = claimed
            count += 1
    return True, None, count
