#!/usr/bin/env python3
"""guide-audit 러너 — CLAUDE.md/AGENTS.md 품질 채점

표준 라이브러리만 사용. rubric-schema.json을 외부에서 읽어 채점.

사용법:
  python3 score_guide.py --project <root>     # 프로젝트 통합 채점
  python3 score_guide.py --file <md>          # 단일 파일 채점
  python3 score_guide.py --project <root> --json   # JSON 출력
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


SCHEMA_FILENAME = "rubric-schema.json"
DEFAULT_IGNORE_DIRS = {"node_modules", ".git", "dist", "build", "target", ".next", ".venv", "venv", "__pycache__"}
GUIDE_FILENAMES = {"CLAUDE.md", "AGENTS.md", "CLAUDE.local.md"}


# ────────────────────────────────────────────────────────────
# 데이터 모델
# ────────────────────────────────────────────────────────────

@dataclass
class FileResult:
    path: str
    type_code: int  # 1=root_map, 2=area_guide, 3=single_guide
    line_count: int
    raw_earned: float
    anti_penalty: float
    adjusted_raw: float
    applicable_max: float
    file_score: float
    grade: str
    category_scores: dict[str, dict] = field(default_factory=dict)
    item_evidence: list[dict] = field(default_factory=list)
    anti_pattern_hits: list[dict] = field(default_factory=list)
    import_redirect_to: str | None = None  # @import 한 줄 파일이면 대상 경로

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "type": self.type_code,
            "line_count": self.line_count,
            "file_score": self.file_score,
            "grade": self.grade,
            "category_scores": self.category_scores,
            "anti_pattern_penalty": self.anti_penalty,
            "anti_pattern_hits": self.anti_pattern_hits,
            "weak_items": [e for e in self.item_evidence if e["earned"] < e["max_points"]],
            "import_redirect_to": self.import_redirect_to,
        }


@dataclass
class TreeResult:
    earned: float
    max_points: float
    penalty: float
    missing_areas: list[str] = field(default_factory=list)
    broken_links: list[str] = field(default_factory=list)
    duplicate_rules: list[dict] = field(default_factory=list)


@dataclass
class ProjectResult:
    root: str
    project_score: float
    grade: str
    weighted_avg: float
    tree_penalty: float
    files: list[FileResult] = field(default_factory=list)
    tree: TreeResult | None = None
    top_recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "project_path": self.root,
            "project_score": self.project_score,
            "grade": self.grade,
            "weighted_avg": self.weighted_avg,
            "tree_penalty": self.tree_penalty,
            "files_audited": [f.to_dict() for f in self.files],
            "tree_results": {
                "T1_missing_areas": self.tree.missing_areas if self.tree else [],
                "T2_broken_links": self.tree.broken_links if self.tree else [],
                "T3_duplicate_rules": self.tree.duplicate_rules if self.tree else [],
            } if self.tree else None,
            "top_recommendations": self.top_recommendations,
        }


# ────────────────────────────────────────────────────────────
# 스키마 로드
# ────────────────────────────────────────────────────────────

def load_schema(start_dir: Path) -> dict:
    candidates = [
        start_dir / SCHEMA_FILENAME,
        Path(__file__).resolve().parent / SCHEMA_FILENAME,
        Path(__file__).resolve().parent.parent / SCHEMA_FILENAME,
    ]
    for path in candidates:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(f"rubric-schema.json not found. Tried: {[str(p) for p in candidates]}")


# ────────────────────────────────────────────────────────────
# 파일 발견 + 타입 분류
# ────────────────────────────────────────────────────────────

def discover_guides(root: Path, schema: dict) -> list[Path]:
    patterns = set(schema.get("discovery", {}).get("patterns", list(GUIDE_FILENAMES)))
    ignore_dirs = set(schema.get("discovery", {}).get("ignore_dirs", list(DEFAULT_IGNORE_DIRS)))
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs and not d.startswith(".")]
        for name in filenames:
            if name in patterns:
                found.append(Path(dirpath) / name)
    return sorted(found)


def classify_type(path: Path, root: Path, content: str) -> int:
    """타입 분류 휴리스틱.
    1 = root_map: repo root에 있고 영역 링크가 있는 map 구조
    2 = area_guide: 서브디렉토리에 있거나 8섹션(WHAT/CONTENTS/...) 템플릿
    3 = single_guide: repo root에 있는데 map 구조가 아닌 단일 가이드
    """
    is_at_root = path.parent.resolve() == root.resolve()
    has_area_section = bool(re.search(r"^#+\s*(영역별\s*가이드|Areas|영역\s*가이드)", content, re.MULTILINE))
    has_map_links = bool(re.search(r"\[[^\]]+\]\([^)]+/(CLAUDE|AGENTS)\.md\)", content))
    has_8sec = sum(
        1 for kw in ("WHAT", "CONTENTS", "HOW", "HOW NOT", "WHERE", "WHY", "LEARNED CAUTIONS")
        if re.search(rf"^#+\s*\d?\.?\s*\*?\*?{re.escape(kw)}", content, re.MULTILINE)
    ) >= 4

    if is_at_root and (has_area_section or has_map_links):
        return 1
    if has_8sec or not is_at_root:
        return 2
    return 3


# ────────────────────────────────────────────────────────────
# 헬퍼: 라인 카운트, 헤딩 카운트, HTML 주석 제외
# ────────────────────────────────────────────────────────────

def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--[\s\S]*?-->", "", text)


def is_import_redirect(text: str) -> str | None:
    """파일 본문이 단일 `@<상대경로>.md` import 한 줄이면 그 경로를 반환.

    HTML 주석과 빈 줄은 무시한다. both 모드의
    `CLAUDE.md = @./AGENTS.md` 구조를 알아채기 위해 사용.

    예시 인정 패턴:
        @./AGENTS.md
        @../shared/AGENTS.md
        @AGENTS.md

    여러 줄/본문이 섞여 있으면 None (그건 일반 가이드로 채점).
    """
    stripped = strip_html_comments(text)
    lines = [l.strip() for l in stripped.splitlines() if l.strip()]
    if len(lines) != 1:
        return None
    m = re.match(r"^@(\.{0,2}/?[\w./-]+\.md)\s*$", lines[0])
    return m.group(1) if m else None


def count_non_comment_lines(text: str) -> int:
    stripped = strip_html_comments(text)
    return sum(1 for line in stripped.splitlines() if line.strip())


def heading_counts(text: str) -> tuple[int, int]:
    h1 = len(re.findall(r"^# [^\n]+", text, re.MULTILINE))
    h2 = len(re.findall(r"^## [^\n]+", text, re.MULTILINE))
    return h1, h2


def find_section(text: str, keywords: list[str]) -> tuple[int, int] | None:
    """헤딩에 keyword가 포함된 섹션의 (start, end) byte offset 반환. 없으면 None."""
    pattern = re.compile(
        r"^(#{1,6})\s*.*?(?:" + "|".join(re.escape(k) for k in keywords) + r").*?$",
        re.MULTILINE | re.IGNORECASE,
    )
    match = pattern.search(text)
    if not match:
        return None
    start = match.start()
    level = len(match.group(1))
    after = text[match.end():]
    next_heading = re.search(rf"^#{{1,{level}}}\s", after, re.MULTILINE)
    end = match.end() + (next_heading.start() if next_heading else len(after))
    return start, end


def count_section_items(text: str, section_keywords: list[str]) -> int:
    span = find_section(text, section_keywords)
    if not span:
        return 0
    body = text[span[0]:span[1]]
    items = re.findall(r"^\s*[-*]\s+\S", body, re.MULTILINE)
    return len(items)


def section_body(text: str, section_keywords: list[str]) -> str:
    span = find_section(text, section_keywords)
    if not span:
        return ""
    return text[span[0]:span[1]]


# ────────────────────────────────────────────────────────────
# 카테고리별 채점기
# ────────────────────────────────────────────────────────────

def score_A1(text: str, item: dict) -> tuple[float, str]:
    section_kw = item["detection"]["section_keywords"]
    count = count_section_items(text, section_kw)
    if find_section(text, section_kw):
        if count >= 3:
            return 8.0, f"HOW NOT 섹션 + {count}개 항목"
        return 4.0, f"HOW NOT 섹션 + {count}개 항목 (만점 조건 ≥3)"
    return 0.0, "HOW NOT 섹션 없음"


def score_A2(text: str, item: dict, a1_score: float) -> tuple[float, str]:
    if a1_score == 0:
        return 0.0, "A1 0점이라 skip"
    section_kw = ["HOW NOT", "⛔", "금지", "Never", "Don't", "주의사항"]
    body = section_body(text, section_kw)
    if not body:
        return 0.0, "HOW NOT 본문 없음"
    items = re.findall(r"^\s*[-*]\s+(.+)$", body, re.MULTILINE)
    if not items:
        return 0.0, "HOW NOT 항목 없음"
    reason_patterns = item["detection"]["reason_patterns"]
    with_reason = sum(
        1 for it in items
        if any(p in it for p in reason_patterns)
    )
    ratio = with_reason / len(items)
    if ratio >= 1.0:
        return 7.0, f"{with_reason}/{len(items)} 항목에 이유 명시 (100%)"
    if ratio >= 0.5:
        return 4.0, f"{with_reason}/{len(items)} 항목에 이유 명시 ({ratio:.0%})"
    return 0.0, f"{with_reason}/{len(items)} 항목만 이유 명시 ({ratio:.0%})"


def score_A3(text: str, item: dict) -> tuple[float, str]:
    section_kw = item["detection"]["section_keywords"]
    body = section_body(text, section_kw)
    if not body:
        return 0.0, "WHY 섹션 없음"
    content_lines = [l for l in body.splitlines()[1:] if l.strip() and not l.strip().startswith("<!--")]
    placeholders = item["detection"]["placeholder_patterns"]
    is_placeholder = all(any(p in l for p in placeholders) or l.strip().startswith("{") for l in content_lines if l.strip())
    if content_lines and not is_placeholder:
        return 5.0, f"WHY 섹션 + {len(content_lines)}줄 콘텐츠"
    return 0.0, "WHY 섹션 비어있거나 placeholder만"


def score_A4(text: str, item: dict, file_path: Path) -> tuple[float, str]:
    section_kw = item["detection"]["section_keywords"]
    body = section_body(text, section_kw)
    if not body:
        return 0.0, "LEARNED CAUTIONS 섹션 없음"

    item_pattern = item["detection"]["item_pattern"]
    inline_items = re.findall(item_pattern, body, re.MULTILINE)

    # 새 구조: 본문 LEARNED CAUTIONS 섹션이 @./LEARNED_CAUTIONS.md 를 참조하면
    # 같은 폴더의 별도 파일에서 누적 항목을 함께 카운트한다.
    external_file = file_path.parent / "LEARNED_CAUTIONS.md"
    references_external = bool(re.search(r"@\./LEARNED_CAUTIONS\.md", body)) and external_file.exists()
    external_items: list = []
    if references_external:
        external_text = external_file.read_text(encoding="utf-8", errors="ignore")
        external_items = re.findall(item_pattern, external_text, re.MULTILINE)

    total_items = len(inline_items) + len(external_items)
    if total_items >= 1:
        if references_external:
            return 5.0, (
                f"누적 항목 {total_items}개 "
                f"(본문 {len(inline_items)} + LEARNED_CAUTIONS.md {len(external_items)})"
            )
        return 5.0, f"누적 항목 {total_items}개"

    if references_external:
        return 2.0, "LEARNED_CAUTIONS.md 분리 구조 — 별도 파일이 placeholder 상태"
    return 2.0, "섹션은 있으나 누적 항목 없음 (placeholder 상태)"


def score_B1(text: str, item: dict) -> tuple[float, str]:
    visible = strip_html_comments(text)
    visible_words = max(1, len(visible.split()))
    vague_terms = item["detection"]["vague_terms"]["ko"] + item["detection"]["vague_terms"]["en"]
    hits = 0
    for term in vague_terms:
        hits += len(re.findall(re.escape(term), visible))
    ratio = hits / max(1, visible_words / 100)  # per 100 words
    if hits == 0:
        return 10.0, "추상 표현 0개"
    if hits <= 2:
        return 5.0, f"추상 표현 {hits}개 (낮은 빈도)"
    return 0.0, f"추상 표현 {hits}개 (과다)"


def score_B2(text: str, item: dict) -> tuple[float, str]:
    visible = strip_html_comments(text)
    patterns = item["detection"]["regex_patterns"]
    hits = []
    for p in patterns:
        pattern = p["pattern"] if isinstance(p, dict) else p
        matches = re.findall(pattern, visible, re.MULTILINE | re.IGNORECASE)
        if matches:
            hits.append((p.get("name", pattern[:20]) if isinstance(p, dict) else pattern[:20], len(matches)))
    total = sum(c for _, c in hits)
    if total >= 5:
        return 10.0, f"측정 가능 패턴 {total}개 매치"
    if total >= 1:
        return 5.0, f"측정 가능 패턴 {total}개 매치 (만점 ≥5)"
    return 0.0, "측정 가능 패턴 0개"


def score_C1(text: str, item: dict) -> tuple[float, str]:
    visible = strip_html_comments(text)
    # 코드 블록 + 인라인 코드 모두 검사
    code_regions = []
    code_regions.extend(re.findall(r"```[\s\S]+?```", visible))
    code_regions.extend(re.findall(r"`[^`\n]+`", visible))
    blob = "\n".join(code_regions).lower()
    categories = item["detection"]["categories"]
    matched = set()
    for cat_name, cmds in categories.items():
        for cmd in cmds:
            if cmd.lower() in blob:
                matched.add(cat_name)
                break
    if len(matched) >= 3:
        return 10.0, f"명령어 카테고리 {len(matched)}개: {sorted(matched)}"
    if len(matched) >= 1:
        return 5.0, f"명령어 카테고리 {len(matched)}개: {sorted(matched)} (만점 ≥3)"
    return 0.0, "빌드/테스트/린트/타입체크 명령어 0개"


def score_C2(text: str, item: dict) -> tuple[float, str]:
    visible = strip_html_comments(text)
    patterns = item["detection"]["regex_patterns"]
    hits = 0
    for p in patterns:
        if re.search(p, visible, re.IGNORECASE):
            hits += 1
    if hits >= 1:
        return 5.0, f"명령어 가드 {hits}개 매치"
    return 0.0, "명령어 가드 없음"


def score_D1(text: str, item: dict) -> tuple[float, str]:
    h1, h2 = heading_counts(text)
    if h1 == 1 and h2 >= 3:
        return 3.0, f"H1×{h1} + H2×{h2}"
    if h2 >= 1:
        return 1.0, f"H1×{h1} + H2×{h2} (만점 조건: H1=1 AND H2≥3)"
    return 0.0, f"H1×{h1} + H2×{h2}"


def score_D2(text: str, item: dict, file_path: Path) -> tuple[float, str]:
    """root용 — 영역 링크 카운트"""
    visible = strip_html_comments(text)
    links = re.findall(r"\[[^\]]+\]\(([^)]+/(?:CLAUDE|AGENTS)\.md)\)", visible)
    if not links:
        return 0.0, "Map 링크 없음"
    # 실제 영역 폴더 수와 비교
    root = file_path.parent
    area_dirs = [d for d in root.iterdir() if d.is_dir() and not d.name.startswith(".") and d.name not in DEFAULT_IGNORE_DIRS]
    has_guide_dirs = sum(1 for d in area_dirs if (d / "CLAUDE.md").exists() or (d / "AGENTS.md").exists())
    if has_guide_dirs > 0 and len(links) >= has_guide_dirs:
        return 3.0, f"Map 링크 {len(links)}개 (영역 {has_guide_dirs}개와 일치)"
    if len(links) >= 1:
        return 1.0, f"Map 링크 {len(links)}개 (영역 폴더 {has_guide_dirs}개)"
    return 0.0, "Map 링크 0개"


def score_D2_prime(text: str, item: dict) -> tuple[float, str]:
    """area_guide용 — 8섹션 매칭 (영어/한국어 aliases 지원)

    스키마의 `required_sections`는 다음 두 포맷 모두 받는다:
    1. 문자열 리스트: ["WHAT", "CONTENTS", ...]
    2. aliases 객체: [{"canonical": "WHAT", "aliases": ["WHAT", "역할", ...]}, ...]
    """
    required = item["detection"]["required_sections"]
    headings = re.findall(r"^#+\s+(.+?)\s*$", text, re.MULTILINE)
    headings_blob = "\n".join(headings)

    matched: list[str] = []
    for sec in required:
        if isinstance(sec, dict):
            canonical = sec["canonical"]
            aliases = sec.get("aliases", [canonical])
        else:
            canonical = sec
            aliases = [sec]
        for alias in aliases:
            if re.search(re.escape(alias), headings_blob, re.IGNORECASE):
                matched.append(canonical)
                break

    n = len(matched)
    if n >= 6:
        return 3.0, f"섹션 {n}개 매치: {matched}"
    if n >= 4:
        return 1.0, f"섹션 {n}개 매치: {matched} (만점 ≥6)"
    return 0.0, f"섹션 {n}개 매치: {matched}"


def score_D3(text: str, item: dict) -> tuple[float, str]:
    lines = count_non_comment_lines(text)
    if lines <= 100:
        return 3.0, f"{lines}줄"
    if lines <= 200:
        return 1.0, f"{lines}줄 (만점 ≤100)"
    return 0.0, f"{lines}줄 (과다)"


def score_D4(text: str, item: dict) -> tuple[float, str]:
    visible = strip_html_comments(text)
    # @import 라인 또는 인라인 @path/file.md 둘 다 인정
    imports = re.findall(r"@[\w./-]+\.md\b", visible)
    external_links = re.findall(r"\[[^\]]+\]\((?!#)[^)]+\.md\)", visible)
    if len(imports) >= 1 or len(external_links) >= 2:
        return 3.0, f"@import {len(imports)}개 + 외부 md 링크 {len(external_links)}개"
    if len(external_links) == 1:
        return 1.0, f"외부 md 링크 1개 (만점 조건: @import ≥1 OR 외부링크 ≥2)"
    return 0.0, "@import / 외부 md 링크 없음"


def score_D5(text: str, item: dict) -> tuple[float, str]:
    blocks = re.findall(r"<!--[\s\S]*?-->", text)
    non_empty = [b for b in blocks if b.strip() not in ("<!---->", "<!-- -->")]
    total_lines = sum(b.count("\n") + 1 for b in non_empty)
    if len(non_empty) >= 2 and total_lines >= 5:
        return 3.0, f"HTML 주석 블록 {len(non_empty)}개 + {total_lines}줄"
    if len(non_empty) >= 1:
        return 1.0, f"HTML 주석 블록 {len(non_empty)}개 + {total_lines}줄 (만점 조건: 블록 ≥2 + 라인 ≥5)"
    return 0.0, "HTML 주석 없음 (사람용 안내가 컨텍스트 오염)"


def score_E1(text: str, item: dict) -> tuple[float, str]:
    section_kw = item["detection"]["section_keywords"]
    fallback_kw = item["detection"]["fallback_keywords"]
    if find_section(text, section_kw):
        return 4.0, "WHERE 섹션 존재"
    hits = sum(text.count(kw) for kw in fallback_kw)
    if hits >= 1:
        return 4.0, f"의존성 키워드 {hits}개"
    return 0.0, "WHERE 섹션/의존성 키워드 없음"


def score_E2(text: str, item: dict, self_path: Path) -> tuple[float, str]:
    visible = strip_html_comments(text)
    links = re.findall(r"\[[^\]]+\]\(((?!#)[^)]+\.md)\)", visible)
    # self 제외
    external = [l for l in links if not l.endswith(self_path.name)]
    if len(external) >= 1:
        return 3.0, f"cross-link {len(external)}개"
    return 0.0, "다른 영역 cross-link 없음"


def score_F1(text: str, item: dict, file_path: Path) -> tuple[float, str | None]:
    """git 히스토리 기반. skip 가능."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(file_path)],
            capture_output=True, text=True, timeout=5, cwd=file_path.parent,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return -1.0, None  # skip: no git history
        last_ts = int(result.stdout.strip())
        days_since = (datetime.now(timezone.utc).timestamp() - last_ts) / 86400
        # 파일 자체가 7일 미만이면 skip
        if days_since < 7:
            return -1.0, None
        if days_since <= 90:
            return 5.0, f"최근 수정 {days_since:.0f}일 전"
        if days_since <= 180:
            return 2.0, f"최근 수정 {days_since:.0f}일 전 (만점 ≤90)"
        return 0.0, f"최근 수정 {days_since:.0f}일 전 (오래됨)"
    except (subprocess.SubprocessError, FileNotFoundError, ValueError):
        return -1.0, None


