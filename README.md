# Agentic Project Init

> AI 에이전틱 작업(Claude Code · Codex · Antigravity · Cursor)에 최적화된 프로젝트 구조를 자동으로 초기화하는 스킬입니다.

## TL;DR

- root에는 **map만**, 영역별 가이드는 **그 영역 폴더 안에** 둡니다.
- 에이전트가 작업 중인 영역의 가이드만 로드 → **컨텍스트 토큰 절약**.
- 코드만 봐선 알 수 없는 함정·배경을 **7섹션 템플릿(WHAT / CONTENTS / HOW / HOW NOT / WHERE / WHY / LEARNED CAUTIONS)** 으로 명시합니다.
- `/learn` 명령으로 작업 중 발견한 주의사항을 해당 영역 가이드에 누적합니다.

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

### 2. 7섹션 템플릿 = 코드 외 지식의 명시화

각 영역 가이드는 동일한 7섹션 구조입니다:

1. **WHAT** — 이 모듈은 무엇을 하는가
2. **CONTENTS** — 파일/디렉토리와 기술 스택
3. **HOW** — 일반적인 수정은 어떻게 하는가
4. **⛔ HOW NOT** — 시스템을 깨뜨리는 비명백한 함정 (이유 한 줄 필수)
5. **WHERE** — 다른 모듈과의 의존성
6. **WHY** — 코드에 안 적힌 배경 지식
7. **⚠️ LEARNED CAUTIONS** — `/learn`으로 누적

특히 4(HOW NOT)와 6(WHY)는 **사람만 알 수 있는 지식**을 명시적으로 담는 자리입니다. 코드 리뷰에서 매번 같은 지적을 반복하지 않게 됩니다.

<br/>

### 3. /learn 누적 = 같은 실수 두 번 안 함

작업 중 잘못된 가정으로 실수가 발생하면:

```
/learn DB 마이그레이션 시 alembic 버전 미반영 → staging에서 컬럼 누락
```

해당 영역 가이드의 "⚠️ LEARNED CAUTIONS"에 자동 추가됩니다. 다음 세션부터 에이전트가 같은 실수를 안 합니다.

<br/>

### 4. 멀티 에이전트 협업

한 프로젝트에서 팀원들이 서로 다른 에이전트(Claude Code, Codex 등)를 써도 동일한 가이드를 봅니다.

- `both` 모드 → `CLAUDE.md` ↔ `AGENTS.md` 양방향 sync (pre-commit hook)
- 한쪽 수정해도 commit 시 자동으로 따라갑니다.

<br/><br/>

## 정량 효과

이 구조는 다음 두 가지를 동시에 노립니다:

- **토큰 사용량 감소** — 단일 CLAUDE.md 대비 작업당 로드되는 컨텍스트가 줄어듭니다. 영역이 많을수록 격차가 커집니다.
- **잘못된 가정 빈도 감소** — 영역 격리로 다른 영역의 룰이 현재 영역에 잘못 적용되는 일이 줄어듭니다.

<br/><br/>

## Case Study: 실제 프로젝트 적용 측정

> ⚠️ 한 프로젝트(7영역)에 적용해 측정한 결과입니다. 영역 수·작업 종류·codebase 크기에 따라 효과는 달라질 수 있습니다. 다른 프로젝트의 측정 결과는 PR로 환영합니다.

**v1**: 단일 root README만 있는 상태. **v2**: 이 스킬을 적용해 root map + 7개 영역 가이드 + `/learn` 명령(총 9개 파일)을 추가한 상태.

<br/>

### 진입 비용 비교 (시나리오 5개)

AI 에이전트가 작업 시 *반드시 읽어야 하는* 컨텍스트의 라인 수입니다.

| 시나리오 | v1 (단일 README) | v2 (map + 영역 가이드) | 절감 |
|---------|---------------:|---------------------:|------:|
| "이 프로젝트 뭐야?" | 169줄 | 78줄 | −54% |
| "EDA 단계 수정" | 414줄 | 127줄 | −69% |
| "stat 가설 추가" | 1,412줄 | 138줄 | −90% |
| "clean → model 의존성" | 1,143줄 | 194줄 | −83% |
| "전체 흐름 파악" | 1,143줄 | 449줄 | −61% |

토큰·비용 환산은 라인당 ~18 토큰 가정 + Opus 4.7 입력 단가 기반의 *추정값*입니다.

<br/>

### 구조 지표

- AI-Ready 점수: ~26/100 (AI-Hostile) → ~57/100 (AI-Fragile), +31점
- Module 진입점 수: 1 → 9
- 평균 context 라인/파일: 169 → 68.7
- Cache hit ratio: 92.4% → 93.94%

<br/><br/>

## 에이전트별 호환성

| 에이전트 | 메모리 파일 | User-level 스킬 위치 | 슬래시 명령 |
|---------|------------|---------------------|-----------|
| Claude Code | `CLAUDE.md` | `~/.claude/skills/` | `.claude/commands/` |
| Codex | `AGENTS.md` | `~/.agents/skills/` | `$skill-name` 호출 |
| Antigravity | `AGENTS.md` 또는 `GEMINI.md` | `~/.gemini/antigravity/skills/` | `.agents/workflows/` |
| Cursor | `AGENTS.md` 또는 `.cursor/rules/` | `~/.cursor/skills/` | SKILL.md 내 |

