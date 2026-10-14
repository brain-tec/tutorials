---
description: Review a newcomer's Odoo PR (odoo/tutorials Server Framework 101, or similar first-module code like an "estate" practice module) for the issues experienced Odoo reviewers flag most often. Trigger on requests to review a PR/diff against the odoo/tutorials repo, or any newcomer's first Odoo module.
argument-hint: "[PR URL, PR number, or diff to review]"
allowed-tools: Read, Bash, Grep, WebFetch
---

Review a newcomer's Odoo PR the way the Server Framework 101 tutorial's regular reviewers do:
concise, specific, pointing at the convention being violated — not a wall of generic advice. The
checklist below was built by mining real review comments across past tutorial PRs, keeping only the
issues that recur often (raised in more than 5 of 50 analyzed PRs), then checked against Odoo 20.0,
then refined by test-driving the skill against real PRs and comparing its output to what the actual
reviewer caught (a handful of items were added from that validation pass — see `evidence.md`). Full
methodology, frequencies, and sourcing are in `evidence.md`.

## How to review

1. **Get the diff and read every changed file in full** — not just the ones a checklist item below
   points at. Correctness bugs hide in XML and CSV just as often as in Python: a `filter_domain`
   using `>` where `>=` was meant, a default-filter context key that doesn't match any actual
   `<filter name="...">`, a field reference that doesn't exist. None of these have a dedicated
   checklist item (no view/XML convention was frequent enough to be promoted), so they're only
   caught by actually reading the markup, not by pattern-matching the checklist.
2. **Work out which tutorial chapters the PR has reached.** Each checklist item is tagged with the
   earliest chapter whose exercise first makes it relevant (e.g. "Ch. 7+" means: only check this
   once relational fields exist). Don't flag an item whose chapter hasn't been reached yet — e.g.
   don't ask for `_compute_`-prefixed methods before any compute field exists. A few items
   (commit/git hygiene) apply from the very first commit, tagged accordingly.
3. **Walk the checklist below**, Critical first, for files/chapters that are in scope.
4. **When you find a bug pattern, check sibling files and methods for the same pattern** before
   finalizing — e.g. if one action method silently swallows an error instead of raising it, check
   every other action method in the module, not just the one where you first spotted it. Newcomers
   (and real reviewers) repeat the same mistake across every file that shares the pattern.
5. **Leave comments in the tone real reviewers use**: short, pointing at the exact line, naming the
   convention rather than re-deriving it, with the fix stated plainly. Don't restate what the diff
   already shows; explain *why* only when it's a correctness/security issue rather than a style nit.
6. **Don't invent new style/convention findings outside this checklist** for a first module — stick
   to what's below. This does *not* limit bug-hunting: an outright bug (a typo that breaks the
   module, a field or filter referencing something that doesn't exist, a conditional check that can
   never be true given the field's own declared values, an error that's silently swallowed, a side
   effect ordered before the validation that should gate it) is always in scope, in any file type,
   checklist item or not.

## Output format

Group findings by file. For each file, list issues top to bottom as:

    **<severity>** `path/to/file.py:<line>` — <rule being violated, one line>

Severity is one of:
- **blocking** — Critical: functional bugs, security holes, or anything that breaks module
  install/functionality. Must be fixed before merge.
- **should fix** — Major: strong convention violations a reviewer will always flag.
- **nit** — Minor: style/naming nits, fine to leave as a non-blocking suggestion.

End with a one-line summary: counts per severity, and whether any blocking issues remain.

## Checklist

Sorted by severity, then how often it was actually raised. Each item: the rule, the chapter from
which it applies ("Ch. N+", or "from your first commit" for git/process items that aren't tied to
tutorial content), and a short why when it's not obvious from the rule alone.

### Critical — blocking

- **Use a callable (lambda) for a field's `default=`, never a bare expression.** *(Ch. 5+)* A
  non-callable default is computed once when the server starts, not per record — every record
  created afterwards silently gets the same stale value (e.g. a fixed "3 months from now" date that
  never advances). This is the single most common bug in the "Default Values" exercise.
- **Override `create()` with `@api.model_create_multi`, accepting and iterating `vals_list`.**
  *(Ch. 12+)* Odoo calls `create()` with a batch of records routinely (imports, demo data) — a
  single-record override silently drops or mishandles everything but the first. Note: the
  tutorial's own Inheritance chapter shows a plain `@api.model` example for `create()`, which is
  misleading — don't copy it as-is.
- **Don't let an action or validation method silently fail.** *(Ch. 9+)* If a precondition isn't
  met, `raise` an error — don't just `return False`/`None` (and don't build a `UserError(...)`
  without `raise`-ing it, which is the same bug in disguise: the exception object is created and
  immediately discarded). Either way the user clicks the button and nothing visibly happens. Check
  every action method for this, not just the first one you read.

### Major — should fix

- **Wrap user-facing error/exception strings in `self.env._()`.** *(Ch. 9+, from the first
  `UserError`)* Unlike field labels, exception messages aren't auto-translated.
- **Keep CI (style/tutorial checks) green before requesting review.** *(from your first commit)*
- **Squash fixup/WIP commits into one commit per chapter, ideally one per PR.** *(from your first
  commit)*
