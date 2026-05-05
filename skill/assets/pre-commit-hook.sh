#!/usr/bin/env bash
# pre-commit hook: CLAUDE.md ↔ AGENTS.md 자동 sync

set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
SYNC_SCRIPT="$REPO_ROOT/scripts/sync-agents-md.sh"

if [[ ! -f "$SYNC_SCRIPT" ]]; then
    echo "[WARN] sync-agents-md.sh 를 찾을 수 없습니다. sync를 건너뜁니다." >&2
    exit 0
fi

if [[ ! -x "$SYNC_SCRIPT" ]]; then
    echo "[WARN] sync-agents-md.sh 에 실행 권한이 없습니다. sync를 건너뜁니다." >&2
    exit 0
fi

if ! "$SYNC_SCRIPT"; then
    echo "" >&2
    echo "[pre-commit] CLAUDE.md ↔ AGENTS.md sync 실패. 위 오류를 해결 후 다시 commit하세요." >&2
    exit 1
fi

exit 0
