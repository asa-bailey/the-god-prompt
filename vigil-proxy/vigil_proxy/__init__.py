"""vigil-proxy — minimal, honest reference implementation of the Vigil predicate layer.

What this package enforces: machine-checkable predicates (tool allowlist/denylist,
per-tool rate limits, regex dual-use escalation, session action caps) plus a
tamper-evident hash-chained action log.

What it does NOT do: moral judgment, alignment, or semantic evaluation of any kind.
See README.md in this directory for the full boundary statement.
"""

__version__ = "0.1.0"