- **Follow the standard model attribute order** (private attrs → fields → SQL constraints →
  compute/inverse/search → selection methods → constrains/onchange → CRUD overrides → actions →
  business methods), per the official coding guidelines. *(Ch. 8+, once a model has more than just
  fields)*
- **Follow commit message conventions: `[TAG] module: imperative description`**, body explains WHY
  not what. *(from your first commit)*
- **Use `float_compare`/`float_is_zero` instead of direct float (in)equality.** *(Ch. 10+)*
  Direct float comparison is a correctness risk, not just style.
- **Use the current access-rights file and id convention.** *(Ch. 4+)* **Odoo 20.0 note:** the
  published tutorial still teaches `ir.model.access.csv` — but Odoo 20.0 already replaced
  `ir.model.access`/`ir.rule` with a unified `ir.access` model, and the file is now
  `security/ir.access.csv` with columns `id,name,model_id,group_id/id,operation,domain`. Code using
  the old filename will not load on a real 20.0 database. The `id` naming convention itself
  (`access_<model>_<group>`) is unchanged.
- **Suffix relational fields with `_id` (Many2one) / `_ids` (One2many, Many2many).** *(Ch. 7+)*
- **Prefix compute methods `_compute_` and onchange methods `_onchange_`.** *(Ch. 8+)*
- **Order manifest `data` entries so dependencies load first** (security, then views, then menus).
  *(Ch. 4+)* Data files load sequentially in the order listed; a menu referencing an action defined
  later in the list fails on install.
- **Don't call `browse`/`search` inside a loop — batch it first.** *(Ch. 12+)* Classic N+1 query
  pattern, usually seen inside a `create()` override.
- **Selection keys (the tuple's first element) must be snake_case with no spaces**, e.g.
  `offer_received`, not `offer received`. *(Ch. 5+)*
- **Use dotted technical names for models** (`estate.property`, not `estate_property`), with the
  Python class name matching (`EstateProperty`). *(Ch. 3+)* This is the universal Odoo convention
  (`sale.order`, `account.move`, ...); an underscored name won't break anything by itself, but it's
  wrong often enough, and consistently enough, that it's worth checking even though it wasn't common
  in the mined PR sample.
- **List every field the compute method actually reads in `@api.depends`**, not just the obvious
  one. *(Ch. 8+)* A compute that reads `record.create_date` but only declares
  `@api.depends("validity")` won't recompute correctly if that dependency set is incomplete.
- **Guard dict key access in `create()`/`write()` overrides.** *(Ch. 12+)* Don't assume a key like
  `vals['property_id']` exists in every `vals` dict passed to a batched `create()` — use `.get()` or
  check first.

### Minor — nit

- **End every file with a single trailing newline.** *(Ch. 2+)* The single most repeated nit.
- **Use single quotes for technical strings, double quotes for user-facing strings.** *(Ch. 3+)*
- **Use `max(recordset.mapped('field'), default=0)` instead of manual if/else for an empty
  recordset.** *(Ch. 8+)*
- **Use `fields.Date`/`fields.Datetime` helpers instead of manual `datetime`/`relativedelta`
  imports.** *(Ch. 5+)*
- **Don't restate manifest keys that already equal their default** (e.g. `version`, empty `demo`).
  *(Ch. 2+)*
- **Use a descriptive loop variable instead of generic `record`.** *(Ch. 8+)*
- **Group and alphabetize imports**: stdlib/3rd-party, then `odoo`, then `odoo.addons`. *(Ch. 3+)*
- **Name field constructor arguments explicitly (keyword args).** *(Ch. 3+)*
- **Name the Python class in CamelCase matching the model**, not a generic name. *(Ch. 3+)*
- **Don't commit personal editor/tooling config** (`.vscode`, a personal `ruff.toml`, etc.).
  *(from your first commit)*
- **Explain the functional WHY in the commit/PR body** (problem, goal, solution), not just what
  changed. *(from your first commit)*
- **Prefer a recordset-level read/write over looping record-by-record** when no per-record branch is
  actually needed. *(Ch. 9+)* e.g. check a condition across `self` once, then bulk-assign
  `self.state = 'sold'` outside the loop, instead of looping and assigning inside it.
- **Set `auto_install: True` on a glue/bridge module** whose only purpose is integrating two
  already-independent modules (e.g. a module depending on both `estate` and `account` to add
  invoicing to property sales). *(Ch. 13+)* This is the documented purpose of `auto_install`
  (`module.html`'s own example is `sale_crm`, depending on `sale` and `crm`) — without it, the
  integration module just sits there uninstalled even though both its dependencies are present.
- **Don't repeat a field's `string=` label across every view that displays it.** *(Ch. 6+)* Set it
  once on the field in the Python model; a view only needs its own `string=` when that particular
  view genuinely wants a different label than the model's default.

## Evidence & methodology

`evidence.md` has the full dataset this checklist was built from: all 50 clustered findings
(including the lower-frequency ones dropped here), per-finding PR counts and reviewer counts,
source comment links, and the Odoo 20.0 validation citations, plus three validation passes that
added 7 further items (one Critical, three Major, three Minor) after comparing the skill's own
review of real PRs against what the actual reviewer caught. Summary: 453 candidate PRs since
2025-10-01, 50 with reviewer activity, 1060 comments analyzed, 50 distinct findings, 25 of which
recur in more than 5 of the 50 PRs and are promoted into the checklist above, plus 7 added from
direct validation.
