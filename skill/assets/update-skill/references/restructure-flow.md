# --restructure 영역 경계 재구성 절차

영역의 분할·병합·이름 변경·삭제를 다루는 별도 흐름. 일반 `/update`와 분리된 이유는:
- 결정이 비가역에 가까움 (파일 이동, 가이드 재배치, import 재연결까지 동반)
- 사용자 결정 보호 원칙(LEARNED_CAUTIONS 보존, 변경 이력 주석)을 별도 단계에서 더 엄격히 적용해야 함
- 일반 update 인터뷰 흐름에 끼우면 작업 시간이 크게 늘어남

호출:
- Claude Code/Cursor/Antigravity: `/update --restructure` 또는 `/update --restructure <영역>`
- Codex: `$update --restructure ...`

---

## 트리거 (일반 update에서 감지된 시점에 사용자가 별도 실행)

- 한 영역의 파일 수가 임계치 초과 (기본 50+, 사용자 조정 가능)
- 한 영역에 책임 카테고리가 여러 개 섞임 (예: 날짜·문자열·HTTP·DB 헬퍼가 한 `utils/`에)
- 영역이 비대해져 본문 가이드가 100줄을 넘김 (분할 안내가 부족하다고 판단되면)
- 사용자가 명시적으로 "이 영역을 둘로 쪼개자" 라고 요청

---

## 절차

### 1) 대상 영역 확정

- 인자 없으면 root map의 영역 목록을 보여주고 어느 영역을 다룰지 묻는다.
- 인자가 있으면 그 영역만 대상.
- 동시에 여러 영역을 다루지 않는다 (한 번에 한 영역). 영역이 여러 개라면 사용자 선택 후 차례로.

### 2) 현재 상태 스냅샷

- 대상 영역 폴더의 1-depth 파일 목록 + 각 파일의 첫 줄/주요 export 추출
- 현재 본문 가이드(AGENTS.md/CLAUDE.md)의 8섹션 내용 읽기
- 현재 `LEARNED_CAUTIONS.md` 항목 수와 내용 요약
- 외부에서 이 영역으로 들어오는 강결합 `@import` 목록 (다른 영역의 WHERE 확인)

### 3) 책임 카테고리 추출 (제안)

코드 스캔 기반으로 책임 군집을 추출해 사용자에게 제안:

```
src/utils/ 안에서 다음 책임 카테고리가 보입니다:

  [A] 날짜·시간 (8 파일): parse_date.ts, format_time.ts, ...
  [B] 문자열 (12 파일): slugify.ts, truncate.ts, ...
  [C] HTTP (5 파일): retry.ts, fetch_with_timeout.ts, ...
  [D] DB 헬퍼 (3 파일): db_connect.ts, ...
  [?] 분류 모호 (4 파일): misc.ts, helpers.ts, common.ts, util.ts

분류가 맞나요? (수정/병합/추가 가능)
```

사용자 응답에 따라 카테고리 확정. 모호한 파일은 사용자가 분류하거나 그대로 두기로 결정.

### 4) 재구성 옵션 제시

확정된 카테고리를 바탕으로 옵션 제시 (`AskUserQuestion` 사용 권장):

```
src/utils/ 를 어떻게 재구성할까요?

[1] 카테고리별 분할 — utils/{date, string, http, db} 4개 서브영역으로 분할
[2] 책임별 별도 영역 — src/lib/date/, src/lib/string/ 등으로 영역 자체 분리
[3] 일부만 분할 — DB만 떼서 src/db-helpers/ 로 (날짜·문자열·HTTP는 utils 유지)
[4] 다른 안 (자유 입력)
[5] 지금 안 정함 (취소)
```

### 5) 이동 계획 작성 (사용자 확인 필수)

선택된 옵션을 구체적인 이동 계획으로 변환:

```
이동 계획:

  파일 이동:
    src/utils/parse_date.ts → src/lib/date/parse.ts
    src/utils/format_time.ts → src/lib/date/format.ts
    ... (8건)

  영역 가이드:
    + 새 영역 src/lib/date/ 생성 — AGENTS.md (가벼운 뼈대), LEARNED_CAUTIONS.md (빈 placeholder)
    + 새 영역 src/lib/string/ 생성 — 동일
    - 기존 src/utils/AGENTS.md 의 8섹션 중 일부 내용 이전 (아래 매핑 참조)
    - 기존 src/utils/ 영역 자체는 유지? 삭제?

  root map:
    - "src/utils" 항목 제거 (또는 축소)
    + "src/lib/date", "src/lib/string", ... 항목 추가

  강결합 @import 재연결:
    apps/api/WHERE 의 @../utils/AGENTS.md → @../lib/date/AGENTS.md (필요한 영역만)
    ... (3건)

이대로 진행할까요? 단계별 확인 옵션도 있습니다.
```

**원칙**:
- 사용자가 명시 승인하기 전에 어떤 파일도 이동·수정하지 않는다.
- 옵션: "한 번에 전체 진행" / "단계별로 확인하며 진행" / "취소". 단계별을 기본으로 권장.

### 6) LEARNED_CAUTIONS.md 이전 (가장 신중한 단계)

이게 restructure에서 가장 무거운 의사결정이다. 사용자 결정 자산을 잃지 않도록.

**원칙**:
- LEARNED_CAUTIONS.md의 각 항목은 새 영역 중 어디로 가야 하는지 사용자가 결정한다. AI가 자동 분류 금지.
- 항목별로 사용자에게 묻는다 (한꺼번에 묶어 제시하되 결정은 항목별):

