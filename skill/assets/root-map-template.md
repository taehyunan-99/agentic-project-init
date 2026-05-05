# {PROJECT_NAME} - {AGENT_NAMES} 작업 지침

> 이 파일은 **map** 역할을 한다. 작업 시 해당 영역의 {GUIDE_FILENAME}을 먼저 읽고 진행한다.
>
> root에 모든 가이드를 몰아넣지 않고 영역별로 분리한 이유는 토큰 효율 + 컨텍스트 정확도다.
> 작업 영역만 정확히 참조하면 다른 영역 가이드가 컨텍스트를 오염시키지 않는다.

## 프로젝트 구조

```
{PROJECT_TREE}
```

## 영역별 가이드

작업 영역에 해당하는 {GUIDE_FILENAME}을 먼저 읽고 진행한다.

{AREA_LIST}
<!-- 예시:
- **apps/frontend** — UI 작업 → [`apps/frontend/CLAUDE.md`](apps/frontend/CLAUDE.md)
- **apps/backend** — API 작업 → [`apps/backend/CLAUDE.md`](apps/backend/CLAUDE.md)
-->

## 영역 가이드의 구조

각 영역의 {GUIDE_FILENAME}은 다음 7섹션으로 구성된다:

1. **WHAT** — 이 모듈이 무엇을 하는가
2. **CONTENTS** — 디렉토리 맵 + 기술 스택
3. **HOW** — 일반적인 수정은 어떻게 하는가
4. **HOW NOT** — 시스템을 깨뜨리는 비명백한 함정
5. **WHERE** — 다른 모듈과의 의존성
6. **WHY** — 코드에 안 적힌 배경 지식
7. **LEARNED CAUTIONS** — `/learn`으로 누적

## 주의사항 학습 (`/learn`)

작업 중 실수가 발생하면 `/learn [메모]`로 해당 영역 {GUIDE_FILENAME}의 "⚠️ LEARNED CAUTIONS" 섹션에 누적한다.

- 인자 없이 호출하면 최근 대화에서 자동 추론
- 인자가 있으면 그 내용을 추가
- 커맨드 위치: {LEARN_COMMAND_PATH}
