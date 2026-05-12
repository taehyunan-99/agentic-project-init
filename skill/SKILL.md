---
name: agentic-project-init
description: 임의 프로젝트 폴더를 AI 에이전틱 작업에 최적화된 구조로 초기화한다. root에 영역 map을 두고 각 영역마다 8섹션 작업 가이드(WHAT/CONTENTS/HOW/HOW NOT/WHERE/WHY/COMMANDS/LEARNED CAUTIONS)를 생성하며, 동시에 `learn` 스킬을 함께 설치해 작업 중 발견된 실수/주의사항을 영역별 가이드에 누적할 수 있게 한다. 사람용 작성 안내문은 HTML 주석으로 격리되어 자동 로드 시 토큰 비용 0. `/agentic-project-init` 슬래시 명령으로 직접 실행하는 스킬이며 자동 트리거하지 않는다. 인자에 따라 출력 파일명이 달라진다 — `claude`는 `CLAUDE.md`, `agents`는 `AGENTS.md`(Codex/Antigravity/Cursor 호환), `both`는 둘 다 + 양방향 sync 자동화(pre-commit hook + sync 스크립트). 인자 없이 호출하면 어떤 환경인지 사용자에게 묻고 대기한다. 이 스킬의 핵심은 (1) 토큰 효율을 위한 map 구조와 (2) 코드만 봐선 알 수 없는 함정·배경 지식을 영역별 가이드에 명시적으로 담는 것이다.
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

| 인자 | 출력 파일 | sync 자동화 |
|------|-----------|-------------|
| `claude` | `CLAUDE.md` | ❌ |
| `agents` | `AGENTS.md` | ❌ |
| `both` | `CLAUDE.md` + `AGENTS.md` | ✅ pre-commit hook + sync 스크립트 |
| (없음) | 사용자에게 위 3개 중 어느 환경인지 묻고 대기 | — |

`both` 모드에서는 두 파일이 항상 동일한 내용을 유지하도록 git pre-commit hook이 자동으로 양방향 동기화를 처리한다. 한쪽만 수정해도 commit 시 다른 쪽이 자동으로 따라온다.

## 절차

다음 7단계를 순서대로 진행한다. 각 단계는 사용자 확인이 필요한 곳이 명시되어 있으니 주의한다.

### 1) 인자 파싱 및 모드 확정

- 인자가 `claude`이면 → **CLAUDE 모드** (`CLAUDE.md`만 생성)
- 인자가 `agents`이면 → **agents 모드** (`AGENTS.md`만 생성, Codex/Antigravity/Cursor 호환)
- 인자가 `both`이면 → **Both 모드** (`CLAUDE.md` + `AGENTS.md` + sync hook)
- **인자가 비어있으면**: 자동으로 모드를 가정하지 않는다. 다음 안내를 그대로 출력하고 사용자 응답을 대기한다.

  ```
  어떤 환경에서 진행할까요? 다음 중 하나를 선택해주세요:

    claude  — Claude Code용 (CLAUDE.md + .claude/skills/learn/)
    agents  — Codex/Cursor/Antigravity용 (AGENTS.md + .agents/skills/learn/ + .agents/workflows/learn.md)
    both    — 두 환경 모두 + 양방향 sync hook (멀티 에이전트 협업 시)
  ```

  사용자가 답한 값을 인자로 받은 것처럼 처리해 위 분기로 들어간다. 응답이 위 3개 중 하나가 아니면 다시 묻는다.

- 그 외 인자(위 3개에 없는 값)는 잘못된 입력으로 안내하고 중단한다.

선택된 모드와 어떤 파일들이 생성될지 한 줄로 사용자에게 알린다.

### 2) git 리포 검증

`git rev-parse --show-toplevel`로 현재 위치가 git 리포지토리인지 확인한다.

- git 리포가 아니면: Both 모드는 pre-commit hook을 설치할 수 없으므로 "git 리포가 아닙니다. `git init` 후 다시 실행하거나, claude/agents 모드로 전환하시겠습니까?" 라고 묻고 중단/전환 대기.
- claude/agents 모드는 git 없이도 동작하므로 경고만 출력하고 계속.

### 3) 기존 파일 충돌 검사

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
- **CLAUDE 모드**: `CLAUDE.md`만
- **agents 모드**: `AGENTS.md`만 (Codex/Antigravity/Cursor가 모두 읽음)
- **Both 모드**: 두 파일 모두 동일 내용

**영역별 가이드 파일** — 각 영역 폴더에 동일하게 생성.

**`learn` 스킬** — `assets/learn-skill/` 디렉터리 전체를 다음 위치에 복사:
- CLAUDE 모드: `.claude/skills/learn/`
- agents 모드: `.agents/skills/learn/` + `.agents/workflows/learn.md` (`assets/learn-workflow.md`에서 복사)
- Both 모드: 위 두 경로 모두

호출 방식:
- Claude Code/Cursor/Antigravity: `/learn <메모>` 또는 `/learn`
- Codex: `$learn <메모>` 또는 `$learn`

폴더가 없으면 생성한다.

**Both 모드 추가 작업**: `assets/sync-agents-md.sh`와 `assets/pre-commit-hook.sh`를 다음 위치로 복사하고 실행 권한 설정.
- `scripts/sync-agents-md.sh` (sync 스크립트)
- `.githooks/pre-commit` (hook)

스크립트 내부의 `DIRS` 배열은 확정된 영역 목록으로 치환한다(템플릿의 placeholder를 실제 경로 리스트로 교체).

### 7) 마무리 안내

생성된 파일 목록을 보여주고 다음을 사용자에게 안내한다.

**Both 모드일 때만**:
```
hook을 활성화하려면 한 번만 실행하세요:
  git config core.hooksPath .githooks
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
- `assets/sync-agents-md.sh` — Both 모드용 양방향 sync 스크립트
- `assets/pre-commit-hook.sh` — Both 모드용 pre-commit hook
