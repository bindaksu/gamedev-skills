#!/usr/bin/env python3
"""Build site/index.html (catalog artifact) from skills/*/SKILL.md."""
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
TEMPLATE = ROOT / "tools" / "site_template.html"
OUT = ROOT / "site" / "index.html"


def load(skill_dir: Path) -> dict:
    text = (skill_dir / "SKILL.md").read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    fm = yaml.safe_load(m.group(1))
    body = text[m.end():]
    ui = yaml.safe_load((skill_dir / "agents" / "openai.yaml").read_text())["interface"]
    refs = sorted(str(p.relative_to(skill_dir)) for p in (skill_dir / "references").glob("*.md")) \
        if (skill_dir / "references").exists() else []
    related = sorted(set(re.findall(r"\bgamedev-[a-z0-9-]*[a-z0-9]\b", body)) - {fm["name"]})
    lines = text.count("\n") + 1
    ref_lines = sum((skill_dir / r).read_text().count("\n") + 1 for r in refs)
    return {
        "name": fm["name"],
        "category": fm.get("metadata", {}).get("category", "other"),
        "title": ui["display_name"],
        "short": ui["short_description"],
        "prompt": ui["default_prompt"],
        "description": " ".join(str(fm["description"]).split()),
        "lines": lines,
        "refLines": ref_lines,
        "refs": refs,
        "related": related,
        "body": body,
        "raw": text,
    }


def main():
    data = [load(d) for d in sorted(SKILLS.iterdir()) if (d / "SKILL.md").exists()]
    html = TEMPLATE.read_text().replace("/*__DATA__*/[]", json.dumps(data).replace("</", "<\\/"))
    OUT.write_text(html)
    print(f"{len(data)} skills -> {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
