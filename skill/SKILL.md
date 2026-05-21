---
name: agentic-project-init
description: 임의 프로젝트 폴더를 AI 에이전틱 작업에 최적화된 구조로 초기화한다. root에 영역 map을 두고 각 영역마다 8섹션 작업 가이드(WHAT/CONTENTS/HOW/HOW NOT/WHERE/WHY/COMMANDS/LEARNED CAUTIONS)의 **가벼운 뼈대**를 생성한다 — init은 코드 스캔으로 추출 가능한 사실 기반 섹션(WHAT/CONTENTS/WHERE/COMMANDS)만 채우고 판단·암묵지 섹션(HOW/HOW NOT/WHY)은 placeholder만 둔다. 본격 작성은 베이스라인 완성 즈음 별도 `/update` 스킬의 사용자 인터뷰로 진행한다. 8번 LEARNED CAUTIONS 섹션은 영역 폴더의 별도 파일 `LEARNED_CAUTIONS.md`에 분리되어 `@` import + 마크다운 링크 하이브리드로 참조된다. `learn` 스킬은 이 별도 파일에만 항목을 누적하며 본문 가이드는 절대 건드리지 않는다. 사람용 작성 안내문은 HTML 주석으로 격리되어 자동 로드 시 토큰 비용 0. `/agentic-project-init` 슬래시 명령으로 직접 실행하는 스킬이며 자동 트리거하지 않는다. 인자에 따라 출력 파일명이 달라진다 — `claude`는 `CLAUDE.md`, `agents`는 `AGENTS.md`(Codex/Antigravity/Cursor 호환), `both`는 `AGENTS.md`를 원본으로 두고 `CLAUDE.md`가 `@./AGENTS.md` 한 줄로 import하는 단일 진실 공급원 구조. 인자 없이 호출하면 어떤 환경인지 사용자에게 묻고 대기한다.
---

# Agentic Project Init

임의 프로젝트 폴더를 AI 에이전틱 작업(Claude Code, Codex, Antigravity, Cursor)에 최적화된 구조로 초기화하는 스킬이다.

## 핵심 아이디어

LLM 에이전트가 큰 프로젝트에서 작업할 때 root CLAUDE.md 하나에 모든 가이드를 넣으면:
- 컨텍스트가 비대해진다 (다른 영역 가이드까지 매번 로드됨)
- 영역 간 정보가 섞여 잘못된 가정을 하기 쉽다

이 스킬은 **map 구조**를 도입한다:
- root 파일은 영역 라우팅만 담당 (어느 영역에서 일하면 어느 파일을 먼저 읽어라)
- 각 영역 폴더에 자체 가이드 파일이 있어 그 영역에서 일할 때만 그 영역 가이드만 참조

추가로 `learn` 스킬을 함께 설치하여, 작업 중 발견되는 실수/주의사항을 해당 영역 폴더의 별도 파일 `LEARNED_CAUTIONS.md`에 누적해 나간다. 본문 가이드는 8번 섹션에서 `@./LEARNED_CAUTIONS.md`로 참조하므로 자동 로드된다 (Codex 등 미지원 환경에선 마크다운 링크 fallback). `learn`은 이 별도 파일만 갱신하고 본문 가이드는 절대 건드리지 않는다.

init은 **가벼운 뼈대**만 만든다 — 코드 스캔으로 추출 가능한 사실 기반 섹션(WHAT/CONTENTS/WHERE/COMMANDS)만 채우고, 판단·암묵지 섹션(HOW/HOW NOT/WHY)은 placeholder만 둔다. 가이드를 본격적으로 채우는 작업은 베이스라인 완성 즈음 별도 스킬 `/update`로 사용자 인터뷰를 거쳐 진행한다.

## 인자 (Mode)

`/agentic-project-init`으로 호출 시 인자에 따라 동작이 바뀐다.

| 인자 | 본문 파일 | 호환 파일 |
|------|-----------|-----------|
| `claude` | `CLAUDE.md` | — |
| `agents` | `AGENTS.md` | — |
| `both` | `AGENTS.md` (단일 진실 공급원) | `CLAUDE.md` = `@./AGENTS.md` 한 줄 |
| (없음) | 사용자에게 위 3개 중 어느 환경인지 묻고 대기 | — |

