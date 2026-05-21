# Agentic Project Init

**English | [한국어](README.md)**

A skill that automatically initializes a project structure optimized for agentic AI work.

> Supported agents: Claude Code · Codex · Antigravity · Cursor

<br/><br/>

## TL;DR

- Keep **only a map** at the root; per-area guides live **inside their own area folders** → only the active area loads, **saving context tokens**.
- Pitfalls and background that can't be inferred from code alone are made explicit via an **8-section template (WHAT / CONTENTS / HOW / HOW NOT / WHERE / WHY / COMMANDS / LEARNED CAUTIONS)**.
- Each guide opens with a **first-line mission + Tradeoff** so the LLM grasps the rule's intent and cost together.
- Three-step workflow: **`init` (lightweight skeleton)** → **`/learn` (accumulate cautions)** → **`/update` (fill guides via interview)**.
- The `/guide-audit` command scores every guide against a deterministic rubric.

<br/><br/>

## Why This Structure

### 1. Limits of a single CLAUDE.md

The common pattern is to cram every guideline into a single `CLAUDE.md` at the project root.

Problems:

- **Context bloat** — even when working only on the frontend, the backend, DB, and infra guidelines all enter the context.
- **Cross-area information pollution** — the agent misapplies another area's rules to the current area.
- **The longer the file, the more lower-priority rules are ignored** — LLMs tend to skim past instructions in the middle/back of long documents (lost-in-the-middle).

<br/>

### 2. What code alone can't tell you no longer disappears

If the README only says "this directory is the X module", the agent will:

- not know "why this pattern" → refactor it arbitrarily.
- not know "the real reason this function must not be touched" → modify it carelessly.
- not know domain terms, past incidents, or why a different path was avoided → repeat the same mistakes.

<br/><br/>

## Strengths of This Structure

### 1. Map + area guides = token efficiency

| Pattern | Amount entering context |
|------|----------------------|
| Single CLAUDE.md (e.g. 800 lines) | Always all 800 lines |
| Map (50 lines) + area guide (150 lines) | 50 + 150 = 200 lines |

The gap widens for larger projects. The agent reads the root map first and loads only the guide for the single area it works on.

<br/>

### 2. 8-section template = making non-code knowledge explicit

Every area guide uses the same 8-section structure:

1. **WHAT** — what this module does
2. **CONTENTS** — files/directories and tech stack
3. **HOW** — how to make ordinary changes
4. **⛔ HOW NOT** — non-obvious pitfalls that break the system (a one-line reason is required)
5. **WHERE** — dependencies on other modules
6. **WHY** — background knowledge not written in the code
7. **COMMANDS** — build/test/lint + area-specific command guards
8. **⚠️ LEARNED CAUTIONS** — split out into `LEARNED_CAUTIONS.md`

Sections 4 (HOW NOT) and 6 (WHY) are the slots that explicitly hold **knowledge only humans can know**. Since code-only inference would only add noise there, init fills **only 1·2·5·7**, while **3·4·6 are filled by the `/update` interview through user decisions**. Authoring guidance meant for humans is isolated in HTML comments, so it costs 0 tokens on automatic load.

<br/>

### 3. First-line mission + Tradeoff = awareness of a rule's intent and cost

Right below each area guide's heading there are two slots:

```markdown
# Frontend Work Guide

Prevent schema drift in backend API contracts and domain variable names. No guessing, no `any`, no arbitrary changes.

**Tradeoff**: pinning the contract as the backend SoT → giving up the freedom for the frontend to evolve on its own, in exchange for moving 422/500 errors to compile time.
```

- **First-line mission**: lets the LLM immediately grasp this area's **essential purpose** — what this area prevents, in one sentence.
- **Tradeoff**: states what this rule gives up and what it gains. Exposed in the body so the LLM is automatically aware of it on entering the area — the key device for not losing the rule's essence in edge cases.

<br/>

### 4. /learn accumulation = never make the same mistake twice

When a mistake arises from a wrong assumption during work:

```
/learn Forgot to bump the alembic version during DB migration → missing column in staging
```

A single line is appended to that area folder's `LEARNED_CAUTIONS.md`, which the main guide auto-imports. From the next session on, the agent won't repeat the same mistake.

<br/>

### 5. /update interview = grow the guide alongside the code

Once a baseline is in place, running `/update` walks each area through **9 question types** (change facts, conventions, anti-patterns, tacit knowledge, drift, etc.). Every proposal carries a **one-line rationale** (commit ID, file location), so even unfamiliar areas remain decidable.

After the interviews, the skill checks for **6 cross-area conflicts** (convention contradiction / WHERE duplication / HOW NOT vs HOW / terminology / dependency direction / COMMANDS). If any conflict is left unresolved, the update is marked **incomplete** and the next run re-asks that conflict first.

