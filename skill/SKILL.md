---
name: agentic-project-init
description: 임의 프로젝트 폴더를 AI 에이전틱 작업에 최적화된 구조로 초기화한다. root에 영역 map을 두고 각 영역마다 8섹션 작업 가이드(WHAT/CONTENTS/HOW/HOW NOT/WHERE/WHY/COMMANDS/LEARNED CAUTIONS)를 생성하며, 동시에 `learn` 스킬을 함께 설치해 작업 중 발견된 실수/주의사항을 영역별 가이드에 누적할 수 있게 한다. 사람용 작성 안내문은 HTML 주석으로 격리되어 자동 로드 시 토큰 비용 0. `/agentic-project-init` 슬래시 명령으로 직접 실행하는 스킬이며 자동 트리거하지 않는다. 인자에 따라 출력 파일명이 달라진다 — `claude`는 `CLAUDE.md`, `agents`는 `AGENTS.md`(Codex/Antigravity/Cursor 호환), `both`는 `AGENTS.md`를 원본으로 두고 `CLAUDE.md`가 `@./AGENTS.md` 한 줄로 import하는 단일 진실 공급원 구조. 인자 없이 호출하면 어떤 환경인지 사용자에게 묻고 대기한다. 이 스킬의 핵심은 (1) 토큰 효율을 위한 map 구조와 (2) 코드만 봐선 알 수 없는 함정·배경 지식을 영역별 가이드에 명시적으로 담는 것이다.
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

추가로 `learn` 스킬을 함께 설치하여, 작업 중 발견되는 실수/주의사항을 해당 영역 가이드의 "⚠️ LEARNED CAUTIONS" 섹션에 누적해 나간다.

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

### 5) 영역별 가이드 초안 작성

각 영역에 대해 디렉토리 내용을 가볍게 스캔(파일 목록 + 핵심 파일 1-2개의 첫 부분)하여 다음 템플릿을 채운다. 템플릿은 `assets/area-guide-template.md`를 참고한다.

이 가이드는 **에이전트가 해당 영역에서 코드를 건드리기 전에 반드시 알아야 할 컨텍스트**를 제공하는 것이 목적이다. 단순한 디렉토리 설명이 아니라, 코드만 읽어서는 알 수 없는 의도/함정/배경을 적는 자리다.

8섹션 모델(WHAT / CONTENTS / HOW / HOW NOT / WHERE / WHY / COMMANDS / LEARNED CAUTIONS)을 따른다. 사람용 작성 안내문은 HTML 주석(`<!-- ... -->`)으로 격리해 자동 로드 시 토큰 비용을 0으로 만든다 (Claude Code는 컨텍스트 주입 전 주석 블록을 제거).

```markdown
# {영역명} 작업 가이드

## 1. WHAT — 이 모듈은 무엇을 하는가
{1-3문장. 시스템 안에서의 역할과 책임.}

## 2. CONTENTS — 파일/디렉토리와 기술 스택
- `{경로}` — {역할}

기술 스택: {추론된 스택}

## 3. HOW — 일반적인 수정은 어떻게 하는가
{이 영역의 수정 절차/패턴.}

## 4. ⛔ HOW NOT — 시스템을 깨뜨리는 비명백한 함정 (중요)
- {함정} — {왜 안 되는지}
- {함정} — {왜 안 되는지}
- {함정} — {왜 안 되는지}

## 5. WHERE — 다른 모듈과의 의존성
- 의존: ...
- 피의존: ...
- 경계: ...

## 6. WHY — 코드에 안 적힌 배경 지식
- {도메인 용어 정의 / 약어}
- {과거 incident 또는 시도했다 철회한 접근}
- {다른 길로 안 간 이유}

## 7. COMMANDS — 빌드/테스트/린트
- 빌드: `{명령어}`
- 테스트: `{명령어}`
- 린트: `{명령어}`
- 타입체크: `{명령어}`

**명령어 가드**:
- {예: production DB 직접 쓰기 금지 — staging 검증 우회}

## 8. ⚠️ LEARNED CAUTIONS — 학습된 주의사항
_(아직 없음)_
```

**중요한 원칙**:

- **WHAT/HOW/WHERE는 추론으로 채운다** — 디렉토리/파일 내용에서 1-3문장 초안을 만들 수 있다. 사용자가 검토 후 보정.
- **HOW NOT과 WHY는 추측에 한계가 있다** — 일반적 함정(예: any 타입 회피, DB 직접 쓰기 금지)은 스택 기반으로 제시할 수 있지만, 진짜 가치 있는 항목(프로젝트 고유 함정, 도메인 결정 배경)은 사용자만 알 수 있다. 추론한 항목에는 "추정이므로 검토 필요" 표시를 붙이고, 추론할 수 없는 항목은 비워두되 placeholder 한 줄(예: "_(이 영역의 비명백한 함정이 있다면 채워주세요. `learn` 스킬로도 누적 가능합니다)_")을 남겨 사용자가 채울 자리를 명시한다.
- **HOW NOT의 형식**: 항목마다 "왜 안 되는지" 한 줄을 함께 적도록 한다. 이유가 없는 룰은 LLM이 흘려보낸다.