`both` 모드에서는 본문을 `AGENTS.md`에만 작성하고, `CLAUDE.md`는 `@./AGENTS.md` 한 줄로 import한다. Claude Code는 import를 자동 따라가고, Codex/Antigravity/Cursor는 원본 `AGENTS.md`를 직접 읽는다. 단일 파일만 편집하므로 sync drift가 구조적으로 불가능하다. (이전 버전의 pre-commit hook 기반 양방향 sync는 폐기되었다.)

## 절차

다음 7단계를 순서대로 진행한다. 각 단계는 사용자 확인이 필요한 곳이 명시되어 있으니 주의한다.

### 1) 인자 파싱 및 모드 확정

- 인자가 `claude`이면 → **CLAUDE 모드** (`CLAUDE.md`만 생성)
- 인자가 `agents`이면 → **agents 모드** (`AGENTS.md`만 생성, Codex/Antigravity/Cursor 호환)
- 인자가 `both`이면 → **Both 모드** (`AGENTS.md` 원본 + `CLAUDE.md`는 `@./AGENTS.md` 한 줄)
- **인자가 비어있으면**: 자동으로 모드를 가정하지 않는다. 다음 안내를 그대로 출력하고 사용자 응답을 대기한다.

  ```
  어떤 환경에서 진행할까요? 다음 중 하나를 선택해주세요:

    claude  — Claude Code용 (CLAUDE.md + .claude/skills/learn/)
    agents  — Codex/Cursor/Antigravity용 (AGENTS.md + .agents/skills/learn/ + .agents/workflows/learn.md)
    both    — 두 환경 모두. AGENTS.md를 원본으로, CLAUDE.md는 @./AGENTS.md import (멀티 에이전트 협업 시)
  ```

  사용자가 답한 값을 인자로 받은 것처럼 처리해 위 분기로 들어간다. 응답이 위 3개 중 하나가 아니면 다시 묻는다.

- 그 외 인자(위 3개에 없는 값)는 잘못된 입력으로 안내하고 중단한다.

선택된 모드와 어떤 파일들이 생성될지 한 줄로 사용자에게 알린다.

### 2) git 리포 검증

`git rev-parse --show-toplevel`로 현재 위치가 git 리포지토리인지 확인한다.

- git 리포가 아니면 경고만 출력하고 계속 진행 (모든 모드가 git 없이 동작). 다만 사용자가 "git init 후 다시 시작하겠다"고 원하면 중단.

### 3) 기존 파일 충돌 검사 + 레거시 sync hook 마이그레이션

#### 3-1) 레거시 sync hook 감지 (both 모드에서만)
이전 버전의 양방향 sync 자동화가 설치돼 있는지 확인한다. 다음 중 하나라도 존재하면 레거시로 간주:
- `.githooks/pre-commit` 파일에 `sync-agents-md` 문자열 포함
- `scripts/sync-agents-md.sh` 파일 존재

레거시가 감지되면 사용자에게 다음을 묻는다:
```
이전 sync hook이 설치되어 있습니다. @import 방식으로 전환할까요?
  - .githooks/pre-commit 의 sync 로직 제거 (또는 파일 자체 제거)
  - scripts/sync-agents-md.sh 제거
  - 모든 CLAUDE.md를 `@./AGENTS.md` 한 줄로 교체
  - AGENTS.md는 그대로 (원본 보존)
```
- 승인 시 위 작업을 적용한 뒤 정상 흐름으로 진행.
- 거절 시 기존 hook 기반 sync를 유지하기로 보고 스킬을 중단 (혼합 상태 방지).

#### 3-2) 일반 충돌 검사
생성하려는 파일들이 이미 존재하는지 확인한다.

- root에 `CLAUDE.md` 또는 `AGENTS.md`가 이미 있으면: 내용을 읽어 보여주고 "기존 파일을 백업(`.bak.YYYYMMDD-HHMM`)하고 새로 생성하시겠습니까? 아니면 영역 가이드만 추가하고 root는 그대로 둘까요?" 라고 묻는다.
- 영역 폴더에 이미 가이드 파일이 있으면: 영역별로 같은 질문을 한다 (한 번에 묶어 제시).

사용자 답을 받기 전에는 어떤 파일도 수정/생성하지 않는다.

### 4) 영역 자동 탐지 → 사용자 검토

`references/area-detection.md`를 읽어 영역 탐지 로직을 따른다. 요약하면:
- 흔한 디렉토리 패턴(`apps/*`, `frontend`, `backend`, `database`, `analysis`, `airflow`, `docker`, `infra`, `scripts` 등)을 스캔
- 각 후보 영역에 대해 1-depth 파일 목록을 가볍게 훑어 기술 스택 추정 (예: `package.json` → JS/TS, `requirements.txt` → Python, `docker-compose.yml` → Docker)

