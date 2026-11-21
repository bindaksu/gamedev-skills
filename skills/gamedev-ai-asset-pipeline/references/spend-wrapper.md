# Spend Wrapper, Cache and Halo Check (reference code)

Read this when implementing the pipeline's spend wrapper, cache or byte-gate checks for the first time, or when auditing an existing wrapper against the rules in SKILL.md. Python 3.10+, stdlib only for the wrapper; Pillow for the halo check. POSIX `fcntl` locks work across processes on one machine; agents on several machines need a shared lock service instead [inference]. The code was exercised against a fake vendor (dry-run, timeout then poll, cache hit, cap refusal, model mismatch, bad flag) before publication; wire your vendor and re-run those cases before the first paid call.

## 1. What the wrapper guarantees

| Rule | Where in the code |
|---|---|
| Lock across sum, cap check, reserve and submit | `run()`, first `ledger.locked()` block |
| Reserved line written before the vendor can charge | `reserve` appended before `submit()` |
| Spend metered from the ledger, never the balance | `Ledger.state()` folds reconciled actuals plus open quotes |
| One run id per asset; an open job for that run id is polled, not resubmitted | the `for ... else` search for `submitted` or `ambiguous` |
| Ambiguous outcome recorded, never retried | `poll()` returning `None` appends `ambiguous` and exits 5 |
| Content-hash cache, no force flag | `cache_key()`; a reconciled attempt with the same key returns its file |
| Model mismatch stops the run and is never served from cache | `mismatch` flag on the reconcile row, exit 4 |
| Dry-run by default; unknown or abbreviated flags refused | `dry_run=True`; `argparse` with `allow_abbrev=False` |
| Two agents polling the same job count it once | reconcile skipped if the attempt is already reconciled |

Exit codes: 0 done or cache hit, 2 usage error, 3 cap, 4 model mismatch, 5 ambiguous pending, 6 licence blocked, 7 dry-run only.

## 2. spend.py

```python
"""spend.py - one wrapper per vendor: lock, reserve, submit, reconcile. Python 3.10+, stdlib only."""
import argparse
import fcntl
import hashlib
import json
import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path

# 2 is left to argparse usage errors
EXIT_OK, EXIT_CAP, EXIT_MISMATCH, EXIT_AMBIGUOUS, EXIT_BLOCKED, EXIT_DRY = 0, 3, 4, 5, 6, 7


def cache_key(model_id, tool_version, prompt, ref_hashes, params, variant):
    blob = json.dumps({"model": model_id, "tool": tool_version, "prompt": prompt,
                       "refs": list(ref_hashes), "params": params, "variant": variant},
                      sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class Ledger:
    def __init__(self, path: Path):
        self.path = path
        self.lock_path = path.with_suffix(".lock")

    @contextmanager
    def locked(self):
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.lock_path, "w") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)          # blocks until no other agent holds it
            try:
                yield
            finally:
                fcntl.flock(lk, fcntl.LOCK_UN)

    def rows(self):
        if not self.path.exists():
            return []
        return [json.loads(l) for l in self.path.read_text().splitlines() if l.strip()]

    def append(self, row):
        row = {"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **row}
        with open(self.path, "a") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return row

    def state(self):
        """Fold the log: spent, open reservations, and per-attempt status."""
        attempts, spent = {}, 0.0
        for r in self.rows():
            key = (r["run_id"], r["attempt"])
            a = attempts.setdefault(key, {})
            a.update({k: v for k, v in r.items() if k not in ("t", "event")})
            a["status"] = r["event"]
            if r["event"] == "reconcile":
                spent += float(r["actual"])
        reserved = sum(float(a["quote"]) for a in attempts.values() if a["status"] != "reconcile")
        return spent, reserved, attempts


def run(ledger, vendor, run_id, attempt, key, quote, cap, submit, poll, requested_model,
        dry_run=True, blocked=False):
    """submit() -> job_id ; poll(job_id) -> dict(status, actual, model, file) or None on timeout."""
    if blocked:
        return EXIT_BLOCKED, "licence blocked in register"
    with ledger.locked():
        spent, reserved, attempts = ledger.state()
        for (rid, _), a in attempts.items():
            if rid == run_id and a["status"] in ("submitted", "ambiguous"):
                job = a.get("job_id")
                break
        else:
            job = None
        if job is None:
            for a in attempts.values():
                if (a.get("cache_key") == key and a["status"] == "reconcile" and a.get("file")
                        and not a.get("mismatch")):
                    return EXIT_OK, a["file"]                      # cache hit: no spend
            if spent + reserved + quote > cap:
                return EXIT_CAP, f"cap {cap}: spent {spent} + reserved {reserved} + quote {quote}"
            if dry_run:
                return EXIT_DRY, f"would spend {quote}; total after {spent + reserved + quote} of {cap}"
            ledger.append({"event": "reserve", "vendor": vendor, "run_id": run_id, "attempt": attempt,
                           "cache_key": key, "quote": quote, "cap": cap})
            job = submit()                                         # vendor may charge here
            ledger.append({"event": "submitted", "run_id": run_id, "attempt": attempt, "job_id": job})
    result = poll(job)                                             # outside the lock
    with ledger.locked():
        _, _, attempts = ledger.state()
        att = next(n for (rid, n), a in attempts.items() if rid == run_id and a.get("job_id") == job)
        if attempts[(run_id, att)]["status"] == "reconcile":       # another agent polled it first
            return EXIT_OK, attempts[(run_id, att)].get("file")
        if result is None:
            ledger.append({"event": "ambiguous", "run_id": run_id, "attempt": att, "job_id": job})
            return EXIT_AMBIGUOUS, f"job {job} unresolved; poll it, do not resubmit"
        row = {"event": "reconcile", "run_id": run_id, "attempt": att, "job_id": job,
               "actual": result["actual"], "model_reported": result.get("model")}
        mismatch = bool(result.get("model")) and result["model"] != requested_model
        if result.get("file"):
            row.update(file=result["file"], raw_sha256=sha256_file(result["file"]))
        if mismatch:
            row["mismatch"] = True                                 # never served from cache
        ledger.append(row)
    if mismatch:
        return EXIT_MISMATCH, f"requested {requested_model}, vendor reported {result['model']}"
    return EXIT_OK, result.get("file")


def parse(argv):
    p = argparse.ArgumentParser(allow_abbrev=False)
    p.add_argument("--brief", required=True, type=Path, help="JSON brief; the prompt lives in this file")
    p.add_argument("--spend", action="store_true", help="actually submit; default is dry-run")
    return p.parse_args(argv)                                      # unknown flags exit 2
```

