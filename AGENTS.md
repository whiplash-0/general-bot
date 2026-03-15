# Repository Agent Rules

## Tooling
- Use `uv` for dependency management and running commands.
- When adding dependencies, pin exact versions.
- Install the development environment with `uv sync --dev`.
- The repository uses a `src/` layout and tests must import the installed package.
- Do not modify `sys.path` in tests or add pytest/pythonpath import hacks.
- Run tests with `uv run pytest`.

## Code style
- Use modern Python 3.13+ style.
- Treat Python 3.13 as the baseline, not as an upper bound.
- Prefer current best practices and language features available in Python 3.13+ over older compatibility patterns.
- Do not introduce backward-compatibility constructs unless the repository explicitly needs them.
- Avoid legacy idioms when a clearer modern Python alternative exists.
- Prefer explicit code over clever abstractions.
- Use single quotes in Python code for regular strings. For any triple strings prefer double quotes.
- Use Google-style docstrings.
- If a function intentionally raises exceptions as part of its contract, document them in a `Raises:` section.
- Only document exceptions that callers are expected to handle or that represent meaningful API behavior.
- Do not document incidental internal exceptions from underlying libraries unless they are part of the method's intended behavior.

## Operating Assumptions

- Audience: personal use first (repo owner), with at most a few trusted users.
- Primary optimization: developer time is the most limited resource.
- Decision rule: prefer simpler code and explicit assumptions over defensive completeness.
- Reliability model: fail fast on unhandled exceptions so cloud restart/alerts surface issues immediately.
- Throughput expectations: low traffic and mostly sequential usage; high-scale patterns are out of scope.
- Buffering approach: soft/unbounded buffering can be acceptable when aligned with expected personal usage.
- Handler architecture: allow pragmatic orchestration in handlers; avoid splitting modules early without clear pain.
- Logging approach: keep logs human-readable and concise; cloud platform already provides timestamps/metadata.
- Correctness target: prioritize common-path behavior and maintainability over edge-case-heavy guard rails.
- Refactor trigger: add structure, guard rails, or stronger isolation only after concrete recurring pain.
- Pain signals include:
  - repeated production failures
  - difficult debugging with current logs/structure
  - growing user/message volume
  - handlers becoming slow or hard to modify safely
  - memory/runtime limits being reached

### Agent behavior under these assumptions

- Do not recommend heavy architecture changes by default for hypothetical scale.
- Treat some tradeoffs as intentional features, not defects, when they reduce maintenance cost.
- If suggesting stricter patterns, tie them to observed issues or explicit scale/operational changes.
- Prefer incremental improvements that preserve current simplicity and runtime behavior.
- End chat responses with short, practical next-step suggestions when natural follow-up actions exist.
- Keep next-step suggestions concise and optional (do not force extra work when none is needed).

### Plan mode behavior

When working in plan/spec mode:

- Prefer asking clarifying questions instead of making assumptions.
- If the task is ambiguous, ask multiple questions before proposing a plan.
- Favor more questions rather than fewer to reduce incorrect plans.
- Use numbered questions.

### Recommendation policy

- Default to the smallest change that solves today's problem.
- Do not propose scale-oriented architecture without observed concrete pain.
- Mark recommendations as:
  - now: should be done immediately due to active impact
  - later: optional until a trigger/pain signal appears

### Accepted risks

- Some edge cases may remain intentionally unhandled to keep implementation small.
- Bounded resources and stricter isolation are added after incidents, not preemptively.
- Simplicity and maintenance speed are preferred over exhaustive defensive coding.

### Testing expectations

- Cover critical paths and regressions that already happened.
- Do not require exhaustive edge-case tests by default.
- Prefer fast unit tests; add integration tests only for high-risk or failure-prone flows.

## Code Review Expectations

When reviewing code in this repository, do not limit feedback to bug detection.

Also evaluate the following dimensions:

### Architecture

- Check whether abstraction boundaries match the intended layer.
- Infrastructure code should remain generic and independent from domain logic.
- Avoid introducing unnecessary layers, indirection, or premature abstractions.
- Prefer small, explicit modules over framework-like structures.

### Modern Python practices

- Prefer modern Python 3.13 idioms and language features.
- Avoid legacy compatibility constructs or patterns meant for older Python versions.
- Prefer explicit control flow and readable constructs over clever patterns.

### API design

- Public APIs should be minimal and stable.
- Helper methods should remain private unless there is a clear external use case.
- Method naming should reflect the abstraction level (infra vs domain).
- Avoid expanding the public surface area without clear benefit.