```
src/utils/LEARNED_CAUTIONS.md 의 12개 항목을 어디로 옮길까요?

  [1] (2026-03-12) Date 파싱 시 타임존 명시 안 하면 UTC 가정됨
       → src/lib/date/ 로 이전?
  [2] (2026-03-18) DB 커넥션 풀 누수 — connect 후 finally close 누락 패턴
       → src/lib/db/ 로 이전?
  [3] (2026-04-02) slugify 한국어 처리 시 NFC 정규화 필수
       → src/lib/string/ 로 이전?
  ...
```

선택지:
- 명시한 새 영역으로 이전
- 다른 영역으로 (자유 입력)
- 분류 모호 → 임시 영역 또는 원본 위치 유지
- 이 항목 자체 폐기 (사용자 명시 동의 필요, 기본은 보존)

이전 시 형식:
- 원본 항목 그대로 새 위치 LEARNED_CAUTIONS.md에 추가
- 원본 파일에는 변경 이력 주석으로 남김:
  ```markdown
  <!-- moved 2026-05-21: "(2026-03-12) Date 파싱 시..." → src/lib/date/LEARNED_CAUTIONS.md -->
  ```

### 7) 본문 가이드 8섹션 재배치

각 섹션마다 다른 처리 필요:

| 섹션 | 처리 방법 |
|---|---|
| **WHAT** | 새 영역별로 새로 작성 (원본 WHAT을 분할). 사용자 확인. |
| **CONTENTS** | 자동 — 새 폴더 구조에 맞게 재생성 |
| **HOW** | 사용자 결정 자산. 어느 영역으로 갈지 항목별로 사용자가 결정. 공통이면 root map 또는 양쪽 모두. |
| **HOW NOT** | 사용자 결정 자산. LEARNED_CAUTIONS와 동일 절차로 항목별 결정. |
| **WHERE** | 자동 — 새 의존 관계 추출 + 사용자 확인 |
| **WHY** | 사용자 결정 자산. 항목별 결정. |
| **COMMANDS** | 빌드/테스트/린트는 자동 — 새 폴더 구조에 맞게 갱신. 영역 고유 가드는 사용자 결정. |

변경 이력 주석은 모든 사용자 결정 자산 이전 시 원본에 남긴다.

### 8) 외부 강결합 import 재연결

다른 영역의 WHERE 섹션이 사라진/이름 바뀐 영역을 `@import` 하고 있으면 자동으로 깨진다.

- 영향받는 `@import` 목록을 미리 추출 (2단계 스냅샷에서 확보)
- 새 영역 중 어디로 연결할지 사용자에게 묻는다:
  ```
  apps/api/AGENTS.md 의 WHERE 에서 @../utils/AGENTS.md 를 import 중입니다.
  새 영역들 중 어디로 연결할까요?
    [1] @../lib/date/AGENTS.md
    [2] @../lib/db/AGENTS.md
    [3] 둘 다
    [4] 강결합이 더 이상 필요 없음 (마크다운 링크로 약결합 전환)
  ```

### 9) 실행 + 단계별 검증

각 단계 끝나면 검증:

- 파일 이동 후: 원본 위치에 파일이 없고 새 위치에 있는지 `ls`로 확인
- 가이드 생성 후: 새 영역 폴더에 본문 가이드 + LEARNED_CAUTIONS.md 둘 다 있는지 확인
- @import 재연결 후: 새 경로가 실제로 존재하는지 확인
- root map 갱신 후: 영역 링크가 모두 유효한지 확인

검증 실패 시 즉시 중단하고 사용자에게 보고. 자동 롤백 시도 금지 (사용자가 git으로 되돌릴 수 있음).

### 10) 마무리 안내

```
--restructure 완료:

  파일 이동: 28건
  새 영역 생성: 3개 (src/lib/date, src/lib/string, src/lib/db)
  기존 영역 처리: src/utils 제거
  LEARNED_CAUTIONS 항목 이전: 12건 (모두 새 위치로)
  강결합 @import 재연결: 5건

다음 단계:
  - git status / git diff 로 변경 확인
  - 테스트 실행 권장 (파일 경로 변경으로 import 깨짐 가능)
  - 사용자가 직접 커밋 (자동 커밋 안 함)
  - 일반 /update 다시 실행해 새 영역들의 HOW/HOW NOT/WHY 등 인터뷰 가능
```

---

## 절대 원칙 (일반 update와 공유)

- 사용자 결정 사항 자동 덮어쓰기 금지
- LEARNED_CAUTIONS.md 항목은 사용자 결정 없이 이동·삭제 금지
- 변경 이력 주석 보존 — 원본에 "어디로 갔는지" 흔적을 남긴다
- 자동 커밋 금지

## 금지

- **자동 분류로 LEARNED_CAUTIONS 항목 이전 금지** — AI가 카테고리 추론은 가능하지만 결정은 항상 사용자
- **사용자 승인 없이 파일 이동 금지** — 5단계 이동 계획 승인 전에 어떤 파일도 옮기지 않는다
- **외부 영역의 강결합 @import 자동 재연결 금지** — 8단계에서 항상 사용자 확인
- **다중 영역 동시 처리 금지** — 한 번에 한 영역. 영역 간 의존이 복잡해 오류 가능성이 커진다
- **취소 시 부분 적용 상태로 두지 않기** — 어디까지 진행됐는지 사용자에게 보고하고, 되돌리려면 git을 쓰라고 안내
