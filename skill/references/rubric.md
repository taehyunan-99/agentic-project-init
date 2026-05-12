# Agentic Project Init — 가이드 파일 품질 루브릭 v1.6

> **v1.6 변경**: "@import 최소주의 원칙" 섹션 신설. 카파시 4원칙(명시성·단순성·surgical·검증가능) 시선에서 @import는 Both 모드 sync + 영역 진입 후 강결합 의존성에만 허용하고, 그 외 모든 참조는 마크다운 링크를 우선한다. `work-checklist.md` 신설 — 가이드 작업 전 점검할 18개 체크리스트.
>
> **v1.5 변경**: G1 안티패턴에 **markdown 디렉토리 트리** 검출 추가 (코드블록 안의 `├`/`└` 라인 5개 이상이면 -3점). `ls`로 알 수 있는 정보를 가이드에 적는 패턴을 도구가 잡도록 함.
>
> **v1.4 변경**: `@./AGENTS.md` 같은 import 한 줄짜리 redirect 파일을 인식해 import 대상의 점수를 차용. 가중 평균은 본문 파일만 카운트 (sync_group 중복 방지).

---

> AI 에이전트용 가이드 파일(`CLAUDE.md` / `AGENTS.md` / 영역 가이드)의 품질을
> 100점 만점으로 평가하는 내부 기준서.
>
> **기본 단위는 "프로젝트 통합 검사"** — 단일 파일이 아니라 프로젝트 내 모든
> `CLAUDE.md` / `AGENTS.md`를 발견·분류·채점한 뒤 트리 합산 점수를 산출한다.
>
> 두 가지 용도로 공유한다.
> 1. **내부 검증** — 이 스킬의 변경이 원칙에 부합하는지 셀프 채점
> 2. **공식 기능** — 사용자가 자신의 프로젝트를 수시로 점검 (예: `/audit`)

## 설계 원칙

이 루브릭은 다음 명제 위에 만든다.

> **"가이드 파일은 사람용 README가 아니라, AI가 같은 실수를 반복하지 않게 하는 가드레일이다."**

- 코드만 봐도 알 수 있는 내용은 **감점은 아니지만 가점도 아니다**. 점수의 기준은 "AI가 이 파일을 안 읽었다면 잘못했을 행동을 막아주는가".
- **프로젝트는 트리다.** 공식 문서: "발견된 모든 파일은 서로를 재정의하지 않고 컨텍스트에 연결됩니다." → 개별 파일 채점에 더해 트리 전체의 정합성도 봐야 한다.
- 평가 항목은 가능한 한 **자동 측정 가능**해야 한다. 정량 측정이 어려운 항목은 휴리스틱(키워드/구조/길이)으로 근사하고 "휴리스틱"임을 명시한다.

## 채점 단위 (v1.2 핵심 변경)

### Step 1 — 발견
프로젝트 루트부터 모든 디렉토리를 재귀 스캔하여 `CLAUDE.md`, `AGENTS.md`, `CLAUDE.local.md` 파일을 수집. (단, `node_modules/`, `.git/`, `dist/`, `build/` 등 표준 ignore 디렉토리는 제외.)

### Step 2 — 타입 분류
각 파일을 다음 3개 타입 중 하나로 분류:

- **Type 1 — Root map**: 프로젝트 루트 + 영역 라우팅 구조(영역별 가이드 섹션 + 영역 폴더 링크)
- **Type 2 — 영역 가이드**: 서브디렉토리에 위치하거나, 7섹션 템플릿(WHAT/HOW NOT 등) 키워드 다수 포함
- **Type 3 — 단일 가이드**: 루트에 있지만 map 구조가 아닌 일반 단일 파일

### Step 3 — 파일별 채점
각 파일을 100점 스케일로 채점 (`(adjusted_raw / applicable_max) * 100`).

### Step 4 — 트리 레벨 채점
T 카테고리(영역 누락, 죽은 link, 규칙 중복)는 **트리 전체에 1회만 적용**하여 별도 점수 산출.

### Step 5 — 프로젝트 총점
```
project_score = weighted_avg(file_scores) - tree_penalty
```
- `weighted_avg`: Type 1은 가중치 2, Type 2/3은 가중치 1 (root map의 영향력 반영).
- `tree_penalty`: T 카테고리에서 잃은 점수가 그대로 프로젝트 총점에서 차감.

### 점수 등급
- **90+** AI-Ready (S) / **75-89** Healthy (A) / **60-74** Functional (B) / **40-59** Fragile (C) / **0-39** Hostile (D)