def score_H1(file_path: Path, root: Path, type_code: int) -> tuple[float, str]:
    rel = file_path.relative_to(root) if file_path.is_relative_to(root) else file_path
    if type_code == 1:
        if file_path.parent.resolve() == root.resolve():
            return 3.0, f"root 위치 ({rel})"
        return 1.0, f"root가 아닌 위치 ({rel})"
    if type_code == 2:
        if file_path.parent.resolve() != root.resolve():
            return 3.0, f"서브디렉토리 위치 ({rel})"
        return 1.0, f"root 위치인데 area_guide ({rel})"
    return 3.0, f"single_guide 위치 ({rel})"


def score_H2(file_path: Path) -> tuple[float, str]:
    """root_map용 — CLAUDE.md와 AGENTS.md 둘 다 있는지"""
    parent = file_path.parent
    has_claude = (parent / "CLAUDE.md").exists()
    has_agents = (parent / "AGENTS.md").exists()
    if has_claude and has_agents:
        return 2.0, "CLAUDE.md + AGENTS.md 동시 존재"
    if has_claude or has_agents:
        return 1.0, "한 파일만 존재"
    return 0.0, "둘 다 없음 (불가능?)"


def score_H3(file_path: Path) -> tuple[float, str]:
    """root_map용 — sync 정합성"""
    parent = file_path.parent
    claude_path = parent / "CLAUDE.md"
    agents_path = parent / "AGENTS.md"
    has_claude = claude_path.exists()
    has_agents = agents_path.exists()
    if not (has_claude and has_agents):
        return 1.0, "single agent OK"
    claude_text = claude_path.read_text(encoding="utf-8", errors="ignore")
    agents_text = agents_path.read_text(encoding="utf-8", errors="ignore")
    if "@./AGENTS.md" in claude_text or "@./CLAUDE.md" in agents_text:
        return 2.0, "linked via @import"
    # diff_ratio 휴리스틱
    short, long_ = sorted([claude_text, agents_text], key=len)
    if len(long_) == 0:
        return 0.0, "drift risk (empty file)"
    common = sum(1 for c in short if c in long_)  # rough
    ratio = abs(len(claude_text) - len(agents_text)) / max(1, len(long_))
    if ratio < 0.05:
        return 2.0, f"content sync (diff_ratio={ratio:.2%})"
    return 0.0, f"drift risk (diff_ratio={ratio:.2%})"


