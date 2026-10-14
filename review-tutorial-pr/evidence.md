# Evidence: reviewer feedback on odoo/tutorials PRs (Server Framework 101)

Reference data for `SKILL.md`. Full methodology, per-finding frequency, representative examples,
source comment links, and Odoo 20.0 validation citations.

## Validation pass: testing the skill against real PRs (added after initial publication)

After the initial 25-item checklist shipped, the skill was test-driven against two real PRs
end-to-end: the skill's own review was written *without* reading the PR's actual comments (to keep
it independent), then compared line-by-line against what the real reviewer (`msho-odoo`, not one of
the 10 reviewers in the original mining set) actually caught across both PRs' full comment history.

- **PR #1408** (base 19.0, estate module through Chapter 10): the skill's review matched well; no
  checklist changes resulted.
- **PR #1415** (base 19.0, estate module through Chapter 13, `create()` override, inheritance, a
  second dependent module): comparison surfaced two kinds of gap:
  1. **Findings the real reviewer raised that weren't in the checklist at all.** Five were common/
     clear-cut enough to promote:
     - Silent failure in action/validation methods (`return False` with no `raise`, or a `UserError`
       built but never raised) — the real reviewer raised this independently in *two different
       files* in the same PR, and the skill's own review only caught one instance because it didn't
       generalize the pattern across sibling files. Promoted as **Critical**, Ch. 9+.
     - Dotted model technical names (`estate.property`, not `estate_property`) with matching class
       names — the real reviewer flagged this explicitly ("apply it in all models, please"), even
       though it wasn't common enough in the original 50-PR mining sample to clear the >5 threshold
       on its own. Promoted as **Major**, Ch. 3+.
     - `@api.depends` missing a field the compute method actually reads (here: `create_date`).
       Promoted as **Major**, Ch. 8+.
     - No guard on dict key access (`vals['property_id']`) in a `create()` override — the real
       reviewer flagged the crash risk explicitly. Promoted as **Major**, Ch. 12+.
     - Looping record-by-record where a recordset-level read/write would do (e.g. checking a
       condition across `self` once instead of per record, then bulk-assigning outside the loop).
       Promoted as **Minor**, Ch. 9+.
  2. **A methodology gap, not a missing rule**: the skill's review never opened the view XML files'
     actual content (`filter_domain`, context default keys, field references) — only checked
     structural things (manifest data order, trailing newlines) — because no XML/view convention
     cleared the >5-PR promotion bar. But the real reviewer caught two outright bugs there: a
     `filter_domain` using `>` where `>=` was intended, and a default-filter context key
     (`search_default_estate_state`) that doesn't match the actual filter's `name` (`state`), so the
     intended default filter silently never applies. Neither is a "convention" — both are bugs that
     only show up by reading the markup. `SKILL.md`'s "How to review" section now explicitly
     instructs reading every changed file's full content (not just where a checklist item points),
     and explicitly scopes "outright bugs" to cover every file type, not just Python.
- **Not real misses**: several of the real reviewer's comments were from earlier revisions and
  already fixed by the PR's head commit (the `default=` lambda, an EOF newline, a `.gitignore` file,
  `auto_install`, a redundant `base` dependency, an empty `models/__init__.py`) — the skill's review,
  based on the final diff, correctly didn't flag these, and that's not counted as a gap.
- **Full review write-ups**: `test_tutorial_review_1.md` and `test_tutorial_review_2.md` (repo root)
  have the complete findings from both test runs.

### Second validation round: PR #1413

A third PR (base 19.0, estate module through Chapter 13, same real reviewer `msho-odoo`) was
reviewed independently and compared against the actual comment history. Full write-up:
`test_tutorial_review_3.md` (repo root).

- **Promoted:** `auto_install: True` on a glue/bridge module (e.g. `estate_account`, depending on
  both `estate` and `account`). The real reviewer flagged this as missing on **both** PRs that
  included such a dependent module (#1415 and #1413) — a 2-for-2 recurrence strong enough to
  override the original mining frequency (3/50, below the >5 threshold). Confirmed against the
  official docs: `module.html` describes exactly this pattern — "generally used for 'link modules'
  implementing synergetic integration between two otherwise independent modules... sale_crm depends
  on both sale and crm and is set to auto_install." Chapter 13 is where the tutorial first
  introduces a second, dependent module.
- **Explicitly NOT promoted, despite recurring:** removing a redundant `'base'` entry from
  `depends` when it's already transitively implied by other listed dependencies. The real reviewer
  suggested this on both PRs too, but it's **contradicted by the official 20.0 docs**: `module.html`
  states plainly, "Module base is always installed in any Odoo instance. But you still need to
  specify it as dependency to make sure your module is updated when base is updated." Since the
  skill targets 20.0, not this reviewer's personal practice, the documented rule wins — this one
  stays out of the checklist. (Recorded here so a future pass doesn't re-add it based on seeing the
  same reviewer comment again.)
- **Not promoted, noted for awareness only:** a missing `journal_id` on an `account.move` created in
  an `estate_account`-style invoicing override (`self.env['account.move'].create({...})` without
  specifying which sales journal to use). This is a real, still-unfixed bug the reviewer caught and
  the skill's review missed — but it requires accounting-domain knowledge rather than a general
  Odoo/Python convention, and was only observed once. Not promoted; worth revisiting if it recurs in
  future validation.
- **Version-calibration note, no change needed:** the skill's review flagged bare `_("...")` (as
  opposed to `self.env._(...)`) as a nit on this 19.0 PR. The real reviewer's own suggested fix uses
  bare `_()`, and 19.0-era code consistently uses it — appearing miscalibrated. But the skill targets
  Odoo **20.0**, where `self.env._()` is the confirmed current form (see the manifest/translation
  research above) — the "miscalibration" is an artifact of testing against an older 19.0 PR, not a
  flaw in the checklist itself. No change made.
- **Independent catch, not in the real reviewer's comments:** `name="Real_Estate"` (literal
  underscore in a user-facing menu label) in `estate_menus.xml` — found only because the skill's
  updated "read every changed file in full" instruction was followed. Direct payoff from the
  previous validation round's fix.

### Third validation round: a review of the review (PR #1413, no new PR)

Rather than testing against a new PR, `test_tutorial_review_3.md`'s own write-up was independently
re-checked (not against the real reviewer's comments this time — a second pass asking "what did the
first review itself miss"). Four confirmed misses resulted, documented in that file's addendum: a
dead conditional (`"cancelled" in <an offer's status list>`, where the offer's own `status` field
can never hold that value — it's a property state, not an offer status), a side effect (invoice
creation) ordered before the validation that should gate it, the same ordering issue's batch-level
corollary, and a stat button placed in `<header>` instead of `button_box`. All four re-verified
against the actual code before being accepted, not taken on faith from the cross-check.

Two of these are generalizable bug *classes*, not PR-specific facts, so they were folded into
`SKILL.md`'s "always in scope" bug list (generically worded, not naming this PR's specific fields):
checking a conditional against a value outside the field's actual `Selection` domain, and a side
effect ordered before its gating validation. The other two (button placement, the batch/per-record
ordering nuance) are recorded here only — too specific/singly-observed to generalize into the
skill's methodology yet.

### Fourth validation round: PR #1385 (lighter real review, recurring gap confirmed a 3rd time)

A fourth PR (base 19.0, reviewer `yoba-odoo` — neither of the two real reviewers seen in prior
rounds, and a notably lighter review: 9 inline comments total vs. dozens on the other three PRs) was
reviewed independently and compared against the actual comment history. Full write-up:
`test_tutorial_review_4.md` (repo root).