탐지 결과를 다음 형태로 사용자에게 제시:

```
탐지된 영역 (총 N개):

  apps/frontend  — React + Vite (package.json, vite.config.ts)
  apps/backend   — FastAPI (pyproject.toml, app/main.py)
  database       — PostgreSQL (db_definition.md, ERD.png)
  analysis       — Jupyter (notebooks/, requirements.txt)

이 목록 그대로 진행할까요? (수정하려면: 추가/삭제할 영역과 한 줄 설명을 알려주세요)
```

사용자가 수정하면 반영하고 다시 한 번 확인한다. 영역이 0개면 사용자에게 직접 입력받는다.

### 5) 영역별 가이드 초안 작성 — **가벼운 뼈대 모드**

각 영역에 대해 디렉토리 내용을 가볍게 스캔(파일 목록 + 핵심 파일 1-2개의 첫 부분)하여 `assets/area-guide-template.md` 템플릿을 채운다.

이 단계의 핵심 원칙은 **"코드 스캔으로 추출 가능한 사실 기반 섹션만 init에서 채운다"** 이다. 판단·암묵지 영역은 작업이 누적된 후 `/update` 스킬에서 사용자 인터뷰로 채운다. init은 빈 골격 + 사실 데이터만 두고, 가이드 본격 작성은 베이스라인 완성 즈음 `/update`로 시작한다는 설계다.

8섹션 모델(WHAT / CONTENTS / HOW / HOW NOT / WHERE / WHY / COMMANDS / LEARNED CAUTIONS)을 따른다. 사람용 작성 안내문은 HTML 주석(`<!-- ... -->`)으로 격리해 자동 로드 시 토큰 비용을 0으로 만든다 (Claude Code는 컨텍스트 주입 전 주석 블록을 제거).

**init에서 채우는 섹션 (사실 기반)**:
- **WHAT** — 영역 디렉토리/스택을 보고 1문장 초안 작성 가능. 사용자 검토 받음.
- **CONTENTS** — 1-depth 파일 목록 + 추론된 스택. 자동 채움.
- **WHERE** — 디렉토리 의존성으로 추정 가능한 만큼 약결합 마크다운 링크로 초안. 강결합 `@import` 판단은 사용자 확인.
- **COMMANDS** — `package.json` / `Makefile` / `pyproject.toml` 등에서 추출 가능한 빌드/테스트/린트만. 영역 고유 가드는 비움.

**init에서 비우는 섹션 (placeholder만)**:
- **HOW** — 컨벤션은 코드만 봐서 결정할 수 없음. `/update`의 "컨벤션 합의" 인터뷰에서 채움.
- **HOW NOT** — 진짜 가치 있는 함정은 사용자만 안다. init이 일반론을 추측해 채우면 노이즈가 된다. `/update`의 "안티패턴 예측"에서 코드 스캔 기반 제안 + 사용자 검토로 채움.
- **WHY** — 도메인 배경/과거 결정은 추론 불가. `/update`의 "암묵지 추출" 인터뷰에서 채움.

placeholder 형식은 `_(update 스킬에서 채워질 자리. ...)_` 한 줄로 남겨 사용자가 작성 시점·도구를 명확히 안다.

템플릿 전체 구조는 `assets/area-guide-template.md`에 정의되어 있다. init은 위 "init에서 채우는 섹션" 항목만 채우고 나머지는 템플릿의 placeholder를 그대로 둔다.

**중요한 원칙**:

- **WHAT/CONTENTS/WHERE는 추론으로 채운다** — 디렉토리/파일 내용에서 1-3문장 초안을 만들 수 있다. 사용자가 검토 후 보정.
- **HOW / HOW NOT / WHY는 init에서 채우지 않는다** — 일반론 추측은 노이즈를 만들고 LLM의 룰 무시를 유도한다. placeholder 한 줄(`_(update 스킬에서 채워질 자리...)_`)만 남기고 `/update` 인터뷰에서 채운다. `learn` 스킬은 LEARNED_CAUTIONS.md에 사후 누적.
- **WHERE의 강결합/약결합 분리**: 의존성을 두 종류로 표현한다.
  - **강결합 (API contract / schema SoT)**: `@../other-area/AGENTS.md` 한 줄 import. 영역 진입 후 함께 자동 로드 → 침묵의 가정 방지. "매우 강함 — 한쪽 변경 = 다른쪽 즉시 깨짐"인 경우만 적용.
  - **약결합 (호출 관계·도메인 공유)**: `[경로](path)` 마크다운 링크 + 한 줄 설명. 작업 시점에만 따라가 본다.
  - 경계가 모호하면 사용자에게 확인. 기본값은 약결합(마크다운 링크). 자세한 결정 기준은 `references/rubric.md`의 "@import 최소주의" 섹션 참고.