# Anti-patterns
def detect_anti_patterns(text: str, schema: dict) -> tuple[float, list[dict]]:
    """두 가지 detection 타입 지원
    - regex_count: regex_patterns flat list + 단일 trigger_threshold
    - regex_count_grouped: groups[].regex_patterns + 그룹별 trigger_threshold,
      한 그룹이라도 임계를 넘으면 페널티 적용 (그룹별 매칭 카운트도 함께 기록)
    """
    visible = strip_html_comments(text)
    items = schema["anti_patterns"]["items"]
    hits = []
    total_penalty = 0.0
    for ap in items:
        det = ap["detection"]
        det_type = det.get("type", "regex_count")

        triggered = False
        match_summary: list[str] = []
        total_matches = 0

        if det_type == "regex_count_grouped":
            for group in det.get("groups", []):
                count = 0
                for p in group.get("regex_patterns", []):
                    count += len(re.findall(p, visible, re.IGNORECASE))
                if count > 0:
                    match_summary.append(f"{group['name']}={count}")
                total_matches += count
                if count >= group.get("trigger_threshold", 1):
                    triggered = True
        else:  # regex_count (default)
            patterns = det.get("regex_patterns", [])
            for p in patterns:
                total_matches += len(re.findall(p, visible, re.IGNORECASE))
            if total_matches >= det.get("trigger_threshold", 1):
                triggered = True

        if triggered:
            hits.append({
                "id": ap["id"],
                "name": ap["name"],
                "matches": total_matches,
                "groups": match_summary,
                "penalty": ap["penalty"],
            })
            total_penalty += ap["penalty"]
    capped = min(total_penalty, schema["anti_patterns"]["max_penalty"])
    return -capped, hits


