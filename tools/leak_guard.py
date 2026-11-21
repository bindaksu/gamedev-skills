#!/usr/bin/env python3
"""Block secrets and private project details from reaching this public repo.

Usage:
  leak_guard.py            scan tracked and untracked (not ignored) files
  leak_guard.py --staged   scan the staged version of staged files (pre-commit)

Built-in checks: private keys, common API-token formats, credential assignments,
author-local paths, public IPv4 addresses, e-mail addresses and device UDIDs.

Private banlist (never committed): one term per line, case-insensitive; a line
starting with "re:" is a regular expression; "#" starts a comment. Read from
$LEAK_GUARD_BANLIST or ~/.config/gamedev-skills/banlist.txt when present. Put
unreleased game names, codenames, hostnames, people and partner names there.

A line containing "leak-guard: allow" is skipped (use sparingly, explain why).
"""
import ipaddress
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_FILES = {"LICENSE", "tools/leak_guard.py"}
ALLOW_MARK = "leak-guard: allow"
EMAIL_OK = ("@example.com", "@example.org", "@users.noreply.github.com", "noreply@anthropic.com", "git@github.com")

PATTERNS = [
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("anthropic key", re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}")),
    ("openai-style key", re.compile(r"\bsk-(?:proj-|live-|test-)?[A-Za-z0-9_-]{24,}")),
    ("stripe/elevenlabs-style key", re.compile(r"\bsk_(?:live_|test_)?[A-Za-z0-9]{24,}")),
    ("github token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})")),
    ("aws key id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("google api key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("slack token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}")),
    ("task/api key", re.compile(r"\btsk_[A-Za-z0-9_-]{20,}")),
    ("credential assignment", re.compile(
        r"(?i)\b(?:api[_-]?key|secret|token|passphrase|password)\b\s*[:=]\s*['\"][^'\"\s<>{}$]{16,}['\"]")),
    ("author-local path", re.compile(r"(?<![\w.-])(?:/Users/[a-z][\w.-]*/|/home/[a-z][\w.-]*/|/private/tmp/|/Volumes/[\w.-]+/)")),
    ("device UDID", re.compile(r"\b[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\b")),
]
IPV4 = re.compile(r"(?<![\w.])(\d{1,3}(?:\.\d{1,3}){3})(?![\w.])")
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def banlist() -> list[tuple[str, re.Pattern]]:
    path = Path(os.environ.get("LEAK_GUARD_BANLIST", Path.home() / ".config/gamedev-skills/banlist.txt"))
    if not path.is_file():
        return []
    out = []
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        rx = line[3:].strip() if line.startswith("re:") else re.escape(line)
        out.append(("banlist", re.compile(rx, re.IGNORECASE)))
    return out


def files(staged: bool) -> list[tuple[str, str]]:
    if staged:
        names = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").split("\0")
        read = lambda n: git("show", f":{n}")
    else:
        names = git("ls-files", "-co", "--exclude-standard", "-z").split("\0")
        read = lambda n: (ROOT / n).read_text()
    out = []
    for n in filter(None, names):
        if n in SKIP_FILES:
            continue
        try:
            out.append((n, read(n)))
        except (UnicodeDecodeError, FileNotFoundError, subprocess.CalledProcessError):
            continue  # binary or vanished
    return out


def public_ip(s: str) -> bool:
    try:
        ip = ipaddress.ip_address(s)
    except ValueError:
        return False
    doc = any(ip in ipaddress.ip_network(n) for n in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"))
    return ip.is_global and not doc


def mask(s: str) -> str:
    return s if len(s) <= 12 else s[:6] + "…" + s[-3:]


def scan(name: str, text: str, ban) -> list[str]:
    hits = []
    for no, line in enumerate(text.splitlines(), 1):
        if ALLOW_MARK in line:
            continue
        for kind, rx in PATTERNS + ban:
            for m in rx.finditer(line):
                shown = m.group(0) if kind in ("author-local path", "banlist") else mask(m.group(0))
                hits.append(f"{name}:{no}: {kind}: {shown}")
        for m in IPV4.finditer(line):
            if public_ip(m.group(1)):
                hits.append(f"{name}:{no}: public IPv4: {m.group(1)}")
        for m in EMAIL.finditer(line):
            if not m.group(0).lower().endswith(EMAIL_OK):
                hits.append(f"{name}:{no}: e-mail: {m.group(0)}")
    return hits


def main(argv: list[str]) -> int:
    staged = "--staged" in argv
    ban = banlist()
    hits = [h for n, t in files(staged) for h in scan(n, t, ban)]
    for h in hits:
        print("LEAK", h)
    note = f"{len(ban)} banlist terms" if ban else "no private banlist found"
    print(f"leak_guard: {len(hits)} finding(s), {note}")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