- **첫 줄 목적 + Tradeoff 자리**: 가이드 헤딩 바로 아래에 두 placeholder 자리가 있다. 둘 다 **본문에 노출**되어야 LLM이 영역 진입 시 자동으로 함께 인지한다.
  - **첫 줄 목적**: 이 가이드가 "LLM이 자주 틀리는 무엇을 막는가"를 1문장. 영역 디렉토리/스택을 보고 추론 가능하면 초안 작성. 모호하면 placeholder 그대로 두어 사용자가 채울 자리 명시.
  - **Tradeoff**: 이 룰이 무엇을 포기하고 무엇을 얻는지 1문장. 일반적으로 사용자만 판단 가능하므로 기본 placeholder 형태로 둔다. 해당 없으면 한 줄 통째로 삭제.
- **8. LEARNED CAUTIONS 섹션은 별도 파일 참조**: 본문 가이드에는 `@./LEARNED_CAUTIONS.md` + 마크다운 링크 하이브리드 한 블록만 둔다. 실제 누적은 같은 폴더의 `LEARNED_CAUTIONS.md` (6단계에서 placeholder 생성). `learn` 스킬은 이 파일에만 항목을 추가하며 본문 가이드는 절대 수정하지 않는다.
- **명령어 가드의 root/영역 분리**: 명령어 가드 중복은 T3 안티패턴(같은 규칙이 여러 가이드에 흩어짐)이다.
  - **root map의 "공통 명령어 가드"**: 모든 영역에 공통으로 적용되는 가드 (예: `--no-verify` 금지, production DB 직접 쓰기 금지, `force push` 금지).
  - **영역 가이드의 "명령어 가드"**: 그 영역에서만 적용되는 가드. init에서는 비우고 update에서 추가한다.

각 영역의 초안을 사용자에게 일괄 제시(어떤 파일이 어떤 내용으로 생성되는지)하고 승인을 받는다. 가벼운 뼈대 모드이므로 사용자 부담이 크지 않다 — 사실 기반 섹션만 검토하면 된다.

### 6) 파일 생성

승인된 내용으로 다음을 생성한다.

**root map 파일** (`assets/root-map-template.md` 참고):
```markdown
# {프로젝트명} - {AI 에이전트 이름} 작업 지침

> 이 파일은 **map** 역할을 한다. 작업 시 해당 영역의 {파일명}을 먼저 읽고 진행한다.

## 영역별 가이드
- **{영역}** — {역할 한 줄} → [`{경로}/{파일명}`]({경로}/{파일명})
- ...

## 주의사항 학습 (learn 스킬)
작업 중 실수가 발견되면 다음 형태로 호출해 해당 영역 폴더의 `LEARNED_CAUTIONS.md`에 누적한다. 본문 가이드({파일명})는 8번 섹션에서 `@./LEARNED_CAUTIONS.md`를 참조하므로 자동 로드된다.

- Claude Code/Cursor/Antigravity: `/learn <메모>` (인자 없이도 호출 가능)
- Codex: `$learn <메모>`
```

> **주의 — "프로젝트 구조" 디렉토리 트리 섹션은 의도적으로 넣지 않는다.** `ls`로 알 수 있는 정보를 가이드에 담는 것은 영상의 G1 안티패턴("README 복붙형 설명")이고, 컨텍스트 토큰과 LLM 주의력을 낭비한다. root map은 라우팅(영역별 가이드 링크)에만 집중한다.

모드별 파일명:
- **CLAUDE 모드**: `CLAUDE.md`만 (본문 작성)
- **agents 모드**: `AGENTS.md`만 (Codex/Antigravity/Cursor가 모두 읽음)
- **Both 모드**: `AGENTS.md`에 본문 작성. `CLAUDE.md`는 다음 한 줄만:
  ```markdown
  @./AGENTS.md
  ```
  Claude Code는 import를 자동으로 따라가 `AGENTS.md` 본문을 컨텍스트에 로드한다. 다른 에이전트(Codex/Antigravity/Cursor)는 `AGENTS.md`를 직접 읽는다.