# ────────────────────────────────────────────────────────────
# 트리 채점 (T 카테고리)
# ────────────────────────────────────────────────────────────

def score_tree(root: Path, files: list[Path], schema: dict) -> TreeResult:
    missing_areas: list[str] = []
    broken_links: list[str] = []
    duplicate_rules: list[dict] = []

    # T1: root map에 명시된 영역 링크가 실제 존재하는지
    root_maps = [f for f in files if f.parent.resolve() == root.resolve() and f.name in ("CLAUDE.md", "AGENTS.md")]
    for rm in root_maps:
        text = rm.read_text(encoding="utf-8", errors="ignore")
        visible = strip_html_comments(text)
        links = re.findall(r"\[[^\]]+\]\(([^)]+/(?:CLAUDE|AGENTS)\.md)\)", visible)
        for link in links:
            target = (rm.parent / link).resolve()
            if not target.exists():
                missing_areas.append(f"{rm.name} → {link}")

    # T2: 모든 가이드의 md 링크가 실제 파일인지
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        visible = strip_html_comments(text)
        links = re.findall(r"\[[^\]]+\]\(((?!https?://|#)[^)]+\.md)(?:#[^)]+)?\)", visible)
        for link in links:
            target = (f.parent / link).resolve()
            if not target.exists():
                broken_links.append(f"{f.relative_to(root)} → {link}")

    # T3: 규칙 중복 — 가이드들의 bullet을 normalize → 0.85+ 유사도
    # 같은 디렉토리의 CLAUDE.md ↔ AGENTS.md 쌍은 sync_group으로 묶고,
    # 같은 그룹 내 bullet 중복은 카운트하지 않는다.
    # placeholder 안내문(예: "_(아직 없음)_", "채워주세요" 류)은 진짜 규칙이 아니므로
    # T3 dedup에서 사전 제외. 템플릿이 의도적으로 여러 영역에 두는 안내문이 안티패턴으로
    # 오인되지 않도록 보호.
    placeholder_markers = [
        "아직 없음",
        "채워주세요",
        "검토 필요",
        "추정 — 검토",
        "추정이므로 검토",
        "비어 있다면",
        "tbd",
        "todo",
        "예:",
        "있다면 추가",
        "있다면 채",
        "필요 시",
        "도입 시",
        "_(",  # markdown italic placeholder 시작
    ]
    all_bullets: list[tuple[str, str, str]] = []  # (file, sync_group, normalized bullet)
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        visible = strip_html_comments(text)
        bullets = re.findall(r"^\s*[-*]\s+(.{15,200})$", visible, re.MULTILINE)
        # sync_group은 "같은 디렉토리 + 가이드 파일 유형"으로 식별
        sync_group = str(f.parent.relative_to(root)) if f.parent.is_relative_to(root) else str(f.parent)
        for b in bullets:
            norm = re.sub(r"\s+", " ", b.lower()).strip()
            norm = re.sub(r"[`*_]", "", norm)
            # placeholder 안내문 제외
            if any(marker in norm for marker in placeholder_markers):
                continue
            all_bullets.append((str(f.relative_to(root)), sync_group, norm))

    # seen: norm → list[(path, sync_group)]
    seen: dict[str, list[tuple[str, str]]] = {}
    for path, group, norm in all_bullets:
        for existing_norm, entries in list(seen.items()):
            if jaccard(norm, existing_norm) >= 0.85:
                # sync_group이 모두 같은 그룹이면 중복으로 카운트하지 않음
                groups_so_far = {g for _, g in entries}
                groups_so_far.add(group)
                if len(groups_so_far) >= 2 and (path, group) not in entries:
                    entries.append((path, group))
                    if len({p for p, _ in entries}) == 2:
                        duplicate_rules.append({
                            "rule": existing_norm[:80],
                            "in_files": [p for p, _ in entries],
                        })
                elif (path, group) not in entries:
                    entries.append((path, group))
                break
        else:
            seen[norm] = [(path, group)]

    t1 = 1.0 if not missing_areas else 0.0
    t2 = 1.0 if not broken_links else 0.0
    t3 = 1.0 if len(duplicate_rules) < 5 else 0.0
    earned = t1 + t2 + t3
    penalty = (3.0 - earned) * 3.33

    return TreeResult(
        earned=earned, max_points=3.0, penalty=penalty,
        missing_areas=missing_areas[:20],
        broken_links=broken_links[:20],
        duplicate_rules=duplicate_rules[:20],
    )