---

## 카테고리 A — Non-Obvious Invariants (25점) 🎯

**"코드만 봐선 알 수 없는 것"을 담고 있는가.** 핵심 카테고리.

### A1. HOW NOT 또는 "금지" 섹션 존재 (8점) — applies_to: 2, 3
- 만점(8): "HOW NOT", "⛔", "금지", "Never", "Don't", "주의사항" 키워드 섹션 + 항목 3개 이상.
- 부분(4): 섹션 존재, 항목 0~2개.
- 0점: 섹션 없음.

### A2. 금지 항목마다 이유 명시 (7점) — applies_to: 2, 3
- 만점(7): HOW NOT의 모든 항목에 이유 패턴(` — `, ` because `, ` 왜냐`, ` 때문`, ` reason`, ` so that `, `→`).
- 부분(4): 절반 이상 이유 있음.
- 0점: 대부분 이유 없음.

### A3. WHY / 배경 지식 섹션 (5점) — applies_to: 2
- 만점(5): WHY 섹션 + 1줄 이상 실제 내용 (placeholder 제외).
- 0점: 없거나 placeholder만.

### A4. LEARNED CAUTIONS — 섹션 + 누적 활동 통합 (5점) — applies_to: 2
- 만점(5): LEARNED CAUTIONS 섹션 + `- (YYYY-MM-DD)` 형식 누적 항목 1개 이상.
- 부분(2): 섹션은 있으나 비어있음.
- 0점: 섹션 없음.

---

## 카테고리 B — Specificity (20점) 📐

### B1. 추상 표현 비율 (10점) — applies_to: 1, 2, 3
- 측정: vague_terms 등장 / 전체 항목 수.
  - ko: `깨끗하게`, `잘 짜`, `잘 작성`, `잘 처리`, `잘 관리`, `적절히`, `꼼꼼하게`, `신경 써서`, `주의해서`, `올바르게`, `좋은 코드`
  - en: `clean code`, `good practice`, `properly`, `carefully`, `well-written`, `appropriate`, `best practice`, `write clean`
- 만점(10): ≤ 5%. 부분(5): ≤ 15%. 0점: > 15%.

### B2. 측정 가능한 규칙 (10점) — applies_to: 2, 3
- 만점(10): 다음 패턴 5개 이상 매치.
  - 숫자 기준, 절대 금지/필수, 강제 표현, 코드블록 안 명령어, PR/CI 가드, 절대 경로.
- 부분(5): 1~4개. 0점: 0개.

---

## 카테고리 C — Commands & Workflows (15점) ⚡

### C1. 빌드/테스트/린트 명령어 명시 (10점) — applies_to: 1, 2, 3
- 만점(10): build/test/lint/typecheck 중 3종 이상 명시 (fenced + inline 둘 다 인정).
- 부분(5): 1~2종. 0점: 없음.

### C2. 명령어 가드 (5점) — applies_to: 1, 2, 3
- 만점(5): "watch 모드 금지", "production DB 직접 쓰기 금지" 등 1개 이상.
- 0점: 없음.

---

## 카테고리 D — Structure & Discoverability (18점) 🧱

### D1. 마크다운 헤딩 구조 (3점) — applies_to: 1, 2, 3
- 만점(3): H1 1개 + H2 ≥ 3개. 부분(1): H2 1~2개. 0점: 없음.

### D2. Map 링크 (3점) — applies_to: 1
- 만점(3): 영역별 가이드 섹션 + 모든 영역 가이드 파일로의 상대경로 링크.
- 부분(1): 일부 링크. 0점: 없음.

### D2'. 8섹션 템플릿 준수 (3점) — applies_to: 2 ⭐ v1.3 확장
- 만점(3): 8섹션 중 6개 이상 매칭.
- 부분(1): 4~5개. 0점: 3개 이하.
- *v1.3 변경*: 영어 키워드만 매칭하던 동작을 **영어/한국어 aliases 매칭**으로 확장. 자생 한국어 가이드도 정상 인정.

| canonical | aliases (헤딩에 포함되면 매칭) |
|---|---|
| WHAT | WHAT, 역할, What |
| CONTENTS | CONTENTS, 포함 내용, 구성, 현재 스펙, Contents, 내용 |
| HOW | HOW, 수정 방법, 작업 방법, How, 어떻게 |
| HOW NOT | HOW NOT, 금지, 금지 사항, 주의사항, ⛔, Don't, Never |
| WHERE | WHERE, 의존성, 경계, 다른 영역, Where, Boundaries |
| WHY | WHY, 배경, 이유, 맥락, Why, Context, Background |
| COMMANDS | COMMANDS, 명령어, 빌드, Commands, Build |
| LEARNED CAUTIONS | LEARNED CAUTIONS, 학습된 주의사항, ⚠️, Lessons, Pitfalls |

