#!/usr/bin/env python3
"""Validate gamedev skill dirs for Claude Code + Codex compatibility.

Usage: validate.py <skill_dir> [<skill_dir> ...]   or   validate.py --all <skills_root>
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML required: pip install pyyaml")

ALLOWED = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}


def roster():
    f = Path(__file__).resolve().parent / "roster.txt"
    return set(f.read_text().split()) if f.exists() else set()


def check(skill: Path) -> list[str]:
    errs = []
    md = skill / "SKILL.md"
    if not md.exists():
        return [f"{skill.name}: SKILL.md missing"]
    extra = [p for p in skill.rglob("SKILL.md") if p != md]
    if extra:
        errs.append(f"nested SKILL.md files: {extra}")
    text = md.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return [f"{skill.name}: bad/missing frontmatter"]
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return [f"{skill.name}: YAML error {e}"]
    bad = set(fm) - ALLOWED
    if bad:
        errs.append(f"disallowed keys {sorted(bad)}")
    name = str(fm.get("name", "")).strip()
    if name != skill.name:
        errs.append(f"name '{name}' != dir '{skill.name}'")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        errs.append("name not kebab-case or > 64 chars")
    desc = str(fm.get("description", "")).strip()
    if not desc:
        errs.append("description missing")
    if len(desc) > 1024:
        errs.append(f"description {len(desc)} chars > 1024")
    if "<" in desc or ">" in desc:
        errs.append("description contains angle brackets")
    lines = text.count("\n") + 1
    if lines > 450:
        errs.append(f"SKILL.md {lines} lines > 450")
    for ref in skill.rglob("*.md"):
        n = ref.read_text().count("\n") + 1
        if n > 800:
            errs.append(f"{ref.relative_to(skill)} {n} lines > 800")
    oy = skill / "agents" / "openai.yaml"
    if not oy.exists():
        errs.append("agents/openai.yaml missing")
    else:
        try:
            ui = (yaml.safe_load(oy.read_text()) or {}).get("interface", {})
            for k in ("display_name", "short_description", "default_prompt"):
                if not ui.get(k):
                    errs.append(f"openai.yaml interface.{k} missing")
            if len(str(ui.get("short_description", ""))) > 80:
                errs.append("openai.yaml short_description > 80 chars")
        except yaml.YAMLError as e:
            errs.append(f"openai.yaml YAML error {e}")
    for r in [md] + list(skill.rglob("*.md")) + list(skill.rglob("*.yaml")):
        if re.search(r"/private/tmp|/Users/[a-z]|scratchpad|SPEC\.md", r.read_text()):
            errs.append(f"{r.relative_to(skill)} contains author-local path")
    # cross refs: any gamedev-* token must exist in roster
    known = roster()
    alltext = text + "".join(r.read_text() for r in skill.rglob("*.md") if r != md)
    for ref in sorted(set(re.findall(r"\bgamedev-[a-z0-9-]*[a-z0-9]\b", alltext))):
        if known and ref not in known and ref != "gamedev-studio":
            errs.append(f"unknown cross-ref {ref}")
    return [f"{skill.name}: {e}" for e in errs]


def main(argv):
    if len(argv) >= 2 and argv[0] == "--all":
        dirs = sorted(p for p in Path(argv[1]).iterdir() if p.is_dir())
    else:
        dirs = [Path(a) for a in argv]
    if not dirs:
        sys.exit(__doc__)
    all_errs = [e for d in dirs for e in check(d)]
    for e in all_errs:
        print("FAIL", e)
    print(f"{len(dirs) - len({e.split(':')[0] for e in all_errs})}/{len(dirs)} skills valid")
    sys.exit(1 if all_errs else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
