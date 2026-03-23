# in-kind Platform: Implementation Plan

**Status:** Working draft — brainstorming output  
**Scope:** Pre-seed Phase 1 (intake, sorting, needs), with future architecture direction  
**Date:** March 2026

---

## Table of Contents

1. [Context and Constraints](#1-context-and-constraints)
2. [Architectural Principles](#2-architectural-principles)
3. [Django App Structure](#3-django-app-structure)
4. [Phase 1 Sprint: Intake, Sorting, Needs](#4-phase-1-sprint-intake-sorting-needs)
5. [Knowledge Repository: inkind-knowledge-repo](#5-knowledge-repository-inkind-knowledge-repo)
   - [Ontology reuse and semantic grounding](#ontology-reuse-and-semantic-grounding)
6. [Inference Engine](#6-inference-engine)
7. [Category Schema: Single Source of Truth](#7-category-schema-single-source-of-truth)
8. [Efficiency-First: Cost Instrumentation](#8-efficiency-first-cost-instrumentation)
9. [DonationCollection, DonationSource, and the Dynamic Warehouse](#9-donationcollection-donationsource-and-the-dynamic-warehouse)
10. [Platform Entry Points: Multi-Application Vision](#10-platform-entry-points-multi-application-vision)
11. [Future Architecture Direction](#11-future-architecture-direction)

**Appendices**
- [Appendix A: Key Decisions Summary](#appendix-a-key-decisions-summary)
- [Appendix B: Constraint Types Summary](#appendix-b-constraint-types-summary)

---

## 1. Context and Constraints

### What exists today

The current prototype is a Django/PostgreSQL/HTMX application deployed with one co-creation partner in Lower Austria (4 users, 2+ months operational). The following is already implemented and working:

- User management and enterprise management
- Storage management (units, hierarchy, rules)
- Item processing (intake, sorting, condition assessment — decomposed into steps)
- Collection processing (arrival collections, unsorted bulk intake — now `DonationCollection`)
- Category configuration (separate app)
- Basic provenance capture (actor, device, timestamp per step)

The key learning from deployment: the hardcoded approach is unsustainable. Every workflow adjustment requires a code change. This is the primary problem Phase 1 addresses.

### What is not yet implemented

- Donor engagement
- Disposal management workflows (beyond "mark for disposal")
- Needs management
- Multi-organisation configuration (only one org deployed)

### Governing constraint

The formal specification defines four research hypotheses. The most critical for Phase 1 is **H1 — Schema Expressibility**: the modular architecture represents ≥90% of operational variation across 5+ organisations through configuration, without engine modification. Every architectural decision in this phase should be evaluated against whether it moves H1 closer to being testable.

---

## 2. Architectural Principles

### The CDSS separation

The architecture follows the knowledge base / inference engine separation established by 40 years of Clinical Decision Support Systems research. Domain knowledge is expressed declaratively in a knowledge base (the `inkind-knowledge-repo`). A domain-agnostic inference engine applies it to current runtime state to produce decisions. The engine never encodes domain logic — it only evaluates declared knowledge against observed state.

### Three-layer formalism stack

| Layer | What it covers | Formalism | Lives in |
|---|---|---|---|
| **L1 — Static schema** | Entity structure, state machines, fragment topology, ω_s schema, UC/PC constraints | LinkML (YAML) | `inkind-knowledge-repo` |
| **L2 — Dynamic constraints** | EC cross-entity enforcement, SQ sequencing checks, UC temporal rules | Generated from L1 (SQL for now) | Generated at load time |
| **L3 — Execution and scoring** | Fragment firing, AV runtime checks, C_s(p) cost computation, provenance writes | Python | `inkind-hub` Django engine |

**Invariant:** references flow downward only. L3 reads L1 and evaluates L2. L2 is generated from L1. L1 knows nothing about L2 or L3.

### Schema level vs instance level

**Schema level** — anything true regardless of which item, actor, or moment in time. The vocabulary of valid states, the structure of preconditions, the topology of fragment connections. Lives in `inkind-knowledge-repo/src/schema/`.

**Instance level** — anything true about a specific organisation or scenario. An org's weight vector, step cost table, selected workflow variant, policy constraints. Lives in `inkind-knowledge-repo/instances/`.

**Runtime state** — what is true about a specific item or actor right now. Current lifecycle state of item 47, current role of the logged-in user. Lives in the Django PostgreSQL database, never in the knowledge repo.

### Efficiency-first, values deferred

The four value dimensions (dignity, equity, efficiency, urgency) are defined in the formal spec. For Phase 1, only **efficiency** is instrumented, and only via path cost `C_s(p)` — not via the reward function `v_efficiency(i, b, p)`, which requires the match step (beneficiaries + distribution) to be in place. Setting `ω_s(efficiency) = 1.0` and all other weights to zero is architecturally honest and directly corresponds to how commercial warehouse systems operate. This gives a clear baseline and a testable first milestone for H4.

---

## 3. Django App Structure

### Do not split by item type

Splitting `item_processing` into `clothing`, `food`, `furniture` apps would encode the current category taxonomy into the app structure — exactly the hardcoding problem being solved. Item types differ in **configuration** (category schema, observation fields, constraints), not in **process structure**. The sorting steps for a winter coat and a dining chair are structurally identical.

### The correct split: by process phase and concern

```
inkind-hub/
├── apps/
│   ├── users/                  # User management, roles, enterprise switching
│   ├── enterprises/            # Enterprise registration, hierarchy, geocoding
│   ├── storage/                # Storage units, hierarchy, rules
│   ├── category_config/        # Item categories, observation schemas, UC/PC constraints
│   │                           # (already exists — the right split)
│   ├── collections/            # DonationCollection — arrival collections replacing batch model
│   ├── item_processing/        # Sorting, condition assessment, individual items
│   ├── needs/                  # NEW — DemandSignal + Campaign entities
│   └── fragments/              # NEW — fragment resolution engine + process episodes
```

### The `fragments` app

This is the most architecturally significant new app. It is the Django implementation of the `ui/` module in the knowledge schema and the process episode tracking layer.

**Owns:**
- `FragmentBinding` model — the compiled resolution table loaded from knowledge repo instances
- `StepCost` model — per-org, per-step-type cost scalars (C_s configuration)
- `ProcessDefinition` model — the launchable process types per entity type and state, loaded from knowledge repo configuration
- `ProcessEpisode` model — a runtime record of one active or completed process instance (see section 4)
- `ProcessStep` model — each completed step within an episode, with provenance fields
- The inference engine service — resolves fragments and evaluates constraints within an episode context

**Does not own:**
- Any business logic about what sorting or intake does
- Any category-specific field definitions (those live in `category_config`)
- Any views that render intake or sorting forms (those live in `item_processing` and `collections`)

**Dependency direction:**

```
item_processing  →  fragments  ←  needs  (future: disposal, storage_ops)
collections    →  fragments
donations        →  fragments
                        ↑
                  category_config
```

`fragments` depends on `category_config`. Everything else depends on `fragments`. `fragments` depends on nothing in `item_processing`. This ensures the engine stays domain-agnostic.

### UI fragment binding logic

A `UIFragmentBinding` resolves four dimensions simultaneously:

- A step type (e.g., `sort_item`)
- A category (e.g., `clothing`, `furniture`) — determines the process path
- An actor role (e.g., `volunteer`, `staff`) — determines guided vs expert mode
- An org_id — selects org-specific overrides if any

The resolution: `(step_type, category, actor_role, org_id)` → template reference + required fields + postcondition state.

**Category is the process path selector.** Clothing and furniture have structurally different sorting steps — different observations required, different attribute sets, different constraint rules. The category dimension in the fragment binding is what causes the engine to route to `sort_clothing_guided` rather than `sort_furniture_guided` without any code distinction between item types. Adding a new category (electronics, food) means adding a new binding block in the knowledge repo configuration — no code deployment.

**Role is the mode selector within a path.** For the same category, a volunteer sees guided mode (more fields, more guidance text) and a staff member sees expert mode (minimal fields, fast path). This is a second dimension of the same routing decision.

**Field-level dependencies within a step** — such as demographic driving available sizes within the clothing sort — are not expressed as separate fragment routing decisions. They are expressed in the category schema's `value_map` and evaluated by the constraint schema. The fragment routing handles coarse process-path selection; the category schema handles fine-grained field dependencies within a step.

This means fragment templates are not hardcoded in views. They are resolved from configuration, making it possible to add a new category process path without a code deployment.

---

## 4. Phase 1 Sprint: Intake, Sorting, Needs

### Scope

**In scope:**
- Per-role UI configuration: guided mode (volunteer) vs. expert mode (staff) resolved from fragment bindings, not hardcoded in views
- Config-driven inventory categories: categories and their observation schemas defined in data, not code
- Step cost configuration: per-org, per-step-type cost scalars configurable by org admin
- Minimal demand signals: create standing and campaign signals (category, signal_type, attributes), surface them in the sorting workflow, mark fulfilled
- Provenance enhancement: add `step_duration_seconds` (derived from timestamp deltas) and `step_cost_configured` to existing provenance records
- `fragments` app: initial implementation with in-memory engine backed by compiled knowledge repo config

**Explicitly out of scope:**
- Donor engagement (any of it)
- Disposal workflows beyond existing "mark for disposal"
- Public visibility of demand signals and reporting
- Beneficiary profiles or matching
- The full `v_efficiency` reward function (requires match step)
- LinkML knowledge repo (observe this deployment first — "complexity from practice")

### Process episodes and templates

A **process episode** is a first-class runtime object representing one instance of a process being executed on a specific entity. The existing launch buttons already initiate processes implicitly — the `ProcessEpisode` model formalises what those buttons create, making episodes queryable, auditable, and cost-measurable.

**Process templates vs process definitions — the meta-level distinction:**

There are two levels here that must not be conflated.

The knowledge repo defines **process templates** — complete, named step sequences available to all organisations. `sort_item_manual`, `sort_item_with_ml`, `sort_item_rapid_triage`. Each template is a fully specified sequence of step type references. Templates are Level 2 configuration: loaded at startup, shared across orgs, changed only when the domain model evolves.

Each org **selects** a template per process type through the Django admin. This selection is Level 3 configuration: a single database row per process type per org. No custom step assembly, no process builder UI. The org admin chooses from a dropdown of available templates; the engine uses their selection to materialise the episode's step sequence at launch.

This is the right scope for Phase 1. Template selection gives org admins meaningful operational control — the difference between ML-assisted and manual sorting is a real decision — without requiring any custom tooling beyond a dropdown.

**Process template in the knowledge repo:**

```yaml
process_templates:

  - id: sort_item_manual
    process_type: sort_item
    label: "Manual sorting"
    description: "Full manual assessment — suitable for all item types"
    is_default: true
    entity_type: donation_item
    launchable_from_states: [received]
    steps:
      - step_type: assign_category
        sequence: 1
        is_optional: false
      - step_type: manual_condition_assessment
        sequence: 2
        is_optional: false
      - step_type: assign_storage
        sequence: 3
        is_optional: false

  - id: sort_item_with_ml
    process_type: sort_item
    label: "Sorting with ML assistance"
    description: "Photo-based ML recognition with human review"
    is_default: false
    entity_type: donation_item
    launchable_from_states: [received]
    steps:
      - step_type: assign_category
        sequence: 1
        is_optional: false
      - step_type: take_photo
        sequence: 2
        is_optional: false
      - step_type: ml_recognition
        sequence: 3
        is_optional: false
      - step_type: review_ml_result
        sequence: 4
        is_optional: false
      - step_type: assign_storage
        sequence: 5
        is_optional: false

  - id: sort_item_rapid_triage
    process_type: sort_item
    label: "Rapid triage"
    description: "Minimal steps for high-volume intake sessions"
    is_default: false
    entity_type: donation_item
    launchable_from_states: [received]
    steps:
      - step_type: assign_category
        sequence: 1
        is_optional: false
      - step_type: assign_storage
        sequence: 2
        is_optional: false

  - id: register_demand_signal
    process_type: register_demand_signal
    label: "Register demand signal"
    is_default: true
    entity_type: demand_signal
    launchable_from_states: [expressed]
    steps:
      - step_type: set_category
        sequence: 1
        is_optional: false
      - step_type: set_signal_type
        sequence: 2
        is_optional: false
      - step_type: set_attributes
        sequence: 3
        is_optional: false
```

The `is_default: true` template is used for any org with no explicit selection, so a new org works correctly before configuring anything.

**Django model structure:**

```
OrgProcessConfig                   ← Level 3, one row per process type per org
├── org                            FK → Enterprise
├── process_type                   # sort_item | register_demand_signal
└── template_id                    # slug reference to a ProcessTemplate
```

```
ProcessEpisode                     ← runtime record per episode instance
├── id                             # UUID
├── process_type                   # sort_item | register_demand_signal
├── template_id                    # which template was selected at launch
├── entity_type                    # donation_item | demand_signal | donation_collection | storage_unit
├── entity_id                      # UUID of the specific entity
├── org                            FK → Enterprise
├── actor                          FK → User
├── actor_role                     # role at launch time — provenance
├── state                          # in_progress | completed | abandoned
├── started_at
├── completed_at                   # nullable
├── abandoned_at                   # nullable
├── step_sequence                  # JSON snapshot of template steps at launch
└── current_sequence_number        # which step the episode is currently on
```

```
ProcessStep                        ← one record per completed step
├── id                             # UUID
├── episode                        FK → ProcessEpisode
├── step_type                      # from the template step
├── sequence_number                # position in the episode
├── fragment_id                    # which fragment binding was resolved
├── started_at
├── completed_at
├── duration_seconds               # derived: completed_at - started_at
├── cost_configured                # c_s scalar at time of execution
├── observations                   # JSON — field values submitted by actor
├── override_flag                  # true if actor overrode a constraint warning
└── provenance_method              # mobile | desktop | scan
```

The `step_sequence` JSON snapshot means that if an org changes their template selection while an episode is in progress, the in-progress episode continues with the snapshotted sequence. Only new episodes use the updated selection.

**The launch flow:**

```
Actor clicks launch button on item detail view
    ↓
engine.available_processes(entity_type, lifecycle_state, org_id)
    → templates matching entity_type + launchable_from_states
    ↓
OrgProcessConfig lookup → org has selected sort_item_with_ml
    (or is_default template if no selection exists)
    ↓
POST /api/org/episodes/
    {process_type: sort_item, entity_type: donation_item, entity_id: <uuid>}
    ↓
Episode created:
    template_id: sort_item_with_ml
    step_sequence: JSON snapshot of template steps
    current_sequence_number: 1
    state: in_progress
    ↓
Redirect to /process/{episode_id}/step/
    → engine resolves step 1 fragment given category + role + org
```

**Step completion and progression:**

```
Actor submits step N
    ↓
ProcessStep record created with observations, cost, duration, override_flag
    ↓
Entity lifecycle_state updated only at the terminal step
    (intermediate steps produce observations, not state transitions)
    ↓
episode.current_sequence_number incremented
    ↓
If more steps remain → redirect to /process/{episode_id}/step/
Else → entity transitions to terminal state (e.g., item:stored)
        episode.state = completed
        redirect to entity detail view
```

**Sequencing enforcement:** step N+1 is served only when a `ProcessStep` completion record exists for step N within the episode. Sequencing is enforced via episode progress, not entity lifecycle state — intermediate steps do not each require a named lifecycle state, keeping the entity state machine clean.

**Abandoned episodes:** episodes with `state = in_progress` older than a configurable threshold are detected and marked `abandoned` by a background task or on the next launch attempt for the same entity. The entity's lifecycle_state reverts (`sorting_in_progress → received`), preventing items from getting stuck.

**What episodes enable:**

- `C_s(p) = Σ ProcessStep.cost_configured` — total path cost per episode, directly computable
- Observed vs configured cost: `Σ duration_seconds` vs `Σ cost_configured` across orgs
- Efficiency UI at launch — estimated cost of the selected template shown before the actor begins
- Template comparison — episode cost data directly comparable across orgs using different templates

**URL structure:**

```
/process/{episode_id}/step/     # current step in the episode
/process/{episode_id}/summary/  # episode completion summary
/items/{id}/                    # entity detail — shows launch buttons for valid processes
/needs/                         # application list views — no episode machinery
/storage/{id}/                  # storage unit detail
```

Middleware enforces that any view under `/process/` requires an active `ProcessEpisode` matching the `episode_id`. Application views outside `/process/` never touch the episode machinery.

### State management

Introduce explicit lifecycle state on `DonationItem` as a controlled vocabulary field with transition validation:

```
announced → received → sorting_in_progress → sorted → stored
```

States are enforced by the model (illegal transitions raise validation errors). The fragment engine reads `item.lifecycle_state` to determine which fragment is valid. This replaces implicit UI-flow sequencing with explicit data-level sequencing — which is the prerequisite for multi-org configuration.

**No state machine library needed at this stage.** A `status` field with transition validation in the model layer is sufficient. The state machine formalism belongs in the knowledge repo schema; Django enforces transitions through model validation.

### Demand signals: the unified need model

The `needs` app owns the demand side of the platform — what organisations want, expressed in a form that the sorting workflow can consult and the donor portal can surface.

**The core insight** is that organisations express demand in two structurally different ways that serve the same purpose: indicating what items are of interest. A standing interest in a category ("we always want children's outerwear size 8-14") and a time-bounded campaign ("30 backpacks by September 1st for back to school") both answer the same question the sorter asks: "is there demand for this item?" The structural difference is an internal concern; from the sorter's and donor's perspective they are the same signal.

This produces a single `DemandSignal` entity with a `signal_type` discriminator rather than two separate models.

**`DemandSignal` model:**

```
DemandSignal
├── id                     # UUID
├── org                    FK → Enterprise
├── signal_type            # standing | campaign | specific
├── category               # clothing | food | furniture | ...
├── attributes             # JSON — {subcategory, demographic, size, ...}
│                          #   matches the category schema's attribute vocabulary
├── quantity_requested     # nullable int — null means "any amount welcome"
├── quantity_fulfilled     # int, derived from matched items
├── campaign               # nullable FK → Campaign
├── holder                 # nullable FK → Beneficiary | SocialOrganisation
├── context_note           # "Back to school for 30 primary school children"
├── deadline               # nullable date
├── urgency_tier           # nullable: low | medium | high | critical
│                          #   only set for campaign and specific types
├── lifecycle_state        # active → partially_fulfilled → fulfilled | expired | withdrawn
├── registered_at
└── public_visibility      # bool — whether to show on donor portal / public API
```

**`signal_type` values:**

`standing` — a permanent interest in a category. No deadline, no quantity target, no urgency. Automatically stays active until explicitly withdrawn. Displayed with lower visual weight in the sorting UI and the donor portal. The organisation declares a standing want, not a specific request.

`campaign` — a bounded coordinated effort tied to a `Campaign`. Has a deadline (inherited from the campaign), a quantity target, and urgency that increases as the deadline approaches and the fulfilment rate falls behind. "30 backpacks by September 1st." Displayed prominently while active.

`specific` — a concrete request for a specific category for a specific holder, independent of any campaign. A social worker registers that a family needs a single item. Has a deadline or urgency tier.

**`Campaign` model:**

```
Campaign
├── id                       # UUID
├── org                      FK → Enterprise
├── title                    # "Back to School 2026"
├── description
├── starts_at
├── ends_at                  # deadline propagates to child DemandSignals
├── target_beneficiary_group # "Primary school children starting September"
├── lifecycle_state          # planned → active → completed | cancelled
└── signals[]                → DemandSignal[] where signal_type = campaign
```

A campaign is a display and coordination wrapper — it groups related `DemandSignal` instances under a shared narrative and timeline. Campaign progress is derived: total `quantity_requested` and `quantity_fulfilled` across its signals. When a campaign's `ends_at` passes, its child signals transition to `expired` if not yet fulfilled.

**Lifecycle states for `DemandSignal`:**

```
active → partially_fulfilled → fulfilled
active → expired        (deadline passed, not fully fulfilled)
active → withdrawn      (org explicitly cancels)
```

`standing` type signals do not follow the expiry path — they stay `active` until explicitly withdrawn.

**How the sorting workflow uses demand signals:**

When an item is being sorted and a category is assigned, the engine queries active `DemandSignal` records for that org and category. The results are sorted by urgency tier (critical → high → medium → low → null) then by deadline proximity. The sorting UI renders:

- **Campaign signals** — a highlighted banner with title, deadline, and fulfilment progress ("Back to School: 18 of 30 collected, deadline September 1st")
- **Standing signals** — a softer indicator ("this organisation has a standing interest in children's outerwear")
- **No active signals** — no indicator; item is routed to general stock

Both signal types influence the same cost-aware path decision: active demand justifies the longer sorting path (collecting more observations) because matching probability is higher. The engine queries `DemandSignal.objects.filter(org=org, category=category, lifecycle_state='active').exists()` — one query, both types.

**Semantic grounding:**

`DemandSignal` grounds in OSSN (`ossn:Goal` — a goal state of the organisation as agent), Open Eligibility tags (need category vocabulary), and `schema:Demand`. `Campaign` grounds in `schema:Event` with `schema:startDate` / `schema:endDate`.

### Success criterion for Phase 1

The falsifiable test for H1 at this stage: **onboard Organisation 2 without a code deployment.** If a materially different organisation (e.g., a food bank instead of a clothing redistribution org) can be configured purely through the admin interface — different category schemas, different step costs, different workflow mode — using the fragment resolution engine loaded from the knowledge repo, H1 has preliminary empirical support.

---

## 5. Knowledge Repository: inkind-knowledge-repo

### Purpose and scope for Phase 1

The knowledge repo is the source of truth for what configuration *should be*. It is not queried at request time. It is compiled and loaded into the Django engine at deployment or admin reload. The repo simultaneously serves as: technical specification, business case documentation (via scenario instances), and funder communication artifact.

### Minimum viable schema for Phase 1

The minimum schema needed to support the sprint without over-engineering:

```
inkind-knowledge-repo/
├── src/inkind/schema/
│   ├── entities/
│   │   ├── donation_item.yaml       # category, condition, lifecycle_state
│   │   ├── donation_collection.yaml # collection_type, parent, lifecycle_state
│   │   ├── storage_location.yaml    # unit, capacity, occupancy
│   │   ├── actor.yaml               # role, experience_level
│   │   ├── organisation.yaml        # config, hierarchy
│   │   ├── donation_source.yaml     # source_type, anonymous_donor_id, lifecycle_state
│   │   ├── demand_signal.yaml       # signal_type, category, attributes, lifecycle_state
│   │   └── campaign.yaml            # title, dates, beneficiary_group, signals[]
│   ├── states/
│   │   ├── item_lifecycle.yaml      # announced → received → sorting_in_progress → sorted → stored
│   │   ├── collection_lifecycle.yaml # open → processing → closed → archived
│   │   └── demand_signal_lifecycle.yaml  # active → partially_fulfilled → fulfilled | expired | withdrawn
│   ├── process/
│   │   ├── step_type.yaml           # catalogue of available step types
│   │   └── process_template.yaml    # named step sequences orgs select from
│   ├── value/
│   │   └── step_cost.yaml           # c_s(step_type) schema — per-org cost configuration
│   ├── ui/
│   │   └── fragment_binding.yaml    # (step_type, category, actor_role) → template_ref + fields
│   ├── categories/                  # category schemas — single source of truth per item type
│   │   ├── clothing.yaml            # attributes, value_map, UC/PC constraints, process_path ref
│   │   ├── furniture.yaml           # attributes, value_map, UC/PC constraints, process_path ref
│   │   └── _base.yaml               # shared attribute types (condition, storage_unit)
│   └── provenance.yaml              # π(s_k) structure
│
├── instances/
│   ├── orgs/
│   │   └── org_a.yaml               # step costs, workflow selection, org-level PC overrides
│   ├── workflows/
│   │   └── standard_intake.yaml     # fragment sequence, step costs
│   └── scenarios/
│       └── winter_coat.yaml         # §3.3 formal spec worked example as data instance
│
└── generated/
    ├── pydantic/                    # gen-pydantic output → installed in inkind-hub
    └── json-schema/                 # gen-json-schema output per category → served to browser
        ├── clothing.json
        └── furniture.json
```

### The category schema structure

Each file in `src/inkind/schema/categories/` is the single source of truth for everything that varies by item type: the attribute set, the `value_map` for dependent fields, the UC/PC constraint rules, and the process path reference. This structure means adding a new item type requires only a new YAML file — no code change anywhere.

A category schema has three distinct sections:

**`attributes`** — the field set for this category with their types, valid values, and display properties. Includes `show_if` conditions for conditionally visible fields.

**`value_map`** — the dependent dropdown logic. Declares which field's valid values depend on another field's current value. The constraint compiler reads this to generate `if/then` blocks in JSON Schema. The frontend reads the same data for live dropdown filtering.

**`constraints`** — the explicit UC and PC rules that go beyond what `value_map` can express. Each rule has a `trigger` (field conditions that activate it), an `action` (block or warn), a user-facing `message`, and an optional `suggest` action (e.g., disposal).

The clothing category schema as a concrete example:

```yaml
id: clothing
label: Clothing
process_path: sort_clothing     # links to fragment_binding.yaml routing

attributes:
  subcategory:
    values: [tops, bottoms, outerwear, underwear, footwear, accessories]
  demographic:
    depends_on: subcategory
    value_map:
      tops:      [baby, child, adult_male, adult_female, unisex]
      underwear: [baby, child, adult_male, adult_female]
      footwear:  [baby, child, adult_male, adult_female, unisex]
  size:
    depends_on: demographic
    value_map:
      baby:         [0-3m, 3-6m, 6-12m, 12-18m, 18-24m]
      child:        [2T, 3T, 4T, 5, 6, 7, 8, 10, 12, 14]
      adult_male:   [XS, S, M, L, XL, XXL]
      adult_female: [XS, S, M, L, XL, XXL]
      unisex:       [XS, S, M, L, XL, XXL]
  condition:
    values: [new, good, fair, poor]
  intact_labels:
    type: boolean
    show_if: {subcategory: [tops, bottoms, outerwear]}

constraints:
  - id: uc-underwear-condition
    type: UC
    trigger: {subcategory: underwear, condition: [fair, poor]}
    action: block
    message: "Underwear must be in new or good condition"
    suggest: disposal
  - id: uc-underwear-adult-used
    type: UC
    trigger: {subcategory: underwear, demographic: [adult_male, adult_female],
              condition: [good, fair, poor]}
    action: block
    message: "Used adult underwear cannot be redistributed"
    suggest: disposal
```

The furniture category schema follows the same structure but with completely different fields, `value_map`, and constraints — demonstrating that the schema format generalises across categorically different item types without any code change.

### Schema level vs instance level in the repo

**Schema level** (in `src/inkind/schema/`) defines the *shape* of valid configuration. The `fragment_binding.yaml` schema declares that a `UIFragmentBinding` has a `precondition_state`, `actor_role`, `template_ref`, `data_fields[]`, and `emits_event`. It does not say what those values are for any specific organisation.

**Category level** (in `src/inkind/schema/categories/`) defines item-type-specific configuration: attribute sets, value maps, and UC rules. This is shared across all organisations — the underwear rule applies everywhere. It changes only when the domain model changes, not when an org changes its settings.

**Instance level** (in `instances/`) gives org-specific values. `org_a.yaml` declares org A's step costs, workflow mode selection, and any PC overrides on top of the shared category constraints. The `scenarios/` directory is the funder communication artifact — self-contained YAML instances that walk through the formal spec's worked examples as real data. `winter_coat.yaml` shows two candidate paths, their step costs, and the net-value comparison. This replaces a Figma presentation and a written business case simultaneously.

### Loading mechanism

At Django application startup (or on admin config reload):

1. The knowledge repo is installed as a Python package via git dependency
2. The `fragments` app `ready()` hook runs the configuration loader
3. The loader reads compiled Pydantic models from the knowledge repo package
4. It builds an in-memory engine index keyed by `(step_type, category, actor_role, org_id)` mapping to resolved fragment definitions
5. Step cost tables are loaded per org into a separate index
6. The `category_config` app loader reads all `src/inkind/schema/categories/*.yaml` files, compiles each to JSON Schema via `gen-json-schema`, and stores the compiled schemas in a `CategoryConstraintSchema` database record keyed by category slug
7. The in-memory constraint index is populated from these database records

The JSON Schema compilation (step 6) runs at reload time, not at request time. When a category YAML changes (new constraint added, `value_map` updated), the admin triggers a reload. The compiler regenerates only the affected category's JSON Schema, updates the database record, and invalidates the in-memory cache for that category. No server restart required.

At request time: zero SQL queries for configuration. The engine reads from the in-memory index only. The only SQL is for runtime state (item's current `lifecycle_state`), which the view already loads anyway. The JSON Schema for the item's category is embedded in the page at render time and served to the browser.

### Validation in CI

`linkml-validate` runs in the knowledge repo's CI pipeline on every commit — validating both schema files and all instance YAML. This is where LinkML's validation tooling belongs: in CI and at load time, not at request time. Invalid configuration is caught before it reaches Django.

### Ontology reuse and semantic grounding

LinkML supports referencing external ontology IRIs on slots and classes via `uri` declarations and `see_also` annotations. This does not import OWL axioms into the schema — it creates semantic grounding that makes the schema interpretable by tools that understand those vocabularies, enables SPARQL federation, and supports the future triplestore backend. The reuse strategy is to reference established IRIs rather than reinvent vocabulary for concepts that already have stable, well-understood definitions.

**Foundational vocabularies — apply across all entity types:**

`schema.org` (`https://schema.org/`) is the primary reuse target for item and product vocabulary. `schema:Product` grounds `DonationItem`. `schema:OfferItemCondition` with its pre-defined values — `schema:NewCondition`, `schema:UsedCondition`, `schema:DamagedCondition`, `schema:RefurbishedCondition` — maps directly onto the condition attribute used in every category schema, avoiding a custom condition vocabulary. `schema:SizeSpecification` and the wearable size group hierarchy cover clothing size/demographic dependencies.

`W3C PROV-O` (`http://www.w3.org/ns/prov#`) grounds the provenance module. `prov:Activity` corresponds to `ProcessStep`, `prov:Entity` to `DonationItem` in a given lifecycle state, `prov:Agent` to `Actor`. The provenance record π(s_k) is a qualified `prov:wasGeneratedBy` association. Using PROV-O IRIs makes the audit trail automatically interoperable with any PROV-aware tool and positions the schema correctly for the federation layer.

`W3C ORG` (`http://www.w3.org/ns/org#`) grounds the organisation entity. `org:Organization` is the base for `SocialOrganisation`, `org:subOrganizationOf` covers the enterprise hierarchy (limit depth 4), `org:hasMember` covers user-enterprise association, `org:Role` covers actor roles within an organisation. ORG builds on PROV-O, so the two compose naturally.

`P-Plan` (`http://purl.org/net/p-plan#`) grounds the process template / execution split. `p-plan:Plan` corresponds to `ProcessTemplate` — an abstract specification of what should happen. `p-plan:Activity` corresponds to `ProcessStep` — a concrete execution of one step in an episode. This is the precise distinction the architecture relies on and P-Plan was designed to express it.

`FOAF` (`http://xmlns.com/foaf/0.1/`) grounds `Actor` as `foaf:Person` and provides `foaf:Organization` as an alternative anchor for `SocialOrganisation`.

**Category-specific vocabularies:**

`CPI — Clothing Product Information Ontology` (`http://www.ebusiness-unibw.org/ontologies/cpi/ns#`) is the most directly reusable vocabulary for the clothing category schema. It extends schema.org and provides: `cpi:ClothingAndAccessories` as the base class for clothing items, `cpi:ClothingSize` for size values, `cpi:designatedFor` for demographic targeting, `cpi:Certification` for quality certifications (intact labels), and `cpi:careInstruction` for washing/care attributes. CC-BY 4.0 licensed. The clothing category schema's attributes should reference CPI IRIs as `see_also` annotations on their slots.

`schema.org wearable vocabulary` — `schema:WearableSizeGroupBaby`, `schema:WearableSizeGroupChildrens`, `schema:WearableSizeGroupAdult`, `schema:WearableSizeSystemEU` — grounds the demographic/size hierarchy in the clothing `value_map` with stable, widely understood IRIs.

`FoodOn` (`http://purl.obolibrary.org/obo/foodon.owl`) is the authoritative open food ontology from OBO Foundry, covering food product types from farm to fork with ~9,000 classes. For the food category schema, FoodOn provides vocabulary for food category taxonomy and the concepts needed for UC constraint rules (expiry, handling conditions, food safety). Selective term import via OntoFox keeps the dependency lightweight — only the relevant branch of the food product hierarchy is imported, not the full ontology.

For furniture and household items, no single authoritative ontology equivalent to CPI or FoodOn exists. `schema:Product` combined with `schema:SizeSpecification` (for dimensions) and GoodRelations' `gr:qualitativeProductOrServiceProperty` pattern covers the structural attributes. The Product Types Ontology (`http://www.productontology.org/`) generates OWL class definitions from Wikipedia for specific furniture types (`pto:Chair`, `pto:Table`, `pto:Bed`) providing IRI-stable category references.

**How reuse appears in the LinkML schema:**

In practice, ontology reuse in `inkind-knowledge-repo` takes two forms. First, slot `uri` declarations map schema slots to external property IRIs — the `condition` slot on `DonationItem` declares `uri: schema:itemCondition`. Second, `see_also` annotations on classes and slots point to the external IRI for documentation and triplestore grounding — the `ClothingItem` class declares `see_also: cpi:ClothingAndAccessories`. Neither form requires importing OWL axioms or running a reasoner at build time. The semantic grounding is lightweight metadata that pays dividends when the triplestore backend is introduced and SPARQL queries can traverse across vocabularies.

**Ontology reuse summary table:**

| Ontology | Namespace | Grounds | License |
|---|---|---|---|
| schema.org | `schema:` | `DonationItem`, condition values, clothing size/demographic, product attributes | CC-BY-SA 4.0 |
| W3C PROV-O | `prov:` | Provenance module — steps, agents, qualified associations | W3C Document License |
| W3C ORG | `org:` | Organisation entity, hierarchy, membership, roles | W3C Document License |
| P-Plan | `p-plan:` | Process templates (plans) and step executions | CC-BY 4.0 |
| FOAF | `foaf:` | Actor as person, organisation as agent | CC0 / open |
| CPI (Clothing Product Information) | `cpi:` | Clothing attributes — size, demographic, certification, care | CC-BY 4.0 |
| FoodOn | `foodon:` | Food category taxonomy, expiry/handling constraint vocabulary | CC0 |
| Product Types Ontology | `pto:` | Furniture and household item type taxonomy | CC-BY-SA 3.0 |
| GoodRelations | `gr:` | Product qualitative properties, condition values (subsumed by schema.org) | CC-BY 3.0 |

---

## 6. Inference Engine

### Location

The inference engine is a service within the `fragments` app. It is not a separate process, not a library, not a microservice. It is a Python class instantiated once at startup and accessed through the `fragments` app config.

### Interface

The engine exposes three primary methods:

```
engine.resolve(step_type, category, actor_role, org_id, lifecycle_state)
    → ResolvedFragment(template_ref, required_fields, postcondition_state,
                       step_cost, emits_event)

engine.get_constraint_schema(category, org_id)
    → JSON Schema (merged UC + org PC rules for this category)

engine.available_processes(entity_type, lifecycle_state, org_id)
    → list[ProcessDefinition]  (which launch buttons to render)
```

All other apps call these interfaces. No other app queries `FragmentBinding`, `StepCost`, `ProcessDefinition`, or `CategoryConstraintSchema` models directly. This discipline keeps the engine domain-agnostic and the rest of the system decoupled from configuration details.

The `available_processes` method is what entity detail views call to decide which launch buttons to render. It returns the process definitions whose `launchable_from_states` includes the entity's current `lifecycle_state`. The template renders one button per returned definition using the definition's `label`. No process names are hardcoded in templates.

### What the engine evaluates

For Phase 1, the engine evaluates four things:

1. **Precondition check** — is the item in a state that permits this fragment? (SQ constraint via state machine)
2. **Fragment resolution** — given step type + category + role + org, which fragment binding applies? (in-memory index lookup across four dimensions)
3. **Cost lookup** — what is `c_s` for this step type under this org's configuration? (in-memory cost table)
4. **Constraint schema retrieval** — return the compiled JSON Schema for this category + org, merged from shared UC rules and org-specific PC overrides

The `get_constraint_schema` method merges two sources: the shared UC constraint schema compiled from `src/inkind/schema/categories/clothing.yaml` (same for all orgs) and any PC constraint additions from `instances/orgs/org_a.yaml` (org-specific). The merged schema is what the browser receives and what server-side POST validation evaluates against.

### JSON Schema as dual-purpose constraint and filter driver

The constraint schema serves two simultaneous roles in the browser:

**Validation** — `ajv` evaluates the full schema against the current form state on every relevant field change. When a violation is detected (underwear + poor condition), `ajv` fires immediately with the configured error message. No server round-trip needed for inline feedback.

**Dropdown filtering** — `ajv` can compute, for any given partial form state, which values for a dependent field would satisfy the schema. When the user selects demographic = baby, the frontend asks `ajv` which size values are valid given that selection. The answer comes from the `value_map`-derived `if/then` blocks in the schema. The size dropdown is filtered to those values. This means the `value_map` drives both validation and filtering from a single compiled schema — one source, two uses, no duplication.

### Actor availability note

When AV constraints are eventually added, they are the one legitimate source of additional SQL in the engine: one query for actor state, bounded and predictable. All other configuration evaluation remains SQL-free.

---

## 7. Category Schema: Single Source of Truth

### The three-level variation structure

Item processing varies at two levels that require different mechanisms:

**Process-level variation** — clothing and furniture require different sequences of steps, different observations, different constraint types. This is handled by fragment routing: the `process_path` field in the category schema links the category to a specific fragment binding block. Selecting tag `clothing` activates the clothing sort path; selecting `furniture` activates the furniture sort path. Adding a new category means adding a new YAML file and a new fragment binding block — no code change.

**Field-level variation within a step** — within the clothing sort step, demographic selection drives which sizes are available. Within the furniture sort step, furniture type drives which materials are relevant. This is handled by the `value_map` in the category schema, compiled into JSON Schema `if/then` blocks, evaluated in the browser by `ajv`.

These two levels are kept strictly separate. Fragment routing never encodes field-level dependencies. The `value_map` never encodes process-path decisions. Each mechanism does exactly one thing.

### The category schema as single source of truth

Each category YAML file in `inkind-knowledge-repo/src/inkind/schema/categories/` is the authoritative definition of everything that varies for that item type. It is the single place where:

- The attribute set is declared (what fields exist for this category)
- The `value_map` is declared (which field values depend on other field values)
- The UC constraints are declared (which value combinations are universally blocked)
- The process path is referenced (which fragment routing block handles this category)

This means a domain expert can understand the complete operational logic for clothing or furniture by reading one YAML file. They do not need to look at Django models, fragment binding tables, or constraint databases. The YAML is the specification.

### The hot-reload flow

```
Admin edits src/inkind/schema/categories/clothing.yaml in knowledge repo
    ↓ commit + push
Admin navigates to "Reload Configuration" in Django admin
    (or webhook fires automatically from repo push)
    ↓
Django fetches updated YAML from knowledge repo
    ↓
constraint_compiler.compile(clothing.yaml)
    → generates clothing.json (JSON Schema)
    → stores in CategoryConstraintSchema db record
    ↓
in-memory constraint index invalidated and refreshed
in-memory fragment routing index refreshed
    ↓
Next item creation request:
  - receives updated JSON Schema embedded in page
  - ajv evaluates new constraints and value_map immediately
  - fragment routing uses updated process_path reference
```

No server restart. No code deployment. The change takes effect on the next page load after the reload is triggered.

### What requires redeployment vs what does not

**Hot-reloadable (no deployment):**
- Adding or removing a constraint rule
- Changing constraint trigger conditions or messages
- Adding or removing values from a `value_map` entry
- Changing which sizes are valid for a demographic
- Adding a new attribute to an existing category
- Changing `show_if` conditions for conditional fields
- Changing step costs per org
- Changing which fragment mode an org uses (guided vs expert)

**Requires code deployment:**
- Adding a new category that needs a genuinely new template (the template file must be deployed)
- Adding a new widget type not currently supported by existing templates
- Adding a new field type that requires custom rendering logic

The boundary is: configuration data is hot-reloadable; template files and rendering code require deployment. In practice, template changes are infrequent — templates are designed to be generic across categories, rendering whatever fields the category schema declares. The common operational changes (adjusting constraints, adding sizes, changing routing) are all in the hot-reloadable category.

### Fragment routing configuration

The fragment binding YAML declares process-path routing by category and role:

```yaml
fragment_bindings:
  - step_type: sort_item
    category: clothing
    actor_role: volunteer
    precondition_state: item:received
    fragment_id: sort_clothing_guided
    template_ref: fragments/sort_clothing.html
    postcondition_state: item:sorted

  - step_type: sort_item
    category: clothing
    actor_role: staff
    precondition_state: item:received
    fragment_id: sort_clothing_expert
    template_ref: fragments/sort_clothing_expert.html
    postcondition_state: item:sorted

  - step_type: sort_item
    category: furniture
    actor_role: volunteer
    precondition_state: item:received
    fragment_id: sort_furniture_guided
    template_ref: fragments/sort_furniture.html
    postcondition_state: item:sorted
```

This is hot-reloadable routing configuration. The engine resolves `(sort_item, clothing, volunteer, org_a)` → `sort_clothing_guided` fragment. The template `fragments/sort_clothing.html` renders the fields declared in the clothing category schema. No code knows about the difference between clothing and furniture — only the configuration does.

### Constraint schema as dual-purpose driver

The compiled JSON Schema per category serves two simultaneous purposes in the browser, driven by `ajv`:

**Validation guard** — fires on field change, blocks invalid combinations (underwear + poor condition), shows the configured user-facing message. Fires again on POST as the server-side integrity check using Python's `jsonschema` library against the same schema.

**Dropdown filtering** — given the current form state, `ajv` computes which values for the next field satisfy the schema. Demographic = baby → only baby sizes satisfy the size constraint → size dropdown filtered to baby sizes. One schema, two uses, zero duplication of constraint logic between the filtering layer and the validation layer.

---

## 8. Efficiency-First: Cost Instrumentation

### The two faces of efficiency

The formal spec's `v_efficiency(i, b, p)` reward function requires the match step — it cannot be computed without beneficiaries. But `C_s(p)` — total path cost — is computable from the supply side alone. Phase 1 focuses entirely on cost instrumentation, deferring the reward function until disposal and distribution are implemented.

### Step cost as configurable data

Each organisation admin configures a cost scalar per step type through the admin interface. This scalar represents the organisation's estimate of operational burden for that step (can be time in minutes, staff-minutes, or a normalised index — the unit is organisation-sovereign). The schema declares `StepCost(step_type, org, cost_scalar)`. The engine reads it. The optimisation evaluates it.

This is the first live implementation of `c_s(s_k, a_k)` becoming real data rather than a formula symbol.

### Path cost accumulation

As a user works through the sorting steps for an item, the engine accumulates `C_s(p)` by summing `c_s` for each completed step. The provenance record for each step captures `step_duration_seconds` (derived from timestamp delta) alongside the configured cost scalar. This gives two cost signals: the configured cost (what the org said the step should cost) and the observed duration (what it actually took). Comparing these across deployments is the first empirical test of whether `c_s` configuration captures real operational variation.

### Path alternatives as the efficiency UI

Once cost data is accumulating, the engine can present path alternatives at the start of a sorting session: "Standard path (5 steps, estimated 8 min/item) vs. rapid triage (3 steps, estimated 3 min/item)." The cost difference is computed from the org's configured step costs. The user chooses. The provenance records which path was chosen.

This is the feature that makes efficiency tangible to the co-creation partner — it looks like workflow optimisation, which is commercially understandable, but architecturally it is the first live demonstration of path-as-optimisation-unit.

### Demand signals as cost signal

When an active `DemandSignal` exists for the category of an item being sorted, the longer path (collecting more observation fields) has lower effective cost-per-outcome because the probability of successful matching is higher. Campaign signals with tight deadlines and low fulfilment rates provide the strongest justification for the longer path. Standing signals provide a softer justification. The engine does not compute this formally in Phase 1 — but the data exists to retrospectively validate this hypothesis once signals and items are linked. This is the provenance substrate for later H4 validation.

---

## 9. DonationCollection, DonationSource, and the Dynamic Warehouse

### DonationCollection: from batch to recursive collection model

The current prototype uses a flat `DonationBatch` (renamed `DonationCollection`) as a simple grouping for items that arrived together. This works for Phase 1 but encodes a fundamentally limited warehouse model: items arrive in a group, get sorted individually, and go to fixed storage locations. Real warehouse operations are more fluid.

A more expressive model treats a `DonationCollection` as a general-purpose grouping of items that can be created at any stage of processing, derived from other collections, and used to represent any meaningful cluster — an arrival, an intermediate sort pass, a named stock, or a campaign fulfilment set. This recursive structure is the data model foundation for a **dynamic warehouse**: one where inventory is organised by operational purpose rather than fixed physical location.

**The model is introduced now in full.** Phase 1 uses only the `arrival` collection type — a direct replacement for `DonationBatch` with identical semantics. The recursive structure, the additional `collection_type` values, and the dynamic warehouse behaviour are explicitly deferred to later phases. Declaring the full data model from the start means the migration path is an extension (adding collection types and process templates), not a rewrite (changing the model structure).

### The DonationCollection data model

```
DonationCollection
├── id                      # UUID
├── org                     FK → Enterprise
├── collection_type         # arrival | working | sorted | stock | campaign | disposed
├── label                   # Human-readable: "Winter clothing — Nov 2026 arrival"
├── parent                  # nullable FK → DonationCollection
│                           #   null for arrival collections (root)
│                           #   set for all derived collections
├── donation_source         # nullable FK → DonationSource
│                           #   set on arrival collections; inherited by children
├── lifecycle_state         # open | processing | closed | archived
├── item_count              # int — items directly registered to this collection
├── total_item_count        # int — derived: items in this + all descendant collections
├── created_at
├── created_by              FK → Actor
└── notes
```

**`collection_type` values and phase:**

| Type | Phase | Description |
|---|---|---|
| `arrival` | Phase 1 | Root collection created when a donation arrives. Replaces `DonationBatch`. Has a `DonationSource`. No parent. |
| `working` | Phase 2 | Temporary intermediate collection during a multi-stage sort pass. Example: "Condition: acceptable — awaiting category sort." |
| `sorted` | Phase 2 | Completed sort stage — stable grouping ready for next stage or individual item registration. |
| `stock` | Phase 2 | Named standing collection of items ready for distribution. Maps to `DemandSignal` of type `standing`. The dynamic warehouse inventory unit. |
| `campaign` | Phase 2 | Collection assembled for a specific campaign. Drawn from `stock` collections. Maps to a `Campaign` entity. |
| `disposed` | Phase 2 | Items culled during sorting. A collection, not individual records — keeps disposal auditable and batchable. |

### Collection hierarchy examples

**Multi-stage sort of a large clothing arrival:**

```
DonationCollection [arrival] "40 bags — Nov 2026"
    ├── DonationCollection [working] "Condition: acceptable"
    │       ├── DonationCollection [sorted] "Children's clothing"
    │       │       ├── DonationItem  ← individually registered
    │       │       └── DonationItem
    │       └── DonationCollection [sorted] "Adult clothing"
    │               └── DonationItem
    └── DonationCollection [disposed] "Damaged / hygiene"
            # items counted but not individually registered
```

**Stock collection built from multiple arrivals:**

```
DonationCollection [stock] "Children's winter clothing — ready"
    ├── DonationItem  (from November arrival)
    ├── DonationItem  (from October arrival)
    └── DonationItem  (from September arrival)
```

**Campaign collection pulling from stock:**

```
DonationCollection [campaign] "Back to School 2026"
    ├── DonationItem  (school bag — pulled from stock)
    ├── DonationItem  (school bag — pulled from stock)
    └── DonationItem  (pencil case — pulled from stock)
```

### The dynamic warehouse concept

A static warehouse assigns items to fixed physical locations — Bin A3, Shelf 2, Rack 4. This requires upfront storage configuration, produces friction when locations change, and makes it difficult to see inventory by operational purpose rather than physical position.

A **dynamic warehouse** organises items by operational collections rather than fixed locations. Physical location is a secondary attribute on the item or collection, not the primary organisational principle. The warehouse's structure emerges from the organisation's operational practice rather than being configured upfront.

Under this model:

**Inventory queries become collection queries.** "How many children's winter coats are ready?" queries the `stock` collection for that category, not a set of fixed bin locations. The answer is correct regardless of where items physically sit.

**Campaign fulfilment is a collection operation.** Fulfilling a campaign means assembling a `campaign` collection from `stock` collections and marking items as distributed. No bin location changes required — collection membership changes.

**`DemandSignal` maps to collections, not items.** A standing `DemandSignal` for children's clothing maps to the corresponding `stock` collection. The gap (demanded − available) is `DemandSignal.quantity_requested − stock.total_item_count`. When a new item is sorted into the stock collection, the gap closes by one automatically.

**Storage location remains available but optional.** The `storage_unit` field on `DonationItem` can still record physical location when known. But it is informational — the system does not require it to function. This resolves the storage setup friction identified in §11.6: organisations can begin processing items before their physical storage layout is formalised.

**The process template system is already designed for this.** Adding multi-stage sorting means adding new process templates (`sort_by_condition`, `sort_by_category`) with new step types (`create_sub_collection`, `move_to_collection`). The fragment routing and episode infrastructure requires no modification — only new configuration in the knowledge repo.

### Phase 1 scope: arrival collections only

Phase 1 uses `DonationCollection` with `collection_type = arrival` only — a direct replacement for `DonationBatch` with identical runtime behaviour:

- One collection per donation event
- No parent collection
- Items individually registered directly from the arrival collection
- `lifecycle_state`: `open → processing → closed`
- `donation_source` FK set on arrival, inherited by child items

**Explicitly deferred to Phase 2+:**
- `working`, `sorted`, `stock`, `campaign`, `disposed` collection types
- Multi-stage sort processes creating derived collections
- `stock` collection ↔ `DemandSignal` mapping
- Campaign collection assembly and fulfilment
- Dynamic warehouse inventory queries replacing bin-based queries

### DonationSource as a first-class entity

`DonationSource` records who or what originated a donation, separately from the items themselves. It is set on the `arrival` collection and propagates to child collections and items — all items from the same arrival trace back to the same source without duplicating identity data.

```
DonationCollection [arrival] ──FK──→ DonationSource (nullable)
    └── DonationItem ── inherits ──→ DonationSource (from parent collection)
```

```
DonationSource
├── id                        # UUID
├── source_type               # enum: anonymous_private | corporate | organisation
├── anonymous_donor_id        # nullable — opaque token from Donor Portal QR code
├── corporate_donor_ref       # nullable FK → CorporateDonor (Year 2)
├── organisation_ref          # nullable FK → Enterprise (for Share workflow)
├── lifecycle_state           # announced → received → acknowledged
├── created_at
└── provenance                # who recorded this source, on what device
```

**Lifecycle:**
```
announced → received → acknowledged
```

`acknowledged` — reached when linked items complete their lifecycle and impact notification is sent. Stub in Phase 1.

**Phase 1 scope:** `source_type: anonymous_private` only. `lifecycle_state: announced | received` only. No `CorporateDonor`, no `organisation_ref`. Introduced now to establish the privacy boundary before intake data accumulates — retrofitting later would require a migration touching every item and collection record.

### Updated app structure

```
inkind-hub/
├── apps/
│   ├── users/
│   ├── enterprises/
│   ├── storage/               # physical location — optional, informational in dynamic warehouse
│   ├── category_config/
│   ├── collections/           # DonationCollection (all types) + DonationSource
│   │                          # Phase 1: arrival type only
│   ├── item_processing/       # DonationItem — registered from collections
│   ├── needs/                 # DemandSignal + Campaign
│   ├── fragments/             # inference engine + process episodes
│   ├── disposal/              # future — disposal workflows
│   └── donors/                # future Year 2 — CorporateDonor, CSRD, Donor Portal API
```

`DonationSource` lives in the `collections` app — it is the source attribute of an arrival collection, not a separate domain concern.

### Impact event groundwork

When a `DonationItem` reaches a terminal lifecycle state (`distributed`, `disposed`, `shared`), the system emits an impact event as a provenance record. The API stub `GET /api/public/impact/{anonymous_donor_id}/` returns an empty list in Phase 1. When the Donor Portal is built (Year 2), it consumes this endpoint as the data feed for "your donation helped someone."

Domain events to declare in the knowledge repo schema: `collection_received`, `item_sorted`, `item_stored`, `collection_fulfilled`, `stock_collection_updated`.

---

## 10. Platform Entry Points: Multi-Application Vision

### The topology

The platform is one backend — one Django REST API, one PostgreSQL database, one inference engine — serving multiple distinct user populations through separate frontend applications, each deployed at its own domain with its own permission scope.

```
┌─────────────────────┐  ┌──────────────────────┐  ┌─────────────────────┐
│     Org Portal       │  │    Donor Portal       │  │  Corporate Portal   │
│   org.inkind.at      │  │  donate.inkind.at     │  │ corporate.inkind.at │
│                      │  │                       │  │  (Year 2)           │
│  Staff · Volunteers  │  │  Private donors       │  │  Corporate CSR      │
│  Org admins          │  │  Impact visibility    │  │  CSRD compliance    │
│  Superusers          │  │  Public needs         │  │  Bulk donations     │
└──────────┬───────────┘  └──────────┬────────────┘  └──────────┬──────────┘
           │                         │                           │
           │ /api/org/               │ /api/public/              │ /api/corporate/
           │                         │ /api/donor/               │
           └─────────────────────────┴───────────────────────────┘
                                     │
                            ┌────────┴────────┐
                            │   inkind-hub      │
                            │  Django REST API  │
                            │  PostgreSQL       │
                            │  Inference Engine │
                            └─────────────────-┘
```

Each portal is a separate repository, separate deployment, separate domain. Each consumes a scoped subset of the backend API. The backend is the single source of truth for all data. No portal has a separate database.

### API surface partitioning

The backend exposes three distinct API namespaces, each with its own authentication scheme and permission scope:

**`/api/org/`** — authenticated by session or token, scoped to the user's organisation membership and role. This is the full operational API: intake, sorting, storage management, needs management, disposal, user administration. Only users registered as organisation staff can access this namespace.

**`/api/public/`** — unauthenticated read-only. Exposes: active demand signals with public visibility flag, organisation public profiles, organisation map data. This is what the Donor Portal and the public landing page consume. No authentication required. No operational data exposed.

**`/api/donor/`** — authenticated by anonymous donor token (not a user account). Exposes: impact events for a specific `anonymous_donor_id`, personal donation history, campaign participation. The authentication mechanism is token-based, where the token is derived from the QR code generated at Donor Portal registration. No PII is stored in the inkind-hub backend — only the anonymous token.

**`/api/corporate/`** (Year 2) — authenticated by corporate API key or OAuth. Exposes: CSRD report generation, bulk donation submission, impact dashboards, tax documentation. Scoped to the `CorporateDonor` profile. Zero overlap with org operational data.

### Org Portal (current — `org.inkind.at`)

This is what exists today. The architecture goal for Phase 1 is to make this portal the first working instance of the multi-portal model — which means introducing the API namespace separation now even though only one portal exists. The org views should be served under `/api/org/` routing, not flat `/api/` routing. This is a minor structural change that prevents a larger refactor when the second portal is built.

The Org Portal is the reference implementation of the platform. All other portals are read-only or narrowly-scoped consumers of data that originates here.

### Donor Portal (Year 2 — `donate.inkind.at`)

The Donor Portal is primarily a read-only consumer of the public API plus a narrow write surface for donor registration and QR code generation. It is not a separate backend — it is a frontend application that calls `/api/public/` and `/api/donor/`.

**Minimal feature set at launch:**
- Browse public needs by organisation and category
- Register as an anonymous donor (generates a QR code / `anonymous_donor_id`)
- View impact of past donations via `/api/donor/impact/{id}/`
- View campaign updates published by organisations

**What the Donor Portal does not do:**
- Manage inventory (org portal only)
- Access beneficiary data (never exposed)
- Store donor PII in the inkind-hub backend (only anonymous token)

The Donor Portal can be a lightweight application — a static site, a simple React app, or an HTMX application — because its backend surface is narrow. The complexity lives in inkind-hub, not here.

**The key Year 1 groundwork:**
- `/api/public/demand-signals/` endpoint returning active public demand signals (standing + active campaigns) — introduce in Phase 1
- `/api/public/organisations/` endpoint returning public org profiles — introduce in Phase 1
- `/api/public/impact/{anonymous_donor_id}/` stub endpoint — introduce in Phase 1, returns empty list until items complete lifecycles
- `anonymous_donor_id` field on `DonationSource` — introduce in Phase 1 as a nullable UUID

None of these require the Donor Portal to exist. They are backend contracts that the Donor Portal will consume when built.

### Corporate Portal (Year 2 — `corporate.inkind.at`)

The corporate portal is the critical Year 2 validation test: zero engine code changes when extending to corporate donors. It is a more complex frontend than the Donor Portal because its primary value is compliance reporting — CSRD documentation, ESG metrics, tax receipts — which requires structured data presentation and export.

**The architectural test:** Adding the corporate portal should require only:
- A new `CorporateDonor` model in the `donors` app (new data, not modified existing data)
- New `/api/corporate/` endpoints (new API surface, not modified existing endpoints)
- A new frontend application consuming those endpoints

It should require zero changes to: `item_processing`, `collections`, `storage`, `needs`, `fragments`, the inference engine, or any existing org API endpoint. If it does require such changes, that is direct evidence against H1 — the domain model failed to generalise, and the engine needed modification.

**`DonationSource` is the bridge.** When a corporate donor submits a bulk donation, the organisation staff creates a `DonationCollection` linked to a `DonationSource` with `source_type: corporate` and a FK to the `CorporateDonor` profile. Everything downstream — sorting, storage, needs matching, disposal — operates identically to any other arrival collection. The corporate-specific behaviour (CSRD report generation, tax documentation) is triggered only when the `DonationSource.source_type == corporate` and the linked items reach terminal states. This is a read path off existing data, not a modification of existing processing logic.

### Repackaging philosophy

The Donor Portal and Corporate Portal are not new products in the sense of new backend logic. They are new **views** on data that already exists in inkind-hub — presented with a different information architecture, different vocabulary, and different permission scope appropriate to their audience.

A donor does not see "inventory items" — they see "donated items" and "impact." A corporate CSR manager does not see "disposal workflows" — they see "material diverted from waste" and "CO₂ equivalent saved." The underlying data is the same. The framing is different. The platform's job is to expose the right data through the right API surface, and let each portal present it in terms that resonate with its audience.

This repackaging approach means the platform grows in surface area without growing proportionally in backend complexity. Each new portal is a new frontend and a new API namespace, not a new database or a new business logic layer.

---

## 11. Future Architecture Direction

### 11.1 Events and reactive execution

The current architecture is request-driven: a user takes an action, a Django view handles it, a response is returned. Fragment resolution is triggered by explicit HTTP requests, not by state transitions.

The transition to event-driven execution is a Year 2 goal, explicitly noted in the whitepaper. The key change: when an item transitions to `stored` state, the system emits an `item_stored` domain event. If an active `DemandSignal` exists for that category, the allocation fragment becomes eligible and the system proactively surfaces this to a manager — rather than requiring the manager to manually check.

**Groundwork to lay now:** Structure the REST API endpoint handlers so that state transitions are explicit and isolated. `POST /items/{id}/complete-sorting/` transitions state and is the natural point for future event emission. When Django signals or an event bus (Kafka, Year 2) are introduced, these endpoints become the event emitters. No rewrite — the transition points are already explicit.

Domain events to define at schema level (in `inkind-knowledge-repo/src/inkind/schema/events/`) before they are implemented in Django: `collection_received`, `item_sorted`, `item_stored`, `collection_fulfilled`, `stock_collection_updated`, `demand_signal_registered`, `demand_signal_fulfilled`, `campaign_launched`, `campaign_completed`. The schema declarations serve as the authoritative vocabulary even before the event bus exists.

### 11.2 RDF triplestore for configuration

The in-memory Python singleton scales to a handful of organisations. As organisations grow and structural configuration divergence increases (different category schemas, different fragment variants per org), a dedicated store becomes necessary.

**Why a triplestore rather than Redis or additional PostgreSQL tables:**

The configuration model is inherently graph-structured. A fragment binding is not a flat record — it is a set of relationships across fragment type, step type, state transition graph, observation schema, constraint set, and org policy. SPARQL traverses this graph natively. SQL requires multi-table JOINs that reconstruct the graph on every query.

More importantly: LinkML already compiles to OWL and SHACL — both RDF-native formats. Loading the knowledge repo into a triplestore is the natural operation, requiring no intermediate transformation step. The engine then queries configuration via SPARQL rather than Python dict lookups.

**Federation alignment:** The whitepaper's Year 3-5 architecture lists SPARQL federation protocols as a delivery item. If the config store is a triplestore now, the federation transition is: each org node runs its own triplestore, and the federated SPARQL layer connects them. If the config store is PostgreSQL or Redis, it must be replaced at federation time rather than extended.

**Candidate stores:** Oxigraph (embeddable, Rust-based, excellent Python bindings, can run in-process in development with no additional service) and Apache Jena/Fuseki (battle-tested, more operational overhead, separate service). The migration path: design the engine interface as an abstraction now, back it with the in-memory Python structure today, replace the backing store with a triplestore when the scaling threshold is reached. The engine's callers never change.

### 11.3 Provenance as learning substrate

Phase 1 provenance captures: actor_id, actor_role, stakeholder_id, method, device, timestamp, step_duration_seconds, step_cost_configured, override_flag.

This is the minimum to satisfy GDPR audit requirements. It is also the training substrate for Years 3-4 hybrid AI. The provenance records accumulating during Phase 1 will later be used for provenance-weighted confidence propagation: training models that trust high-confidence observations (made by experienced actors, not overridden) more than low-confidence ones.

No additional work is needed in Phase 1 to enable this. The key is ensuring provenance records are structured (not just log strings) and queryable. The triplestore, when introduced, is the natural store for provenance records — they are graph-shaped data just like configuration.

### 11.4 Full net-value computation

The Phase 1 cost instrumentation establishes `C_s(p)`. The full objective function:

```
net-value(i, b, p) = Σ ω_s(λ) · v_λ(i, b, p) − C_s(p)
```

becomes computable when:

- Beneficiaries and needs matching (the `b` term) — requires needs management + beneficiary profiles
- Disposal workflows (the full `p` term) — requires disposal implementation
- Value dimension scoring functions (dignity, equity, urgency `v_λ`) — requires operational data from 5+ organisations to validate H2

The sequence: Phase 1 establishes `C_s(p)` via cost instrumentation. A later sprint adds minimal beneficiary matching and establishes `v_urgency` (the simplest scoring function — urgency level and wait time, both observable without distribution data). Then disposal workflows enable `v_efficiency` (storage pressure relieved). Dignity and equity come last as they require the most operational data to validate stable functional forms.

### 11.5 Knowledge repo as federation primitive

Once the knowledge repo is the single source of truth for configuration, it becomes a federation primitive: organisations can share scoring function definitions (`v_λ`) while maintaining sovereign weight vectors (`ω_s`). The formal spec's federation diagram makes this concrete — the shared measurement framework (scoring functions, entity schemas, state vocabularies) lives in the federation layer; the org-sovereign configuration (weight vectors, policy constraints, step costs) lives in each node's own instance files.

The Year 1 goal is to make this separation real in the data: shared schema in `src/inkind/schema/`, org-sovereign configuration in `instances/orgs/`. If this discipline is maintained from the start, the federation transition is a deployment architecture change, not a data model rewrite.

### 11.6 Dynamic warehouse: recursive collections and operational inventory

The static warehouse model — fixed bins, mandatory storage assignment at intake, upfront location configuration — is the source of the onboarding friction identified in the prototype deployment. The `DonationCollection` recursive model introduced in §9 is the architectural resolution. This section describes the full expansion roadmap.

**Phase 2: multi-stage sorting via derived collections.** The process template system gains new step types: `create_sub_collection` and `move_to_collection`. A process template `sort_by_condition` creates two child collections from an arrival collection — "acceptable" and "disposal" — without requiring individual item registration. A subsequent `sort_by_category` template splits the "acceptable" collection into category-specific `sorted` collections. Items are only individually registered (creating `DonationItem` records) when the organisation needs that granularity — for high-value items, campaign fulfilment, or detailed provenance. For bulk low-value items, collection-level tracking is sufficient.

**Phase 2: stock collections as the inventory unit.** Named `stock` collections replace fixed storage zones as the primary inventory organiser. A `stock` collection for "children's winter clothing — ready" contains all items of that type regardless of their physical location. `DemandSignal` of type `standing` maps directly to a `stock` collection: the gap is computed as `DemandSignal.quantity_requested − stock.total_item_count`, updated automatically when items enter or leave the collection. The sorting workflow surfaces this gap as the demand signal indicator, exactly as it surfaces campaign signals today.

**Phase 2: storage location becomes optional and incremental.** With `stock` collections as the inventory unit, physical `StorageLocation` assignment becomes a secondary annotation rather than a required field. An organisation can begin processing items into collections before their physical storage layout is formalised. As they learn their operational patterns, they can annotate collections and items with storage locations incrementally. This resolves the onboarding friction at its root cause — not by simplifying the storage configuration UI, but by removing the dependency on storage configuration as a precondition for operation.

**Phase 3: campaign collection assembly.** A `campaign` collection is assembled from `stock` collections when a campaign is launched. Items are moved from stock into the campaign collection via a process episode. Campaign fulfilment is tracked at the collection level: `campaign.total_item_count / campaign_demand_signal.quantity_requested`. When the campaign collection is handed over or distributed, items transition to `distributed` state and the `DonationSource` impact event chain fires.

**Phase 3: inventory intelligence from collection provenance.** Because every collection operation is a process episode with a provenance record, the system accumulates rich operational data: how long items stay in `working` collections before being sorted, which `stock` collections turn over fastest, which categories accumulate without being matched to demand. This data feeds the efficiency scoring and the path optimisation — collections with high demand signal coverage justify more detailed per-item observations during sorting.

**The configurability test for H1.** The dynamic warehouse expansion is the strongest test of H1. An organisation that operates a multi-stage sort with stock collections and campaign assembly should be configurable entirely through new process templates and collection type configuration — zero engine modifications. The fragment routing system resolves `(create_sub_collection, clothing, staff, org_a)` the same way it resolves `(sort_item, clothing, staff, org_a)`. Collections are entities with lifecycles; the engine treats them like any other entity type.

---

## Appendix A: Key Decisions Summary

| Decision | Choice | Rationale |
|---|---|---|
| Process episodes | First-class `ProcessEpisode` model in `fragments` app | Makes C_s(p) computable; enables efficiency UI at launch; captures abandoned episodes; provides audit trail per process instance |
| Process templates | Defined in knowledge repo YAML (Level 2); org selects one per process type (Level 3 DB row) | Complete step sequences in repo; org selection is a single FK — no custom assembly, no process builder UI |
| Process launch mechanism | Existing buttons formalised — create `ProcessEpisode` on click, redirect to `/process/{id}/step/` | Already implemented as implicit behaviour; model makes it explicit, queryable, and cost-measurable |
| Process customisation scope | Template selection only — no step-level editing in Phase 1 | Sufficient for real operational variation (ML vs manual); keeps complexity out of Phase 1 |
| Step sequence snapshot | Stored as JSON on `ProcessEpisode` at launch | Template changes do not affect in-progress episodes |
| Sequencing enforcement | Via `ProcessStep` completion records, not entity lifecycle states | Intermediate steps produce observations only; entity state advances only at terminal step |
| Abandoned episode handling | Background detection + lifecycle_state revert | Prevents items stuck in `sorting_in_progress`; simple revert logic for Phase 1 |
| URL structure | `/process/{episode_id}/step/` for process-bound; standard resource URLs for application | Middleware enforces episode existence; clean separation between process and application UI |
| App split strategy | By process phase, not item type | Item types differ in configuration, not process structure |
| Fragment ownership | Separate `fragments` app | Cross-app concern; must not create circular dependencies |
| Fragment resolution | `(step_type, category, actor_role, org_id)` → template + fields | Category is the process-path selector; role is the mode selector within a path |
| Field-level dependencies | `value_map` in category schema, not fragment routing | Fragment routing is for coarse process-path decisions; `value_map` handles fine-grained field dependencies within a step |
| Constraint mechanism | JSON Schema compiled from category YAML | Frontend-agnostic; hot-reloadable; drives both validation and dropdown filtering from one source |
| Constraint dual use | JSON Schema drives both `ajv` validation and dropdown filtering | `ajv` computes valid values for dependent fields from the same schema used for validation — no duplication |
| UC vs PC constraints | UC in `src/inkind/schema/categories/*.yaml` (shared); PC in `instances/orgs/*.yaml` (org-specific) | Merged at reload time; browser receives merged schema per org |
| Hot-reload scope | Constraints, value_map, routing config, step costs, process definitions — no restart needed | Template files and rendering code still require deployment |
| State management | Explicit `lifecycle_state` field with transition validation | Prerequisite for fragment precondition checking |
| Events | Deferred to Year 2 | Not needed for request-driven REST API; lay groundwork in endpoint structure |
| Config store (now) | In-memory Python singleton loaded at startup | Sufficient for 1-5 orgs; zero SQL at request time |
| Config store (later) | RDF triplestore (Oxigraph → Fuseki) | Graph query semantics match config structure; federation-native |
| Efficiency approach | Cost instrumentation `C_s(p)` first, reward `v_efficiency` deferred | Reward requires match step; cost is supply-side only |
| Needs scope | `DemandSignal` entity with `signal_type` enum (standing/campaign/specific) + `Campaign` wrapper | Standing and campaign signals have same purpose (indicate items of interest) but different lifecycle and urgency semantics; unified entity avoids UI split |
| DemandSignal standing type | No deadline, no quantity target, no urgency; stays active until withdrawn | Org declares permanent category interest; displayed at lower visual weight than campaigns |
| DemandSignal campaign type | Bounded by Campaign deadline, has quantity target and urgency tier | Time-bounded coordinated effort; urgency increases as deadline approaches and fulfilment lags |
| Campaign entity | Wrapper grouping related DemandSignals under shared title, dates, beneficiary group | Display and coordination artifact; progress derived from child signals; powers donor portal campaign view |
| Sorting workflow demand query | Single query on `DemandSignal` for org + category — both standing and campaign types | Engine does not distinguish types for path cost decision; UI renders them at different visual weight |
| Knowledge repo timing | Schema only for Phase 1; no full separate repo yet | "Complexity from practice" — observe Phase 1 deployment before formalising |
| Value dimensions | Efficiency only (ω_s(efficiency) = 1.0) | Most studied; computable without distribution; commercial baseline |
| Donor information | First-class `DonationSource` entity, not attribute on item | Supports multi-type sources; privacy by design; enables corporate generalisation without engine changes |
| DonationSource scope (Phase 1) | `DonationSource` lives in `collections` app; `anonymous_private` type only | `DonationCollection` owns supply-side abstraction; `CorporateDonor`, CSRD logic, and Donor Portal API deferred to Year 2 |
| Multi-portal topology | One backend, multiple frontend applications per audience | Repackaging not rebuilding; new portals add API surface, not backend logic |
| API namespacing | `/api/org/`, `/api/public/`, `/api/donor/`, `/api/corporate/` | Enforces permission scope structurally; enables portal addition without existing endpoint changes |
| Corporate portal test | Zero engine/model changes when adding corporate portal | Direct H1 validation: `DonationSource.source_type` carries the variance; engine unchanged |
| DonationCollection model | Recursive `parent` FK + `collection_type` enum declared now; Phase 1 uses `arrival` type only | Full model now avoids future migration; `working/sorted/stock/campaign/disposed` types deferred to Phase 2+ |
| Dynamic warehouse | `stock` collections replace fixed storage zones as inventory unit; `storage_unit` becomes optional | Resolves onboarding friction at root cause — no storage configuration required to start operations |
| DonationBatch rename | Renamed to `DonationCollection` throughout | `Batch` has industrial connotations incompatible with social sector vocabulary; German `Sammlung` scales naturally across all collection types |
| Storage setup simplification | Deferred — resolved by dynamic warehouse model instead | `stock` collections organise inventory by operational purpose; physical location annotation is incremental |
| Ontology reuse strategy | `uri` and `see_also` annotations in LinkML — no OWL axiom import | Lightweight semantic grounding; pays dividends when triplestore is introduced; no runtime overhead |
| Condition vocabulary | `schema:OfferItemCondition` values (NewCondition, UsedCondition, DamagedCondition) | Stable, widely understood IRIs; avoids custom vocabulary for a universal concept |
| Provenance grounding | PROV-O — `prov:Activity`, `prov:Agent`, `prov:Entity` | W3C standard; automatic interoperability with PROV-aware tools; correct for future federation |
| Organisation grounding | W3C ORG — `org:Organization`, `org:subOrganizationOf`, `org:Role` | Covers hierarchy, membership, roles; builds on PROV-O naturally |
| Process template grounding | P-Plan — `p-plan:Plan` (template), `p-plan:Activity` (step execution) | Designed precisely for the plan/execution distinction the architecture relies on |
| Clothing vocabulary | CPI ontology (`cpi:`) + schema.org wearable vocabulary | CPI covers size, demographic, care, certification; schema.org covers size groups/systems |
| Food vocabulary | FoodOn (selective import via OntoFox) | Authoritative OBO Foundry ontology; UC constraint terms for expiry and food safety |
| Furniture vocabulary | Product Types Ontology (`pto:`) + schema.org + GoodRelations | No single authoritative furniture ontology; combination covers taxonomy and structural attributes |

---

## Appendix B: Constraint Types Summary

The platform enforces constraints at multiple levels, implemented through different mechanisms and owned by different configuration layers. This table provides a complete reference.

| ID | Type | Name | Formal spec term | Scope | Defined in | Enforced by | Mechanism | Hot-reload | Example |
|---|---|---|---|---|---|---|---|---|---|
| **UC** | Universal Constraint | Item-level field rule | UC | All orgs, all items of a category | `src/inkind/schema/categories/*.yaml` (Level 2) | Server-side JSON Schema validation + `ajv` in browser | JSON Schema `if/then` compiled from category YAML | Yes | Underwear must be in new or good condition |
| **PC** | Policy Constraint | Org-specific field rule | PC | One org, all items of a category | `instances/orgs/*.yaml` (Level 3) or `PolicyConstraint` DB model | Merged into per-org JSON Schema at reload; `ajv` + server-side | JSON Schema `if/then` merged with UC schema | Yes (DB write) | Org A requires intact labels on all tops |
| **SQ** | Sequencing Constraint | Step ordering within an episode | SQ | All orgs | `ProcessTemplate` step sequence (Level 2 YAML) | `ProcessStep` completion records — step N+1 blocked until step N has a completion record | Episode progress tracking in `fragments` app | Yes (template reload) | `assign_storage` cannot precede `assign_category` |
| **FS** | Fragment precondition | Entity state prerequisite for a fragment | Precondition (AV/SQ) | All orgs | `fragment_binding.yaml` — `precondition_state` field (Level 2) | Engine `resolve()` precondition check against `item.lifecycle_state` | In-memory state machine check at episode step resolution | Yes (binding reload) | `sort_item` fragment requires item in `received` state |
| **VM** | Value map dependency | Dependent dropdown filtering | — | All orgs, per category | `src/inkind/schema/categories/*.yaml` — `value_map` block (Level 2) | JSON Schema `if/then` compiled from `value_map`; `ajv` filters dropdown options in browser | Same JSON Schema as UC/PC — dual use for validation and filtering | Yes | Baby demographic → baby sizes only shown |
| **LC** | Lifecycle transition | Entity state machine transitions | — | All orgs | `states/*.yaml` in knowledge repo (Level 2) | Django model `clean()` / `save()` transition validation | Python model layer validation | No (code deploy) | `DonationItem` cannot skip from `received` to `stored` |
| **AV** | Actor availability | Actor authorisation and capacity | AV | Per org | `OrgProcessConfig` + role assignments (Level 3 DB) | Deferred — future engine extension | Runtime DB query against actor state (one query, bounded) | Yes (DB) | Volunteer role cannot perform `manager_approval` step |
| **TC** | Temporal/deadline | Campaign deadline enforcement | — | Per org, per campaign | `Campaign.ends_at` (Level 3 DB) | Background task marks expired `DemandSignal` records; urgency tier updated periodically | Scheduled task + lifecycle state update | Yes (DB) | Campaign ends_at passed → child signals → `expired` |
| **EC** | Cross-entity constraint | Cross-entity consistency rules | EC | All orgs | `src/inkind/schema/` (Level 1/2) — deferred to triplestore phase | Future: SPARQL rules over triplestore; now: application-layer checks | SQL / Python for now; SPARQL when triplestore introduced | Deferred | A `DonationItem` in `stored` state must have a `storage_unit` assigned |

### Constraint layer mapping

```
Layer 1 — Schema          Layer 2 — Base config       Layer 3 — Org config
(knowledge repo schema)   (knowledge repo instances)  (Django database)

UC rules                  Fragment preconditions       PC rules (PolicyConstraint)
VM value maps             Process templates            Step costs (StepCost)
LC lifecycle states        Fragment bindings            Org process selection
EC cross-entity shape      Step type catalogue          OrgProcessConfig
```

### Constraint evaluation points

| When | What is evaluated | Mechanism |
|---|---|---|
| Form field change (browser) | UC + PC (merged JSON Schema) + VM (dropdown filtering) | `ajv` in-browser, schema embedded at page load |
| Form submission (POST) | UC + PC (merged JSON Schema) | Python `jsonschema` library, server-side |
| Episode step resolution | Fragment precondition (FS), step sequencing (SQ) | Engine `resolve()` in-memory check |
| Episode step completion | Lifecycle transition (LC) | Django model validation on save |
| Campaign background task | Temporal deadline (TC), urgency tier update | Celery task or management command |
| Future: triplestore | Cross-entity constraints (EC) | SPARQL rules over RDF graph |

### Constraint ownership at a glance

| Constraint | Who defines it | Who can change it | Change requires deployment? |
|---|---|---|---|
| UC | System architect / domain expert | PR to knowledge repo + reload | No (reload only) |
| VM | Domain expert | PR to knowledge repo + reload | No (reload only) |
| PC | Org admin | Django admin UI or org config page | No (DB write) |
| SQ | Process designer | PR to knowledge repo + reload | No (reload only) |
| FS | Process designer | PR to knowledge repo + reload | No (reload only) |
| LC | System architect | PR to knowledge repo + code change | Yes |
| AV | Org admin (role assignments) | Django admin UI | No (DB write) |
| TC | Org admin (campaign dates) | Campaign edit UI | No (DB write) |
| EC | System architect | Triplestore rule set (future) | No (rule reload, future) |
