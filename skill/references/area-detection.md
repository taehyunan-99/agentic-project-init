# 영역 자동 탐지 규칙

이 문서는 SKILL.md의 4단계(영역 자동 탐지)에서 따르는 휴리스틱이다.

## 목표

임의 프로젝트에서 "AI 에이전트가 작업할 때 컨텍스트를 분리해서 다루면 좋은 단위"를 추출한다.
완벽할 필요는 없다 — 사용자에게 후보를 제시하고 수정받는 것이 전제다.

## 1단계: 디렉토리 패턴 스캔

프로젝트 root에서 1-2 depth까지 스캔하여 다음 패턴에 매칭되는 폴더를 후보로 잡는다.

### Tier 1 — 거의 확실한 영역
이름만으로 영역으로 잡아도 거의 틀리지 않는 폴더들:

- `apps/*` 또는 `packages/*` (monorepo) — 각 하위 폴더 자체를 영역으로
- `frontend/`, `client/`, `web/`, `ui/`
- `backend/`, `server/`, `api/`
- `database/`, `db/`, `schema/`, `migrations/`
- `analysis/`, `notebooks/`, `eda/`, `research/`
- `airflow/`, `dags/`, `pipelines/`
- `docker/`, `infra/`, `infrastructure/`, `terraform/`, `k8s/`, `kubernetes/`
- `mobile/`, `ios/`, `android/`
- `ml/`, `models/`, `training/`
- `digital_twin/`, `simulation/`, `engine/` (도메인 특화)

### Tier 2 — 영역일 수도 아닐 수도
프로젝트 성격에 따라 영역이 될 수도 있고 단순 보조 폴더일 수도 있는 것들:

- `scripts/` — 보통 영역 아님 (공통 스크립트 모음). 단, 비중이 크면 영역으로.
- `docs/` — 보통 영역 아님 (문서 모음).
- `tests/` — 보통 영역 아님 (각 영역에 가까운 테스트는 그 영역에 둔다).
- `tools/`, `cli/` — 비중 보고 판단.

### Tier 3 — 영역 아님 (제외)
- `node_modules/`, `.venv/`, `venv/`, `__pycache__/`, `.git/`
- `dist/`, `build/`, `out/`, `target/`
- `.next/`, `.cache/`, `.pytest_cache/`, `.mypy_cache/`
- `data/` — 보통 데이터셋 저장소이며 코드 작업 영역 아님 (사용자에게 확인)
- 점(`.`)으로 시작하는 폴더는 기본 제외 (단 사용자가 명시적으로 포함 요청 시 예외)

## 2단계: 스택 추론

각 후보 영역에 대해 1-depth만 가볍게 훑어 기술 스택을 추정한다.

### JavaScript / TypeScript
- `package.json` → JS/TS 프로젝트
  - `dependencies`에 `react` → React
  - `next` → Next.js
  - `vue` → Vue
  - `vite` 또는 `vite.config.*` → Vite
  - `typescript` 또는 `tsconfig.json` → TypeScript

### Python
- `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile` → Python
  - `fastapi` → FastAPI
  - `django` → Django
  - `flask` → Flask
  - `pandas`/`numpy`/`scikit-learn` → 분석/ML
  - `airflow` → Airflow
  - `notebook`/`.ipynb` 파일 존재 → Jupyter

### 기타
- `Cargo.toml` → Rust
- `go.mod` → Go
- `pom.xml`/`build.gradle` → Java/Kotlin
- `Dockerfile`, `docker-compose*.yml` → Docker
- `*.sql`, `db_definition.md`, `schema.sql` → DB
- `dags/` 또는 `airflow.cfg` → Airflow
- `terraform/`, `*.tf` → Terraform/IaC

## 3단계: 사용자에게 제시

탐지 결과를 다음 형태로 제시한다:

```
탐지된 영역 (총 N개):

  apps/frontend  — React + Vite (package.json, vite.config.ts)
  apps/backend   — FastAPI (pyproject.toml, app/main.py)
  database       — PostgreSQL (db_definition.md, ERD.png)
  analysis       — Jupyter (notebooks/, requirements.txt)

이 목록 그대로 진행할까요?
- 추가/제외할 영역이 있다면 알려주세요 (예: "scripts도 영역으로", "analysis 빼주세요")
- 영역명/설명을 수정하고 싶으면 말씀해주세요
```

사용자가 수정하면 반영하고 다시 한 번 확인한다.

## Edge Case

- **영역이 0개로 탐지됨**: root에 코드가 평면적으로 배치된 작은 프로젝트. 사용자에게 직접 영역을 입력받거나, "전체를 하나의 영역으로" 옵션을 제시한다.
- **monorepo이고 `apps/*`가 매우 많음**: 너무 많으면 사용자에게 "주요 앱만 골라주세요"라고 묻는다. 모든 하위를 자동으로 다 가이드 파일로 만들면 부담스럽다.
- **`apps/foo` 안에 또 `frontend/backend` 분리**: 보통 `apps/foo` 자체를 한 영역으로 잡는 것이 자연스럽다. 사용자에게 깊이 선택권을 준다.