- **Promoted:** don't repeat a field's `string=` label across every view that displays it — set it
  once on the field in the Python model. The reviewer raised this exact point on this PR
  ("you don't have to set a string for the same field in each XML view... better to identify the
  name of the field in the field definition in the python file"). This is the **third** different
  reviewer, across three different PRs (#1415, #1413, #1385), to raise essentially this same point
  — clearing the same "recurs across multiple independent validation PRs" bar `auto_install` cleared
  at 2. Added as **Minor**, Ch. 6+ (Basic Views — the first chapter where a view references a field
  that already carries a model-level label).
- **Not real misses:** several other comments on this PR (EOF newline, constraints-after-fields
  ordering, security-file-first in manifest `data`, merging a separate `estate_basic_views.xml` into
  `estate_property_views.xml`) were from earlier revisions and already fixed by the head commit —
  correctly not flagged by the skill's review, based on the final diff.
- **No corroboration either way:** this reviewer's 9 comments never touched the skill's
  blocking/should-fix findings on this PR (a frozen `default=` constant, missing
  `self.ensure_one()`/looping across 4 action methods, an unconditional state regression in
  `create()`, invoice-created-before-validation ordering, the access-rights group suffix,
  `auto_install`, `.editorconfig` at the repo root). Unlike the `msho-odoo` rounds, there's no
  independent human judgment to confirm or refute these against — the reviewer simply reviewed more
  lightly on this particular PR (two of three review summaries are just "Nice work").

## What's promoted into SKILL.md vs. archived here only

`SKILL.md` is published in the public tutorial repo, so it only carries a lean, chapter-staged
summary — no reviewer logins, no bad/good code blocks. This file keeps the full record for anyone
who wants to audit it: all 50 clustered findings, not just the ones that made the cut.

- **Promotion rule:** a finding is promoted into `SKILL.md`'s checklist only if it was raised in
  **more than 5 of the 50** analyzed PRs. 25 of the 50 findings qualify. A further 7 items were
  added later from direct validation testing rather than frequency (see "Validation pass" above) —
  `SKILL.md`'s checklist has 32 items in total.
- **Explicit drops** (qualified by frequency but excluded by decision, since the skill ships in the
  public tutorial repo and these are internal-employment conventions, not general Odoo/OSS rules):
  finding #13 ("Set `'license': 'LGPL-3'`", 7/50 PRs) and finding #23 ("Set manifest `author` to
  `'Odoo S.A.'`", 11/50 PRs). Both remain below in the full table/detail, verdict unchanged.
- **Chapter mapping:** each promoted finding is tagged in `SKILL.md` with the earliest Server
  Framework 101 chapter whose exercise first makes the issue possible, determined by reading the
  actual 20.0 tutorial chapter text (not guessed from the rule's category). Notable mapping
  evidence:
  - The `default=` lambda bug (finding #1) traces to Chapter 5's "Default Values" exercise
    ("the default availability date is in 3 months") — the chapter's own prose example uses a
    correct callable (`default=fields.Datetime.now`), but the exercise itself invites the bug.
  - The `create()`/`vals_list` bug (finding #2) traces to Chapter 12 (Inheritance)'s CRUD-override
    exercise ("When an offer is created, the property state should change..."). **Important:** the
    chapter's own reference example shows `@api.model` (not `@api.model_create_multi`) on a
    `create(self, vals_list)` override — this is itself a stale/misleading example relative to real
    Odoo 20.0 convention (confirmed current via `addons/sale/models/sale_order.py` on the `20.0`
    branch, which uses `@api.model_create_multi`). This plausibly explains why the finding is raised
    in 9 distinct PRs by 8 of the 9 reviewers — newcomers are likely copying the tutorial's own
    example.
  - The access-rights finding (#10) and manifest `data`-ordering finding (#14) both trace to
    Chapter 4, which explicitly teaches "data files are loaded sequentially following their order
    in `__manifest__.py`" and still shows `ir.model.access.csv` (see the docs/engine mismatch note
    below).
  - The selection-key snake_case finding (#16) traces to Chapter 5's `state` field exercise ("Five
    values are possible: New, Offer Received, ...") — "Offer Received" is the actual source of the
    `'offer received'` vs `'offer_received'` mistake, not the earlier `garden_orientation` field in
    Chapter 3 (whose values — North/South/East/West — are single words with no snake_case risk).
  - Git/commit-hygiene findings (CI green, squash commits, commit message format, personal editor
    config, commit WHY) aren't tied to tutorial content at all — the numbered chapters don't cover
    the fork/PR workflow — so they're tagged "from your first commit" (first possible at Chapter 2,
    the first chapter with any files to commit).

## Data collection

- **Scope:** PRs in `odoo/tutorials` created on or after 2025-10-01, reviewed or commented on by at
  least one of `ushyme`, `nilu-odoo`, `kfr-odoo`, `cgun-odoo`, `aboo-odoo`, `lost-odoo`, `antonrom1`,
  `ltinel`, `amah-odoo`, `clbr-odoo`.
- **Candidate PRs:** 453 created in that window (search via `repo:odoo/tutorials type:pr
  created:>=2025-10-01`). Of those, **50 PRs** had at least one attributable comment from the 9
  active reviewers. `kfr-odoo` had zero commenting/review activity in this window across all 453
  candidate PRs (independently confirmed via `commenter:kfr-odoo` search restricted to the same
  date range — not a data-collection gap).
- **Comments collected:** 1060 total — 30 general PR conversation comments (`issues/{pr}/comments`),
  940 inline code review comments (`pulls/{pr}/comments`), 90 non-empty review summary bodies
  (`pulls/{pr}/reviews`). All fetched via the GitHub REST API, filtered server-side to the 9 logins
  above; zero PRs failed to fetch.
- **Per-reviewer activity in range** (comments / distinct PRs): lost-odoo 246/13, aboo-odoo 205/12,
  ltinel 187/3, clbr-odoo 125/7, cgun-odoo 71/2, nilu-odoo 58/2, amah-odoo 58/4, antonrom1 56/6,
  ushyme 54/4, kfr-odoo 0/0.
- **Clustering:** comments that pointed at the same underlying issue (even reworded) were merged
  into one finding; pure acknowledgments ("thanks", "LGTM", emoji-only) with no actionable content
  were dropped. 50 distinct findings resulted.
- **"Most common mistakes" exception:** the task spec calls for a separate top-of-skill section if
  any Minor/Major finding appears in **more than half** of the 50 analyzed PRs. The maximum observed
  was exactly 25/50 (trailing newlines) — tied, not exceeding, the threshold — so no finding
  technically qualifies. The two closest (trailing newlines, 25/50; `self.env._()` translation,
  22/50) are called out in `SKILL.md`'s intro instead of a dedicated section, and naturally sort to
  the top of their severity tier.

## Odoo 20.0 validation summary

Validated against the Odoo 20.0 branch of `odoo/odoo` (confirmed FINAL release via
`odoo/release.py`: `version_info = (20, 0, 0, FINAL, 0, '')`; `master` is already `20.1-alpha`) and
the live `https://www.odoo.com/documentation/20.0/` docs.

- **47 Valid**, **3 Changed**, **0 Obsolete**, **0 Unverified**.
- The 3 Changed findings all relate to real API changes landed in/by 20.0: the `ir.model.access.csv`
  → unified `ir.access.csv` rename/schema merge (affects 2 findings), and a corrected rationale for
  the `installable`/`application` manifest finding (the premise that `application: True` implies
  `installable` is false — `installable` defaults to `True` unconditionally, independent of
  `application`).
- **Notable docs/engine mismatch:** the published Odoo 20.0 tutorial
  (`developer/tutorials/server_framework_101/04_securityintro.html`) and the coding guidelines page
  still describe and exemplify `ir.model.access.csv` with `perm_read/perm_write/perm_create/
  perm_unlink` columns — but the actual 20.0 engine source
  (`odoo/addons/base/models/ir_access.py`, `odoo/addons/base/security/ir.access.csv`) has already
  replaced `ir.model.access` + `ir.rule` with a single `ir.access` model (`operation` + optional
  `domain` columns, filename `ir.access.csv`). A module still shipping the old filename will not
  load on a real 20.0 database — there is no backward-compat shim. This skill's checklist uses the
  verified-from-source engine behavior, not the (stale) published docs.

No findings were marked Obsolete, so there is no drop-list appendix.

---

## Frequency & verdict table

| # | Severity | Category | Rule | PRs | Reviewers | Verdict |
|---|---|---|---|---|---|---|
| 1 | Critical | orm | Use a lambda (or callable) for a field's `default=`, not a bare expression | 19/50 | 6 (aboo-odoo, amah-odoo, cgun-odoo, lost-odoo, ltinel, ushyme) | Valid |
| 2 | Critical | orm | Override `create()` with `@api.model_create_multi` and accept/iterate `vals_list` | 9/50 | 8 (aboo-odoo, amah-odoo, antonrom1, cgun-odoo, lost-odoo, ltinel, nilu-odoo, ushyme) | Valid |
| 3 | Critical | orm | Call `self.ensure_one()` in methods that assume a single record | 4/50 | 3 (aboo-odoo, antonrom1, clbr-odoo) | Valid |
| 4 | Major | orm | Wrap user-facing error/exception strings in `self.env._()` for translation | 22/50 | 6 (aboo-odoo, amah-odoo, antonrom1, lost-odoo, nilu-odoo, ushyme) | Valid |
| 5 | Major | git_hygiene | Keep the CI checks (ci/style, ci/tutorial / runbot) green before requesting review | 18/50 | 6 (amah-odoo, antonrom1, cgun-odoo, lost-odoo, ltinel, ushyme) | Valid |
| 6 | Major | git_hygiene | Squash fixup/WIP commits into one commit per chapter (ideally one commit per PR) | 15/50 | 4 (aboo-odoo, antonrom1, lost-odoo, ltinel) | Valid |
| 7 | Major | python_style | Follow the standard Model attribute order (private attrs, fields, SQL constraints, compute/inverse/search, selection, constrains/onchange, CRUD, actions, business methods) | 14/50 | 6 (aboo-odoo, amah-odoo, antonrom1, cgun-odoo, clbr-odoo, ltinel) | Valid |
| 8 | Major | commit_messages | Follow git commit message conventions: `[TAG] module: imperative description` | 13/50 | 5 (aboo-odoo, antonrom1, clbr-odoo, lost-odoo, ltinel) | Valid |
| 9 | Major | orm | Use `float_compare`/`float_is_zero` instead of direct float (in)equality | 12/50 | 5 (aboo-odoo, clbr-odoo, lost-odoo, ltinel, ushyme) | Valid |
| 10 | Major | security | Suffix `ir.model.access.csv` id/name with the target group, and don't re-prefix with the module name | 9/50 | 3 (cgun-odoo, clbr-odoo, lost-odoo) | Changed |
| 11 | Major | naming | Suffix relational field names with `_id` (Many2one) / `_ids` (One2many/Many2many) | 8/50 | 2 (aboo-odoo, clbr-odoo) | Valid |
| 12 | Major | naming | Prefix compute methods with `_compute_` and onchange methods with `_onchange_` | 7/50 | 5 (aboo-odoo, amah-odoo, cgun-odoo, clbr-odoo, ltinel) | Valid |
| 13 | Major | manifest | Set `'license': 'LGPL-3'` in the manifest (community modules) | 7/50 | 3 (amah-odoo, antonrom1, clbr-odoo) | Valid |
| 14 | Major | manifest | Order `data` entries in the manifest so dependencies load first (security, then views, then menus) | 6/50 | 5 (antonrom1, cgun-odoo, clbr-odoo, lost-odoo, nilu-odoo) | Valid |
| 15 | Major | performance | Don't call `browse`/`search` inside a loop — batch it before the loop | 6/50 | 4 (amah-odoo, lost-odoo, nilu-odoo, ushyme) | Valid |
| 16 | Major | naming | Selection field technical key (tuple[0]) must be snake_case with no spaces | 6/50 | 3 (amah-odoo, antonrom1, clbr-odoo) | Valid |
| 17 | Major | orm | Use the new `models.Constraint(...)` class-based API instead of the old `_sql_constraints` tuple list | 3/50 | 3 (aboo-odoo, ltinel, nilu-odoo) | Valid |
| 18 | Major | views_xml | Use the `<list>` view tag, not the legacy `<tree>` tag | 3/50 | 3 (cgun-odoo, clbr-odoo, lost-odoo) | Valid |
| 19 | Minor | python_style | End every file with a single trailing newline | 25/50 | 6 (aboo-odoo, antonrom1, cgun-odoo, clbr-odoo, lost-odoo, ushyme) | Valid |
| 20 | Minor | python_style | Use single quotes for technical strings, double quotes for user-facing strings | 18/50 | 4 (aboo-odoo, antonrom1, cgun-odoo, lost-odoo) | Valid |
| 21 | Minor | orm | Use `max(recordset.mapped('field'), default=0)` instead of manual if/else for empty recordsets | 16/50 | 4 (aboo-odoo, antonrom1, clbr-odoo, ltinel) | Valid |
| 22 | Minor | orm | Use Odoo's `fields.Date`/`fields.Datetime` helpers instead of manual `datetime`/`relativedelta` imports | 14/50 | 5 (aboo-odoo, antonrom1, clbr-odoo, ltinel, ushyme) | Valid |
| 23 | Minor | manifest | Set the manifest `author` to `'Odoo S.A.'` for work done as an Odoo employee | 11/50 | 4 (aboo-odoo, amah-odoo, clbr-odoo, ushyme) | Valid |
| 24 | Minor | manifest | Don't specify manifest keys that already equal their default (`version`, empty `demo`/`assets`) | 11/50 | 4 (antonrom1, clbr-odoo, lost-odoo, ltinel) | Valid |
| 25 | Minor | python_style | Use a descriptive loop variable instead of generic `record` | 10/50 | 4 (aboo-odoo, clbr-odoo, ltinel, nilu-odoo) | Valid |
| 26 | Minor | python_style | Group and alphabetize imports: stdlib/3rd-party, then odoo, then odoo.addons | 8/50 | 4 (aboo-odoo, antonrom1, clbr-odoo, lost-odoo) | Valid |
| 27 | Minor | python_style | Name field constructor arguments explicitly (keyword args) | 7/50 | 3 (clbr-odoo, lost-odoo, ltinel) | Valid |
| 28 | Minor | naming | Name the Python class in CamelCase matching the model/file, not a generic name | 6/50 | 5 (antonrom1, cgun-odoo, clbr-odoo, nilu-odoo, ushyme) | Valid |
| 29 | Minor | git_hygiene | Don't commit personal editor/tooling config (.vscode, local .gitignore additions, ruff.toml) | 6/50 | 4 (amah-odoo, clbr-odoo, ltinel, ushyme) | Valid |
| 30 | Minor | commit_messages | Explain the functional WHY in the PR/commit body (problem, goal, solution), not just what changed | 6/50 | 2 (aboo-odoo, lost-odoo) | Valid |
| 31 | Minor | naming | Model's `_description` is the short user-facing display name, not a long description of the module | 5/50 | 4 (antonrom1, cgun-odoo, clbr-odoo, lost-odoo) | Valid |
| 32 | Minor | views_xml | Prefer nesting `<menuitem>` elements over chaining explicit `parent=` attributes | 4/50 | 4 (antonrom1, clbr-odoo, ltinel, ushyme) | Valid |
| 33 | Minor | orm | Check truthiness of a recordset directly instead of its length | 4/50 | 3 (amah-odoo, clbr-odoo, ltinel) | Valid |
| 34 | Minor | python_style | Add a trailing comma on the last item of multiline lists/dicts/calls | 4/50 | 2 (antonrom1, clbr-odoo) | Valid |
| 35 | Minor | python_style | Don't add an unnecessary `else` after a branch that already returns/raises | 4/50 | 2 (clbr-odoo, ltinel) | Valid |
| 36 | Minor | manifest | Don't set `installable` when `application: True` is already set (it implies installable) | 4/50 | 1 (lost-odoo) | Changed |
| 37 | Minor | git_hygiene | Mark addressed review comments as resolved | 4/50 | 1 (lost-odoo) | Valid |
| 38 | Minor | python_style | Remove the obsolete `# -*- coding: utf-8 -*-` header and old Odoo license boilerplate from new files | 3/50 | 3 (antonrom1, clbr-odoo, lost-odoo) | Valid |
| 39 | Minor | python_style | Write each Selection tuple on its own line, indented, for future extensibility | 3/50 | 2 (antonrom1, clbr-odoo) | Valid |
| 40 | Minor | python_style | Use `comodel_name=` explicitly for Many2one/Many2many instead of a bare positional string | 3/50 | 2 (clbr-odoo, lost-odoo) | Valid |
| 41 | Minor | views_xml | Drop the obsolete `<?xml version="1.0" encoding="utf-8"?>` declaration from new view/data files | 3/50 | 2 (cgun-odoo, nilu-odoo) | Valid |
| 42 | Minor | manifest | Add `auto_install: True` to glue/bridge modules that should install once all their dependencies are present | 3/50 | 1 (lost-odoo) | Valid |
| 43 | Minor | git_hygiene | Prefer `--force-with-lease` over plain `--force` when force-pushing after rewriting history | 2/50 | 2 (clbr-odoo, ltinel) | Valid |
| 44 | Minor | security | Differentiate regular-user from manager/admin access (e.g. restrict delete rights) | 2/50 | 2 (cgun-odoo, nilu-odoo) | Valid |
| 45 | Minor | naming | Name the file after the model/class it defines | 2/50 | 2 (ltinel, nilu-odoo) | Valid |
| 46 | Minor | views_xml | Name an inherited/extending `ir.ui.view` record's `name` field as `<original>.inherit.<module>`, keeping the original xml id | 1/50 | 1 (cgun-odoo) | Valid |
| 47 | Minor | naming | Prefix genuinely private/internal methods with a leading underscore | 1/50 | 1 (lost-odoo) | Valid |
| 48 | Minor | security | Don't ship a module-specific `ir.model.access.csv` in a dependent module that defines no new models | 1/50 | 1 (ushyme) | Changed |
| 49 | Minor | other | Use a `views/` folder (plural), with no `__init__.py` (it holds no Python) | 1/50 | 1 (clbr-odoo) | Valid |
| 50 | Minor | security | Place security data files under `security/`, not `data/` | 1/50 | 1 (clbr-odoo) | Valid |

---

## Full evidence detail

### 1. Use a lambda (or callable) for a field's `default=`, not a bare expression
- **Category:** orm  **Criticality:** Critical  **Verdict:** Valid
- **Frequency:** 19 distinct PRs, 6 distinct reviewers (aboo-odoo, amah-odoo, cgun-odoo, lost-odoo, ltinel, ushyme)
- **PRs:** #1055, #1065, #1071, #1077, #1173, #1198, #1200, #1202, #1205, #1241, #1281, #1282, #1285, #1287, #1412, #1420, #1423, #1429, #1431
- **Notes:** Functional bug, not style: a bare expression is evaluated ONCE at server/registry start, so every record created afterwards gets the same stale default until the server restarts.
- **20.0 citation:** Longstanding ORM behavior (non-callable default evaluated once at class/registry build, not per-record) — unrelated to version. See https://www.odoo.com/documentation/20.0/developer/reference/backend/orm.html
- Bad:
```
date_availability = fields.Date(default=fields.Date.today() + relativedelta(months=3))
```
- Good:
```
date_availability = fields.Date(default=lambda self: fields.Date.today() + relativedelta(months=3))
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1055#discussion_r2619982972 , https://github.com/odoo/tutorials/pull/1281#discussion_r3303362214

### 2. Override `create()` with `@api.model_create_multi` and accept/iterate `vals_list`
- **Category:** orm  **Criticality:** Critical  **Verdict:** Valid
- **Frequency:** 9 distinct PRs, 8 distinct reviewers (aboo-odoo, amah-odoo, antonrom1, cgun-odoo, lost-odoo, ltinel, nilu-odoo, ushyme)
- **PRs:** #1035, #1063, #1075, #1171, #1198, #1241, #1285, #1412, #1414
- **Notes:** Functional bug: the single-vals form silently breaks (or only handles the first record) when Odoo calls create() with a batch of records, which happens routinely (e.g. demo data, imports).
- **20.0 citation:** Confirmed current in 20.0: addons/sale/models/sale_order.py uses `@api.model_create_multi def create(self, vals_list)`. https://raw.githubusercontent.com/odoo/odoo/20.0/addons/sale/models/sale_order.py ; https://www.odoo.com/documentation/20.0/developer/reference/backend/orm.html
- Bad:
```
@api.model
def create(self, vals):
    ...
    return super().create(vals)
```
- Good:
```
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        ...
    return super().create(vals_list)
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1198#discussion_r2958571372 , https://github.com/odoo/tutorials/pull/1035#discussion_r2550270215

### 3. Call `self.ensure_one()` in methods that assume a single record
- **Category:** orm  **Criticality:** Critical  **Verdict:** Valid
- **Frequency:** 4 distinct PRs, 3 distinct reviewers (aboo-odoo, antonrom1, clbr-odoo)
- **PRs:** #1033, #1035, #1281, #1285
- **Notes:** Correctness bug: reading a field directly on `self` (not looping) raises an unhandled traceback when called on a multi-record recordset (e.g. from a server action or the shell), even though it looks fine from the UI.
- **20.0 citation:** Unchanged long-standing API, independent of version.
- Bad:
```
def action_sell(self):
    if self.state == 'cancelled':
        raise UserError(...)
```
- Good:
```
def action_sell(self):
    self.ensure_one()
    if self.state == 'cancelled':
        raise UserError(...)
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1281#discussion_r3303334858 , https://github.com/odoo/tutorials/pull/1285#discussion_r3287480423

### 4. Wrap user-facing error/exception strings in `self.env._()` for translation
- **Category:** orm  **Criticality:** Major  **Verdict:** Valid
- **Frequency:** 22 distinct PRs, 6 distinct reviewers (aboo-odoo, amah-odoo, antonrom1, lost-odoo, nilu-odoo, ushyme)
- **PRs:** #1035, #1055, #1063, #1065, #1072, #1074, #1077, #1082, #1198, #1200, #1202, #1281, #1282, #1283, #1285, #1287, #1412, #1419, #1420, #1423, #1425, #1426
- **Notes:** Field labels/selection values are auto-translated by Odoo, but exception messages are not — this is explained almost identically by 4+ reviewers. Also note the API moved from standalone `_()` to `self.env._()`.
- **20.0 citation:** Confirmed current recommended form in 20.0 coding guidelines: `_()` available at `self.env._`. https://www.odoo.com/documentation/20.0/contributing/development/coding_guidelines.html
- Bad:
```
raise UserError("A sold property cannot be cancelled.")
```
- Good:
```
raise UserError(self.env._("A sold property cannot be cancelled."))
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1077#discussion_r2627305954 , https://github.com/odoo/tutorials/pull/1282#discussion_r3303460343

### 5. Keep the CI checks (ci/style, ci/tutorial / runbot) green before requesting review
- **Category:** git_hygiene  **Criticality:** Major  **Verdict:** Valid
- **Frequency:** 18 distinct PRs, 6 distinct reviewers (amah-odoo, antonrom1, cgun-odoo, lost-odoo, ltinel, ushyme)
- **PRs:** #1033, #1063, #1065, #1067, #1072, #1073, #1074, #1075, #1082, #1171, #1172, #1173, #1200, #1202, #1205, #1241, #1429, #1431
- **Notes:** Reviewers repeatedly ask newcomers to check their own CI/runbot status before or instead of relying on manual review comments for basic style issues.
- **20.0 citation:** Process convention, not Odoo-API dependent.
- Bad:
```
(PR left with a red runbot build for several review rounds)
```
- Good:
```
(push a fix so ci/style and ci/tutorial pass, then ping the reviewer)
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1067#issuecomment-3659918512 , https://github.com/odoo/tutorials/pull/1075#issuecomment-3674792019

### 6. Squash fixup/WIP commits into one commit per chapter (ideally one commit per PR)
- **Category:** git_hygiene  **Criticality:** Major  **Verdict:** Valid
- **Frequency:** 15 distinct PRs, 4 distinct reviewers (aboo-odoo, antonrom1, lost-odoo, ltinel)
- **PRs:** #1030, #1072, #1073, #1082, #1171, #1173, #1281, #1282, #1283, #1287, #1412, #1419, #1420, #1425, #1430
- **Notes:** 'One task -> one PR -> one commit' is stated as the default Odoo practice by multiple reviewers near the end of training; mid-training they accept one commit per tutorial chapter.
- **20.0 citation:** Matches git guidelines' clean-history expectations. https://www.odoo.com/documentation/20.0/contributing/development/git_guidelines.html
- Bad:
```
5 commits: 'wip', 'fix typo', 'address review', 'chapter 3', 'fix ci'
```
- Good:
```
1 commit: '[ADD] estate: chapter 3 - offers'
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1412#pullrequestreview-5264124468 , https://github.com/odoo/tutorials/pull/1281#pullrequestreview-4363146236

### 7. Follow the standard Model attribute order (private attrs, fields, SQL constraints, compute/inverse/search, selection, constrains/onchange, CRUD, actions, business methods)
- **Category:** python_style  **Criticality:** Major  **Verdict:** Valid
- **Frequency:** 14 distinct PRs, 6 distinct reviewers (aboo-odoo, amah-odoo, antonrom1, cgun-odoo, clbr-odoo, ltinel)
- **PRs:** #1033, #1036, #1069, #1071, #1171, #1172, #1173, #1241, #1281, #1283, #1285, #1420, #1425, #1430
- **Notes:** Cited directly from the official coding guidelines ('symbols-and-conventions') by name, by 5+ distinct reviewers — one of the few findings with a direct doc citation baked into the review comment itself.
- **20.0 citation:** Confirmed current in the worked `event.event` example. https://www.odoo.com/documentation/20.0/contributing/development/coding_guidelines.html
- Bad:
```
(action methods defined before fields; constraints mixed in among compute methods)
```
- Good:
```
(private attrs -> fields -> sql constraints -> compute/inverse/search -> selection -> constrains/onchange -> CRUD -> actions -> business methods)
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1036#discussion_r2545003268 , https://github.com/odoo/tutorials/pull/1283#discussion_r3302765542

### 8. Follow git commit message conventions: `[TAG] module: imperative description`
- **Category:** commit_messages  **Criticality:** Major  **Verdict:** Valid
- **Frequency:** 13 distinct PRs, 5 distinct reviewers (aboo-odoo, antonrom1, clbr-odoo, lost-odoo, ltinel)
- **PRs:** #1027, #1030, #1033, #1034, #1072, #1082, #1171, #1283, #1419, #1420, #1425, #1429, #1430
- **Notes:** `[ADD]` is for new module creation only; later work should use `[IMP]`; `[FIX]` is reserved for bug fixes (not lint/formatting, which should be `[CLN]`/`[LINT]` or just squashed away).
- **20.0 citation:** Confirmed current on the live 20.0 doc, tags [FIX]/[REF]/[ADD]/[REM]/[REV]/[MOV]/[REL]/[IMP]/[MERGE]/[CLA]/[I18N]/[PERF]/[CLN]/[LINT] all still listed. https://www.odoo.com/documentation/20.0/contributing/development/git_guidelines.html
- Bad:
```
Added new Fields to Estate module
```
- Good:
```
[ADD] estate: add garden fields to property model
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1171#issuecomment-3908938500 , https://github.com/odoo/tutorials/pull/1028#pullrequestreview-3481913748

### 9. Use `float_compare`/`float_is_zero` instead of direct float (in)equality
- **Category:** orm  **Criticality:** Major  **Verdict:** Valid
- **Frequency:** 12 distinct PRs, 5 distinct reviewers (aboo-odoo, clbr-odoo, lost-odoo, ltinel, ushyme)
- **PRs:** #1033, #1074, #1077, #1082, #1171, #1172, #1173, #1202, #1281, #1283, #1287, #1425
- **Notes:** Direct float comparison is a correctness risk (precision errors), not merely style.
- **20.0 citation:** Confirmed present, same import path, in odoo/tools/float_utils.py on 20.0. https://raw.githubusercontent.com/odoo/odoo/20.0/odoo/tools/float_utils.py
- Bad:
```
if record.selling_price < record.expected_price * 0.9:
```
- Good:
```
if float_compare(record.selling_price, record.expected_price * 0.9, precision_digits=2) < 0:
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1033#discussion_r2546583766 , https://github.com/odoo/tutorials/pull/1171#discussion_r2817817394

### 10. Suffix `ir.model.access.csv` id/name with the target group, and don't re-prefix with the module name
- **Category:** security  **Criticality:** Major  **Verdict:** Changed
- **Frequency:** 9 distinct PRs, 3 distinct reviewers (cgun-odoo, clbr-odoo, lost-odoo)
- **PRs:** #1026, #1028, #1198, #1200, #1202, #1205, #1241, #1423, #1424
- **Notes:** The module-name prefix on the model/xmlid is automatic within that module's own CSV; the group suffix leaves room for adding e.g. a manager rule later without renaming.
- **20.0 form:** The file itself is renamed and its schema merged in 20.0: `security/ir.access.csv` (not `ir.model.access.csv`), columns `id,name,model_id,group_id/id,operation,domain` — `operation` (e.g. `'crud'`,`'r'`,`'cru'`) replaces the four `perm_*` booleans, and an optional `domain` column folds former `ir.rule` record-rule rows into the same file. The `id` naming convention itself (`access_<model_name>_<group_name>`) is unchanged, just under the new filename/schema. Note: the published coding-guidelines page is stale and still shows the old `ir.model.access.csv` filename.
- **20.0 citation:** https://raw.githubusercontent.com/odoo/odoo/20.0/odoo/addons/base/models/ir_access.py ; https://raw.githubusercontent.com/odoo/odoo/20.0/odoo/addons/base/security/ir.access.csv ; coding guidelines page confirmed stale on this point: https://www.odoo.com/documentation/20.0/contributing/development/coding_guidelines.html
- Bad:
```
estate_access_estate_property,estate_property,estate.model_estate_property,base.group_user,1,1,1,1
```
- Good:
```
# 20.0: security/ir.access.csv (old ir.model.access.csv is gone)
id,name,model_id,group_id/id,operation,domain
access_estate_property_user,access_estate_property_user,model_estate_property,base.group_user,crud,
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1198#discussion_r2958598959 , https://github.com/odoo/tutorials/pull/1241#discussion_r3118147173

### 11. Suffix relational field names with `_id` (Many2one) / `_ids` (One2many/Many2many)
- **Category:** naming  **Criticality:** Major  **Verdict:** Valid
- **Frequency:** 8 distinct PRs, 2 distinct reviewers (aboo-odoo, clbr-odoo)
- **PRs:** #1032, #1281, #1283, #1287, #1412, #1419, #1425, #1430
- **20.0 citation:** Standard long-standing Odoo convention, unrelated to version.
- Bad:
```
buyer = fields.Many2one('res.partner')
tags = fields.Many2many('estate.property.tag')
```
- Good:
```
buyer_id = fields.Many2one('res.partner')
tag_ids = fields.Many2many('estate.property.tag')
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1032#discussion_r2546714907 , https://github.com/odoo/tutorials/pull/1420#discussion_r4060724106

### 12. Prefix compute methods with `_compute_` and onchange methods with `_onchange_`
- **Category:** naming  **Criticality:** Major  **Verdict:** Valid
- **Frequency:** 7 distinct PRs, 5 distinct reviewers (aboo-odoo, amah-odoo, cgun-odoo, clbr-odoo, ltinel)
- **PRs:** #1033, #1055, #1071, #1172, #1241, #1281, #1412
- **20.0 citation:** Confirmed current in Method conventions. https://www.odoo.com/documentation/20.0/contributing/development/coding_guidelines.html
- Bad:
```
best_price = fields.Float(compute="get_best_price")
```
- Good:
```
best_price = fields.Float(compute="_compute_best_price")
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1055#discussion_r2619986772 , https://github.com/odoo/tutorials/pull/1281#discussion_r3303323135

### 13. Set `'license': 'LGPL-3'` in the manifest (community modules)
- **Category:** manifest  **Criticality:** Major  **Verdict:** Valid
- **Frequency:** 7 distinct PRs, 3 distinct reviewers (amah-odoo, antonrom1, clbr-odoo)
- **PRs:** #1026, #1027, #1028, #1030, #1032, #1034, #1063
- **20.0 citation:** Confirmed `license` key present/required, value `LGPL-3`, in a real 20.0 manifest. https://raw.githubusercontent.com/odoo/odoo/20.0/addons/product/__manifest__.py
- Bad:
```
{
    'name': 'Real Estate',
    'depends': ['base'],
}
```
- Good:
```
{
    'name': 'Real Estate',
    'depends': ['base'],
    'license': 'LGPL-3',
}
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1026#discussion_r2541134608 , https://github.com/odoo/tutorials/pull/1030#discussion_r2540964880

### 14. Order `data` entries in the manifest so dependencies load first (security, then views, then menus)
- **Category:** manifest  **Criticality:** Major  **Verdict:** Valid
- **Frequency:** 6 distinct PRs, 5 distinct reviewers (antonrom1, cgun-odoo, clbr-odoo, lost-odoo, nilu-odoo)
- **PRs:** #1027, #1033, #1241, #1414, #1424, #1426
- **Notes:** Correctness issue, not just style: a menu item referencing an action defined later in the load order fails on module install.
- **20.0 citation:** General module-loading behavior (data files load in listed order), unrelated to version.
- Bad:
```
'data': [
    'views/estate_menus.xml',
    'views/estate_property_views.xml',
    'security/ir.access.csv',
],
```
- Good:
```
'data': [
    'security/ir.access.csv',
    'views/estate_property_views.xml',
    'views/estate_menus.xml',
],
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1033#discussion_r2541035696 , https://github.com/odoo/tutorials/pull/1027#discussion_r2541031992

### 15. Don't call `browse`/`search` inside a loop — batch it before the loop
- **Category:** performance  **Criticality:** Major  **Verdict:** Valid
- **Frequency:** 6 distinct PRs, 4 distinct reviewers (amah-odoo, lost-odoo, nilu-odoo, ushyme)
- **PRs:** #1055, #1077, #1082, #1200, #1202, #1414
- **Notes:** Classic N+1 query / performance anti-pattern, repeatedly called out across both `create()` overrides and general business logic.
- **20.0 citation:** Confirmed current anti-pattern with explicit before/after example. https://www.odoo.com/documentation/20.0/developer/reference/backend/performance.html
- Bad:
```
for vals in vals_list:
    property = self.env['estate.property'].browse(vals['property_id'])
    ...
```
- Good:
```
property_ids = [v['property_id'] for v in vals_list]
properties = self.env['estate.property'].browse(property_ids)
for vals, property in zip(vals_list, properties):
    ...
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1082#discussion_r2647990571 , https://github.com/odoo/tutorials/pull/1202#discussion_r2973521528

### 16. Selection field technical key (tuple[0]) must be snake_case with no spaces
- **Category:** naming  **Criticality:** Major  **Verdict:** Valid
- **Frequency:** 6 distinct PRs, 3 distinct reviewers (amah-odoo, antonrom1, clbr-odoo)
- **PRs:** #1026, #1028, #1032, #1033, #1055, #1071
- **20.0 citation:** General Odoo convention, unrelated to version.
- Bad:
```
selection=[('offer received', 'Offer Received')]
```
- Good:
```
selection=[('offer_received', 'Offer Received')]
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1026#discussion_r2541117745 , https://github.com/odoo/tutorials/pull/1032#discussion_r2546688933

### 17. Use the new `models.Constraint(...)` class-based API instead of the old `_sql_constraints` tuple list
- **Category:** orm  **Criticality:** Major  **Verdict:** Valid
- **Frequency:** 3 distinct PRs, 3 distinct reviewers (aboo-odoo, ltinel, nilu-odoo)
- **PRs:** #1173, #1283, #1414
- **Notes:** Flagged as a recent API change; one reviewer also mentions a new `models.UniqueIndex` helper. Needs explicit version validation (Step 4) — this looks like a genuine recent/upcoming API change, not an established long-standing rule.
- **20.0 citation:** Confirmed current: `models.Constraint` defined in odoo/orm/table_objects.py and used in addons/sale/models/sale_order.py; `_sql_constraints` tuple-list handling no longer exists in odoo/orm/models.py. https://raw.githubusercontent.com/odoo/odoo/20.0/odoo/orm/table_objects.py
- Bad:
```
_sql_constraints = [
    ('positive_price', 'CHECK(expected_price > 0)', 'Price must be positive.'),
]
```
- Good:
```
_check_positive_price = models.Constraint(
    'CHECK(expected_price > 0)',
    "Price must be positive.",
)
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1173#discussion_r2840972446 , https://github.com/odoo/tutorials/pull/1283#discussion_r3302900930

### 18. Use the `<list>` view tag, not the legacy `<tree>` tag
- **Category:** views_xml  **Criticality:** Major  **Verdict:** Valid
- **Frequency:** 3 distinct PRs, 3 distinct reviewers (cgun-odoo, clbr-odoo, lost-odoo)
- **PRs:** #1028, #1074, #1241
- **Notes:** Explicitly noted as a renamed tag (tree was the old name); independently confirmed current/required in Odoo 20.0 docs.
- **20.0 citation:** Confirmed current: doc explicitly states list views' root element is `list` (previous name `tree`); `tree` not recognized anywhere in ir_ui_view.py on 20.0. https://www.odoo.com/documentation/20.0/developer/reference/user_interface/view_architectures.html
- Bad:
```
<record id="estate_property_view_list" model="ir.ui.view">
    <field name="arch" type="xml">
        <tree string="Properties">
```
- Good:
```
<record id="estate_property_view_list" model="ir.ui.view">
    <field name="arch" type="xml">
        <list string="Properties">
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1028#discussion_r2541441314 , https://github.com/odoo/tutorials/pull/1074#discussion_r2626435386

### 19. End every file with a single trailing newline
- **Category:** python_style  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 25 distinct PRs, 6 distinct reviewers (aboo-odoo, antonrom1, cgun-odoo, clbr-odoo, lost-odoo, ushyme)
- **PRs:** #1026, #1027, #1028, #1030, #1032, #1033, #1034, #1065, #1072, #1073, #1074, #1075, #1079, #1082, #1198, #1200, #1202, #1241, #1287, #1412, #1424, #1425, #1429, #1430, #1431
- **Notes:** By far the single most frequently repeated nitpick across every file type (.py, .xml, .csv) and nearly every reviewer; several reviewers note it's what Ruff/CI (ci/style) auto-fixes.
- **20.0 citation:** General convention, unrelated to version.
- Bad:
```
from odoo import fields, models


class EstateProperty(models.Model):
    ...
    _name = 'estate.property'
```
- Good:
```
...same content, with a newline character after the final line...
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1082#discussion_r2635061124 , https://github.com/odoo/tutorials/pull/1200#discussion_r2945272238

### 20. Use single quotes for technical strings, double quotes for user-facing strings
- **Category:** python_style  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 18 distinct PRs, 4 distinct reviewers (aboo-odoo, antonrom1, cgun-odoo, lost-odoo)
- **PRs:** #1034, #1035, #1072, #1073, #1074, #1082, #1198, #1200, #1202, #1205, #1241, #1281, #1287, #1412, #1419, #1423, #1424, #1431
- **Notes:** Widely repeated but reviewers themselves note it's a team-by-team tacit convention, not an enforced rule — several explicitly say 'not everybody follows that' or 'pick one and be consistent'.
- **20.0 citation:** General/team convention, unrelated to version.
- Bad:
```
_name = "estate.property"
_description = 'Estate Property'
```
- Good:
```
_name = 'estate.property'
_description = "Estate Property"
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1423#discussion_r4060079598 , https://github.com/odoo/tutorials/pull/1241#discussion_r3128758234

### 21. Use `max(recordset.mapped('field'), default=0)` instead of manual if/else for empty recordsets
- **Category:** orm  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 16 distinct PRs, 4 distinct reviewers (aboo-odoo, antonrom1, clbr-odoo, ltinel)
- **PRs:** #1026, #1027, #1028, #1033, #1034, #1035, #1172, #1173, #1281, #1282, #1283, #1285, #1287, #1412, #1420, #1425
- **20.0 citation:** General Python/ORM idiom, unrelated to version.
- Bad:
```
if record.offer_ids:
    record.best_price = max(record.offer_ids.mapped('price'))
else:
    record.best_price = 0.0
```
- Good:
```
record.best_price = max(record.offer_ids.mapped('price'), default=0.0)
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1026#discussion_r2546817591 , https://github.com/odoo/tutorials/pull/1173#discussion_r2826485599

### 22. Use Odoo's `fields.Date`/`fields.Datetime` helpers instead of manual `datetime`/`relativedelta` imports
- **Category:** orm  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 14 distinct PRs, 5 distinct reviewers (aboo-odoo, antonrom1, clbr-odoo, ltinel, ushyme)
- **PRs:** #1024, #1026, #1028, #1032, #1033, #1034, #1036, #1065, #1075, #1077, #1173, #1282, #1283, #1287
- **Notes:** Also flags a type mismatch: using a Datetime-producing expression as the default for a Date field triggers an unnecessary cast.
- **20.0 citation:** General convention, unrelated to version.
- Bad:
```
from datetime import datetime
from dateutil.relativedelta import relativedelta
...
default=lambda self: datetime.now() + relativedelta(months=3)
```
- Good:
```
default=lambda self: fields.Date.add(fields.Date.today(), months=3)
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1024#discussion_r2540914679 , https://github.com/odoo/tutorials/pull/1065#discussion_r2627677655

### 23. Set the manifest `author` to `'Odoo S.A.'` for work done as an Odoo employee
- **Category:** manifest  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 11 distinct PRs, 4 distinct reviewers (aboo-odoo, amah-odoo, clbr-odoo, ushyme)
- **PRs:** #1024, #1063, #1069, #1077, #1079, #1281, #1283, #1285, #1412, #1425, #1430
- **Notes:** This is an Odoo-R&D-employee-specific convention (work-for-hire), not a general Odoo/OSS rule — won't apply outside this internal-training context.
- **20.0 citation:** Internal Odoo-employee convention (not a public doc rule) — unaffected by the 20.0 engine change, still applicable under the same condition (work done as an Odoo employee).
- Bad:
```
'author': 'John Doe',
```
- Good:
```
'author': 'Odoo S.A.',
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1077#discussion_r2626882628 , https://github.com/odoo/tutorials/pull/1281#discussion_r3303385740

### 24. Don't specify manifest keys that already equal their default (`version`, empty `demo`/`assets`)
- **Category:** manifest  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 11 distinct PRs, 4 distinct reviewers (antonrom1, clbr-odoo, lost-odoo, ltinel)
- **PRs:** #1028, #1032, #1034, #1035, #1072, #1074, #1082, #1171, #1172, #1173, #1198
- **20.0 citation:** Confirmed `_DEFAULT_MANIFEST` mechanism still exists in 20.0 (see installable/application entry below for the same file).
- Bad:
```
'version': '1.0',
'demo': [],
```
- Good:
```
(omit both — 1.0 and [] are already the defaults)
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1028#discussion_r2541404584 , https://github.com/odoo/tutorials/pull/1198#discussion_r2945186022

### 25. Use a descriptive loop variable instead of generic `record`
- **Category:** python_style  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 10 distinct PRs, 4 distinct reviewers (aboo-odoo, clbr-odoo, ltinel, nilu-odoo)
- **PRs:** #1032, #1033, #1171, #1172, #1173, #1281, #1282, #1283, #1287, #1414
- **20.0 citation:** General style, unrelated to version.
- Bad:
```
for record in self:
    record.best_price = ...
```
- Good:
```
for property in self:
    property.best_price = ...
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1026#discussion_r2546809525 , https://github.com/odoo/tutorials/pull/1171#discussion_r2816754175

### 26. Group and alphabetize imports: stdlib/3rd-party, then odoo, then odoo.addons
- **Category:** python_style  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 8 distinct PRs, 4 distinct reviewers (aboo-odoo, antonrom1, clbr-odoo, lost-odoo)
- **PRs:** #1024, #1034, #1035, #1036, #1281, #1283, #1287, #1423
- **Notes:** Cited as the Ruff/CI-enforced rule, with a direct link to the coding guidelines' imports section.
- **20.0 citation:** Confirmed current 3-group ordering. https://www.odoo.com/documentation/20.0/contributing/development/coding_guidelines.html
- Bad:
```
from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
```
- Good:
```
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1036#discussion_r2545256746 , https://github.com/odoo/tutorials/pull/1283#discussion_r3302784593

### 27. Name field constructor arguments explicitly (keyword args)
- **Category:** python_style  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 7 distinct PRs, 3 distinct reviewers (clbr-odoo, lost-odoo, ltinel)
- **PRs:** #1027, #1074, #1172, #1198, #1200, #1205, #1423
- **Notes:** Matches the team CLAUDE.md rule to always pass field constructor args by keyword.
- **20.0 citation:** Team convention, unaffected by version.
- Bad:
```
buyer_id = fields.Many2one('res.partner', True, False)
```
- Good:
```
buyer_id = fields.Many2one(comodel_name='res.partner', copy=False)
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1200#discussion_r2945281006 , https://github.com/odoo/tutorials/pull/1198#discussion_r2945234751

### 28. Name the Python class in CamelCase matching the model/file, not a generic name
- **Category:** naming  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 6 distinct PRs, 5 distinct reviewers (antonrom1, cgun-odoo, clbr-odoo, nilu-odoo, ushyme)
- **PRs:** #1024, #1027, #1032, #1079, #1250, #1426
- **20.0 citation:** General convention, unrelated to version; consistent with the worked example in coding_guidelines.html.
- Bad:
```
class Property(models.Model):
    _name = 'estate.property'
```
- Good:
```
class EstateProperty(models.Model):
    _name = 'estate.property'
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1026#discussion_r2541074096 , https://github.com/odoo/tutorials/pull/1079#discussion_r2630382711

### 29. Don't commit personal editor/tooling config (.vscode, local .gitignore additions, ruff.toml)
- **Category:** git_hygiene  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 6 distinct PRs, 4 distinct reviewers (amah-odoo, clbr-odoo, ltinel, ushyme)
- **PRs:** #1026, #1028, #1032, #1069, #1077, #1173
- **20.0 citation:** General git hygiene, unrelated to version.
- Bad:
```
committing .vscode/settings.json or a personal ruff.toml alongside the module
```
- Good:
```
add them to your global/local gitignore instead; keep the PR to module files only
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1065#discussion_r2627615469 , https://github.com/odoo/tutorials/pull/1082#discussion_r2648000773

### 30. Explain the functional WHY in the PR/commit body (problem, goal, solution), not just what changed
- **Category:** commit_messages  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 6 distinct PRs, 2 distinct reviewers (aboo-odoo, lost-odoo)
- **PRs:** #1082, #1281, #1282, #1283, #1285, #1287
- **20.0 citation:** Confirmed current: "Body must explain WHY, not what... 'PO team asked me to do it' is not an acceptable why." https://www.odoo.com/documentation/20.0/contributing/development/git_guidelines.html
- Bad:
```
(commit body left empty, or restates 'add fields to model')
```
- Good:
```
PROBLEM: newcomers need a way to track real-estate offers
GOAL: let a salesperson record and accept/refuse offers
SOLUTION: new estate.property.offer model + state machine
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1082#issuecomment-3675026744 , https://github.com/odoo/tutorials/pull/1281#pullrequestreview-4363146236

### 31. Model's `_description` is the short user-facing display name, not a long description of the module
- **Category:** naming  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 5 distinct PRs, 4 distinct reviewers (antonrom1, cgun-odoo, clbr-odoo, lost-odoo)
- **PRs:** #1027, #1028, #1033, #1202, #1241
- **20.0 citation:** Confirmed `_name`/`_description` still the first required private attributes in the worked example. https://www.odoo.com/documentation/20.0/contributing/development/coding_guidelines.html
- Bad:
```
_description = "Starting module for Estate - manages real estate properties and offers"
```
- Good:
```
_description = "Estate Property"
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1027#discussion_r2540989104 , https://github.com/odoo/tutorials/pull/1202#discussion_r2973531712

### 32. Prefer nesting `<menuitem>` elements over chaining explicit `parent=` attributes
- **Category:** views_xml  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 4 distinct PRs, 4 distinct reviewers (antonrom1, clbr-odoo, ltinel, ushyme)
- **PRs:** #1024, #1036, #1079, #1173
- **20.0 citation:** General view-authoring style, unrelated to version.
- Bad:
```
<menuitem id="estate_menu_root" name="Real Estate"/>
<menuitem id="estate_property_menu" parent="estate_menu_root"/>
```
- Good:
```
<menuitem id="estate_menu_root" name="Real Estate">
    <menuitem id="estate_property_menu" .../>
</menuitem>
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1079#discussion_r2630403877 , https://github.com/odoo/tutorials/pull/1173#discussion_r2816946204

### 33. Check truthiness of a recordset directly instead of its length
- **Category:** orm  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 4 distinct PRs, 3 distinct reviewers (amah-odoo, clbr-odoo, ltinel)
- **PRs:** #1026, #1028, #1055, #1173
- **20.0 citation:** Long-standing recordset convention (bool reflects non-emptiness), unrelated to version.
- Bad:
```
if len(record.offer_ids) > 0:
```
- Good:
```
if record.offer_ids:
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1026#discussion_r2546815473 , https://github.com/odoo/tutorials/pull/1055#discussion_r2620010611

### 34. Add a trailing comma on the last item of multiline lists/dicts/calls
- **Category:** python_style  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 4 distinct PRs, 2 distinct reviewers (antonrom1, clbr-odoo)
- **PRs:** #1032, #1033, #1034, #1036
- **Notes:** Rationale given explicitly: keeps git blame/diffs clean when a later PR appends another line.
- **20.0 citation:** General Python style, unrelated to version.
- Bad:
```
'data': [
    'security/ir.access.csv',
    'views/estate_menus.xml'
],
```
- Good:
```
'data': [
    'security/ir.access.csv',
    'views/estate_menus.xml',
],
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1034#discussion_r2540845478 , https://github.com/odoo/tutorials/pull/1032#discussion_r2541126686

### 35. Don't add an unnecessary `else` after a branch that already returns/raises
- **Category:** python_style  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 4 distinct PRs, 2 distinct reviewers (clbr-odoo, ltinel)
- **PRs:** #1026, #1032, #1056, #1171
- **20.0 citation:** General Python style, unrelated to version.
- Bad:
```
if record.state == 'sold':
    raise UserError(...)
else:
    record.state = 'cancelled'
```
- Good:
```
if record.state == 'sold':
    raise UserError(...)
record.state = 'cancelled'
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1032#discussion_r2546718965 , https://github.com/odoo/tutorials/pull/1171#discussion_r2817193728

### 36. Don't set `installable` when `application: True` is already set (it implies installable)
- **Category:** manifest  **Criticality:** Minor  **Verdict:** Changed
- **Frequency:** 4 distinct PRs, 1 distinct reviewers (lost-odoo)
- **PRs:** #1072, #1073, #1074, #1082
- **20.0 form:** The premise is incorrect: `_DEFAULT_MANIFEST` in odoo/modules/module.py sets `installable: True` and `application: False` as fully INDEPENDENT defaults — `application` does not imply or set `installable`. The correct reasoning is simply that `installable` already defaults to `True` unconditionally, so writing `installable: True` explicitly is redundant regardless of `application`'s value (same category as the other "don't restate manifest defaults" finding, not a special case of `application`).
- **20.0 citation:** https://raw.githubusercontent.com/odoo/odoo/20.0/odoo/modules/module.py
- Bad:
```
'application': True,
'installable': True,
```
- Good:
```
'application': True,
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1072#discussion_r2623603402 , https://github.com/odoo/tutorials/pull/1082#discussion_r2635065263

### 37. Mark addressed review comments as resolved
- **Category:** git_hygiene  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 4 distinct PRs, 1 distinct reviewers (lost-odoo)
- **PRs:** #1072, #1073, #1198, #1205
- **20.0 citation:** GitHub process convention, unrelated to Odoo version.
- Bad:
```
(20 open review threads left unresolved after pushing fixes)
```
- Good:
```
(click 'Resolve conversation' on each thread once the fix is pushed)
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1171#issuecomment-3945540975 , https://github.com/odoo/tutorials/pull/1198#pullrequestreview-3973551267

### 38. Remove the obsolete `# -*- coding: utf-8 -*-` header and old Odoo license boilerplate from new files
- **Category:** python_style  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 3 distinct PRs, 3 distinct reviewers (antonrom1, clbr-odoo, lost-odoo)
- **PRs:** #1034, #1035, #1429
- **20.0 citation:** Python 3 default encoding makes the header unnecessary; unrelated to Odoo version.
- Bad:
```
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright...
from odoo import fields, models
```
- Good:
```
from odoo import fields, models
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1035#discussion_r2549131027 , https://github.com/odoo/tutorials/pull/1429#discussion_r4034816314

### 39. Write each Selection tuple on its own line, indented, for future extensibility
- **Category:** python_style  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 3 distinct PRs, 2 distinct reviewers (antonrom1, clbr-odoo)
- **PRs:** #1026, #1028, #1035
- **20.0 citation:** General style, unrelated to version.
- Bad:
```
selection=[('new','New'),('offer_received','Offer Received'),('sold','Sold')]
```
- Good:
```
selection=[
    ('new', 'New'),
    ('offer_received', 'Offer Received'),
    ('sold', 'Sold'),
],
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1026#discussion_r2541117745 , https://github.com/odoo/tutorials/pull/1035#discussion_r2549155362

### 40. Use `comodel_name=` explicitly for Many2one/Many2many instead of a bare positional string
- **Category:** python_style  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 3 distinct PRs, 2 distinct reviewers (clbr-odoo, lost-odoo)
- **PRs:** #1032, #1074, #1198
- **20.0 citation:** General/team convention, matches field-specific attribute ordering rule, unaffected by version.
- Bad:
```
partner_id = fields.Many2one('res.partner')
```
- Good:
```
partner_id = fields.Many2one(comodel_name='res.partner')
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1074#discussion_r2626382359 , https://github.com/odoo/tutorials/pull/1198#discussion_r2945234751

### 41. Drop the obsolete `<?xml version="1.0" encoding="utf-8"?>` declaration from new view/data files
- **Category:** views_xml  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 3 distinct PRs, 2 distinct reviewers (cgun-odoo, nilu-odoo)
- **PRs:** #1241, #1414, #1426
- **Notes:** lxml (which processes Odoo's XML) assumes the default version/encoding, so this is dead weight in every new file.
- **20.0 citation:** Long-standing Odoo data-file convention, unrelated to version.
- Bad:
```
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record ...>
```
- Good:
```
<odoo>
    <record ...>
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1414#discussion_r4104697502 , https://github.com/odoo/tutorials/pull/1426#discussion_r4133987006

### 42. Add `auto_install: True` to glue/bridge modules that should install once all their dependencies are present
- **Category:** manifest  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 3 distinct PRs, 1 distinct reviewers (lost-odoo)
- **PRs:** #1198, #1200, #1205
- **20.0 citation:** Confirmed `auto_install` defaults to `False` in `_DEFAULT_MANIFEST` on 20.0, so explicit `True` is still required for bridge modules. https://raw.githubusercontent.com/odoo/odoo/20.0/odoo/modules/module.py
- Bad:
```
(estate_account depends on estate + account but has no auto_install key)
```
- Good:
```
'auto_install': True,
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1198#discussion_r2958623011 , https://github.com/odoo/tutorials/pull/1205#discussion_r2980211102

### 43. Prefer `--force-with-lease` over plain `--force` when force-pushing after rewriting history
- **Category:** git_hygiene  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 2 distinct PRs, 2 distinct reviewers (clbr-odoo, ltinel)
- **PRs:** #1024, #1173
- **Notes:** --force-with-lease protects against silently clobbering commits pushed by someone else to the same branch in the meantime.
- **20.0 citation:** General git safety practice, unrelated to Odoo version.
- Bad:
```
git push --force
```
- Good:
```
git push --force-with-lease
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1024#pullrequestreview-3481245713 , https://github.com/odoo/tutorials/pull/1173#pullrequestreview-3841513449

### 44. Differentiate regular-user from manager/admin access (e.g. restrict delete rights)
- **Category:** security  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 2 distinct PRs, 2 distinct reviewers (cgun-odoo, nilu-odoo)
- **PRs:** #1241, #1414
- **Notes:** Raised as a design question rather than a hard rule in both PRs — treat as a discussion point, not a strict checklist item.
- **20.0 citation:** See the ir.access.csv rename citation above.
- Bad:
```
access_estate_property_user,...,base.group_user,1,1,1,1  (full CRUD for every user, no manager tier)
```
- Good:
```
access_estate_property_user,...,base.group_user,1,1,1,0
access_estate_property_manager,...,estate.group_manager,1,1,1,1
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1241#discussion_r3128853966 , https://github.com/odoo/tutorials/pull/1414#discussion_r4104688536

### 45. Name the file after the model/class it defines
- **Category:** naming  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 2 distinct PRs, 2 distinct reviewers (ltinel, nilu-odoo)
- **PRs:** #1172, #1414
- **20.0 citation:** General convention, unrelated to version.
- Bad:
```
estate/models/inherited_model.py  (extends res.users)
estate/models/property.py  (defines estate.property.type)
```
- Good:
```
estate/models/res_users.py
estate/models/estate_property_type.py
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1172#discussion_r2832341108 , https://github.com/odoo/tutorials/pull/1414#discussion_r4104679514

### 46. Name an inherited/extending `ir.ui.view` record's `name` field as `<original>.inherit.<module>`, keeping the original xml id
- **Category:** views_xml  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 1 distinct PRs, 1 distinct reviewers (cgun-odoo)
- **PRs:** #1241
- **20.0 citation:** Confirmed current. https://www.odoo.com/documentation/20.0/contributing/development/coding_guidelines.html
- Bad:
```
<record id="my_custom_user_view" model="ir.ui.view">
    <field name="name">users_form_estate</field>
```
- Good:
```
<record id="view_users_form" model="ir.ui.view">
    <field name="name">res.users.view.form.inherit.estate</field>
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1241#discussion_r3137794245 , https://github.com/odoo/tutorials/pull/1241#discussion_r3137801917

### 47. Prefix genuinely private/internal methods with a leading underscore
- **Category:** naming  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 1 distinct PRs, 1 distinct reviewers (lost-odoo)
- **PRs:** #1198
- **Notes:** Rationale given: any method without a leading underscore is callable from the external API (RPC), so internal helpers should be marked private.
- **20.0 citation:** General Python/Odoo convention, unrelated to version.
- Bad:
```
def check_selling_price(self):
```
- Good:
```
def _check_selling_price(self):
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1198#discussion_r2958555444

### 48. Don't ship a module-specific `ir.model.access.csv` in a dependent module that defines no new models
- **Category:** security  **Criticality:** Minor  **Verdict:** Changed
- **Frequency:** 1 distinct PRs, 1 distinct reviewers (ushyme)
- **PRs:** #1075
- **20.0 form:** Same filename/schema rename as above: the file to avoid duplicating is `ir.access.csv` in 20.0, not `ir.model.access.csv`. The underlying principle (don't duplicate access rows for a module defining no new models) is unaffected.
- **20.0 citation:** https://raw.githubusercontent.com/odoo/odoo/20.0/odoo/addons/base/models/ir_access.py
- Bad:
```
# dependent_module/security/ir.model.access.csv duplicating base module access rows
```
- Good:
```
# 20.0: don't ship a redundant security/ir.access.csv at all if the module defines no new models
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1075#discussion_r2646893556

### 49. Use a `views/` folder (plural), with no `__init__.py` (it holds no Python)
- **Category:** other  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 1 distinct PRs, 1 distinct reviewers (clbr-odoo)
- **PRs:** #1027
- **20.0 citation:** General Odoo module structure convention, unrelated to version.
- Bad:
```
estate/view/estate_property_views.xml
estate/view/__init__.py
```
- Good:
```
estate/views/estate_property_views.xml
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1027#discussion_r2541030261

### 50. Place security data files under `security/`, not `data/`
- **Category:** security  **Criticality:** Minor  **Verdict:** Valid
- **Frequency:** 1 distinct PRs, 1 distinct reviewers (clbr-odoo)
- **PRs:** #1027
- **20.0 citation:** General Odoo module structure convention, unrelated to version.
- Bad:
```
estate/data/ir.access.csv
```
- Good:
```
estate/security/ir.access.csv
```
- **Evidence:** https://github.com/odoo/tutorials/pull/1027#discussion_r2540975179
