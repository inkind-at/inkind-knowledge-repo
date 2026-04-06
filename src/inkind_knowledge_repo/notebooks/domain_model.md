# in-kind Domain Model

## What the knowledge repo is

The `inkind-knowledge-repo` is the declarative knowledge layer of the platform. It is not queried at runtime — it is compiled and loaded into the Django application's in-memory engine at startup. The repo defines the *vocabulary and rules* of the domain; the Django app enforces them.

Two distinct levels live in the repo:

**Schema** (`src/inkind/schema/`) — shapes that are true regardless of which item, actor, or organisation. Category attribute definitions, lifecycle state machines, process step catalogues, UI routing tables.

**Instances** (`instances/`) — concrete values for specific organisations and scenarios. An org's weight vector, its selected process templates, its step cost overrides, and worked example scenarios.

---

## Core entities

**DonationItem** — a single physical item moving through intake and redistribution. Has a `lifecycle_state` (received → sorting\_in\_progress → stored → allocated → rejected) and an `observations` JSON blob that accumulates during sorting.

**DonationCollection** — an arrival batch. Items are registered inside a collection; the collection is the unit of intake, the item is the unit of sorting.

**DemandSignal** — a registered need expressed by a beneficiary or case worker. Carries category, attributes (size, demographic), urgency tier, and lifecycle state (draft → active → fulfilled).

**Campaign** — a time-bounded drive linking demand signals to a deadline. Multiple demand signals can be attached to one campaign.

**StorageLocation** — a physical storage unit. Items are assigned to storage locations at the end of a sort episode.

**Actor** — a user with a role (`volunteer` or `staff`). Role determines which UI fragment mode is served (guided vs. expert).

**Organisation** (`SocialOrganisation`) — the operational unit. Owns items, storage, and configuration. All process configuration is org-scoped.

---

## The optimisation objective

Every design decision in the schema traces back to one equation:

```
net-value(i, b, p) = Σ ω_s(λ) · v_λ(i, b, p) − C_s(p)
```

`i` = item, `b` = beneficiary, `p` = process path, `ω_s` = org's value weights, `v_λ` = scoring function per value dimension, `C_s(p)` = path cost.

**The path `p` is the optimisation variable.** The same item delivered to the same beneficiary via different paths has different net value because paths determine which observations are collected (and therefore which `v_λ` dimensions are scorable) and what the path costs. Phase 1 instruments only `C_s(p)` — the reward side requires the match step (beneficiaries), which is out of scope until later phases.

---

## Process templates

A `ProcessTemplate` is a complete process path — one candidate `p`. It defines an ordered sequence of steps, a completeness tier (what observations it produces), and category affinity hints (which categories it is optimised for).

**Orgs select which templates are active** through the Django admin (`OrgProcessConfig` — one row per process type per org). Only selected templates enter the feasible candidate set. There is no runtime capability check: the admin enabling a template is responsible for ensuring its preconditions are met. Preconditions are annotated on the template as human-readable strings shown in the admin UI.

**Process path types** group templates by technique:
- `manual_assessment` — human only, always usable
- `ml_assisted` — photo → ML inference → review; requires trained model
- `barcode_first` — scan → registry lookup → review; requires scanner
- `rapid_triage` — minimal observations; re-sort eligible

**Category affinity** (`preferred` / `neutral` / `discouraged`) is an expected-value prior. The engine weights feasible paths by affinity when multiple paths are available for an item's category. It does not gate selection — it influences the net-value ranking.

**Completeness tier** determines which `v_λ` scoring functions are available downstream. A `minimal` path (rapid triage) omits condition and category detail; items sorted this way cannot be matched on condition until re-sorted with a complete path.

---

## Step types and fragment bindings

A `StepType` is an atomic operation in the step catalogue. It declares what observations it produces, its default cost in minutes, and its input modality (form, camera, barcode scan, automated, confirmation).

A `UIFragmentBinding` maps a (step\_type, category, actor\_role, process\_path\_type) tuple to a Django template reference, required fields, and optional fields. The engine resolves this 5-dimension key at each step to determine which HTML fragment to serve and which fields to validate on POST. More specific bindings override less specific ones (category-specific takes priority over catch-all; role-specific takes priority over role-null).

The separation means: templates define *what* steps run and *when*; fragment bindings define *how* each step renders. Changing the UI of a step requires only a new fragment binding, not a template change.

---

## Process episodes and provenance

A `ProcessEpisode` is a runtime record of one process being executed on a specific entity. It is created when an actor clicks a launch button. It stores: which template was selected, a JSON snapshot of the step sequence at launch, the org and actor at launch time, and current progress (`current_sequence_number`).

A `ProcessStep` record is created for each completed step within an episode. It carries: which fragment was served, the actor's submitted observations, the step cost at execution time (`cost_configured`), duration in seconds, and an override flag if the actor acknowledged a constraint warning.

These two models make `C_s(p) = Σ ProcessStep.cost_configured` directly computable per episode. They also provide the provenance substrate for the later neural learning phase (provenance-weighted training uses per-step actor, confidence, and duration signals).

---

## Constraint evaluation

Two constraint types gate step completion:

**UC (Universal Constraints)** — domain-wide rules that apply regardless of org. Defined in category schemas. Example: adult used underwear cannot be redistributed regardless of org.

**PC (Policy Constraints)** — org-specific rules. Defined in org instance files. Example: one org requires intact care labels for clothing donations.

Constraints are compiled from the LinkML schema into JSON Schema per category, then served to the browser. `ajv` evaluates them on every field change for inline feedback and again on POST server-side. The same schema file drives both validation and dropdown filtering — value map dependencies (`subcategory → demographic → size`) generate `if/then` JSON Schema blocks that `ajv` uses to filter dropdowns progressively.

---

## How the Django app connects to the repo

At startup the `fragments` app loads the compiled Pydantic package generated from the knowledge repo (`gen-pydantic` output). It builds three in-memory indices:

- **Template index** — `{process_type: [ProcessTemplate]}` filtered by org's `OrgProcessConfig` selections
- **Fragment index** — `{(step_type, category, role, path_type, org_id): UIFragmentBinding}` for O(1) resolution
- **Cost index** — `{(org_id, step_type): float}` from `StepCost` overrides, falling back to `StepType.default_cost`

The `available_processes()` engine method returns the feasible template list for an entity's current lifecycle state and the org's active selections. The `resolve_fragment()` method resolves the five-dimension key to a binding. The `get_constraint_schema()` method merges the shared UC JSON Schema with the org's PC additions into a single schema served to the browser.

All other Django apps (`item_processing`, `collections`, `needs`) depend on `fragments` but `fragments` depends on nothing in those apps. Category-specific business logic lives entirely in the knowledge repo YAML — no code knows the difference between clothing and furniture.
