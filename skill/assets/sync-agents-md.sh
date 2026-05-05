#!/usr/bin/env bash
# CLAUDE.md ↔ AGENTS.md 양방향 sync 스크립트
# git staging 상태 기준으로 판단 (mtime 불사용)

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# 대상 폴더 목록 (root는 빈 문자열)
# 스킬 사용 시 이 배열을 실제 영역 경로로 치환한다.
DIRS=(
    ""
    # __AREAS_PLACEHOLDER__
)

# 파일이 staged 상태인지 판단
file_is_staged() {
    local file="$1"
    git diff --cached --name-only 2>/dev/null | grep -qxF "$file"
}

CONFLICT_FOUND=0

for DIR in "${DIRS[@]}"; do
    if [[ -z "$DIR" ]]; then
        CLAUDE="CLAUDE.md"
        AGENTS="AGENTS.md"
        LABEL="root"
    else
        CLAUDE="$DIR/CLAUDE.md"
        AGENTS="$DIR/AGENTS.md"
        LABEL="$DIR"
    fi

    # 둘 다 없으면 건너뜀
    if [[ ! -f "$CLAUDE" && ! -f "$AGENTS" ]]; then
        continue
    fi

    # 한쪽 누락 처리: 존재하는 쪽으로 복원 + git add
    if [[ ! -f "$CLAUDE" && -f "$AGENTS" ]]; then
        echo "[SYNC] $LABEL: CLAUDE.md 누락 → AGENTS.md에서 복원"
        cp "$AGENTS" "$CLAUDE"
        git add "$CLAUDE"
        continue
    fi

    if [[ -f "$CLAUDE" && ! -f "$AGENTS" ]]; then
        echo "[SYNC] $LABEL: AGENTS.md 누락 → CLAUDE.md에서 복원"
        cp "$CLAUDE" "$AGENTS"
        git add "$AGENTS"
        continue
    fi

    # 이하 둘 다 존재
    CLAUDE_STAGED=0
    AGENTS_STAGED=0
    file_is_staged "$CLAUDE" && CLAUDE_STAGED=1 || true
    file_is_staged "$AGENTS" && AGENTS_STAGED=1 || true

    # Case A: CLAUDE.md만 staged → CLAUDE.md → AGENTS.md
    if [[ $CLAUDE_STAGED -eq 1 && $AGENTS_STAGED -eq 0 ]]; then
        echo "[SYNC] $LABEL: CLAUDE.md staged → AGENTS.md 동기화"
        cp "$CLAUDE" "$AGENTS"
        git add "$AGENTS"
        continue
    fi

    # Case B: AGENTS.md만 staged → AGENTS.md → CLAUDE.md
    if [[ $CLAUDE_STAGED -eq 0 && $AGENTS_STAGED -eq 1 ]]; then
        echo "[SYNC] $LABEL: AGENTS.md staged → CLAUDE.md 동기화"
        cp "$AGENTS" "$CLAUDE"
        git add "$CLAUDE"
        continue
    fi

    # Case C: 둘 다 staged + 내용 다름 → 충돌
    if [[ $CLAUDE_STAGED -eq 1 && $AGENTS_STAGED -eq 1 ]]; then
        if ! cmp -s "$CLAUDE" "$AGENTS"; then
            echo ""
            echo "[ERROR] 충돌: $CLAUDE ↔ $AGENTS"
            echo ""
            echo "  두 파일이 다릅니다. 차이:"
            echo "  ----- diff -----"
            diff -u "$CLAUDE" "$AGENTS" || true
            echo "  ----------------"
            echo ""
            echo "  해결 방법:"
            echo "  1) 살릴 쪽을 결정하고 다른 쪽을 덮어쓰세요:"
            echo "     cp $CLAUDE $AGENTS   # CLAUDE.md 채택 시"
            echo "     또는"
            echo "     cp $AGENTS $CLAUDE   # AGENTS.md 채택 시"
            echo "  2) 변경된 파일을 stage 후 다시 commit:"
            echo "     git add $CLAUDE $AGENTS"
            echo "     git commit"
            echo ""
            CONFLICT_FOUND=1
        else
            echo "[SYNC] $LABEL: 둘 다 staged, 내용 동일 → OK"
        fi
        continue
    fi

    # Case D: 둘 다 unstaged + 내용 다름 → 충돌
    if [[ $CLAUDE_STAGED -eq 0 && $AGENTS_STAGED -eq 0 ]]; then
        if ! cmp -s "$CLAUDE" "$AGENTS"; then
            echo ""
            echo "[ERROR] 충돌: $CLAUDE ↔ $AGENTS"
            echo ""
            echo "  두 파일이 다릅니다. 차이:"
            echo "  ----- diff -----"
            diff -u "$CLAUDE" "$AGENTS" || true
            echo "  ----------------"
            echo ""
            echo "  한쪽을 살릴 방향으로 동기화 후 stage 하세요."
            echo ""
            CONFLICT_FOUND=1
        fi
        continue
    fi

done

if [[ $CONFLICT_FOUND -eq 1 ]]; then
    exit 1
fi

exit 0