### D3. 길이 (3점) — applies_to: 1, 2, 3
- 만점(3): **100줄 이하** (영상 권장 그대로).
- 부분(1): 100~200줄. 0점: 200줄 초과.
- *예외*: D4의 분할로 본문이 100줄 이하면 만점.

### D4. @import / 분할 활용 (3점) — applies_to: 1, 2, 3
- 만점(3): `@./...md` import ≥ 1 OR 외부 마크다운 링크 ≥ 2.
- 부분(1): 외부 링크 1개. 0점: 없음.
- *v1.6 보강*: 양적 매칭만 보는 D4 점수와 별개로, **"어디에 @import를 써야 하는가"는 아래 "@import 최소주의 원칙"을 따른다.** 자동 채점은 양만 본다.

---

## 부속 원칙 — @import 최소주의 ⭐ v1.6 신설

`@import`는 컨텍스트에 본문을 **자동 주입**하는 강한 단언이다. 카파시 4원칙으로 보면 다음 비용이 있다.

| 카파시 원칙 | @import의 비용 |
|---|---|
| Don't assume — 가정 명시 | 침묵으로 컨텍스트 주입 → LLM이 자기 가정을 인지 못함 |
| Simplicity First | 한 단계 추상화 추가 |
| Surgical changes | 한 줄 변경으로 모든 미래 세션에 영향 |
| Define success criteria | 항상 로드되니 "이 정보가 작동했는지" 사후 추적 불가 |

→ **@import는 그 추상화 없이는 안 되는 케이스에만 쓴다.** 그 외는 마크다운 링크가 카파시 원칙에 더 부합한다.

### @import 허용 케이스 (3가지)

| 케이스 | 위치 | 이유 |
|---|---|---|
| 1. Both 모드 CLAUDE.md ↔ AGENTS.md | 모든 레벨 (root + 영역) | 에이전트 호환 sync. 마크다운 링크로 대체 불가 |
| 2. 영역 진입 후 강결합 의존 (API contract / schema SoT) | 영역 가이드 안에서만 | 영역 진입 후라 토큰 비용 부담 없음. 침묵의 가정 방지가 더 큼 |
| (제외) root에서 영역 자동 import | — | map의 토큰 절약 핵심 가치 보존 |

### 마크다운 링크 우선 케이스

- 영역 라우팅 (root → 영역 가이드)
- 영역 간 약결합 cross-link (호출 관계·도메인 공유)
- 공통 정책 (Git 컨벤션·DB 변경 절차 등)
- 보조 docs 참조

### 결정 기준 — 결합의 "거리"

| 결합 강도 | 사례 | 권장 |
|---|---|---|
| 매우 강함 — 한쪽 변경 = 다른쪽 즉시 깨짐 | API contract, schema 정의 | **@import** |
| 강함 — 작업 시 동시 검토 권장 | 같은 도메인 개념 공유 | 마크다운 링크 + WHERE 섹션 |
| 보통 — 호출 관계 | 한쪽이 다른쪽 라이브러리 사용 | 마크다운 링크 |

**"매우 강함 vs 강함"의 경계가 모호한 케이스는 사용자 판단으로 결정한다.** 자동 룰을 강제하지 않는다.

### 영역 진입 시나리오 (사례)

```
1. root CLAUDE.md (얇은 map, 영역 라우팅 마크다운 링크) → 항상 로드
2. LLM이 "apps/backend 작업하자" 결정 → backend/AGENTS.md 로드 (영역 진입)
3. backend/AGENTS.md 안에 @../digital_twin/AGENTS.md import → 자동 함께 로드
   ← 영역 진입 후라 토큰 비용 적정. 침묵의 가정 방지 가치가 큼.
```

map의 토큰 절약 핵심(영역 1개만 로드)은 보존되고, 강결합 의존성만 자동 끌려옴.

### D5. HTML 주석으로 메타 안내 격리 (3점) ⭐ v1.2 신설 — applies_to: 1, 2, 3
- 만점(3): `<!-- ... -->` 블록 ≥ 2개 + 그 내부 총 라인 수 ≥ 5줄.
  - 격리 대상: 작성 가이드, placeholder 안내, 인용블록 메타 설명 등 **사람만 봐도 되는 콘텐츠**.