def jaccard(a: str, b: str) -> float:
    sa = set(a.split())
    sb = set(b.split())
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / max(1, len(sa | sb))


# ────────────────────────────────────────────────────────────
# 파일 단위 채점
# ────────────────────────────────────────────────────────────

def score_file(path: Path, root: Path, schema: dict, type_code: int | None = None) -> FileResult:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if type_code is None:
        type_code = classify_type(path, root, text)

    item_results: list[dict] = []
    a1_score = 0.0

    for cat in schema["categories"]:
        for it in cat["items"]:
            if type_code not in it["applies_to"]:
                continue
            iid = it["id"]
            evidence = ""
            score = 0.0
            try:
                if iid == "A1":
                    score, evidence = score_A1(text, it); a1_score = score
                elif iid == "A2":
                    score, evidence = score_A2(text, it, a1_score)
                elif iid == "A3":
                    score, evidence = score_A3(text, it)
                elif iid == "A4":
                    score, evidence = score_A4(text, it, path)
                elif iid == "B1":
                    score, evidence = score_B1(text, it)
                elif iid == "B2":
                    score, evidence = score_B2(text, it)
                elif iid == "C1":
                    score, evidence = score_C1(text, it)
                elif iid == "C2":
                    score, evidence = score_C2(text, it)
                elif iid == "D1":
                    score, evidence = score_D1(text, it)
                elif iid == "D2":
                    score, evidence = score_D2(text, it, path)
                elif iid == "D2_prime":
                    score, evidence = score_D2_prime(text, it)
                elif iid == "D3":
                    score, evidence = score_D3(text, it)
                elif iid == "D4":
                    score, evidence = score_D4(text, it)
                elif iid == "D5":
                    score, evidence = score_D5(text, it)
                elif iid == "E1":
                    score, evidence = score_E1(text, it)
                elif iid == "E2":
                    score, evidence = score_E2(text, it, path)
                elif iid == "F1":
                    score, ev = score_F1(text, it, path)
                    if score < 0:
                        continue  # skip
                    evidence = ev or ""
                elif iid == "H1":
                    score, evidence = score_H1(path, root, type_code)
                elif iid == "H2":
                    score, evidence = score_H2(path)
                elif iid == "H3":
                    score, evidence = score_H3(path)
                else:
                    continue
            except Exception as e:
                evidence = f"채점 오류: {e}"
                score = 0.0
            item_results.append({
                "id": iid,
                "name": it["name"],
                "category": cat["id"],
                "earned": score,
                "max_points": it["max_points"],
                "evidence": evidence,
            })

    # anti-patterns
    anti_penalty, anti_hits = detect_anti_patterns(text, schema)

    raw_earned = sum(r["earned"] for r in item_results)
    applicable_max = sum(r["max_points"] for r in item_results)
    adjusted_raw = max(0.0, raw_earned + anti_penalty)
    file_score = round((adjusted_raw / applicable_max) * 100, 1) if applicable_max > 0 else 0.0

    # 카테고리별 집계
    cat_scores: dict[str, dict] = {}
    for r in item_results:
        cid = r["category"]
        cat_scores.setdefault(cid, {"earned": 0.0, "max": 0.0})
        cat_scores[cid]["earned"] += r["earned"]
        cat_scores[cid]["max"] += r["max_points"]

    return FileResult(
        path=str(path.relative_to(root)) if path.is_relative_to(root) else str(path),
        type_code=type_code,
        line_count=count_non_comment_lines(text),
        raw_earned=raw_earned,
        anti_penalty=anti_penalty,
        adjusted_raw=adjusted_raw,
        applicable_max=applicable_max,
        file_score=file_score,
        grade=grade_of(file_score, schema),
        category_scores={k: {"earned": round(v["earned"], 1), "max": round(v["max"], 1)} for k, v in cat_scores.items()},
        item_evidence=item_results,
        anti_pattern_hits=anti_hits,
    )