각 경로는 공식 docs 기준입니다 ([Claude Code](https://code.claude.com/docs/en/skills.md) · [Codex](https://developers.openai.com/codex/skills) · [Antigravity](https://antigravity.google/docs/skills) · [Cursor](https://cursor.com/docs/skills)).

<br/><br/>

## 설치

**한 번 user-level에 설치하면 모든 프로젝트에서 `/agentic-project-init`로 호출할 수 있습니다.** 호출 시 그 시점의 작업 디렉토리에 구조를 생성하므로, 프로젝트마다 따로 설치할 필요가 없습니다.

본인이 사용하는 에이전트 한 줄만 실행하세요.

<br/>

### Linux / macOS

**Claude Code**:
```bash
git clone https://github.com/taehyunan-99/agentic-project-init /tmp/api && mkdir -p ~/.claude/skills && cp -r /tmp/api/skill ~/.claude/skills/agentic-project-init && rm -rf /tmp/api
```

**Codex**:
```bash
git clone https://github.com/taehyunan-99/agentic-project-init /tmp/api && mkdir -p ~/.agents/skills && cp -r /tmp/api/skill ~/.agents/skills/agentic-project-init && rm -rf /tmp/api
```

**Antigravity**:
```bash
git clone https://github.com/taehyunan-99/agentic-project-init /tmp/api && mkdir -p ~/.gemini/antigravity/skills && cp -r /tmp/api/skill ~/.gemini/antigravity/skills/agentic-project-init && rm -rf /tmp/api
```

**Cursor**:
```bash
git clone https://github.com/taehyunan-99/agentic-project-init /tmp/api && mkdir -p ~/.cursor/skills && cp -r /tmp/api/skill ~/.cursor/skills/agentic-project-init && rm -rf /tmp/api
```

<br/>

### Windows (PowerShell)

**Claude Code**:
```powershell
git clone https://github.com/taehyunan-99/agentic-project-init $env:TEMP\api; New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills"; Copy-Item -Recurse $env:TEMP\api\skill "$env:USERPROFILE\.claude\skills\agentic-project-init"; Remove-Item -Recurse -Force $env:TEMP\api
```

**Codex**:
```powershell
git clone https://github.com/taehyunan-99/agentic-project-init $env:TEMP\api; New-Item -ItemType Directory -Force "$env:USERPROFILE\.agents\skills"; Copy-Item -Recurse $env:TEMP\api\skill "$env:USERPROFILE\.agents\skills\agentic-project-init"; Remove-Item -Recurse -Force $env:TEMP\api
```

**Antigravity**:
```powershell
git clone https://github.com/taehyunan-99/agentic-project-init $env:TEMP\api; New-Item -ItemType Directory -Force "$env:USERPROFILE\.gemini\antigravity\skills"; Copy-Item -Recurse $env:TEMP\api\skill "$env:USERPROFILE\.gemini\antigravity\skills\agentic-project-init"; Remove-Item -Recurse -Force $env:TEMP\api
```

**Cursor**:
```powershell
git clone https://github.com/taehyunan-99/agentic-project-init $env:TEMP\api; New-Item -ItemType Directory -Force "$env:USERPROFILE\.cursor\skills"; Copy-Item -Recurse $env:TEMP\api\skill "$env:USERPROFILE\.cursor\skills\agentic-project-init"; Remove-Item -Recurse -Force $env:TEMP\api
```

<br/><br/>

## 사용

설치 후 에이전트의 슬래시 명령으로 호출합니다.

```
/agentic-project-init           # 인자 없음 → 어떤 환경인지 사용자에게 묻고 대기
/agentic-project-init claude    # Claude Code용 (CLAUDE.md)
/agentic-project-init agents    # Codex / Antigravity / Cursor용 (AGENTS.md)
/agentic-project-init both      # 둘 다 + 양방향 sync hook
```

<br/>

### 인자별 산출물

| 인자 | 출력 | sync 자동화 |
|------|------|------------|
| `claude` | `CLAUDE.md` + `.claude/commands/learn.md` | ❌ |
| `agents` | `AGENTS.md` + `.agents/workflows/learn.md` | ❌ |
| `both` | 두 파일 모두 | ✅ pre-commit hook |
| (없음) | 위 3개 중 어느 환경인지 사용자에게 묻고 대기합니다 | — |

<br/>

### 동작 흐름 (스킬이 하는 일)

1. 인자 파싱 → 모드 확정 (인자 없으면 사용자에게 환경 질문)
2. git 리포 검증 (both 모드는 git 필수)
3. 기존 파일 충돌 검사
4. 영역 자동 탐지 (`apps/`, `frontend`, `backend`, `database`, ...) → 사용자 검토
5. 영역별 가이드 초안 작성 → 사용자 승인
6. 파일 생성 (root map + 영역 가이드 + `/learn` 명령)
7. (both 모드) sync hook 활성화 안내

<br/><br/>

## FAQ

**Q. CLAUDE.md 하나로 충분한 작은 프로젝트인데도 써야 하나요?**

영역이 1개면 효과가 적습니다. 2~3개부터 의미가 있고 5개 이상에서 진가가 드러납니다.

**Q. 기존 CLAUDE.md가 있는데 덮어써지나요?**

검출 시 백업 옵션을 제공합니다. 사용자 확인 전에는 덮어쓰지 않습니다.

**Q. 한 프로젝트에 Claude Code 사용자와 Codex 사용자가 섞여 있다면?**

`both` 모드로 생성하세요. pre-commit hook이 양방향으로 동기화합니다.

**Q. /learn은 어떻게 동작하나요?**

현재 작업 영역을 추론해 그 영역 가이드의 "⚠️ LEARNED CAUTIONS" 섹션에 한 줄 추가합니다. 영역이 모호하면 사용자에게 확인합니다.

**Q. 다른 에이전트를 추가 지원하려면?**

`.agents/` 표준만 인식하면 별도 작업 없이 동작합니다. 자체 표준이 있는 에이전트라면 issue로 알려주세요.