**스택별 HOW NOT 추론 예시** (검토 필요 표시 필수):
- React/TS: "타입 정의를 `any`로 회피 — 런타임 에러 추적 불가", "API 스키마를 추측해서 호출 — 백엔드와 컨트랙트 깨짐"
- FastAPI: "API 응답 스키마 임의 변경 — 프론트와 컨트랙트 깨짐", "DB 컬럼명 추측 사용 — 운영 시 쿼리 실패"
- DB: "스키마/컬럼명 임의 변경 — 마이그레이션 누락 시 데이터 유실", "production DB 직접 쓰기 — staging 검증 우회"

각 영역의 초안을 사용자에게 일괄 제시(어떤 파일이 어떤 내용으로 생성되는지)하고 승인을 받는다. 사용자가 한 번에 다 채우기 부담스러워하면 "지금 채울 수 있는 만큼만 채우고 나머지는 placeholder로 두세요" 옵션도 안내한다.

### 6) 파일 생성

승인된 내용으로 다음을 생성한다.

**root map 파일** (`assets/root-map-template.md` 참고):
```markdown
# {프로젝트명} - {AI 에이전트 이름} 작업 지침

> 이 파일은 **map** 역할을 한다. 작업 시 해당 영역의 {파일명}을 먼저 읽고 진행한다.

## 프로젝트 구조
{탐지/확정된 구조 트리}

## 영역별 가이드
- **{영역}** — {역할 한 줄} → [`{경로}/{파일명}`]({경로}/{파일명})
- ...

## 주의사항 학습 (learn 스킬)
작업 중 실수가 발견되면 다음 형태로 호출해 해당 영역 {파일명}의 "⚠️ LEARNED CAUTIONS" 섹션에 누적한다.

- Claude Code/Cursor/Antigravity: `/learn <메모>` (인자 없이도 호출 가능)
- Codex: `$learn <메모>`
```

모드별 파일명:
- **CLAUDE 모드**: `CLAUDE.md`만 (본문 작성)
- **agents 모드**: `AGENTS.md`만 (Codex/Antigravity/Cursor가 모두 읽음)
- **Both 모드**: `AGENTS.md`에 본문 작성. `CLAUDE.md`는 다음 한 줄만:
  ```markdown
  @./AGENTS.md
  ```
  Claude Code는 import를 자동으로 따라가 `AGENTS.md` 본문을 컨텍스트에 로드한다. 다른 에이전트(Codex/Antigravity/Cursor)는 `AGENTS.md`를 직접 읽는다.

**영역별 가이드 파일** — 각 영역 폴더에도 동일 패턴 적용. Both 모드면 영역 폴더의 `AGENTS.md`에 본문 작성, `CLAUDE.md`는 `@./AGENTS.md` 한 줄.

**`learn` 스킬** — `assets/learn-skill/` 디렉터리 전체를 다음 위치에 복사:
- CLAUDE 모드: `.claude/skills/learn/`
- agents 모드: `.agents/skills/learn/` + `.agents/workflows/learn.md` (`assets/learn-workflow.md`에서 복사)
- Both 모드: 위 두 경로 모두

호출 방식:
- Claude Code/Cursor/Antigravity: `/learn <메모>` 또는 `/learn`
- Codex: `$learn <메모>` 또는 `$learn`

**`guide-audit` 스킬** (선택) — `assets/guide-audit-skill/` 디렉터리 전체를 같은 규칙으로 복사한다.
- 호출: `/guide-audit` (Codex는 `$guide-audit`)
- 동작: 프로젝트 내 모든 가이드를 v1.2 루브릭(`assets/rubric-schema.json`)으로 채점, 결과는 콘솔에만 출력.
- 의존성: Python 3.8+ (표준 라이브러리만 사용)

폴더가 없으면 생성한다.

**Both 모드 추가 작업**: 없음. `@import` 방식은 외부 스크립트/hook 불요.
- 각 위치(root + 영역 폴더)에 `AGENTS.md` 본문 + `CLAUDE.md` = `@./AGENTS.md` 한 줄.
- 이전 버전의 `sync-agents-md.sh` / `pre-commit-hook.sh`는 폐기되었다.

### 7) 마무리 안내

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
- 생성된 가이드는 초안이다. 각 영역의 "⛔ 금지 사항"을 검토하고 프로젝트 실정에 맞게 수정하라고 안내.
- 작업 중 새로운 주의사항이 발견되면 `learn` 스킬로 누적할 수 있다고 안내 (Claude Code/Cursor/Antigravity는 `/learn`, Codex는 `$learn`).

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
- `assets/area-guide-template.md` — 영역별 가이드 8섹션 템플릿 (HTML 주석으로 작성 안내문 격리)
- `assets/learn-skill/SKILL.md` — `learn` 스킬 정의 (4개 에이전트 공통 본체)
- `assets/learn-workflow.md` — Antigravity workflow 위임 파일
- `assets/guide-audit-skill/` — 가이드 품질 채점 스킬 (v1.3 루브릭 기반)
- `assets/rubric-schema.json` — 자동 채점용 스키마
- `references/rubric.md` — 사람용 평가 기준서