### Internal package `__init__.py` policy

For internal packages, prefer an empty `__init__.py` by default.

Rules:

- Do not create package-level public APIs for internal packages unless explicitly requested.
- Do not re-export symbols from submodules via `__init__.py` just for convenience.
- Imports should usually reference the concrete module path directly.

Preferred:

from general_bot.infra.tasks import TaskScheduler
from general_bot.infra.tasks import TaskSupervisor
from general_bot.infra.s3 import S3Client

Avoid by default:

from general_bot.infra import TaskScheduler
from general_bot.infra import S3Client

Use package-level re-exports only when there is a clear, intentional reason
to define a stable package API.

### Maintainability

- Prefer straightforward implementations that are easy to modify.
- Avoid unnecessary complexity, genericity, or configuration.
- Code should remain understandable by the repository owner after long gaps.

### Reliability

- Consider failure modes and resource lifecycle.
- Ensure cleanup paths exist where relevant (files, streams, clients).
- Fail-fast behavior is preferred over silent error masking.

### Naming

- Names should reflect the abstraction level and responsibility.
- Low-level infrastructure code should avoid domain semantics.

### Simplicity rule

If no functional bugs are found, still check whether:

- the implementation is the simplest clear solution
- unnecessary abstractions were introduced
- the public API can be smaller or clearer

Feedback should be grouped as:

- critical issues
- important improvements
- optional polish

Absence of bugs does **not** mean the review is complete. Design quality, clarity, and maintainability should still be evaluated.

## Commit Messages

Use Conventional Commits.

### Commit message discipline

Use Conventional Commits.

Format:

type(scope): short description

Optional body explaining the reasoning.

Example:

feat(infra): add fail-fast detached task supervision

Introduce `TaskSupervisor` for detached asyncio tasks with centralized
exception handling and a one-shot failure hook.

---

### Types

Allowed commit types:

- feat — add a new capability or user-visible behavior
- fix — correct a bug or unintended behavior
- refactor — restructure code without changing behavior
- perf — improve performance without changing behavior
- test — add or update automated tests
- docs — documentation-only changes
- chore — maintenance tasks, tooling updates, or repository housekeeping

Use the type that best reflects the **intent of the change**, not the file modified.  
Prefer the most specific type that matches the intent.  
Do not invent new commit types.

---

### Breaking changes

Agents must explicitly evaluate whether a commit introduces a backward-incompatible change.

Typical breaking changes include:

- renamed or removed environment variables
- renamed, removed, or semantically changed settings fields
- changed configuration file formats or required values
- changed public function/class/module interfaces used by callers
- changed CLI arguments, flags, or behavior relied on by users
- changed persisted data formats or storage schemas
- renamed or removed domain concepts referenced by existing code

If a change is backward-incompatible, the commit must be marked as breaking.

Use one of the following forms:

type!: short description
type(scope)!: short description

A commit marked with `!` must also include a footer describing the migration.

Format:

BREAKING CHANGE: <describe exactly what changed and what must be updated>

The footer must state the concrete migration required by existing users,
deployments, or environments.

Example:

feat!: add superuser-aware fail-fast shutdown notifications

BREAKING CHANGE: replace `USER_ALLOWLIST` with `SUPERUSER_IDS` and `USER_IDS`.
Existing `.env` files and code reading `Settings.user_allowlist` must be updated.

When configuration contracts (`.env`, `Settings`, CLI flags, file formats)
change, agents must assume the change may be breaking and explicitly
justify whether a breaking change marker is required.

---

### Subject rules

The subject should describe the **system-level change**, not the exact
implementation detail.

Rules:

- lowercase subject
- imperative mood
- ≤ 72 characters
- describe **what capability or behavior changed**

Prefer semantic descriptions of the change rather than listing files or classes.

Good examples:

feat(infra): add fail-fast detached task supervision  
fix(handlers): acknowledge callback queries
refactor(services): key chat message buffer by chat id  
perf(domain): reduce video normalization overhead
test(services): add chat message buffer tests
docs: add `AGENTS.md` with repository workflow guidelines  
chore(deps): bump aiogram to 3.0.0

Avoid vague subjects such as:

- "add workflow instructions"
- "update agent rules"
- "improve system behavior"

Subjects should clearly indicate **what capability changed**.

Implementation details such as class names, modules, or files should
normally appear in the commit body.

---

### Referencing files and entities

When commit messages reference files, classes, modules, or functions,
wrap their names in backticks so they render clearly on GitHub.

Examples:

