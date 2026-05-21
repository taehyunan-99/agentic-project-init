# Agentic Project Init

**[English](README.en.md) | 한국어**

AI 에이전틱 작업에 최적화된 프로젝트 구조를 자동으로 초기화하는 스킬입니다.

> 적용 가능 에이전트: Claude Code · Codex · Antigravity · Cursor

<br/><br/>

## TL;DR

- root에는 **map만**, 영역별 가이드는 **그 영역 폴더 안에** 둡니다.
- 에이전트가 작업 중인 영역의 가이드만 로드 → **컨텍스트 토큰 절약**.
- 코드만 봐선 알 수 없는 함정·배경을 **8섹션 템플릿(WHAT / CONTENTS / HOW / HOW NOT / WHERE / WHY / COMMANDS / LEARNED CAUTIONS)** 으로 명시합니다.
- init은 **가벼운 뼈대**만 만들고(WHAT/CONTENTS/WHERE/COMMANDS), 본격 작성은 베이스라인 완성 즈음 **`/update` 인터뷰**로 사용자와 함께 채워갑니다.
- 각 가이드는 **첫 줄에 미션 1문장**과 **Tradeoff 주석 블록**을 둬서 LLM이 룰의 의도와 비용을 함께 인지하게 합니다.
- LEARNED CAUTIONS는 **별도 파일(`LEARNED_CAUTIONS.md`)** 로 분리해 본문 가이드와 독립적으로 누적합니다. `/learn` 명령으로 한 줄씩 사후 누적, 본문 가이드는 절대 건드리지 않습니다.
- `/update --restructure`로 영역 경계 재구성도 가능 (사용자 확인을 거친 파일 이동 + 가이드 재배치).
- `/guide-audit` 명령으로 프로젝트 내 모든 가이드를 결정적 루브릭으로 채점합니다.

<br/><br/>

## 왜 이 구조인가

### 1. 단일 CLAUDE.md의 한계

일반적인 패턴은 프로젝트 루트에 `CLAUDE.md` 하나에 모든 가이드를 몰아넣는 것입니다.

문제점:

- **컨텍스트 비대** — frontend만 작업해도 backend·DB·infra 가이드가 모두 컨텍스트에 들어옵니다.
- **영역 간 정보 오염** — 에이전트가 다른 영역 룰을 현재 영역에 잘못 적용합니다.
- **파일이 길어질수록 후순위 룰이 무시됩니다** — LLM은 긴 문서의 중간/뒤쪽 지시를 흘려보내는 경향(lost-in-the-middle)이 있습니다.

<br/>

### 2. 코드만 봐선 알 수 없는 것이 사라집니다

README에 "이 디렉토리는 X 모듈입니다" 정도만 적혀 있으면 에이전트는:

- "왜 이 패턴인가"를 모르고 → 멋대로 리팩토링합니다.
- "이 함수를 건드리면 안 되는 진짜 이유"를 모르고 → 함부로 수정합니다.
- 도메인 용어, 과거 incident, 다른 길로 안 간 이유를 몰라 → 같은 실수를 반복합니다.

<br/><br/>

## 이 구조의 강점

### 1. Map + 영역 가이드 = 토큰 효율

| 패턴 | 컨텍스트에 들어가는 양 |
|------|----------------------|
| 단일 CLAUDE.md (예: 800줄) | 항상 800줄 전체 |
| Map(50줄) + 영역 가이드(150줄) | 50 + 150 = 200줄 |

대규모 프로젝트일수록 격차가 커집니다. 에이전트는 root map을 먼저 보고 작업 영역 한 곳의 가이드만 로드합니다.

<br/>

### 2. 8섹션 템플릿 = 코드 외 지식의 명시화

각 영역 가이드는 동일한 8섹션 구조입니다:

1. **WHAT** — 이 모듈은 무엇을 하는가 *(init에서 채움)*
2. **CONTENTS** — 파일/디렉토리와 기술 스택 *(init에서 채움)*
3. **HOW** — 일반적인 수정은 어떻게 하는가 *(`/update` 인터뷰에서 채움)*
4. **⛔ HOW NOT** — 시스템을 깨뜨리는 비명백한 함정 (이유 한 줄 필수) *(`/update` 인터뷰에서 채움)*
5. **WHERE** — 다른 모듈과의 의존성 *(init에서 채움)*
6. **WHY** — 코드에 안 적힌 배경 지식 *(`/update` 인터뷰에서 채움)*
7. **COMMANDS** — 빌드/테스트/린트 명령어 + 영역 고유 명령어 가드 *(init은 빌드/테스트만, 가드는 `/update`)*
8. **⚠️ LEARNED CAUTIONS** — 별도 파일 `LEARNED_CAUTIONS.md`로 분리. `learn` 스킬이 사후 누적.

