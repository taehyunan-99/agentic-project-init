# {PROJECT_NAME} - {AGENT_NAMES} 작업 지침

{이 프로젝트의 핵심 의도 — 영역 라우팅 외에 LLM이 root에서 즉시 알아야 할 1문장.}

<!--
첫 줄 미션의 예:
- "운영 안전을 위해 production DB 직접 쓰기 금지. 모든 작업은 staging 검증 후."
- "API contract는 backend가 SoT. frontend·analysis는 그 정의를 따른다."
모호하면 placeholder 그대로 두어 사용자가 채울 자리를 명시한다.
-->

<!--
== Tradeoff 자리 (선택) ==
이 룰을 따르면 잃는 것/얻는 것을 한 줄로 명시한다. 본문에 노출되어야 LLM이 자동으로 함께 인지한다.
형식: `**Tradeoff**: {잃는 것} 포기 → {얻는 것}.`
예: `**Tradeoff**: 영역 경계가 모호한 작업은 두 가이드를 모두 읽어야 함 — 약간의 토큰 비용을 부담하는 대신 단일 거대 가이드의 lost-in-the-middle을 차단한다.`
해당 없으면 아래 한 줄을 통째로 삭제. (이 주석은 작성 안내이므로 채운 뒤 삭제 가능)
-->

**Tradeoff**: {잃는 것} 포기 → {얻는 것}.

<!--
이 파일은 map 역할을 한다. 작업 시 해당 영역의 {GUIDE_FILENAME}을 먼저 읽고 진행한다.

root에 모든 가이드를 몰아넣지 않고 영역별로 분리한 이유는 토큰 효율 + 컨텍스트 정확도다.
작업 영역만 정확히 참조하면 다른 영역 가이드가 컨텍스트를 오염시키지 않는다.
-->

<!--
디렉토리 트리(`ls`로 알 수 있는 정보)는 의도적으로 넣지 않는다.
영상의 G1 안티패턴("README 복붙형 설명") — 코드만 봐도 알 수 있는 내용을
가이드에 적으면 컨텍스트 토큰과 LLM 주의력을 낭비한다.
필요하면 사용자가 직접 추가하되, 기본 템플릿은 라우팅(map) 역할만 담는다.
-->

## 영역별 가이드

작업 영역에 해당하는 {GUIDE_FILENAME}을 먼저 읽고 진행한다.

{AREA_LIST}
<!-- 예시:
- **apps/frontend** — UI 작업 → [`apps/frontend/CLAUDE.md`](apps/frontend/CLAUDE.md)
- **apps/backend** — API 작업 → [`apps/backend/CLAUDE.md`](apps/backend/CLAUDE.md)
-->

## 영역 가이드의 구조

<!--
각 영역의 {GUIDE_FILENAME}은 다음 8섹션 템플릿을 따른다.
init은 가벼운 뼈대만 만든다 — WHAT/CONTENTS/WHERE/COMMANDS(빌드·테스트·린트)는 코드 스캔 기반 초안,
HOW/HOW NOT/WHY는 placeholder. 본격 작성은 베이스라인 완성 즈음 /update 인터뷰로 채운다.
-->

1. **WHAT** — 이 모듈이 무엇을 하는가 *(init에서 채움)*
2. **CONTENTS** — 디렉토리 맵 + 기술 스택 *(init에서 채움)*
3. **HOW** — 일반적인 수정은 어떻게 하는가 *(`/update` 인터뷰에서 채움)*
4. **HOW NOT** — 시스템을 깨뜨리는 비명백한 함정 *(`/update` 인터뷰에서 채움)*
5. **WHERE** — 다른 모듈과의 의존성 *(init에서 채움)*
6. **WHY** — 코드에 안 적힌 배경 지식 *(`/update` 인터뷰에서 채움)*
7. **COMMANDS** — 빌드/테스트/린트 + 영역 고유 명령어 가드 *(init은 빌드/테스트/린트만, 가드는 `/update`)*
8. **LEARNED CAUTIONS** — 별도 파일 `LEARNED_CAUTIONS.md`에 분리. `learn` 스킬이 누적

## 공통 명령어

<!--
모든 영역에 공통으로 적용되는 명령어. 영역별 명령어는 각 가이드의 7. COMMANDS 참고.
없으면 LLM이 추측해 잘못된 명령을 시도한다.
-->

- 빌드: `{예: npm run build}`
- 테스트: `{예: npm test -- --run}` <!-- watch 모드는 자동화에서 hang을 유발하므로 명시적으로 끈다 -->
- 린트: `{예: npm run lint:fix}`
- 타입체크: `{예: tsc --noEmit}`

**공통 명령어 가드** (모든 영역에 적용):
<!-- 영역 가이드에는 영역 고유 가드만 두고, 공통 가드는 여기에 모은다. -->

- {예: --no-verify 사용 금지 — pre-commit hook 우회로 broken state commit}
- {예: production DB 직접 쓰기 금지 — staging 검증 우회}
- {예: --force push 금지 — 공유 브랜치 히스토리 손실}

## 주의사항 학습 (learn 스킬)

<!--
작업 중 실수가 발견되면 다음 형태로 호출해 해당 영역 폴더의
LEARNED_CAUTIONS.md에 누적한다.
본문 가이드({GUIDE_FILENAME})는 8번 섹션에서 @./LEARNED_CAUTIONS.md를 참조하므로 자동 로드된다.
learn 스킬은 LEARNED_CAUTIONS.md만 갱신하고 본문 가이드는 절대 건드리지 않는다.
-->

- Claude Code/Cursor/Antigravity: `/learn <메모>` (인자 없이도 호출 가능)
- Codex: `$learn <메모>`

스킬 위치: {LEARN_SKILL_PATH}

<!--
== 분할 안내 ==
이 root map이 100줄을 넘기 시작하면 토픽별 파일로 분할한다.
예: 영역 수가 많아 라우팅 섹션이 비대해지면 영역 카테고리별로 묶어 `@./areas-frontend.md`,
`@./areas-backend.md`로 빼거나, 공통 규칙이 많아지면 `@./shared-conventions.md`로 분리.
Claude는 import된 파일을 자동으로 따라간다.
-->

