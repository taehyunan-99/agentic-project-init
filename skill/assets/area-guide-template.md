# {AREA_NAME} 작업 가이드

{이 영역에서 LLM이 가장 자주 틀리는 무엇을 막는가 — 1문장. 첫 줄에 명확한 목적.}

<!--
첫 줄 미션의 예:
- "WebSocket 메시지의 contract 깨짐을 막기 위해 schema는 backend SoT를 따른다."
- "Airflow DAG의 멱등성 위반(같은 데이터 두 번 적재)을 막는다."
모호하면 비워두지 말고 placeholder 그대로 두어 사용자가 채울 자리를 명시한다.
-->

<!--
== Tradeoff 자리 (선택) ==
이 룰을 따르면 잃는 것/얻는 것을 한 줄로 명시한다. 본문에 노출되어야 LLM이 영역 진입 시 자동으로 함께 인지한다.
형식: `**Tradeoff**: {잃는 것} 포기 → {얻는 것}.`
예: `**Tradeoff**: schema 변경 시 frontend·backend 두 PR 필요 — 작은 변경의 편의를 포기하는 대신 contract 깨짐을 차단한다.`
해당 없으면 아래 한 줄을 통째로 삭제. (이 주석은 작성 안내이므로 채운 뒤 삭제 가능)
-->

**Tradeoff**: {잃는 것} 포기 → {얻는 것}.

<!--
== init 시점 안내 ==
이 템플릿은 init 단계에서는 **가벼운 뼈대**로 채워진다.
- 사실 기반 섹션(WHAT / CONTENTS / WHERE)은 코드 스캔으로 초안 작성.
- COMMANDS는 package.json / Makefile 등에서 추출 가능한 빌드·테스트·린트만 init에서 채우고, 영역 고유 가드는 update에서 추가한다.
- 판단·암묵지 섹션(HOW / HOW NOT / WHY)은 placeholder만 두고 update 인터뷰에서 채운다.
- LEARNED CAUTIONS는 별도 파일(LEARNED_CAUTIONS.md)로 분리되어 learn 스킬이 누적한다.

코드만 읽어선 알 수 없는 의도/함정/배경은 update가 사용자와 인터뷰하며 채운다.
-->

## 1. WHAT — 이 모듈은 무엇을 하는가
<!-- 1-3문장. 시스템 안에서의 역할과 책임. "이 영역이 없어지면 무엇이 안 되는가"로 검증. init에서 코드 스캔 기반 초안 작성. -->

{이 영역이 시스템에서 담당하는 역할 한 줄}

## 2. CONTENTS — 파일/디렉토리와 기술 스택
<!-- 1-depth 파일 목록 + 추론된 스택. update가 자동 갱신하는 사실 기반 섹션. -->

- `{경로}` — {역할}
- `{경로}` — {역할}

기술 스택: {예: React, TypeScript, Vite}

## 3. HOW — 일반적인 수정은 어떻게 하는가
<!--
이 영역에서 변경할 때 따르는 패턴/관례.
init에서는 placeholder. update 인터뷰("컨벤션 합의" 유형)에서 사용자와 합의하며 채운다.
- 어느 레이어부터 손대는가
- 어느 파일을 항상 함께 갱신하는가 (예: schema 변경 시 ERD도)
- 테스트는 어디에 추가하는가
- 새 기능 추가 시 따라야 할 디렉토리 규칙
-->

_(update 스킬에서 채워질 자리. 작업 중 패턴이 정립되면 `/update`로 인터뷰 진행)_

## 4. ⛔ HOW NOT — 시스템을 깨뜨리는 비명백한 함정 (중요)
<!--
코드를 봐도 명확하지 않지만 어기면 시스템이 깨지는 규칙.
init에서는 placeholder. update 인터뷰("안티패턴 예측" 유형)에서 코드 스캔 기반 제안 + 사용자 검토로 채운다.
항목마다 "왜 안 되는지" 한 줄을 함께 쓴다 — 이유가 없으면 LLM이 룰을 무시한다.
-->

_(update 스킬에서 채워질 자리. 사용자 결정 사항이므로 init은 비워둔다)_