특히 4(HOW NOT)와 6(WHY)는 **사람만 알 수 있는 지식**을 명시적으로 담는 자리이고, 7(COMMANDS)은 LLM이 명령어를 추측하지 못하게 막는 가드입니다.

`/update` 인터뷰가 채워야 할 슬롯은 init이 placeholder로 남겨두고, 본격 작성은 베이스라인 완성 즈음 시작합니다. 코드 추측만으로는 노이즈가 되는 영역이라 사용자 결정을 거쳐서만 채웁니다.

사람이 봐도 되는 작성 안내문은 HTML 주석으로 격리되어 자동 로드 시 토큰 비용 0입니다.

<br/>

### 3. 첫 줄 미션 + Tradeoff = 룰의 의도와 비용 인지

각 영역 가이드의 헤딩 바로 아래에는 두 자리가 있습니다:

```markdown
# Frontend 작업 가이드

백엔드 API 컨트랙트와 도메인 변수명에서의 schema drift를 막는다. 추측·`any`·임의 변경 금지.

**Tradeoff**: contract를 backend SoT로 고정 → frontend 단독 진화의 자유를 포기하는 대신 422/500을 컴파일 타임으로 옮긴다.
```

- **첫 줄 미션**: LLM이 이 영역의 **본질적 목적**을 즉시 인지. "이 영역이 무엇을 막는가"를 한 문장으로.
- **Tradeoff**: 이 룰이 무엇을 포기하고 무엇을 얻는지 명시. 본문에 노출해 LLM이 영역 진입 시 자동으로 함께 인지하게 합니다 — 경계 케이스에서 룰의 본질을 놓치지 않는 핵심 장치입니다.

<br/>

### 4. /learn 누적 = 같은 실수 두 번 안 함

작업 중 잘못된 가정으로 실수가 발생하면:

```
/learn DB 마이그레이션 시 alembic 버전 미반영 → staging에서 컬럼 누락
```

해당 영역 폴더의 `LEARNED_CAUTIONS.md`에 한 줄 추가됩니다. 본문 가이드의 8번 섹션이 이 파일을 `@./LEARNED_CAUTIONS.md`로 참조하므로 자동 로드되고, `learn`은 본문 가이드를 절대 수정하지 않습니다. 사용자가 직접 작성한 부분과 누적분이 한 파일에 섞이지 않아 보존 규칙도 명확해집니다.

다음 세션부터 에이전트가 같은 실수를 안 합니다.

<br/>

### 5. /update 인터뷰 = 코드에 맞춰 가이드를 같이 키운다

베이스라인이 잡힌 뒤 `/update`를 실행하면, 영역마다 다음 9가지 질문 유형으로 사용자와 인터뷰합니다:

1. 변경 사실 확인 (파일·엔드포인트 추가/삭제)
2. 삭제·이전 확인
3. 외부 의존성 변화
4. 컨벤션 합의 (혼재 패턴 발견 시)
5. 안티패턴 예측 (HOW NOT 후보 제시)
6. 암묵지 추출 (특이 선택의 이유)
7. 드리프트 감지 (기존 HOW vs 실제 코드)
8. 신규 LEARNED CAUTIONS 후보 (fix 클러스터 등)
9. 영역 경계 재검토 (의견 제시만 — 결정은 `/update --restructure`)

각 제안은 **근거 한 줄**(커밋 ID, 파일 위치, 발견 횟수)을 함께 보여줘서 잘 모르는 영역도 판단할 수 있습니다. 인터뷰가 끝나면 영역 간 가이드 충돌 6종(컨벤션 모순 / WHERE 중복 / HOW NOT vs HOW / 용어 불일치 / 의존 방향 / COMMANDS)을 검사하고, **충돌이 미해소면 update 자체가 미완료**로 표시됩니다. 다음 `/update`가 그 충돌부터 다시 묻습니다.

**사용자 결정 사항은 자동 덮어쓰지 않습니다.** 변경이 필요하면 반드시 확인을 받고, 이전 결정은 변경 이력 주석으로 보존합니다.

