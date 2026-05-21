# Agentic Project Init

**English | [한국어](README.md)**

A skill that automatically initializes a project structure optimized for agentic AI work.

> Supported agents: Claude Code · Codex · Antigravity · Cursor

<br/><br/>

## TL;DR

- Keep **only a map** at the root; per-area guides live **inside their own area folders**.
- The agent loads only the guide for the area it is working on → **saves context tokens**.
- Pitfalls and background that can't be inferred from code alone are made explicit via an **8-section template (WHAT / CONTENTS / HOW / HOW NOT / WHERE / WHY / COMMANDS / LEARNED CAUTIONS)**.
- init produces a **lightweight skeleton only** (WHAT/CONTENTS/WHERE/COMMANDS). The judgement and tacit-knowledge sections are filled in later via the **`/update` interview** once a baseline is in place.
- Each guide opens with a **one-sentence mission** and a **Tradeoff comment block** so the LLM grasps the rule's intent and cost together.
- LEARNED CAUTIONS lives in a **separate file (`LEARNED_CAUTIONS.md`)**, decoupled from the main guide. `/learn` appends one line at a time; the main guide is never touched.
- `/update --restructure` reshapes area boundaries when needed (file moves + guide reshuffling, all behind user confirmation).
- The `/guide-audit` command scores every guide in the project against a deterministic rubric.

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

1. **WHAT** — what this module does *(filled by init)*
2. **CONTENTS** — files/directories and tech stack *(filled by init)*
3. **HOW** — how to make ordinary changes *(filled by the `/update` interview)*
4. **⛔ HOW NOT** — non-obvious pitfalls that break the system (a one-line reason is required) *(filled by the `/update` interview)*
5. **WHERE** — dependencies on other modules *(filled by init)*
6. **WHY** — background knowledge not written in the code *(filled by the `/update` interview)*
7. **COMMANDS** — build/test/lint commands + area-specific command guards *(init covers build/test only; guards come from `/update`)*
8. **⚠️ LEARNED CAUTIONS** — split out into `LEARNED_CAUTIONS.md`; the `learn` skill accumulates entries there.

In particular, 4 (HOW NOT) and 6 (WHY) are the slots that explicitly hold **knowledge only humans can know**, and 7 (COMMANDS) is a guard that stops the LLM from guessing commands.

The slots `/update` is expected to fill are left as placeholders by init; the substantive writing begins around the baseline-completion milestone. These are areas where code-only inference would only add noise, so they are only filled through user decisions.

Authoring guidance meant for humans is isolated in HTML comments, so it costs 0 tokens on automatic load.

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

A single line is appended to that area folder's `LEARNED_CAUTIONS.md`. The main guide's section 8 references this file via `@./LEARNED_CAUTIONS.md`, so it loads automatically — and `learn` never touches the main guide. User-authored content and accumulated entries no longer share a file, which keeps the preservation rules crisp.

From the next session on, the agent won't repeat the same mistake.

<br/>

### 5. /update interview = grow the guide alongside the code

Once a baseline is in place, running `/update` walks through each area with the user via 9 question types:

1. Change-fact confirmation (file/endpoint additions/removals)
2. Deletion / move confirmation
3. External dependency shifts
4. Convention agreement (when mixed patterns appear)
5. Anti-pattern prediction (HOW NOT candidates)
6. Tacit-knowledge extraction (reasons behind unusual choices)
7. Drift detection (existing HOW vs. actual code)
8. New LEARNED CAUTIONS candidates (e.g., fix clusters)
9. Area boundary review (advisory only — decisions go to `/update --restructure`)

Every proposal carries a **one-line rationale** (commit ID, file location, occurrence count) so even unfamiliar areas remain decidable. After the per-area interviews, the skill checks for 6 kinds of cross-area conflicts (convention contradiction / WHERE duplication / HOW NOT vs HOW / terminology mismatch / dependency direction / COMMANDS divergence). **If even one conflict is left unresolved, the update itself is marked incomplete** and the next `/update` re-asks about that conflict first.

