---
name: guide-audit
description: 사용자가 `/guide-audit` (또는 Codex의 `$guide-audit`)으로 명시 호출했을 때만 동작한다. 자동/암묵 트리거 금지. 프로젝트 내 모든 CLAUDE.md/AGENTS.md를 발견·분류·채점해 루브릭 기준 프로젝트 총점을 산출한다. 인자에 따라 모드가 갈린다 — 인자 없으면 현재 작업 디렉토리를 프로젝트 루트로 보고 통합 채점, `/guide-audit <경로>` 형태로 파일 경로를 주면 단일 파일 채점. 결과는 콘솔에만 출력하고 파일을 만들지 않는다.
---

# guide-audit — CLAUDE.md/AGENTS.md 품질 채점

## 입력 형태

| 호출 | 동작 |
|------|------|
| `/guide-audit` (Codex는 `$guide-audit`) | 현재 작업 디렉토리(또는 git repo root)를 프로젝트 루트로 보고 통합 채점 |
| `/guide-audit <경로>` | 해당 경로가 디렉토리면 프로젝트 채점, 파일이면 단일 파일 채점 |

## 절차

1. **루트 확정**
   - 인자가 없으면 현재 작업 디렉토리에서 `git rev-parse --show-toplevel`을 시도해 repo root를 채점 루트로 삼는다. 실패하면 현재 작업 디렉토리.
   - 인자가 디렉토리면 그 경로를 루트로 삼는다.
   - 인자가 단일 `.md` 파일이면 단일 파일 채점 모드로 분기 (절차 5번으로).

2. **러너 위치 결정**
   - 스킬 자산: `<skill_dir>/score_guide.py`
   - 스킬은 일반적으로 `~/.claude/skills/guide-audit/score_guide.py` 또는 프로젝트의 `.claude/skills/guide-audit/score_guide.py`에 설치돼 있다.
   - 스키마: `<skill_dir>/rubric-schema.json` (러너가 자동 탐지)

3. **러너 실행 (프로젝트 모드)**
   - 명령: `python3 <skill_dir>/score_guide.py --project <root>`
   - 러너가 자동으로:
     - 가이드 파일 발견 (`CLAUDE.md`, `AGENTS.md`, `CLAUDE.local.md`)
     - 무시 디렉토리 제외 (`node_modules`, `.git`, `dist`, `build`, `target`, `.next`, `.venv`, `venv`, `__pycache__`)
     - 타입 분류 (root_map / area_guide / single_guide)
     - 카테고리별 채점 + anti-pattern 패널티
     - 트리 일관성(T) 채점
     - 가중 평균 → 프로젝트 총점

4. **결과 정리 후 출력**
   - 러너 stdout(JSON) 또는 표 형식을 파싱해 사용자에게 다음 순서로 보고:
     1. **프로젝트 총점 + 등급** (S/A/B/C/D)
     2. **파일별 점수 표** (path / type / file_score / grade)
     3. **카테고리별 breakdown** (가장 낮은 점수 카테고리 강조)
     4. **0점/부분점 항목의 evidence** (어떤 패턴이 안 잡혔는지)
     5. **트리 일관성 결과** (T1 누락 영역, T2 죽은 링크, T3 중복 규칙)
     6. **Top 3 개선 추천** (ROI 큰 순)
   - 절차 종료. 파일 생성/수정/commit 일절 없음.

5. **단일 파일 채점 (인자가 파일일 때)**
   - 명령: `python3 <skill_dir>/score_guide.py --file <path>`
   - 출력: file_score + 카테고리별 점수 + 0점 항목 evidence
   - 프로젝트 통합 채점(T 카테고리, 가중 평균)은 건너뛴다.

## 원칙

- **읽기 전용**: 가이드 파일을 수정하지 않는다. 채점 결과만 콘솔에 출력.
- **결정적 채점**: 패턴 매칭 기반이라 같은 입력 → 같은 점수. LLM 주관 평가가 끼지 않음.
- **루브릭 1:1 대응**: `rubric-schema.json`의 가중치/패턴을 그대로 사용. 점수 해석은 `references/rubric.md` 참조.

## 금지

- **명시 호출 없이 자동 발동 금지** — 사용자가 `/guide-audit`을 직접 입력하지 않은 상황에서 "지금 채점해드릴까요?" 류로 선제 발동하지 않는다.
- 채점 결과를 파일로 저장 (사용자가 명시적으로 `> result.md`로 리다이렉트할 때만)
- 채점 결과 기반으로 가이드 파일을 자동 수정 (개선 추천만 출력, 적용은 사용자 결정)
- 점수 인플레/디플레 — 스키마에 없는 가산점/감점을 임의로 적용

## 의존성

- Python 3.8+ (러너 스크립트 실행)
- 표준 라이브러리만 사용 (외부 패키지 불요)
- `git` (F1 신선도 채점에만 사용. 없으면 F1 skip)

## 트러블슈팅

- **"러너 스크립트를 찾을 수 없음"**: 스킬이 올바르게 설치됐는지 확인. `~/.claude/skills/guide-audit/score_guide.py` 또는 프로젝트의 `.claude/skills/guide-audit/score_guide.py`에 있어야 함.
- **"가이드 파일이 0개 발견됨"**: 채점 루트에 `CLAUDE.md`/`AGENTS.md`가 없거나 무시 디렉토리에만 있음. `/agentic-project-init`로 먼저 가이드를 생성하는 것이 선행 조건.
- **F1이 항상 skip**: git 히스토리가 없거나 파일이 commit된 지 7일 미만. 정상 동작.