<br/>

### 6. /update --restructure = 영역 경계 재구성

영역이 비대해지거나 책임이 섞이면 `/update --restructure <영역>`으로 영역 자체를 다시 그릴 수 있습니다.

- 책임 카테고리 추출 → 분할/병합 옵션 → 파일 이동 계획 → **LEARNED_CAUTIONS 항목 이전 (항목별 사용자 결정)** → 본문 가이드 8섹션 재배치 → 외부 강결합 `@import` 재연결 → 단계별 검증
- 한 번에 한 영역만, 자동 커밋 없음, 사용자 승인 전엔 파일 이동 0건.
- 사용자가 누적한 LEARNED_CAUTIONS는 AI가 임의 분류하지 않고 항목별로 어디로 갈지 결정합니다.

<br/>

### 7. /guide-audit 결정적 채점 = 품질 회귀 방지

`/guide-audit` 명령으로 프로젝트 내 모든 가이드를 100점 만점 루브릭으로 채점합니다. 패턴 매칭 기반이라 같은 입력 → 같은 점수.

- 7개 카테고리(A~H) + 트리 일관성(T) + 안티패턴(G) 통합 채점
- 파일별 점수 + 카테고리별 breakdown + 0점 항목 evidence + Top 개선 추천
- `@import` redirect 파일 자동 인식 (`@./AGENTS.md` 한 줄짜리 `CLAUDE.md`는 import 대상 점수 차용)

채점 결과는 콘솔에만 출력되며 가이드 파일을 수정하지 않습니다 (읽기 전용).

<br/>

### 8. 멀티 에이전트 협업

한 프로젝트에서 팀원들이 서로 다른 에이전트(Claude Code, Codex 등)를 써도 동일한 가이드를 봅니다.

- `both` 모드 → root와 모든 영역 폴더에서 `AGENTS.md`를 본문으로 두고 `CLAUDE.md`는 `@./AGENTS.md` 한 줄로 import.
- 단일 파일만 편집하므로 sync drift가 구조적으로 불가능합니다. 외부 스크립트/hook 불필요.

<br/><br/>

## 정량 효과

### 검증 질문

> 동일 코드·동일 AI 모델·동일 작업에서 **문서 구조 하나만** 바꾸면 AI 에이전트의 토큰 비용이 어떻게 변하나?

<br/>

### 실험 셋업

- **대상**: 규모가 다른 실제 프로젝트 3개 — A(소) / B(중) / C(대, 다영역 시스템)
- **비교**: 가이드 없음(코드만) vs 구조 적용(영역 맵 + 8섹션 가이드)
- **작업**: 난이도 상승 5단계 시나리오 (전체 파악 → 다영역 통합 변경 계획)
- **지표**: 토큰 합계 (= AI 작업 비용)
- **통제**: 서브에이전트 0, 되묻기 차단, git 격리, 글자 단위 동일 프롬프트, 측정 세션 ≠ 집계 세션

<br/>

### 결과: 구조가 토큰 비용을 줄인다

| | 프로젝트 A (소) | 프로젝트 B (중) | 프로젝트 C (대) |
|---|--:|--:|--:|
| 토큰 (가이드 없음 → 구조 적용) | 744k → 701k | 2,222k → 1,489k | 4,720k → 2,780k |
| **토큰 절감** | **+6%** | **+33%** | **+41%** |

확정된 것:

1. **구조 적용이 가이드 없음보다 토큰을 적게 쓴다** — 3개 프로젝트 일관.
2. **효과는 규모에 비례** — 소규모 +6% → 대규모 +41%.

> **문서 구조의 가치는 비용에 있다. 크고 복잡한 프로젝트일수록 토큰을 더 크게 절감한다.**

<br/>

> ⚠️ 한계: 3개 프로젝트로 일반화는 제한적입니다. 단 "규모↑ → 구조 효과↑"는 일관 관찰되며, 영역 수·작업 종류·codebase 크기에 따라 절감폭은 달라질 수 있습니다.

<br/><br/>

## 에이전트별 호환성

| 에이전트 | 메모리 파일 | User-level 스킬 위치 |
|---------|------------|---------------------|
| Claude Code | `CLAUDE.md` | `~/.claude/skills/` |
| Codex | `AGENTS.md` | `~/.agents/skills/` |
| Antigravity | `AGENTS.md` 또는 `GEMINI.md` | `~/.gemini/antigravity/skills/` |
| Cursor | `AGENTS.md` 또는 `.cursor/rules/` | `~/.cursor/skills/` |