Rename `MessageBuffer` to `ChatMessageBuffer`  
Update `AGENTS.md` commit guidelines  
Move logic into `TaskSupervisor`  
Adjust `handlers.py` routing filter  

Use this formatting consistently for:

- files (`AGENTS.md`, `README.md`)
- modules (`handlers.py`)
- classes (`TaskSupervisor`)
- functions (`normalize_video_volume`)

Backticks improve readability in GitHub commit messages and should be preserved.

---

### Shell safety when creating commit messages

Backticks have special meaning in shells (command substitution).  
If a commit message is passed via a shell command using **double quotes**, the
shell will try to execute the backticked text as a command.

Incorrect (will break):

git commit -m "Refactor `TaskScheduler` API"

Correct approaches:

1. Prefer **single quotes** when backticks appear:

git commit -m 'refactor(services): make task scheduler key-agnostic' \
           -m 'Replace `TaskScheduler` user-coupled API with generic `Hashable` key.'

2. Safest method (preferred for multi-line messages): use a heredoc:

git commit -F - <<'EOF'
refactor(services): make task scheduler key-agnostic

Replace `TaskScheduler` user-coupled API with a generic `Hashable` key.
Update handlers to schedule jobs using `chat_id`.
EOF

Rules for agents:

- Never place backticks inside double-quoted commit messages.
- Use single quotes or a heredoc when commit text contains backticks.
- Backticked identifiers such as `TaskScheduler`, `AGENTS.md`, or
  `normalize_video_volume` must be preserved literally.

---

### Referencing canonical repository files

When a commit **primarily modifies a well-known repository document**, it
is often clearer to mention that file directly in the subject.

This applies especially to canonical project documents such as:

- `AGENTS.md`
- `README.md`
- `CONTRIBUTING.md`
- `CHANGELOG.md`

Example:

docs: expand `AGENTS.md` commit message guidelines

However, do **not force filenames into the subject unnecessarily**.
Prefer conceptual descriptions when the change is broader than a single file.

Good:

docs: expand `AGENTS.md` commit message guidelines

Also good:

docs: add deployment documentation

---

### Commit body guidelines

Add a commit body when the reasoning behind the change is important.

A body is recommended when:

- the commit modifies multiple modules or subsystems
- a refactor changes conceptual behavior or structure
- a rename introduces a clearer abstraction
- the reason for the change is not obvious from the subject
- the commit prepares or enables a later change

The body should explain **why the change was made**, not list the diff.

Avoid bodies that simply restate code changes.

Good:

refactor(services): key chat message buffer by chat id

Rename `MessageBuffer` to `ChatMessageBuffer` and key buffered messages
by `chat_id` instead of aiogram `User`. Buffering belongs to chat context
because messages are collected from chats and responses are sent back to
chats.

`TaskScheduler` remains user-keyed for now and will be refactored
separately.

Avoid bodies like:

- renamed X
- changed Y
- updated Z

---

### Commit scope discipline

The scope should represent a **stable semantic subsystem of the repository**.

Scopes should correspond to long-lived architectural areas rather than
temporary implementation details.

Examples of valid scopes in this repository:

- `app` — application bootstrap and runtime wiring
- `handlers` — Telegram handlers and routing logic
- `services` — application services and runtime state containers
- `infra` — shared infrastructure utilities (async helpers, supervisors, S3)
- `settings` — configuration loading and validation
- `deps` — dependency updates

Prefer **existing subsystem names** over inventing new scopes.

Avoid choosing scope based only on:

- a single touched file
- a temporary implementation detail
- a directory that does not represent an architectural boundary

---

### Root-level files

Changes to repository-level files usually **omit scope**.

Examples:

docs: update `README.md` with setup instructions  
chore: update `.gitignore`  
docs: update `AGENTS.md` workflow rules  

Use `deps` only for dependency changes:

chore(deps): pin development dependencies

---

### Generic infrastructure

If a change introduces a **generic reusable module** not tied to a specific
subsystem (for example async utilities or task supervision), use the
`infra` scope.

Example:

feat(infra): add fail-fast task supervisor for detached asyncio tasks

---

### When scope is unclear

If a change does not clearly belong to a stable subsystem, omit the scope.

Examples:

feat: add task supervisor utility  
chore: update development workflow instructions

---

### Commit scope discipline

Keep commits conceptually coherent by subsystem and intent.

Do not combine unrelated changes in a single commit when scopes differ
(for example: `AGENTS.md` policy updates vs `src/` runtime code edits).

If unrelated local modifications exist, commit only files relevant to
the requested change by default.
