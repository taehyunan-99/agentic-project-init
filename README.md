# Agentic Project Init

AI 에이전틱 작업에 최적화된 프로젝트 구조를 자동으로 초기화하는 스킬입니다.

> 적용 가능 에이전트: Claude Code · Codex · Antigravity · Cursor

<br/><br/>

## TL;DR

- root에는 **map만**, 영역별 가이드는 **그 영역 폴더 안에** 둡니다.
- 에이전트가 작업 중인 영역의 가이드만 로드 → **컨텍스트 토큰 절약**.
- 코드만 봐선 알 수 없는 함정·배경을 **8섹션 템플릿(WHAT / CONTENTS / HOW / HOW NOT / WHERE / WHY / COMMANDS / LEARNED CAUTIONS)** 으로 명시합니다.
- 각 가이드는 **첫 줄에 미션 1문장**과 **Tradeoff 주석 블록**을 둬서 LLM이 룰의 의도와 비용을 함께 인지하게 합니다 (안드레 카파시 CLAUDE.md 원칙 #16/#17).
- `/learn` 명령으로 작업 중 발견한 주의사항을 해당 영역 가이드에 누적합니다.
- `/guide-audit` 명령으로 프로젝트 내 모든 가이드를 결정적 루브릭으로 채점합니다 (100점 만점, S/A/B/C/D 등급).

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

1. **WHAT** — 이 모듈은 무엇을 하는가
2. **CONTENTS** — 파일/디렉토리와 기술 스택
3. **HOW** — 일반적인 수정은 어떻게 하는가
4. **⛔ HOW NOT** — 시스템을 깨뜨리는 비명백한 함정 (이유 한 줄 필수)
5. **WHERE** — 다른 모듈과의 의존성
6. **WHY** — 코드에 안 적힌 배경 지식
7. **COMMANDS** — 빌드/테스트/린트 명령어 + 영역 고유 명령어 가드
8. **⚠️ LEARNED CAUTIONS** — `learn` 스킬로 누적

특히 4(HOW NOT)와 6(WHY)는 **사람만 알 수 있는 지식**을 명시적으로 담는 자리이고, 7(COMMANDS)은 LLM이 명령어를 추측하지 못하게 막는 가드입니다.

사람이 봐도 되는 작성 안내문은 HTML 주석으로 격리되어 자동 로드 시 토큰 비용 0입니다.

<br/>

### 3. 첫 줄 미션 + Tradeoff = 룰의 의도와 비용 인지

각 영역 가이드의 헤딩 바로 아래에는 두 자리가 있습니다:

```markdown
# Frontend 작업 가이드

백엔드 API 컨트랙트와 도메인 변수명에서의 schema drift를 막는다. 추측·`any`·임의 변경 금지.

<!--
== Tradeoff (카파시 원칙 #17) ==
hook 단위로 API를 캡슐화하면 단순 fetch 한 줄의 편의를 포기하는 대신 schema drift 격리·테스트 가능성을 얻는다.
타입을 backend schema와 1:1로 묶으면 클라이언트만 빠르게 진화시킬 자유를 포기하는 대신 422/500을 컴파일 타임으로 옮긴다.
-->
```

- **첫 줄 미션** (카파시 #16): LLM이 이 영역의 **본질적 목적**을 즉시 인지. "이 영역이 무엇을 막는가"를 한 문장으로.
- **Tradeoff 주석** (카파시 #17): 이 룰이 무엇을 포기하고 무엇을 얻는지 명시. LLM이 경계 케이스에서 룰의 본질을 놓치지 않게 합니다. HTML 주석이라 자동 로드 토큰 비용 0.

<br/>

### 4. /learn 누적 = 같은 실수 두 번 안 함

작업 중 잘못된 가정으로 실수가 발생하면:

```
/learn DB 마이그레이션 시 alembic 버전 미반영 → staging에서 컬럼 누락
```

해당 영역 가이드의 "⚠️ LEARNED CAUTIONS"에 자동 추가됩니다. 다음 세션부터 에이전트가 같은 실수를 안 합니다.

<br/>

### 5. /guide-audit 결정적 채점 = 품질 회귀 방지

`/guide-audit` 명령으로 프로젝트 내 모든 가이드를 100점 만점 루브릭으로 채점합니다. 패턴 매칭 기반이라 같은 입력 → 같은 점수 (LLM 주관 평가 없음).

- 7개 카테고리(A~H) + 트리 일관성(T) + 안티패턴(G) 통합 채점
- 파일별 점수 + 카테고리별 breakdown + 0점 항목 evidence + Top 개선 추천
- `@import` redirect 파일 자동 인식 (`@./AGENTS.md` 한 줄짜리 `CLAUDE.md`는 import 대상 점수 차용)

채점 결과는 콘솔에만 출력되며 가이드 파일을 수정하지 않습니다 (읽기 전용).

<br/>

### 6. 멀티 에이전트 협업

한 프로젝트에서 팀원들이 서로 다른 에이전트(Claude Code, Codex 등)를 써도 동일한 가이드를 봅니다.

- `both` 모드 → `AGENTS.md`를 본문으로 두고 `CLAUDE.md`는 `@./AGENTS.md` 한 줄로 import.
- 단일 파일만 편집하므로 sync drift가 구조적으로 불가능합니다. 외부 스크립트/hook 불필요.

<br/><br/>

## 정량 효과

이 구조는 두 가지를 동시에 노립니다 — **토큰 사용량 감소**(영역이 많을수록 작업당 로드되는 컨텍스트 격차가 커짐)와 **잘못된 가정 빈도 감소**(영역 격리로 다른 영역의 룰이 현재 영역에 잘못 적용되는 일이 줄어듦).

아래는 한 프로젝트(7영역)에 적용해 측정한 *실측값*입니다. **v1**은 단일 root README만 있는 상태, **v2**는 이 스킬을 적용해 root map + 7개 영역 가이드 + `/learn` 명령(총 9개 파일)을 추가한 상태입니다.

> ⚠️ 영역 수·작업 종류·codebase 크기에 따라 효과는 달라질 수 있습니다. 다른 프로젝트의 측정 결과는 PR로 환영합니다.

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

<br/>

### 가이드 품질 채점 사례

`/guide-audit`로 외부 프로젝트(7영역, 16개 가이드 파일)에 적용·검증한 결과:

| 단계 | 가이드 품질 점수 | 등급 |
|------|---------------:|:---:|
| 적용 전 (구버전 가이드) | 49.6 / 100 | C |
| 스킬 풀 적용 후 | 79.7 / 100 | A |
| 카파시 미션/Tradeoff 자리 추가 후 | 79.6 / 100 | A |

> 카파시 자리는 자동 채점 항목이 아니라 사람용 시그널 강화이므로 점수 영향은 없습니다. 점수 유지 + LLM의 룰 인지 품질 향상이 목표입니다.

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

<br/>

### `/guide-audit` 호출 방식

| 호출 | 동작 |
|------|------|
| `/guide-audit` | 현재 프로젝트의 모든 가이드 통합 채점 |
| `/guide-audit <경로>` | 디렉토리면 프로젝트 채점, `.md` 파일이면 단일 파일 채점 |

→ Codex에서는 `$guide-audit`. 채점 결과는 콘솔에만 출력되며 파일을 만들지 않습니다. 내부적으로 `score_guide.py` (Python 3, 표준 라이브러리만 사용)가 `rubric-schema.json`을 읽어 결정적 채점합니다.

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
| `claude` | `CLAUDE.md` + `.claude/skills/learn/SKILL.md` | — |
| `agents` | `AGENTS.md` + `.agents/skills/learn/SKILL.md` + `.agents/workflows/learn.md` | — |
| `both` | `AGENTS.md` (모든 위치) + `.claude/skills/learn/` + `.agents/skills/learn/` + `.agents/workflows/learn.md` | `CLAUDE.md` = `@./AGENTS.md` 한 줄 |
| (없음) | 위 3개 중 어느 환경인지 사용자에게 묻고 대기합니다 | — |

`both` 모드는 본문을 `AGENTS.md` 한 파일에만 둡니다. Claude Code는 `CLAUDE.md`의 `@./AGENTS.md` import를 자동 따라가 같은 본문을 봅니다. 단일 파일만 편집하므로 sync drift가 구조적으로 불가능합니다.

<br/>

### 동작 흐름 (스킬이 하는 일)

1. 인자 파싱 → 모드 확정 (인자 없으면 사용자에게 환경 질문)
2. git 리포 검증 (필수 아님 — 없어도 진행)
3. 기존 파일 충돌 검사 (있으면 사용자 확인 후 백업 또는 덮어쓰기)
4. 영역 자동 탐지 (`apps/`, `frontend`, `backend`, `database`, ...) → 사용자 검토
5. 영역별 가이드 초안 작성 (8섹션 + 카파시 미션/Tradeoff 자리) → 사용자 승인
6. 파일 생성 (root map + 영역 가이드 + `learn` 스킬). Both 모드면 `CLAUDE.md`는 `@./AGENTS.md` 한 줄짜리 import 파일로 생성
7. 마무리 안내 + `/guide-audit`로 채점 권장

<br/><br/>

## FAQ

**Q. CLAUDE.md 하나로 충분한 작은 프로젝트인데도 써야 하나요?**

영역이 1개면 효과가 적습니다. 2~3개부터 의미가 있고 5개 이상에서 진가가 드러납니다.

**Q. 기존 CLAUDE.md가 있는데 덮어써지나요?**

검출 시 백업 옵션을 제공합니다. 사용자 확인 전에는 덮어쓰지 않습니다.

**Q. 한 프로젝트에 Claude Code 사용자와 Codex 사용자가 섞여 있다면?**

`both` 모드로 생성하세요. `AGENTS.md`가 단일 진실 공급원이 되고 `CLAUDE.md`는 `@./AGENTS.md` import로 자동 동기화됩니다.

**Q. `/learn`은 어떻게 동작하나요?**

현재 작업 영역을 추론해 그 영역 가이드의 "⚠️ LEARNED CAUTIONS" 섹션에 한 줄 추가합니다. 영역이 모호하면 사용자에게 확인합니다.

호출은 에이전트별로 다릅니다 — Claude Code/Cursor/Antigravity는 `/learn`, Codex는 `$learn`. 인자 없이 호출하면 최근 대화에서 잘못된 내용을 자동 추출합니다.

**Q. `/guide-audit`는 가이드를 수정하나요?**

아니요. 읽기 전용입니다. 채점 결과만 콘솔에 출력하고 개선 추천을 보여줍니다. 적용 여부는 사용자가 결정합니다.

**Q. 카파시 첫 줄 미션/Tradeoff는 꼭 채워야 하나요?**

자동 채점에 포함되지 않지만 영역 가이드 품질에 큰 영향을 줍니다. 영역 진입 시 LLM이 본질적 목적을 즉시 인지하고, Tradeoff를 통해 경계 케이스에서 룰의 한계를 함께 고려하게 됩니다. 빈 자리는 placeholder로 둬서 사용자가 채울 자리를 명시합니다.
