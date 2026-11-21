# Security

## Reporting

Report a vulnerability or an accidental leak (a key, a private path, a private project detail) through GitHub's private vulnerability reporting: **Security → Report a vulnerability** on this repository. Please do not open a public issue for it.

## What this repository must never contain

- Secrets: API keys, tokens, signing material, `.env` files.
- Author-local paths, hostnames, IP addresses, device identifiers.
- Private project details: unreleased game names or codenames, people's names, partner names, internal business figures. Lessons from real projects are written at genre level.

## Guards

- `tools/leak_guard.py` scans for the above. It runs in CI on every push and pull request, and in the pre-commit hook.
- Enable the hook once per clone: `git config core.hooksPath .githooks`.
- Maintainers keep a private banlist of names outside the repository (`~/.config/gamedev-skills/banlist.txt` or `$LEAK_GUARD_BANLIST`); the hook applies it to every commit.
- GitHub secret scanning with push protection is on, and the default branch rejects force pushes and deletion.