For boundary changes, use `/update --restructure <area>` to redraw the area itself (one at a time, zero file moves before user approval).

**User decisions are never auto-overwritten** — any change requires explicit confirmation, with previous decisions preserved as change-history comments.

<br/>

### 6. /guide-audit deterministic scoring = quality regression prevention

The `/guide-audit` command scores every guide in the project against a 100-point rubric. It is pattern-matching based, so the same input → the same score.

- Combined scoring across 7 categories (A–H) + tree consistency (T) + anti-patterns (G)
- Per-file score + per-category breakdown + evidence for 0-point items + top improvement recommendations
- Automatic recognition of `@import` redirect files (a one-line `CLAUDE.md` of `@./AGENTS.md` borrows the import target's score)

Scoring results are printed only to the console and do not modify guide files (read-only).

<br/>

### 7. Multi-agent collaboration

Even when teammates use different agents (Claude Code, Codex, etc.) in one project, they see the same guides.

- `both` mode → `AGENTS.md` is the body at the root and in every area folder, while `CLAUDE.md` imports it with a single line of `@./AGENTS.md`.
- Since only one file is edited, sync drift is structurally impossible. No external scripts/hooks needed.

<br/><br/>

## Quantitative Effect

### Verification question

> With the same code, same AI model, and same task, when you change **only the documentation structure**, how does the AI agent's token cost change?

<br/>

### Experiment setup

- **Targets**: 3 real projects of different sizes — A (small) / B (medium) / C (large, multi-area system)
- **Comparison**: no guide (code only) vs. structure applied (area map + 8-section guides)
- **Tasks**: a 5-step scenario of increasing difficulty (whole-project comprehension → multi-area integrated change plan)
- **Metric**: total tokens (= AI work cost)
- **Controls**: zero subagents, no clarifying questions, git isolation, character-identical prompts, measurement session ≠ aggregation session

<br/>

### Result: structure reduces token cost

| | Project A (small) | Project B (medium) | Project C (large) |
|---|--:|--:|--:|
| Tokens (no guide → structure applied) | 744k → 701k | 2,222k → 1,489k | 4,720k → 2,780k |
| **Token savings** | **+6%** | **+33%** | **+41%** |

What's confirmed:

1. **Structure applied uses fewer tokens than no guide** — consistent across all 3 projects.
2. **The effect scales with size** — small +6% → large +41%.

> **The value of documentation structure is in cost. The larger and more complex the project, the greater the token savings.**

<br/>

> ⚠️ Limitation: generalization from 3 projects is limited. However, "larger scale → larger structural effect" is consistently observed, and the savings will vary with the number of areas, task type, and codebase size.

<br/><br/>

## Per-Agent Compatibility

| Agent | Memory file | User-level skill location |
|---------|------------|---------------------|
| Claude Code | `CLAUDE.md` | `~/.claude/skills/` |
| Codex | `AGENTS.md` | `~/.agents/skills/` |
| Antigravity | `AGENTS.md` or `GEMINI.md` | `~/.gemini/antigravity/skills/` |
| Cursor | `AGENTS.md` or `.cursor/rules/` | `~/.cursor/skills/` |

Each path follows the official docs ([Claude Code](https://code.claude.com/docs/en/skills.md) · [Codex](https://developers.openai.com/codex/skills) · [Antigravity](https://antigravity.google/docs/skills) · [Cursor](https://cursor.com/docs/skills)).

<br/>

### How `/learn` is invoked

| Agent | Invocation |
|---------|------|
| Claude Code / Cursor / Antigravity | `/learn` (or `/learn <note>`) |
| Codex | `$learn` (or `$learn <note>`) |

→ Codex uses a `$` prefix. The append target is the current area's `LEARNED_CAUTIONS.md`; the main guide is never touched.

<br/>

### How `/update` is invoked

| Invocation | Behavior |
|------|------|
| `/update` | General update across all areas (9 question-type interview + 6-conflict verification) |
| `/update <area path>` | Updates only the specified area |
| `/update --restructure [area]` | Separate flow for area-boundary reshaping (file moves + guide reshuffling + LEARNED entry transfer) |

→ In Codex it is `$update`. Run it first right after baseline completion, then monthly — or whenever a major feature lands, a bug-fix cluster appears, a dependency is swapped, or you're cutting a release. (Avoid mid-refactor; run after it lands.)

<br/>

### How `/guide-audit` is invoked

| Invocation | Behavior |
|------|------|
| `/guide-audit` | Combined scoring of all guides in the current project |
| `/guide-audit <path>` | Project scoring if a directory, single-file scoring if a `.md` file |

→ In Codex it's `$guide-audit`. Scoring results are printed only to the console and create no files.

It is installed alongside the project just like `/learn`, in `.claude/skills/guide-audit/` (or `.agents/skills/guide-audit/`). Internally, `score_guide.py` (Python 3, standard library only) reads `rubric-schema.json` for deterministic scoring.

<br/><br/>

## Installation

**Install once at the user level and you can invoke `/agentic-project-init` from any project.** On invocation it generates the structure in the working directory at that moment, so there is no need to install it per project.

Run only the one line for the agent you use.

<br/>

### Linux / macOS

> For safe reinstallation, the existing installation is removed first (`rm -rf <target>`).

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

## Usage

After installation, invoke it via the agent's slash command.

```
/agentic-project-init           # no args → asks the user which environment and waits
/agentic-project-init claude    # for Claude Code (CLAUDE.md)
/agentic-project-init agents    # for Codex / Antigravity / Cursor (AGENTS.md)
/agentic-project-init both      # AGENTS.md body + CLAUDE.md = @./AGENTS.md (single source of truth)
```

<br/>

### Outputs per argument

| Argument | Body file | Compatibility file |
|------|-----------|-----------|
| `claude` | `CLAUDE.md` + per-area `LEARNED_CAUTIONS.md` + `.claude/skills/` (`learn`/`update`/`guide-audit`) | — |
| `agents` | `AGENTS.md` + per-area `LEARNED_CAUTIONS.md` + `.agents/skills/` (same three) + `.agents/workflows/` | — |
| `both` | `AGENTS.md` (all locations) + per-area `LEARNED_CAUTIONS.md` + `.claude/skills/` + `.agents/skills/` + `.agents/workflows/` | `CLAUDE.md` = one line of `@./AGENTS.md` |
| (none) | Asks the user which of the above 3 environments and waits | — |

`both` mode keeps the body in a single `AGENTS.md` file only. Claude Code automatically follows the `@./AGENTS.md` import in `CLAUDE.md` and sees the same body. Since only one file is edited, sync drift is structurally impossible.

The per-area `LEARNED_CAUTIONS.md` is auto-imported by section 8 of the main guide via `@./LEARNED_CAUTIONS.md`, with a Markdown-link fallback for `@`-unsupported environments such as Codex.

<br/>

### Operation flow (what the skill does)

1. Parse args → confirm mode (if no args, ask the user about the environment)
2. Verify git repo (not required — proceeds even without one)
3. Check for existing file conflicts (if any, back up or overwrite after user confirmation)
4. Auto-detect areas (`apps/`, `frontend`, `backend`, `database`, ...) → user review
5. Draft per-area guides as a **lightweight skeleton** — WHAT/CONTENTS/WHERE/COMMANDS get code-scan-based drafts; HOW/HOW NOT/WHY are left as placeholders (to be filled by `/update`) → user approval
6. Generate files (root map + area guides + per-area `LEARNED_CAUTIONS.md` placeholders + `learn`/`update`/`guide-audit` skills). In both mode, `CLAUDE.md` is generated as a one-line `@./AGENTS.md` import file
7. Self-verify skill installation (check `learn`/`update`/`guide-audit` paths + per-area `LEARNED_CAUTIONS.md` exist; if missing, rerun step 6) → final guidance + recommend running `/update` once the baseline is complete

<br/><br/>

## FAQ

**Q. My project is small enough for a single CLAUDE.md — should I still use this?**

With only 1 area the effect is small. It becomes meaningful from 2–3 areas, and its real value shows at 5+.

**Q. I already have a CLAUDE.md — will it be overwritten?**

On detection it offers a backup option. It never overwrites before user confirmation.

**Q. What if one project has both Claude Code users and Codex users?**

Generate with `both` mode. `AGENTS.md` becomes the single source of truth and `CLAUDE.md` auto-syncs via the `@./AGENTS.md` import.

**Q. How does `/learn` work?**

It appends one line to the current area's `LEARNED_CAUTIONS.md` (the main guide is never modified). If the area is ambiguous, it asks. Invoked without args, it auto-extracts the wrong assumption from the recent conversation.

**Q. When should I run `/update`?**

First run around baseline completion, then whenever a major feature lands, an external dependency is swapped, a bug-fix cluster appears, or you're cutting a release. Every proposal carries a one-line rationale (commit IDs, file locations), user decisions are never auto-overwritten, and any unresolved cross-area conflict marks the update incomplete.

**Q. What's different about `/update --restructure`?**

Plain `/update` only edits guide content; `--restructure` reshapes the areas themselves — splitting, merging, or renaming them. It covers file moves, guide reshuffling, and `LEARNED_CAUTIONS` entry transfer, all gated on user confirmation, one area at a time.

**Q. Does `/guide-audit` modify guides?**

No. It is read-only. It only prints scoring results to the console and shows improvement recommendations. Whether to apply them is the user's decision.