- 부분(1): 주석 블록 1개 이상이지만 라인 수 < 5.
- 0점: HTML 주석 없음.
- *근거*: 공식 문서 "블록 수준 HTML 주석은 컨텍스트에 주입되기 전 제거됩니다." → 사람용 안내문은 주석으로, 토큰 비용 0. (Read 도구로 직접 열 때는 보임)

---

## 카테고리 E — Cross-Reference & Boundaries (7점) 🔗

### E1. WHERE / 의존성 명시 (4점) — applies_to: 2
- 만점(4): WHERE 섹션 OR "의존", "depends on", "called by", "피의존" 키워드 ≥ 1.
- 0점: 없음.

### E2. 다른 영역 cross-link (3점) — applies_to: 2
- 만점(3): 다른 영역의 가이드 파일로 가는 마크다운 링크 ≥ 1.
- 0점: 없음.

---

## 카테고리 F — Living Document Signals (5점) 🌱

### F1. 마지막 수정 신선도 (5점) — applies_to: 1, 2, 3
- 만점(5): git last commit ≤ 90일.
- 부분(2): 90~180일. 0점: > 180일.
- *skip_if*: git 정보 없음 OR 파일 생성 < 7일.

---

## 카테고리 H — Placement & Multi-Agent (7점) 🌐

### H1. 올바른 위치 (3점) — applies_to: 1, 2
- 만점(3): 자동 로드 위치(루트의 `CLAUDE.md`/`AGENTS.md`/`.claude/CLAUDE.md`, 또는 서브디렉토리의 `CLAUDE.md`/`AGENTS.md`).
- 부분(1): `docs/` 등 비자동 로드 위치.
- 0점: 잘못된 위치.

### H2. AGENTS.md 동시 존재 (2점) — applies_to: 1
- 만점(2): 같은 디렉토리에 CLAUDE.md AND AGENTS.md 둘 다 존재.
- 부분(1): 한쪽만. 0점: 둘 다 없음 (사실상 N/A).

### H3. CLAUDE.md ↔ AGENTS.md sync 정합성 (2점) ⭐ v1.2 신설 — applies_to: 1
- 만점(2): 두 파일이 (a) `@import`로 연결됨 OR (b) 내용이 거의 동일(diff < 5%).
- 부분(1): 한쪽만 존재 (단일 도구 환경, 정상).
- 0점: 양쪽 다 있는데 import도 없고 내용도 다름 (drift 위험).
- *근거*: 영상 "AGENTS.md 트릭" — 한 파일을 두 도구가 공유. drift된 두 파일은 가장 위험한 안티패턴.

---

## 카테고리 T — Tree Consistency (3점) 🌳 ⭐ v1.2 신설

> 트리 전체에 1회만 적용. 개별 파일 채점이 아니라 **프로젝트 단위 정합성**.

### T1. 영역 누락 (1점)
- 만점(1): root map이 가리키는 모든 영역에 실제 가이드 파일 존재.
- 0점: 1개 이상 누락.
- *자동 검출*: root map의 마크다운 링크 vs 실제 파일 시스템 비교.

### T2. 죽은 cross-link (1점)
- 만점(1): 모든 영역 가이드의 cross-link가 실제 파일/섹션을 가리킴.
- 0점: 1개 이상 broken.
- *자동 검출*: 모든 `*.md`의 마크다운 링크 → 파일 존재 + 앵커 매치 확인.

### T3. 규칙 중복 (1점) ⭐ v1.3 sync 쌍 제외
- 만점(1): 같은 bullet/규칙이 여러 가이드에 반복 등장하지 않음.
- 0점: 5개 이상 중복.
- *자동 검출*: 모든 가이드의 bullet 텍스트를 normalize 후 fuzzy match (≥ 0.85 유사도).
- *권고*: 중복은 root로 끌어올리거나 한 곳만 남기고 제거.
- *v1.3 제외 룰*: **같은 디렉토리의 `CLAUDE.md` ↔ `AGENTS.md` 쌍 사이 bullet 중복은 카운트하지 않는다.** 그 둘은 sync 의도된 중복이므로 안티패턴이 아님. (`both` 모드 프로젝트가 부당 감점되던 문제 해결)

---

## 카테고리 G — Anti-Patterns (감점, 최대 -5점)