## 5. WHERE — 다른 모듈과의 의존성

<!--
의존성을 결합 강도에 따라 두 가지로 표현한다 (자세한 결정 기준: `references/rubric.md`의 "@import 최소주의").

1. 강결합 (API contract / schema SoT) — `@<상대경로>` 한 줄 import.
   영역 진입 후 자동으로 함께 로드되어 침묵의 가정을 방지한다.
   "한쪽 변경 = 다른쪽 즉시 깨짐" 케이스에만 사용.

2. 약결합 (호출 관계·도메인 공유·운영 시점 참고) — 마크다운 링크 + 한 줄 설명.
   작업 시점에만 따라가 본다.

경계가 모호하면 약결합(마크다운 링크)이 기본값.
init에서는 디렉토리 의존성으로 추정 가능한 만큼 초안 작성. 강결합 판단은 사용자 확인.
-->

<!-- 강결합 — 자동 import (해당 시 한두 줄) -->
@../{other-area}/{가이드 파일명}

- **의존**: {예: [`apps/backend/CLAUDE.md`](../backend/CLAUDE.md)의 `/api/users` 엔드포인트}
- **피의존**: {예: [`apps/admin/CLAUDE.md`](../admin/CLAUDE.md)의 권한 체크 미들웨어}
- **경계 / 어댑터**: {외부 시스템·다른 영역과 닿는 지점, 컨트랙트 위치}

## 6. WHY — 코드에 안 적힌 배경 지식
<!--
도메인 지식, 과거 결정의 맥락, "왜 이렇게 짰는지". 코드만 봐선 절대 모르는 것.
init에서는 placeholder. update 인터뷰("암묵지 추출" 유형)에서 사용자에게 질문하며 채운다.
`learn` 스킬(`/learn` 또는 Codex의 `$learn`)로 LEARNED_CAUTIONS.md에도 누적 가능.
-->

_(update 스킬에서 채워질 자리. 사용자 결정 사항이므로 init은 비워둔다)_

## 7. COMMANDS — 빌드/테스트/린트
<!--
이 영역에서 자주 쓰는 명령어. 코드블록 또는 inline code로 명시.
init에서는 package.json/Makefile 등에서 추출 가능한 만큼만. 영역 고유 가드는 update에서 채운다.

== 가드 분리 원칙 ==
- root map의 "공통 명령어 가드"와 중복되는 가드는 여기에 다시 적지 않는다 (T3 중복 안티패턴).
- 이 영역에서만 적용되는 가드만 영역 가이드에 둔다.
- 모호하면 root에 두고 영역에서는 생략한다.
-->

_(init은 코드에서 추출 가능한 빌드/테스트/린트 명령만 채운다. 영역 고유 가드는 update에서 추가)_

## 8. ⚠️ LEARNED CAUTIONS — 학습된 주의사항
<!--
누적된 주의사항은 별도 파일에 보관됩니다.
- Claude Code / Cursor / Gemini-Antigravity: 아래 @ 참조가 자동 로드됩니다.
- OpenAI Codex 등 미지원 환경: 아래 링크를 직접 열어 확인하세요.

`learn` 스킬(`/learn` 또는 Codex의 `$learn`)은 LEARNED_CAUTIONS.md에만 항목을 추가하며,
이 본문 파일은 절대 수정하지 않습니다. update 스킬도 LEARNED_CAUTIONS.md를 자동 덮어쓰지 않습니다.
-->

@./LEARNED_CAUTIONS.md

자세한 내용은 [LEARNED_CAUTIONS.md](./LEARNED_CAUTIONS.md) 참조.

<!--
== 분할 안내 ==
이 파일이 100줄을 넘기 시작하면 영상 권고에 따라 토픽별 파일로 분할한다.
예: 컨벤션이 길어졌다면 `@./conventions.md`, 도메인 용어가 많아졌다면 `@./glossary.md`로 빼고
이 파일에서 `@./conventions.md` 한 줄로 import. Claude는 import된 파일을 자동으로 따라간다.
분할 후에도 본문이 100줄 이하로 유지되면 D3 + D4 양쪽 만점.
-->
