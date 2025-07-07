# Vector‑Free Code‑Aware LangGraph Architecture

## 1 Problem Statement

Build a LangGraph pipeline that can:

1. Accept a **feature request** and optional **planning documents**.
2. Inspect an existing codebase + docs *without* vector embeddings.
3. Decide whether to **draft a planning doc** or **implement code changes**.
4. Break large work into PR‑sized steps, then iteratively locate relevant files with static search tools and write code.

---

## 2 Planning Process Overview

We separate *what to build* from *how to slice the work* by using two planning tiers.

### 2.1 Strategy Planner — *Big‑Picture Design*

Acts like the project architect.

- **Responsibility**: Ensure a high‑level plan exists that maps the feature onto the current repo. If the user’s doc is sufficient, pass it forward (on borderline cases, it should pass forward); otherwise it drafts a additional document in MD format to describe the feature and its requirements, adding clarifying questions if required (for easy to answer questions, it should make a best guess). The node should make an assessment whether the doc it has made represents an opinionated decision making or is a neutral expansion/clarification, and wether it has sufficient information to hand off to the step planner. if the former it should flag the new document for review.
- **Inputs**
  - `feature_request` (text)
  - Optional user‑supplied design doc
  - `file_manifest` (directory listing) + brief summary
  - High‑level symbol stats (`symbol_index`)
- **Outputs**
  - `planning_doc` (Markdown)
  - `complexity_flag` → `plan_first` | `code_now`
  - Optional `review_flag` for human approval

### 2.2 Step Planner — *PR‑Sized Task List*

Behaves like the project manager.

- **Responsibility**: Turn the approved `planning_doc` into reviewable steps (ideally small, though sometimes large refactors are unavoidable). It should have a preference for keeping the code-base running without errors at each step (e.g. using modular code with abstract interfaces, or stubbing functions which will later be used which provide hardcoded values).
- **Inputs**
  - `planning_docs` (from human inpur and strategy planner node)
- **Outputs**
  - `step_list` – ordered list of step objects
    ```json
    [
      {"id":1,"title":"Add dark‑mode toggle","files":["src/ui/settings.py"],"rationale":"Expose user control"},
      {"id":2,"title":"Persist preference","files":["src/storage/settings.py"],"rationale":"Store choice"}
    ]
    ```
  - Warnings when a step exceeds budget (triggers further splitting)

---

## 3 Shared Data Model (`AgentState`)

| Field                | Type                   | Purpose                                   |
| -------------------- | ---------------------- | ----------------------------------------- |
| `feature_request`    | `str`                  | Original user request                     |
| `planning_doc`       | `Optional[str]`        | High‑level design (supplied or generated) |
| `file_manifest`      | `list[str]`            | All repo file paths                       |
| `symbol_index`       | `dict[str, list[str]>` | Tag → files (ctags/tree‑sitter)           |
| `candidate_snippets` | `list[str]`            | Grep/tree‑sitter excerpts during search   |
| `relevant_files`     | `list[str]`            | Files deemed pertinent                    |
| `step_list`          | `list[Step]`           | PR‑sized tasks                            |
| `messages`           | `list[BaseMessage]`    | Running log / audit trail                 |

*Heavy artefacts (full file bodies) stay on disk; state holds only metadata.*

---

## 4 Tool Layer (No Vectors)

| Tool | Implementation                 | Output                       |
| ---- | ------------------------------ | ---------------------------- |
| `file_enumerate`   | `os.walk`, filters             | `[paths]`                    |
| `ctags_index`   | `ctags -R --fields=+n`         | `symbol_index` dict          |
| `grep_search`   | ripgrep (`rg -nHI -A5 -B2`)    | list of “file\:line snippet” |
| `tree_sitter_extract`   | Language‑aware body extraction | code chunks                  |
| `write_file`   | Already exists in codebase. Some mods needed.     |              |

All tools are deterministic, cacheable, and fast.

---

## 5 Graph‑Level Flow Overview

```
 bootstrap_codebase ─► strategy_planner ─► step_planner ─► loop_steps ─► validate?
```

### 5.1 `bootstrap_codebase` node *(once per session)*

1. `file_enumerate` → `state.file_manifest`
2. `ctags_index`    → `state.symbol_index`

### 5.2 `strategy_planner` node

Uses inputs in §2.1 to (optionally) create additional `planning_doc`. If `review_flag` is set, execution pauses for human approval. Can set `complexity_flag`.

### 5.3 `step_planner` node

Consumes `planning_doc` and `relevant_files`; outputs `step_list`.

### 5.4 `loop_steps` sub‑graph *(iterates over **`step_list`**)*

For each step:

1. **fine\_scan** – grep/tree‑sitter on the step’s files → fresh snippets
2. **generate\_code** – build prompt with step + snippets → `proposed_changes`
3. **apply\_changes** – call `write_file`; append to `code_changes`
4. **validate** – run linters/tests; on failure attach errors and jump back to regenerate.

### 5.5 `validate` node (optional global pass)

Run project‑wide tests; failure may trigger new bug‑fix steps.

---

## 6 Design Rationale

- **Context economy:** Only small snippets reach the LLM.
- **Determinism:** ripgrep/ctags outputs are repeatable → easier debugging.
- **No exotic infra:** avoids vector DB and embedding costs.
- **Clear hand‑offs:** Strategy → Steps → Automated code keeps humans in control at meaningful checkpoints.

---

## 7 Next‑Step Checklist

1. Implement `ctags_index` & `grep_search` tools.
2. Build `bootstrap_codebase`, `strategy_planner`, and `step_planner` nodes.
3. Scaffold `loop_steps` as a LangGraph sub‑graph with fine‑scan, code‑gen, apply, validate.
4. Unit test with a toy repo: ensure `step_list` respects budgets and `relevant_files` non‑empty.
5. Decide validation tooling (pytest, mypy, flake8, etc.).

---

ℹ️ Feel free to comment inline or flag sections for change; we’ll iterate as needed.