def grade_of(score: float, schema: dict) -> str:
    th = schema["grade_thresholds"]
    if score >= th["S_AI_Ready"]:
        return "S"
    if score >= th["A_Healthy"]:
        return "A"
    if score >= th["B_Functional"]:
        return "B"
    if score >= th["C_Fragile"]:
        return "C"
    return "D"


# ────────────────────────────────────────────────────────────
# 프로젝트 단위 집계
# ────────────────────────────────────────────────────────────

def score_project(root: Path, schema: dict) -> ProjectResult:
    guides = discover_guides(root, schema)
    if not guides:
        return ProjectResult(
            root=str(root), project_score=0.0, grade="D",
            weighted_avg=0.0, tree_penalty=0.0,
            top_recommendations=["가이드 파일이 없습니다. `/agentic-project-init`로 먼저 생성하세요."],
        )

    # redirect 파일을 사전 분류하여 본문 파일만 정상 채점,
    # redirect 파일은 본문 파일의 점수를 차용한다.
    redirect_map: dict[Path, Path] = {}  # redirect_path → target_path
    body_guides: list[Path] = []
    for g in guides:
        text = g.read_text(encoding="utf-8", errors="ignore")
        redirect = is_import_redirect(text)
        if redirect:
            target = (g.parent / redirect).resolve()
            if target.exists() and target in [x.resolve() for x in guides]:
                redirect_map[g] = target
                continue
        body_guides.append(g)

    body_results: dict[Path, FileResult] = {}
    for g in body_guides:
        body_results[g.resolve()] = score_file(g, root, schema)

    file_results: list[FileResult] = []
    for g in guides:
        if g in redirect_map:
            target = redirect_map[g]
            tr = body_results.get(target.resolve())
            if tr is None:
                file_results.append(score_file(g, root, schema))
                continue
            # 본문 결과를 차용하되 path/line_count는 redirect 파일 자신의 것 유지
            rel_path = str(g.relative_to(root)) if g.is_relative_to(root) else str(g)
            redirect_text = g.read_text(encoding="utf-8", errors="ignore")
            file_results.append(FileResult(
                path=rel_path,
                type_code=tr.type_code,
                line_count=count_non_comment_lines(redirect_text),
                raw_earned=tr.raw_earned,
                anti_penalty=tr.anti_penalty,
                adjusted_raw=tr.adjusted_raw,
                applicable_max=tr.applicable_max,
                file_score=tr.file_score,
                grade=tr.grade,
                category_scores=tr.category_scores,
                item_evidence=tr.item_evidence,
                anti_pattern_hits=tr.anti_pattern_hits,
                import_redirect_to=str(target.relative_to(root)) if target.is_relative_to(root) else str(target),
            ))
        else:
            file_results.append(body_results[g.resolve()])

    tree = score_tree(root, guides, schema)

    # 가중 평균은 본문 파일만 카운트 (redirect는 중복 카운트 방지)
    body_for_avg = [fr for fr in file_results if fr.import_redirect_to is None]
    type_weights = {1: 2, 2: 1, 3: 1}
    weighted_sum = sum(fr.file_score * type_weights[fr.type_code] for fr in body_for_avg)
    weight_total = sum(type_weights[fr.type_code] for fr in body_for_avg)
    weighted_avg = round(weighted_sum / max(1, weight_total), 1) if weight_total > 0 else 0.0
    project_score = round(max(0.0, min(100.0, weighted_avg - tree.penalty)), 1)

    recommendations = generate_recommendations(file_results, tree)

    return ProjectResult(
        root=str(root),
        project_score=project_score,
        grade=grade_of(project_score, schema),
        weighted_avg=weighted_avg,
        tree_penalty=round(tree.penalty, 1),
        files=file_results,
        tree=tree,
        top_recommendations=recommendations,
    )