각 경로는 공식 docs 기준입니다 ([Claude Code](https://code.claude.com/docs/en/skills.md) · [Codex](https://developers.openai.com/codex/skills) · [Antigravity](https://antigravity.google/docs/skills) · [Cursor](https://cursor.com/docs/skills)).

<br/>

### `/learn` 호출 방식

| 에이전트 | 호출 |
|---------|------|
| Claude Code / Cursor / Antigravity | `/learn` (또는 `/learn <메모>`) |
| Codex | `$learn` (또는 `$learn <메모>`) |

→ Codex는 사용자 정의 호출이 `$` 접두사이므로 다른 에이전트와 다릅니다. 그 외 동작은 동일합니다.
누적 대상은 **현재 작업 영역의 `LEARNED_CAUTIONS.md`** 한 파일이며 본문 가이드는 수정하지 않습니다.

<br/>

### `/update` 호출 방식

| 호출 | 동작 |
|------|------|
| `/update` | 전 영역 일반 갱신 (9개 질문 유형 인터뷰 + 6개 충돌 검증) |
| `/update <영역경로>` | 특정 영역만 갱신 |
| `/update --restructure [영역]` | 영역 경계 재구성 별도 흐름 (파일 이동 + 가이드 재배치 + LEARNED 항목 이전) |

→ Codex에서는 `$update` 형식. **언제 실행하면 좋은가**:

- 베이스라인 완성 직후 — 가이드 본격 채우기 시작
- 주요 기능 추가 후 — 새 패턴이 컨벤션이 될지 결정
- 버그 fix 클러스터 발생 후 — 반복 실수를 `LEARNED_CAUTIONS.md`에 박제
- 외부 의존성 교체 후 — HOW/COMMANDS 갱신
- 온보딩·릴리즈 직전 — 가이드 최신성 보장

권장 주기는 월 1회 또는 위 신호 발생 시. 대규모 리팩터링 진행 중에는 피하고 완료 후 실행하세요.

<br/>

### `/guide-audit` 호출 방식

| 호출 | 동작 |
|------|------|
| `/guide-audit` | 현재 프로젝트의 모든 가이드 통합 채점 |
| `/guide-audit <경로>` | 디렉토리면 프로젝트 채점, `.md` 파일이면 단일 파일 채점 |

→ Codex에서는 `$guide-audit`. 채점 결과는 콘솔에만 출력되며 파일을 만들지 않습니다.

`/learn`과 동일하게 프로젝트의 `.claude/skills/guide-audit/` (또는 `.agents/skills/guide-audit/`)에 함께 설치됩니다. 내부적으로 `score_guide.py` (Python 3, 표준 라이브러리만 사용)가 `rubric-schema.json`을 읽어 결정적 채점합니다.

<br/><br/>

## 설치

**한 번 user-level에 설치하면 모든 프로젝트에서 `/agentic-project-init`로 호출할 수 있습니다.** 호출 시 그 시점의 작업 디렉토리에 구조를 생성하므로, 프로젝트마다 따로 설치할 필요가 없습니다.

본인이 사용하는 에이전트 한 줄만 실행하세요.

<br/>

### Linux / macOS

> 재설치 시 안전하도록 기존 설치를 먼저 삭제합니다 (`rm -rf <대상>`).

**Claude Code**:
```bash
rm -rf /tmp/api ~/.claude/skills/agentic-project-init && git clone https://github.com/taehyunan-99/agentic-project-init /tmp/api && mkdir -p ~/.claude/skills && cp -r /tmp/api/skill ~/.claude/skills/agentic-project-init && rm -rf /tmp/api
```

**Codex**:
```bash
rm -rf /tmp/api ~/.agents/skills/agentic-project-init && git clone https://github.com/taehyunan-99/agentic-project-init /tmp/api && mkdir -p ~/.agents/skills && cp -r /tmp/api/skill ~/.agents/skills/agentic-project-init && rm -rf /tmp/api
```

**Antigravity**:
```bash
rm -rf /tmp/api ~/.gemini/antigravity/skills/agentic-project-init && git clone https://github.com/taehyunan-99/agentic-project-init /tmp/api && mkdir -p ~/.gemini/antigravity/skills && cp -r /tmp/api/skill ~/.gemini/antigravity/skills/agentic-project-init && rm -rf /tmp/api
```

**Cursor**:
```bash
rm -rf /tmp/api ~/.cursor/skills/agentic-project-init && git clone https://github.com/taehyunan-99/agentic-project-init /tmp/api && mkdir -p ~/.cursor/skills && cp -r /tmp/api/skill ~/.cursor/skills/agentic-project-init && rm -rf /tmp/api
```

<br/>

### Windows (PowerShell)

**Claude Code**:
```powershell
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $env:TEMP\api, "$env:USERPROFILE\.claude\skills\agentic-project-init"; git clone https://github.com/taehyunan-99/agentic-project-init $env:TEMP\api; New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills"; Copy-Item -Recurse $env:TEMP\api\skill "$env:USERPROFILE\.claude\skills\agentic-project-init"; Remove-Item -Recurse -Force $env:TEMP\api
```

**Codex**:
```powershell
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $env:TEMP\api, "$env:USERPROFILE\.agents\skills\agentic-project-init"; git clone https://github.com/taehyunan-99/agentic-project-init $env:TEMP\api; New-Item -ItemType Directory -Force "$env:USERPROFILE\.agents\skills"; Copy-Item -Recurse $env:TEMP\api\skill "$env:USERPROFILE\.agents\skills\agentic-project-init"; Remove-Item -Recurse -Force $env:TEMP\api
```

**Antigravity**:
```powershell
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $env:TEMP\api, "$env:USERPROFILE\.gemini\antigravity\skills\agentic-project-init"; git clone https://github.com/taehyunan-99/agentic-project-init $env:TEMP\api; New-Item -ItemType Directory -Force "$env:USERPROFILE\.gemini\antigravity\skills"; Copy-Item -Recurse $env:TEMP\api\skill "$env:USERPROFILE\.gemini\antigravity\skills\agentic-project-init"; Remove-Item -Recurse -Force $env:TEMP\api
```

**Cursor**:
```powershell
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $env:TEMP\api, "$env:USERPROFILE\.cursor\skills\agentic-project-init"; git clone https://github.com/taehyunan-99/agentic-project-init $env:TEMP\api; New-Item -ItemType Directory -Force "$env:USERPROFILE\.cursor\skills"; Copy-Item -Recurse $env:TEMP\api\skill "$env:USERPROFILE\.cursor\skills\agentic-project-init"; Remove-Item -Recurse -Force $env:TEMP\api
```

<br/><br/>

## 사용

설치 후 에이전트의 슬래시 명령으로 호출합니다.

```
/agentic-project-init           # 인자 없음 → 어떤 환경인지 사용자에게 묻고 대기
/agentic-project-init claude    # Claude Code용 (CLAUDE.md)
/agentic-project-init agents    # Codex / Antigravity / Cursor용 (AGENTS.md)
/agentic-project-init both      # AGENTS.md 본문 + CLAUDE.md = @./AGENTS.md (단일 진실 공급원)
```

<br/>

### 인자별 산출물

| 인자 | 본문 파일 | 호환 파일 |
|------|-----------|-----------|
| `claude` | `CLAUDE.md` + 영역별 `LEARNED_CAUTIONS.md` + `.claude/skills/` (`learn`/`update`/`guide-audit`) | — |
| `agents` | `AGENTS.md` + 영역별 `LEARNED_CAUTIONS.md` + `.agents/skills/` (동일 3개) + `.agents/workflows/` | — |
| `both` | `AGENTS.md` (모든 위치) + 영역별 `LEARNED_CAUTIONS.md` + `.claude/skills/` + `.agents/skills/` + `.agents/workflows/` | `CLAUDE.md` = `@./AGENTS.md` 한 줄 |
| (없음) | 위 3개 중 어느 환경인지 사용자에게 묻고 대기합니다 | — |

`both` 모드는 본문을 `AGENTS.md` 한 파일에만 둡니다. Claude Code는 `CLAUDE.md`의 `@./AGENTS.md` import를 자동 따라가 같은 본문을 봅니다. 단일 파일만 편집하므로 sync drift가 구조적으로 불가능합니다.

영역별 `LEARNED_CAUTIONS.md`는 본문 가이드의 8번 섹션에서 `@./LEARNED_CAUTIONS.md`로 자동 import되며, Codex 등 `@` 미지원 환경을 위한 마크다운 링크 fallback도 함께 들어갑니다.

<br/>

### 동작 흐름 (스킬이 하는 일)

1. 인자 파싱 → 모드 확정 (인자 없으면 사용자에게 환경 질문)
2. git 리포 검증 (필수 아님 — 없어도 진행)
3. 기존 파일 충돌 검사 (있으면 사용자 확인 후 백업 또는 덮어쓰기)
4. 영역 자동 탐지 (`apps/`, `frontend`, `backend`, `database`, ...) → 사용자 검토
5. 영역별 가이드 **가벼운 뼈대** 작성 — WHAT/CONTENTS/WHERE/COMMANDS는 코드 스캔 기반 초안, HOW/HOW NOT/WHY는 placeholder (`/update`에서 채움) → 사용자 승인
6. 파일 생성 (root map + 영역 가이드 + 영역별 `LEARNED_CAUTIONS.md` placeholder + `learn`/`update`/`guide-audit` 스킬). Both 모드면 `CLAUDE.md`는 `@./AGENTS.md` 한 줄짜리 import 파일로 생성
7. 스킬 설치 자가 검증(`learn`/`update`/`guide-audit` 경로 + 영역별 `LEARNED_CAUTIONS.md` 존재 확인, 누락 시 6단계 재실행) → 마무리 안내 + 베이스라인 완성 즈음 `/update` 시작 권장

<br/><br/>

## FAQ

**Q. CLAUDE.md 하나로 충분한 작은 프로젝트인데도 써야 하나요?**

영역이 1개면 효과가 적습니다. 2~3개부터 의미가 있고 5개 이상에서 진가가 드러납니다.

**Q. 기존 CLAUDE.md가 있는데 덮어써지나요?**

검출 시 백업 옵션을 제공합니다. 사용자 확인 전에는 덮어쓰지 않습니다.

**Q. 한 프로젝트에 Claude Code 사용자와 Codex 사용자가 섞여 있다면?**

`both` 모드로 생성하세요. `AGENTS.md`가 단일 진실 공급원이 되고 `CLAUDE.md`는 `@./AGENTS.md` import로 자동 동기화됩니다.

**Q. `/learn`은 어떻게 동작하나요?**

현재 작업 영역을 추론해 그 영역 폴더의 `LEARNED_CAUTIONS.md`에 한 줄 추가합니다. 본문 가이드(`AGENTS.md`/`CLAUDE.md`)는 절대 수정하지 않습니다 — 본문은 8번 섹션에서 `@./LEARNED_CAUTIONS.md`를 참조하므로 자동 로드됩니다. 영역이 모호하면 사용자에게 확인합니다.

호출은 에이전트별로 다릅니다 — Claude Code/Cursor/Antigravity는 `/learn`, Codex는 `$learn`. 인자 없이 호출하면 최근 대화에서 잘못된 내용을 자동 추출합니다.

**Q. `/update`는 언제 실행하나요?**

init은 가벼운 뼈대만 만들기 때문에, 베이스라인이 완성되어 패턴이 잡힐 즈음 처음 실행합니다. 이후 주요 기능 추가/외부 의존성 교체/버그 fix 클러스터/온보딩 직전에 갱신하면 됩니다. 인터뷰는 영역별로 묶여 제시되고 각 제안에 근거(커밋 ID, 파일 위치)가 붙어 잘 모르는 영역도 판단 가능합니다. 사용자가 결정한 내용은 자동 덮어쓰지 않으며, 영역 간 충돌이 미해소면 update 자체가 미완료로 표시됩니다.

**Q. `/update --restructure`는 무엇이 다른가요?**

일반 `/update`는 가이드 내용만 갱신하지만, `--restructure`는 영역 자체를 분할/병합/이름 변경/삭제합니다. 파일 이동·가이드 재배치·`LEARNED_CAUTIONS` 항목 이전·외부 강결합 `@import` 재연결까지 모두 포함하되 모든 단계가 사용자 확인을 거칩니다. 한 번에 한 영역만 처리하며, 자동 커밋 없이 git diff로 검토 후 사용자가 직접 커밋합니다.

**Q. `/guide-audit`는 가이드를 수정하나요?**

아니요. 읽기 전용입니다. 채점 결과만 콘솔에 출력하고 개선 추천을 보여줍니다. 적용 여부는 사용자가 결정합니다.
