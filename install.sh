#!/usr/bin/env bash
# Install the gamedev-studio skill pack for Claude Code and/or OpenAI Codex.
#
#   ./install.sh                 # install for Claude Code + Codex (user scope)
#   ./install.sh --claude        # Claude Code only   (~/.claude/skills)
#   ./install.sh --codex         # Codex only         ($CODEX_HOME/skills, default ~/.codex/skills)
#   ./install.sh --project DIR   # project scope: DIR/.claude/skills + DIR/.agents/skills
#   ./install.sh --only a,b,c    # subset by skill name (combine with any target flag)
#   ./install.sh --uninstall     # remove pack skills from the chosen targets
#   ./install.sh --dry-run       # print actions only
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$HERE/skills"
CLAUDE=1; CODEX=1; PROJECT=""; ONLY=""; UNINSTALL=0; DRY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --claude) CLAUDE=1; CODEX=0 ;;
    --codex) CLAUDE=0; CODEX=1 ;;
    --project) PROJECT="${2:?--project needs a dir}"; shift ;;
    --only) ONLY="${2:?--only needs names}"; shift ;;
    --uninstall) UNINSTALL=1 ;;
    --dry-run) DRY=1 ;;
    -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
  shift
done

targets=()
if [[ -n "$PROJECT" ]]; then
  [[ $CLAUDE == 1 ]] && targets+=("$PROJECT/.claude/skills")
  [[ $CODEX == 1 ]] && targets+=("$PROJECT/.agents/skills")
else
  [[ $CLAUDE == 1 ]] && targets+=("$HOME/.claude/skills")
  [[ $CODEX == 1 ]] && targets+=("${CODEX_HOME:-$HOME/.codex}/skills")
fi

skills=()
for d in "$SRC"/gamedev-*/; do
  n="$(basename "$d")"
  if [[ -z "$ONLY" || ",$ONLY," == *",$n,"* ]]; then skills+=("$n"); fi
done
[[ ${#skills[@]} -gt 0 ]] || { echo "no skills matched" >&2; exit 1; }

run() { if [[ $DRY == 1 ]]; then echo "+ $*"; else "$@"; fi; }

for t in "${targets[@]}"; do
  run mkdir -p "$t"
  for n in "${skills[@]}"; do
    if [[ $UNINSTALL == 1 ]]; then
      [[ -d "$t/$n" ]] && run rm -rf "$t/$n"
    else
      run rm -rf "$t/$n"
      run cp -R "$SRC/$n" "$t/$n"
    fi
  done
  verb=$([[ $UNINSTALL == 1 ]] && echo removed || echo installed)
  echo "$verb ${#skills[@]} skills -> $t"
done
[[ $UNINSTALL == 1 ]] || echo "Restart Claude Code / Codex to load new skills."