def generate_recommendations(files: list[FileResult], tree: TreeResult) -> list[str]:
    recs: list[tuple[float, str]] = []
    # redirect 파일은 본문과 중복 추천 방지를 위해 제외
    for fr in files:
        if fr.import_redirect_to is not None:
            continue
        for item in fr.item_evidence:
            gap = item["max_points"] - item["earned"]
            if gap > 0:
                impact = gap * (1 if fr.type_code != 1 else 2)
                recs.append((impact, f"[{fr.path}] {item['id']} {item['name']}: +{gap:.0f}점 가능 ({item['evidence']})"))
    if tree.missing_areas:
        recs.append((10.0, f"[프로젝트] T1 영역 누락 {len(tree.missing_areas)}건 — 죽은 영역 링크 정리"))
    if tree.broken_links:
        recs.append((8.0, f"[프로젝트] T2 죽은 cross-link {len(tree.broken_links)}건"))
    if len(tree.duplicate_rules) >= 5:
        recs.append((6.0, f"[프로젝트] T3 중복 규칙 {len(tree.duplicate_rules)}건 — 한 곳으로 통합"))
    recs.sort(reverse=True, key=lambda x: x[0])
    return [r[1] for r in recs[:5]]


# ────────────────────────────────────────────────────────────
# 출력 포맷
# ────────────────────────────────────────────────────────────