## 3. Wiring a vendor

`submit()` sends the request and returns the vendor's job id. It must not retry internally: switch off SDK auto-retries for the submit call, because an SDK retry after a dropped connection is exactly the double charge the ledger exists to prevent. `poll(job_id)` waits up to a fixed deadline and returns a dict with `status`, `actual` (the charge from the vendor's receipt or job record, not your quote), `model` (the model the vendor reports) and `file` (the downloaded raw output), or `None` on timeout.

```python
def make_vendor(client, model_id, prompt, params):
    def submit():
        return client.create_job(model=model_id, prompt=prompt, **params, max_retries=0)["id"]
    def poll(job_id, deadline_s=600):
        end = time.time() + deadline_s
        while time.time() < end:
            j = client.get_job(job_id)
            if j["status"] in ("succeeded", "failed"):
                path = client.download(j) if j["status"] == "succeeded" else None
                return {"status": j["status"], "actual": j["charged"], "model": j.get("model"), "file": path}
            time.sleep(5)
        return None                       # ambiguous: the next run polls this job id again
    return submit, poll
```

The client calls are placeholders; map them to your vendor's job API. Where a tool has no job id (some CLI image tools), treat the session id as the job id and recover output from the tool's session folder before declaring the attempt ambiguous.

Calling it:

```python
brief = json.loads(args.brief.read_text())
key = cache_key(brief["model"], TOOL_VERSION, brief["prompt"],
                [sha256_file(r) for r in brief["refs"]], brief["params"], brief["variant"])
code, info = run(Ledger(LEDGER_DIR / f"{vendor}.jsonl"), vendor, brief["run_id"], brief["attempt"], key,
                 quote=price_quote(brief), cap=PHASE_CAP[vendor], submit=submit, poll=poll,
                 requested_model=brief["model"], dry_run=not args.spend,
                 blocked=register_blocked(brief["model"]))
sys.exit(code)
```

After exit 0, write the provenance manifest row (SKILL.md, deliverable 4) from the brief, the reconcile line and the file hash. After exit 4, mark the model blocked in the Model Register.

## 4. halo.py

```python
"""halo.py - edge-colour and sharpness checks on the FINAL encoded file. Needs Pillow."""
from PIL import Image, ImageFilter


def halo_ratio(path, key=(255, 0, 255), tol=60, ring=2):
    """Share of visible pixels within ring px of full transparency whose RGB is within tol of the key."""
    im = Image.open(path).convert("RGBA")
    alpha = im.getchannel("A")
    transparent = alpha.point(lambda a: 255 if a == 0 else 0)
    near = transparent.filter(ImageFilter.MaxFilter(2 * ring + 1))
    hits = total = 0
    for (r, g, b, a), n in zip(im.getdata(), near.getdata()):
        if a == 0 or n == 0:
            continue
        total += 1
        if (r - key[0]) ** 2 + (g - key[1]) ** 2 + (b - key[2]) ** 2 <= tol * tol:
            hits += 1
    return hits / total if total else 0.0


def sharpness(source_px, drawn_pt, device_scale):
    """Source pixels per device pixel at the largest drawn size; must be at least 1.0."""
    return source_px / (drawn_pt * device_scale)
```

- Run `halo_ratio` on the final encoded file (after WebP, ASTC preview decode or whatever ships), with the key colour you generated on.
- Starting threshold [inference]: fail above 0.005 (0.5% of edge pixels) at `tol=60`, then tune per palette; art whose own palette sits near the key colour needs a different key, not a looser tolerance.
- `sharpness(source_px, drawn_pt, device_scale)` takes the largest drawn size on the largest supported device; fail below 1.0.

## 5. Ledger hygiene

- One ledger file per vendor, append-only, fsync per line, never edited by hand. Corrections are new lines.
- Keep the ledger and manifest in version control or a backed-up store. They are the evidence for the cost report and the store disclosure.
- Reconcile weekly against the vendor's billing export. A difference means a call bypassed the wrapper; find it before raising any cap.
- Vendor keys live only in the tooling package. Add a test that fails if a vendor endpoint or key pattern appears in shipped source.