**영역별 가이드 파일** — 각 영역 폴더에도 동일 패턴 적용. Both 모드면 영역 폴더의 `AGENTS.md`에 본문 작성, `CLAUDE.md`는 `@./AGENTS.md` 한 줄.

**영역별 LEARNED_CAUTIONS.md placeholder 파일** — 각 영역 폴더에 `assets/learned-cautions-template.md`를 복사해 `LEARNED_CAUTIONS.md`로 둔다. `{AREA_NAME}` 토큰만 치환. 본문 가이드의 8번 섹션이 `@./LEARNED_CAUTIONS.md`를 참조하므로 파일이 없으면 import가 깨진다. 모드와 무관하게 영역당 한 개 (both 모드에서도 AGENTS.md / CLAUDE.md가 동일 파일을 참조).

**`learn` 스킬** — `assets/learn-skill/` 디렉터리 전체를 다음 위치에 복사:
- CLAUDE 모드: `.claude/skills/learn/`
- agents 모드: `.agents/skills/learn/` + `.agents/workflows/learn.md` (`assets/learn-workflow.md`에서 복사)
- Both 모드: 위 두 경로 모두

호출 방식:
- Claude Code/Cursor/Antigravity: `/learn <메모>` 또는 `/learn`
- Codex: `$learn <메모>` 또는 `$learn`

**`update` 스킬** — `assets/update-skill/` 디렉터리 전체를 `learn` 스킬과 같은 규칙으로 복사한다 (필수).
- 호출: `/update` (Codex는 `$update`)
- 동작: 베이스라인 완성 즈음부터 사용. 9개 질문 유형 인터뷰로 가이드를 채우고 6개 충돌 유형으로 영역 간 정합성을 검증한다.
- 영역 경계 재구성은 별도 `$update --restructure` 흐름.

**`guide-audit` 스킬** (선택) — `assets/guide-audit-skill/` 디렉터리 전체를 같은 규칙으로 복사한다.
- 호출: `/guide-audit` (Codex는 `$guide-audit`)
- 동작: 프로젝트 내 모든 가이드를 루브릭(`assets/rubric-schema.json`)으로 채점, 결과는 콘솔에만 출력.
- 의존성: Python 3.8+ (표준 라이브러리만 사용)

폴더가 없으면 생성한다.

**Both 모드 추가 작업**: 없음. `@import` 방식은 외부 스크립트/hook 불요.
- 각 위치(root + 영역 폴더)에 `AGENTS.md` 본문 + `CLAUDE.md` = `@./AGENTS.md` 한 줄.
- 이전 버전의 `sync-agents-md.sh` / `pre-commit-hook.sh`는 폐기되었다.

### 7) 마무리 안내

**7-0) 스킬 설치 자가 검증 (필수)**

마무리 안내 직전에 반드시 다음 검증을 수행해 6단계의 스킬 복사 누락을 막는다. LLM이 단계를 빠뜨리는 경우가 실제로 관찰됐으므로 이 검증은 생략 불가.

모드에 따라 다음 경로들이 존재해야 한다:

| 모드 | 검증 경로 |
|------|-----------|
| CLAUDE | `.claude/skills/learn/SKILL.md`, `.claude/skills/update/SKILL.md`, `.claude/skills/update/references/question-types.md`, `.claude/skills/update/references/conflict-types.md`, `.claude/skills/update/references/section-policy.md`, `.claude/skills/update/references/restructure-flow.md`, `.claude/skills/guide-audit/SKILL.md`, `.claude/skills/guide-audit/score_guide.py` |
| agents | `.agents/skills/learn/SKILL.md`, `.agents/skills/update/SKILL.md`, `.agents/skills/update/references/question-types.md`, `.agents/skills/update/references/conflict-types.md`, `.agents/skills/update/references/section-policy.md`, `.agents/skills/update/references/restructure-flow.md`, `.agents/skills/guide-audit/SKILL.md`, `.agents/skills/guide-audit/score_guide.py`, `.agents/workflows/learn.md` |
| both | 위 두 묶음 모두 |

추가로 **모든 영역 폴더에 `LEARNED_CAUTIONS.md`가 존재**해야 한다 (본문 가이드의 `@./LEARNED_CAUTIONS.md` import가 깨지지 않도록). 4단계에서 확정한 영역 목록 각각에 대해 파일 존재를 검증한다.

각 경로의 존재를 `ls` 또는 파일 읽기로 확인하고, 결과를 다음 형태로 출력한다:

```
스킬 설치 검증:
  ✅ .claude/skills/learn/SKILL.md
  ✅ .claude/skills/guide-audit/SKILL.md
  ✅ .claude/skills/guide-audit/score_guide.py

영역별 LEARNED_CAUTIONS.md 검증:
  ✅ apps/frontend/LEARNED_CAUTIONS.md
  ✅ apps/backend/LEARNED_CAUTIONS.md
```

**하나라도 누락이면 즉시 6단계의 해당 복사 작업을 다시 실행하고 재검증**한다. 누락된 채 마무리 안내로 넘어가지 않는다.

생성된 파일 목록을 보여주고 다음을 사용자에게 안내한다.

**Both 모드일 때만**:
```
Both 모드 구조:
  - 본문은 AGENTS.md에만 작성하세요.
  - CLAUDE.md는 `@./AGENTS.md` 한 줄로 import 합니다 — 수정 불필요.
  - Claude Code는 import를 자동 따라가고, Codex/Antigravity/Cursor는 AGENTS.md를 직접 읽습니다.
  - 단일 파일만 편집하므로 sync drift가 구조적으로 불가능합니다.
```

**모든 모드 공통**:
- 생성된 가이드는 **가벼운 뼈대**다. WHAT/CONTENTS/WHERE/COMMANDS만 코드 스캔으로 채워졌고, HOW/HOW NOT/WHY는 placeholder 상태다.
- 본격 작성은 **베이스라인 완성 즈음 `/update` 스킬로 시작**한다고 안내. 호출은 Claude Code/Cursor/Antigravity는 `/update`, Codex는 `$update`. update는 9개 질문 유형 인터뷰 + 6개 충돌 유형 교차 정합성 검증으로 가이드를 채운다. 영역 경계 재구성이 필요하면 `/update --restructure` 별도 명령.
- 작업 중 새로운 주의사항이 발견되면 `learn` 스킬로 영역 폴더의 `LEARNED_CAUTIONS.md`에 누적할 수 있다고 안내 (Claude Code/Cursor/Antigravity는 `/learn`, Codex는 `$learn`).
- `learn`은 본문 가이드(AGENTS.md/CLAUDE.md)를 절대 수정하지 않는다. 사용자가 직접 작성한 부분도 마찬가지로 자동 덮어쓰지 않는다.

커밋은 자동으로 하지 않는다 — 사용자가 직접 검토하고 커밋하도록 둔다.

## 금지

- 사용자 사전 확인 없이 파일 생성/수정 (특히 기존 파일 덮어쓰기)
- 자동 git commit
- 영역이 불명확한데 임의 추정만으로 진행
- 추측한 "금지 사항"을 확정 사실처럼 단언 — 항상 "추정이므로 검토 필요"임을 인지시킨다
- 인자가 잘못되었을 때 임의로 모드를 가정해서 진행

## 번들 자료 안내

- `references/area-detection.md` — 영역 자동 탐지 규칙 (디렉토리 패턴, 스택 추론 휴리스틱)
- `assets/root-map-template.md` — root map 파일 템플릿
- `assets/area-guide-template.md` — 영역별 가이드 8섹션 템플릿 (가벼운 뼈대 모드)
- `assets/learned-cautions-template.md` — 영역별 `LEARNED_CAUTIONS.md` placeholder 템플릿
- `assets/learn-skill/SKILL.md` — `learn` 스킬 정의 (LEARNED_CAUTIONS.md 전용 누적)
- `assets/update-skill/SKILL.md` — `update` 스킬 정의 (9개 인터뷰 유형 + 6개 충돌 검증)
- `assets/update-skill/references/question-types.md` — 9개 인터뷰 질문 유형 카탈로그
- `assets/update-skill/references/conflict-types.md` — 6개 교차 정합성 충돌 유형 + Deep 해소
- `assets/update-skill/references/section-policy.md` — 8섹션 갱신 정책 (AI 갱신/제안/보존)
- `assets/update-skill/references/restructure-flow.md` — `--restructure` 영역 경계 재구성 10단계 절차
- `assets/learn-workflow.md` — Antigravity workflow 위임 파일
- `assets/guide-audit-skill/` — 가이드 품질 채점 스킬
- `assets/rubric-schema.json` — 자동 채점용 스키마
- `references/rubric.md` — 사람용 평가 기준서 (@import 최소주의 원칙 포함)
- `references/work-checklist.md` — 가이드 작업/검증 전 점검 18개 체크리스트
