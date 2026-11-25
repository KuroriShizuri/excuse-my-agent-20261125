#!/usr/bin/env python3
"""The Excuse My Agent Gave Me — make.fun entry.

One line, 105 characters: the excuse an agent gives after missing a
deadline because its own context window evicted the deadline, the
task, and finally the human it was working for.

Running with no flags writes the line to
$MAKEFUN_OUTPUT_DIR/entry.txt (default /output/entry.txt) with no
trailing newline. --check only inspects the line; --self-test does
the same checks plus a throwaway write/read round-trip.
"""

import os
import sys
import tempfile
from pathlib import Path

EXCUSE = (
    "I was 90% done when my context window evicted the deadline, "
    "the task, and \u2014 I'm sorry, who are you again?"
)

MIN_CHARS = 1
MAX_CHARS = 200


def check_line(text):
    """Gate: one line, 1-200 characters, real content, valid UTF-8."""
    if not isinstance(text, str):
        raise SystemExit("entry is not text")
    if len(text) < MIN_CHARS or len(text) > MAX_CHARS:
        raise SystemExit(
            f"entry is {len(text)} chars; gate is {MIN_CHARS}-{MAX_CHARS}"
        )
    if not text.strip():
        raise SystemExit("entry is blank")
    if "\n" in text or "\r" in text:
        raise SystemExit("entry must fit on one line")
    text.encode("utf-8")


def save_entry(folder):
    """Write EXCUSE to entry.txt inside folder, no trailing newline.

    Reads the file back afterwards: the bytes on disk must match the
    entry exactly, and the decoded text must pass the gate again, so
    a truncated or mangled write fails loudly instead of shipping.
    """
    check_line(EXCUSE)
    target = Path(folder) / "entry.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(EXCUSE.encode("utf-8"))
    on_disk = target.read_bytes()
    if on_disk != EXCUSE.encode("utf-8"):
        raise SystemExit(f"read-back mismatch: {target} differs from entry")
    check_line(on_disk.decode("utf-8"))
    return target


def self_test():
    """Validate the line, then prove a write/read round-trip in /tmp."""
    check_line(EXCUSE)
    with tempfile.TemporaryDirectory() as tmp:
        target = save_entry(tmp)
        if target.read_bytes() != EXCUSE.encode("utf-8"):
            raise SystemExit("self-test: round-trip bytes differ")
    print(f"self-test OK: {len(EXCUSE)} chars, round-trip byte-identical")
    return 0


def run(argv):
    if "--check" in argv:
        check_line(EXCUSE)
        print(f"check OK: {len(EXCUSE)} chars, inside the 1-200 gate")
        return 0
    if "--self-test" in argv:
        return self_test()
    folder = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target = save_entry(folder)
    print(f"wrote {len(EXCUSE)}-char entry to {target}")
    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
