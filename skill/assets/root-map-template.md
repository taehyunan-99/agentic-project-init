# {PROJECT_NAME} - {AGENT_NAMES} 작업 지침

<!--
이 파일은 map 역할을 한다. 작업 시 해당 영역의 {GUIDE_FILENAME}을 먼저 읽고 진행한다.

root에 모든 가이드를 몰아넣지 않고 영역별로 분리한 이유는 토큰 효율 + 컨텍스트 정확도다.
작업 영역만 정확히 참조하면 다른 영역 가이드가 컨텍스트를 오염시키지 않는다.
-->

## 프로젝트 구조

```
{PROJECT_TREE}
```

## 영역별 가이드

작업 영역에 해당하는 {GUIDE_FILENAME}을 먼저 읽고 진행한다.

{AREA_LIST}
<!-- 예시:
- **apps/frontend** — UI 작업 → [`apps/frontend/CLAUDE.md`](apps/frontend/CLAUDE.md)
- **apps/backend** — API 작업 → [`apps/backend/CLAUDE.md`](apps/backend/CLAUDE.md)
-->

## 영역 가이드의 구조

<!-- 각 영역의 {GUIDE_FILENAME}은 다음 8섹션 템플릿을 따른다. -->

1. **WHAT** — 이 모듈이 무엇을 하는가
2. **CONTENTS** — 디렉토리 맵 + 기술 스택
3. **HOW** — 일반적인 수정은 어떻게 하는가
4. **HOW NOT** — 시스템을 깨뜨리는 비명백한 함정
5. **WHERE** — 다른 모듈과의 의존성
6. **WHY** — 코드에 안 적힌 배경 지식
7. **COMMANDS** — 빌드/테스트/린트 명령어
8. **LEARNED CAUTIONS** — `learn` 스킬로 누적

## 공통 명령어

<!--
모든 영역에 공통으로 적용되는 명령어. 영역별 명령어는 각 가이드의 7. COMMANDS 참고.
없으면 LLM이 추측해 잘못된 명령을 시도한다.
-->

- 빌드: `{예: npm run build}`
- 테스트: `{예: npm test -- --run}` <!-- watch 모드는 자동화에서 hang을 유발하므로 명시적으로 끈다 -->
- 린트: `{예: npm run lint:fix}`
- 타입체크: `{예: tsc --noEmit}`

**명령어 가드**:
- {예: --no-verify 사용 금지 — pre-commit hook 우회로 broken state commit}

## 주의사항 학습 (learn 스킬)

<!--
작업 중 실수가 발견되면 다음 형태로 호출해 해당 영역 {GUIDE_FILENAME}의
"⚠️ LEARNED CAUTIONS" 섹션에 누적한다.
-->

- Claude Code/Cursor/Antigravity: `/learn <메모>` (인자 없이도 호출 가능)
- Codex: `$learn <메모>`

스킬 위치: {LEARN_SKILL_PATH}