**User decisions are never auto-overwritten.** Any change requires explicit confirmation, and previous decisions are preserved as change-history comments.

<br/>

### 6. /update --restructure = reshaping area boundaries

When an area grows oversized or responsibilities blur, `/update --restructure <area>` lets you redraw the area itself.

- Extract responsibility categories → propose split/merge options → file-move plan → **transfer LEARNED_CAUTIONS entries (per-item user decision)** → reshuffle the 8-section main guide → rewire external strong-coupling `@import`s → step-by-step verification.
- One area at a time, no automatic commits, zero file moves before user approval.
- LEARNED_CAUTIONS entries accumulated by the user are never auto-classified by AI — each item's destination is decided by the user.

<br/>

### 7. /guide-audit deterministic scoring = quality regression prevention

The `/guide-audit` command scores every guide in the project against a 100-point rubric. It is pattern-matching based, so the same input → the same score.

- Combined scoring across 7 categories (A–H) + tree consistency (T) + anti-patterns (G)
- Per-file score + per-category breakdown + evidence for 0-point items + top improvement recommendations
- Automatic recognition of `@import` redirect files (a one-line `CLAUDE.md` of `@./AGENTS.md` borrows the import target's score)

Scoring results are printed only to the console and do not modify guide files (read-only).

<br/>

### 8. Multi-agent collaboration

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

→ Codex uses a `$` prefix for custom invocations, so it differs from the other agents. Otherwise the behavior is identical.
The append target is **a single `LEARNED_CAUTIONS.md` in the current area folder**; the main guide is never touched.

<br/>

### How `/update` is invoked

| Invocation | Behavior |
|------|------|
| `/update` | General update across all areas (9 question-type interview + 6-conflict verification) |
| `/update <area path>` | Updates only the specified area |
| `/update --restructure [area]` | Separate flow for area-boundary reshaping (file moves + guide reshuffling + LEARNED entry transfer) |

→ In Codex it is `$update`. **When to run it**:

- Right after baseline completion — start filling the guides in earnest
- After major feature additions — decide whether a new pattern becomes the convention
- After a bug fix cluster — pin recurring mistakes into `LEARNED_CAUTIONS.md`
- After external dependency swaps — refresh HOW/COMMANDS
- Right before onboarding/release — keep the guides current

Recommended cadence: monthly or whenever the signals above appear. Avoid running it mid-refactor — run it after the refactor lands.

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

It infers the current work area and appends one line to that area folder's `LEARNED_CAUTIONS.md`. The main guide (`AGENTS.md` / `CLAUDE.md`) is never modified — section 8 of the main guide references `@./LEARNED_CAUTIONS.md`, so it loads automatically. If the area is ambiguous, it asks the user.

The invocation differs per agent — Claude Code/Cursor/Antigravity use `/learn`, Codex uses `$learn`. Invoked without args, it auto-extracts the wrong assumption from the recent conversation.

**Q. When should I run `/update`?**

Since init only creates a lightweight skeleton, the first run is around the baseline-completion milestone, when patterns have settled. After that, run it whenever a major feature lands, an external dependency is swapped, a bug-fix cluster appears, or you're about to onboard someone / cut a release. The interview groups questions per area and tags each proposal with concrete evidence (commit IDs, file locations) so unfamiliar areas remain decidable. User decisions are never auto-overwritten, and if any cross-area conflict is left unresolved the update is marked incomplete.

**Q. What's different about `/update --restructure`?**

Plain `/update` only edits guide content; `--restructure` reshapes the areas themselves — splitting, merging, renaming, or removing them. It covers file moves, guide reshuffling, `LEARNED_CAUTIONS` entry transfer, and rewiring external strong-coupling `@import`s, but every step is gated on user confirmation. It handles one area at a time, with no automatic commits — review via `git diff` and commit yourself.

**Q. Does `/guide-audit` modify guides?**

No. It is read-only. It only prints scoring results to the console and shows improvement recommendations. Whether to apply them is the user's decision.
