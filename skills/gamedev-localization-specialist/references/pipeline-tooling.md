# Localization Pipeline Tooling

Read this when setting up CI checks, the pseudo-locale, font character sets, or the i18n code audit.

## 1. i18n code audit: grep patterns (C# / Unity example)

```bash
# String concatenation feeding UI text
grep -rnE '\.text\s*=\s*[^;]*"\s*\+' Assets/Scripts
grep -rnE 'string\.Format\(\s*"[A-Za-z]' Assets/Scripts       # English grammar baked into format strings
# Hardcoded literals assigned to text components
grep -rnE '\.(text|SetText)\s*\(?\s*=?\s*"[A-Za-z][^"]{2,}"' Assets/Scripts
# Code-side plurals
grep -rnE '==\s*1\s*\?\s*"' Assets/Scripts
# Culture-sensitive case mapping on display text
grep -rnE 'ToUpperInvariant|ToLowerInvariant|\.ToUpper\(\)|\.ToLower\(\)' Assets/Scripts
# Number and date formatting without culture
grep -rnE '\.ToString\("(N|C|F)[0-9]?"\)|DateTime\.Now\.ToString\(' Assets/Scripts
```

Each hit is reviewed, not auto-fixed: IDs and file paths legitimately use invariant culture.

## 2. Pseudo-locale generator

```python
#!/usr/bin/env python3
"""Generate a pseudo locale: accented, padded +40%, bracketed, ICU-safe."""
import json, re, sys

ACCENT = str.maketrans("aceinosuyACEINOSUY", "àçéîñöšüýÀÇÉÎÑÖŠÜÝ")
TOKEN = re.compile(r"(\{[^{}]*\}|<[^>]+>|%\w|\\n)")   # ICU args, tags, printf, newline

def pseudo(text: str, pad: float = 0.4) -> str:
    parts = TOKEN.split(text)
    out = "".join(p if TOKEN.fullmatch(p) else p.translate(ACCENT) for p in parts)
    filler = "~" * max(1, int(len(text) * pad))
    return f"[{out}{filler}]"

def main(src: str, dst: str) -> None:
    strings = json.load(open(src, encoding="utf-8"))
    json.dump({k: pseudo(v) for k, v in strings.items()},
              open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
```

Note: this simple splitter does not descend into ICU plural branches. For nested messages, parse with an ICU message parser and transform only literal text nodes.

What pseudo-loc catches: hardcoded strings (they show without brackets), truncation (the closing bracket is missing), missing glyph coverage for accented Latin, and concatenation (brackets appear mid-sentence).

## 3. Character set extraction for static font atlases

```python
#!/usr/bin/env python3
"""Collect the unique characters per language from string tables, plus a floor set."""
import json, sys, unicodedata
from pathlib import Path

def charset(paths, floor_file=None):
    chars = set()
    for p in paths:
        for v in json.load(open(p, encoding="utf-8")).values():
            chars.update(unicodedata.normalize("NFC", v))
    if floor_file:
        chars.update(Path(floor_file).read_text(encoding="utf-8"))
    chars.update("0123456789%+-×:/.,!?()[]")          # numerals and UI punctuation
    return "".join(sorted(c for c in chars if not c.isspace()))

if __name__ == "__main__":
    out = charset(sys.argv[2:], floor_file=sys.argv[1] or None)
    print(f"{len(out)} glyphs", file=sys.stderr)
    sys.stdout.write(out)
```

Run it per language in CI and fail the build if the font asset's character table is missing any character in the output. That check alone eliminates shipped tofu.

## 4. CI gates

| Gate | Fails when |
|---|---|
| Key lint | Key without context, screenshot, or placeholder description |
| ICU parse | Any translation fails to parse, or has different argument names than source |
| Placeholder parity | Translation drops or adds a `{arg}` or tag |
| Length budget | Rendered width (measured with the real font at UI size) exceeds the box |
| Glyph coverage | Character set not covered by primary plus fallback fonts |
| Pseudo-loc screenshot diff | Truncation or unbracketed text on any screen in the capture suite |
| Stale strings | Source changed after translation without re-translation flag |

Measure width with the real font, not character counts. "WWWW" and "iiii" are both 4 characters.

## 5. Continuous localization for LiveOps

```
D-15  event strings written, context and screenshots attached, pushed to TMS
D-10  string freeze (text); VO freeze at D-20 if voiced
D-7   translations back; automated gates run
D-5   LQA in context on device, all tier-1 languages
D-3   fixes merged; final pseudo-loc and glyph pass
D-0   ship; late text fixes via remote config keys only (no new keys after freeze)
```

## 6. TMS and vendor kit contents

- Glossary: term, part of speech, definition, do-not-translate flag, approved translation per language.
- Style guide per language: formality (tu/vous, du/Sie, desu/masu), tone per character, number and date conventions, capitalization rules, punctuation (French spaces before ! ? : ;).
- Character bible: names, gender, age, speech style, catchphrases.
- Screenshot library keyed to string keys.
- Query channel with a 24-hour answer SLA and a shared query log.
- Translation memory export per release, so repeated event text costs less each time.