def print_text_report(result: ProjectResult, single_file: bool = False) -> None:
    if single_file and result.files:
        fr = result.files[0]
        print(f"## 단일 파일 채점: {fr.path}")
        print(f"\n- type: {fr.type_code} ({'root_map' if fr.type_code == 1 else 'area_guide' if fr.type_code == 2 else 'single_guide'})")
        print(f"- file_score: **{fr.file_score} / 100**  (grade {fr.grade})")
        print(f"- raw {fr.raw_earned:.1f} + anti_penalty {fr.anti_penalty:.1f} → adjusted {fr.adjusted_raw:.1f} / applicable_max {fr.applicable_max:.1f}")
        print(f"- 줄 수(주석 제외): {fr.line_count}")
        print("\n### 카테고리별")
        for cid, sc in sorted(fr.category_scores.items()):
            ratio = sc["earned"] / sc["max"] * 100 if sc["max"] > 0 else 0
            mark = " 🔴" if ratio == 0 else " ⚠️" if ratio < 50 else ""
            print(f"- {cid}: {sc['earned']:.1f} / {sc['max']:.1f}  ({ratio:.0f}%){mark}")
        print("\n### 부분점/0점 항목 evidence")
        weak = [it for it in fr.item_evidence if it["earned"] < it["max_points"]]
        for it in weak:
            print(f"- **{it['id']} {it['name']}** ({it['earned']:.0f}/{it['max_points']}) — {it['evidence']}")
        if fr.anti_pattern_hits:
            print("\n### Anti-pattern hits")
            for ap in fr.anti_pattern_hits:
                print(f"- {ap['id']} {ap['name']}: {ap['matches']}회 매치, -{ap['penalty']}점")
        return

    print(f"# guide-audit — 프로젝트 채점 결과\n")
    print(f"- **루트**: `{result.root}`")
    print(f"- **프로젝트 총점**: **{result.project_score} / 100**  (grade **{result.grade}**)")
    print(f"- weighted_avg {result.weighted_avg} − tree_penalty {result.tree_penalty}")
    print(f"- 채점 파일: {len(result.files)}개")

    print("\n## 파일별 점수\n")
    print("| Path | Type | Score | Grade | Note |")
    print("|---|---|---|---|---|")
    type_label = {1: "root_map", 2: "area_guide", 3: "single_guide"}
    for fr in result.files:
        note = f"→ @{fr.import_redirect_to}" if fr.import_redirect_to else ""
        print(f"| `{fr.path}` | {type_label.get(fr.type_code, '?')} | {fr.file_score} | {fr.grade} | {note} |")

    print("\n## 파일별 카테고리 breakdown\n")
    # redirect 파일은 본문과 중복이라 본문만 표시
    for fr in result.files:
        if fr.import_redirect_to is not None:
            continue
        print(f"### `{fr.path}` ({fr.file_score}, {fr.grade})")
        for cid, sc in sorted(fr.category_scores.items()):
            ratio = sc["earned"] / sc["max"] * 100 if sc["max"] > 0 else 0
            mark = " 🔴" if ratio == 0 else " ⚠️" if ratio < 50 else ""
            print(f"- {cid}: {sc['earned']:.1f} / {sc['max']:.1f}  ({ratio:.0f}%){mark}")
        weak = [it for it in fr.item_evidence if it["earned"] < it["max_points"]]
        if weak:
            print(f"  부분점/0점:")
            for it in weak[:6]:
                print(f"  - {it['id']}: {it['evidence']}")
        if fr.anti_pattern_hits:
            print(f"  Anti-pattern: {', '.join(ap['id'] for ap in fr.anti_pattern_hits)}")

    if result.tree:
        print("\n## 트리 일관성 (T)\n")
        print(f"- T1 영역 누락: {len(result.tree.missing_areas)}건")
        for x in result.tree.missing_areas[:5]:
            print(f"  - {x}")
        print(f"- T2 죽은 link: {len(result.tree.broken_links)}건")
        for x in result.tree.broken_links[:5]:
            print(f"  - {x}")
        print(f"- T3 중복 규칙: {len(result.tree.duplicate_rules)}건")
        for x in result.tree.duplicate_rules[:3]:
            print(f"  - {x['rule']!r}  in  {x['in_files']}")

    if result.top_recommendations:
        print("\n## Top 개선 추천\n")
        for r in result.top_recommendations:
            print(f"- {r}")


# ────────────────────────────────────────────────────────────
# main
# ────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="guide-audit 러너")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--project", type=str, help="프로젝트 루트 디렉토리")
    g.add_argument("--file", type=str, help="단일 가이드 파일 (.md)")
    parser.add_argument("--type", type=int, choices=[1, 2, 3], help="단일 파일 모드에서 타입 강제 (1=root_map, 2=area_guide, 3=single_guide)")
    parser.add_argument("--json", action="store_true", help="JSON으로 출력")
    args = parser.parse_args(argv)

    if args.project:
        root = Path(args.project).resolve()
        if not root.is_dir():
            print(f"❌ 디렉토리가 아님: {root}", file=sys.stderr)
            return 2
        schema = load_schema(root)
        result = score_project(root, schema)
    else:
        path = Path(args.file).resolve()
        if not path.is_file():
            print(f"❌ 파일이 아님: {path}", file=sys.stderr)
            return 2
        try:
            root = Path(subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"], cwd=path.parent, text=True
            ).strip())
        except Exception:
            root = path.parent
        schema = load_schema(root)
        # redirect 파일을 단독 채점하면 0점이 나오므로 대상 파일을 대신 채점
        redirect = is_import_redirect(path.read_text(encoding="utf-8", errors="ignore"))
        if redirect:
            target = (path.parent / redirect).resolve()
            if target.is_file():
                fr = score_file(target, root, schema, type_code=args.type)
                fr.import_redirect_to = str(target.relative_to(root)) if target.is_relative_to(root) else str(target)
                fr.path = f"{path.relative_to(root) if path.is_relative_to(root) else path} → @{redirect}"
            else:
                print(f"❌ import 대상 파일을 찾을 수 없음: {target}", file=sys.stderr)
                return 2
        else:
            fr = score_file(path, root, schema, type_code=args.type)
        result = ProjectResult(
            root=str(root),
            project_score=fr.file_score,
            grade=fr.grade,
            weighted_avg=fr.file_score,
            tree_penalty=0.0,
            files=[fr],
            tree=None,
        )

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print_text_report(result, single_file=bool(args.file))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