### G1. README 복붙형 설명 (-3점) ⭐ v1.5 확장
두 그룹 중 하나라도 트리거되면 -3점:
- **자연어 패턴 (5번 이상)**: "이 프로젝트는 X 사용", "src/에 Y 있음", "uses React", "is a Python application" 등 코드로 알 수 있는 설명.
- **디렉토리 트리 (1번 이상)** ⭐ v1.5 신설: markdown 코드블록 안에 `├`/`└` 라인이 5개 이상이면 안티패턴. `ls`로 알 수 있는 정보를 가이드에 적으면 컨텍스트 토큰과 LLM 주의력을 낭비한다.

### G2. 인사말 / 마무리 멘트 (-1점)
- "안녕하세요", "Hello", "감사합니다", "Thank you" 등 1개 이상.

### G3. 일반 베스트 프랙티스 나열 (-1점)
- "DRY 원칙", "SOLID 원칙", "write clean code", "DRY principle", "SOLID principles", "KISS principle" 등 3개 이상.

---

## 종합 점수 계산

### 파일 단위 (각 CLAUDE.md/AGENTS.md)

```
applicable_max = sum(item.max_points for item in items if type_code in item.applies_to)
raw_earned    = sum(item.computed_score)
anti_penalty  = max(-5, sum(triggered_penalties) * -1)
adjusted_raw  = max(0, raw_earned + anti_penalty)
file_score    = round((adjusted_raw / applicable_max) * 100, 1)
```

### 트리 단위

```
tree_max     = sum(T.max_points)  # = 3
tree_earned  = sum(T.computed_score)
tree_penalty = (tree_max - tree_earned) * tree_penalty_weight  # 기본 3.33
                # T에서 1점 잃을 때마다 프로젝트 총점에서 약 3.33점 차감
                # → T 만점이면 페널티 0, T 0점이면 -10점
```

### 프로젝트 총점

```
weights        = {Type 1: 2, Type 2: 1, Type 3: 1}
weighted_avg   = sum(file_score * weights[file.type]) / sum(weights[file.type])
project_score  = round(max(0, min(100, weighted_avg - tree_penalty)), 1)
```

## 타입별 적용 항목 요약

| 항목 | 만점 | Type 1 | Type 2 | Type 3 |
|------|:--:|:--:|:--:|:--:|
| A1 HOW NOT | 8 | – | ✅ | ✅ |
| A2 이유 명시 | 7 | – | ✅ | ✅ |
| A3 WHY | 5 | – | ✅ | – |
| A4 LEARNED | 5 | – | ✅ | – |
| B1 추상 표현 | 10 | ✅ | ✅ | ✅ |
| B2 측정 가능 | 10 | – | ✅ | ✅ |
| C1 명령어 | 10 | ✅ | ✅ | ✅ |
| C2 명령어 가드 | 5 | ✅ | ✅ | ✅ |
| D1 헤딩 | 3 | ✅ | ✅ | ✅ |
| D2 Map 링크 | 3 | ✅ | – | – |
| D2' 7섹션 | 3 | – | ✅ | – |
| D3 길이 | 3 | ✅ | ✅ | ✅ |
| D4 @import | 3 | ✅ | ✅ | ✅ |
| D5 HTML 주석 | 3 | ✅ | ✅ | ✅ |
| E1 WHERE | 4 | – | ✅ | – |
| E2 cross-link | 3 | – | ✅ | – |
| F1 신선도 | 5 | ✅ | ✅ | ✅ |
| H1 위치 | 3 | ✅ | ✅ | – |
| H2 AGENTS.md 동시 | 2 | ✅ | – | – |
| H3 sync 정합성 | 2 | ✅ | – | – |
| **applicable_max** | **97** | **52** | **90** | **67** |
| G1~G3 감점 | -5 | ✅ | ✅ | ✅ |
| **T 카테고리 (트리 1회)** | 3 | — 트리 전체 — | | |

> A~H 합 = 97점, T 카테고리 = 3점, 총 100점.
> Type별 applicable_max가 다르므로 정규화로 100점 스케일 통일.

## 변경 이력

- **v1.2 (2026-05-12)** — 프로젝트 통합 검사 모델로 전환
  - 채점 단위: 단일 파일 → 프로젝트 전체 (root map + 모든 영역 가이드)
  - 신설: D5 (HTML 주석 격리), H3 (CLAUDE↔AGENTS sync), T 카테고리 (트리 일관성)
  - 가중치 재배분: D 20→18, E 10→7, H 5→7, T +3 = 100
  - D3 기준 100줄로 유지 (영상 권장 그대로)
- v1.1 (2026-05-12) — 리뷰 피드백 반영 (anti_penalty 단계, 100점 정확화, A4·F2 통합 등)
- v1 (2026-05-12) — 초기 정의
