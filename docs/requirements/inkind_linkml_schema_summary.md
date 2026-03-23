# inkind-knowledge-repo: LinkML Schema Summary

**Status:** Working reference — derived from implementation plan  
**Date:** March 2026  
**Scope:** Phase 1 schemas with future schema stubs

---

## Overview

The `inkind-knowledge-repo` defines the declarative knowledge layer of the in-kind donation coordination platform. It is not queried at runtime — it is compiled and loaded into `inkind-hub`'s inference engine at startup or on admin reload. Every schema here has a corresponding runtime consumer in the Django application; the schema is the contract between the knowledge layer and the execution engine.

The repository is a standard LinkML project generated via the LinkML cookiecutter. Schemas live in `src/inkind/schema/`. Category schemas live in `src/inkind/schema/categories/`. Org-specific instance data lives in `instances/`.

**Generated artefacts consumed by `inkind-hub`:**
- `generated/pydantic/` — installed as a Python package, used for configuration loading and in-memory engine indices
- `generated/json-schema/` — one JSON Schema file per category, served to the browser for `ajv` validation and dropdown filtering

---

## Repository Structure

```
inkind-knowledge-repo/
├── src/inkind/schema/
│   ├── entities/              # Core domain entity schemas
│   │   ├── donation_item.yaml
│   │   ├── donation_collection.yaml
│   │   ├── donation_source.yaml
│   │   ├── storage_location.yaml
│   │   ├── actor.yaml
│   │   ├── organisation.yaml
│   │   ├── demand_signal.yaml
│   │   └── campaign.yaml
│   ├── states/                # Lifecycle state machine schemas
│   │   ├── item_lifecycle.yaml
│   │   ├── collection_lifecycle.yaml
│   │   └── demand_signal_lifecycle.yaml
│   ├── process/               # Process template and step type schemas
│   ├── ui/                    # Fragment binding and routing schemas
│   ├── value/                 # Value dimension and cost schemas
│   ├── categories/            # Category-specific schemas (one file per item type)
│   │   ├── _base.yaml
│   │   ├── clothing.yaml
│   │   ├── furniture.yaml
│   │   └── food.yaml
│   └── provenance.yaml        # Provenance record schema
├── instances/
│   ├── orgs/                  # Org-specific configuration instances
│   ├── workflows/             # Process template instances
│   └── scenarios/             # Formal spec worked examples as instance data
└── generated/
    ├── pydantic/              # gen-pydantic output
    └── json-schema/           # gen-json-schema output — one file per category
        ├── clothing.json
        └── furniture.json
```

---

## Schema Groups

### Group 1 — Entities (`src/inkind/schema/entities/`)

Core domain objects. Each schema defines a LinkML class with slots, types, and external ontology grounding via `uri` and `see_also` annotations.

---

#### `donation_item.yaml`

The central operational entity. Represents a single physical item moving through the intake and redistribution lifecycle.

| Slot | Type | Required | Notes |
|---|---|---|---|
| `id` | `uriorcurie` | yes | UUID, primary identifier |
| `category` | `CategoryEnum` | yes | Resolved from `src/inkind/schema/categories/` vocabulary |
| `condition` | `ConditionEnum` | yes | `uri: schema:itemCondition` |
| `lifecycle_state` | `ItemLifecycleStateEnum` | yes | Validated transitions only |
| `source_collection` | `DonationCollection` | no | FK — which collection this item was registered from |
| `donation_source` | `DonationSource` | no | FK — nullable, privacy boundary |
| `storage_unit` | `StorageLocation` | no | FK — set when item reaches `stored` state |
| `observations` | `ObservationSet` | no | JSON — category-specific attribute values |
| `created_at` | `datetime` | yes | |
| `updated_at` | `datetime` | yes | |

**External grounding:**
- Class `see_also: schema:Product`
- `condition` slot `uri: schema:itemCondition`
- `condition` values map to `schema:NewCondition`, `schema:UsedCondition`, `schema:DamagedCondition`, `schema:RefurbishedCondition`

**Phase:** Phase 1

---

#### `donation_collection.yaml`

A general-purpose grouping of items. In Phase 1, used only as `arrival` type — a direct replacement for the former `DonationBatch`. The recursive parent structure and additional `collection_type` values are declared now but used in Phase 2+, enabling the dynamic warehouse model without a future data migration.

| Slot | Type | Required | Notes |
|---|---|---|---|
| `id` | `uriorcurie` | yes | |
| `org` | `SocialOrganisation` | yes | FK |
| `collection_type` | `CollectionTypeEnum` | yes | `arrival | working | sorted | stock | campaign | disposed` |
| `label` | `string` | yes | Human-readable: "Winter clothing — Nov 2026 arrival" |
| `parent` | `DonationCollection` | no | FK — null for arrival collections (root); set for all derived collections |
| `donation_source` | `DonationSource` | no | FK — set on arrival collections; inherited by child collections and items |
| `lifecycle_state` | `CollectionLifecycleEnum` | yes | `open → processing → closed → archived` |
| `item_count` | `integer` | yes | Items directly registered to this collection |
| `total_item_count` | `integer` | yes | Derived — items in this + all descendant collections |
| `created_at` | `datetime` | yes | |
| `created_by` | `Actor` | yes | FK |
| `notes` | `string` | no | |

**`collection_type` values:**

| Value | Phase | Purpose |
|---|---|---|
| `arrival` | Phase 1 | Root collection from a donation event. Replaces `DonationBatch`. |
| `working` | Phase 2 | Temporary intermediate collection during multi-stage sorting. |
| `sorted` | Phase 2 | Stable grouping after a sort stage completes. |
| `stock` | Phase 2 | Named inventory collection ready for distribution. Maps to `DemandSignal.standing`. |
| `campaign` | Phase 2 | Collection assembled for a specific `Campaign`. |
| `disposed` | Phase 2 | Items culled during sorting — auditable at collection level. |

**External grounding:**
- Class `see_also: ceon:Resource` (Circular Economy Ontology Network)
- `collection_type` stock value `see_also: ceon:CircularValueNetwork`

**Phase:** Phase 1 (arrival type only); full model declared for Phase 2+ expansion

---

#### `storage_location.yaml`

A physical storage unit within an organisation's warehouse — a bin, shelf, rack, or zone.

| Slot | Type | Required | Notes |
|---|---|---|---|
| `id` | `uriorcurie` | yes | |
| `org` | `SocialOrganisation` | yes | FK |
| `label` | `string` | yes | Human-readable name ("Bin A3", "Clothing Rack 2") |
| `parent` | `StorageLocation` | no | FK — for hierarchical storage (zone → rack → bin) |
| `capacity` | `integer` | no | Maximum items; null = unlimited |
| `current_occupancy` | `integer` | yes | Derived from linked items |
| `is_active` | `boolean` | yes | |
| `category_affinity` | `CategoryEnum` | no | Preferred category — informational, not enforced |

**Note:** Full storage setup redesign is deferred (see implementation plan §11.6). This schema represents the minimal formalisation of the existing model.

**Phase:** Phase 1 (formalisation of existing model)

---

#### `actor.yaml`

A person interacting with the system — volunteer, staff member, or manager.

| Slot | Type | Required | Notes |
|---|---|---|---|
| `id` | `uriorcurie` | yes | |
| `org` | `SocialOrganisation` | yes | FK |
| `role` | `ActorRoleEnum` | yes | `volunteer | staff | manager | admin` |
| `experience_level` | `ExperienceLevelEnum` | no | `novice | experienced | expert` — informs fragment mode selection |
| `is_active` | `boolean` | yes | |

**External grounding:**
- Class `see_also: foaf:Person`
- `role` slot `see_also: org:Role`

**Phase:** Phase 1

---

#### `organisation.yaml`

A social organisation deploying the platform — the primary operational tenant.

| Slot | Type | Required | Notes |
|---|---|---|---|
| `id` | `uriorcurie` | yes | |
| `name` | `string` | yes | |
| `parent` | `SocialOrganisation` | no | FK — hierarchy depth limit 4 |
| `geo_point` | `GeoPoint` | no | For public map display |
| `is_active` | `boolean` | yes | |
| `config` | `OrgConfig` | no | Inlined config object (timezone, locale, etc.) |

**External grounding:**
- Class `uri: org:Organization`
- `parent` slot `uri: org:subOrganizationOf`

**Phase:** Phase 1 (formalisation of existing model)

---

#### `donation_source.yaml`

Supply-side abstraction — who or what originated a donation. Privacy boundary between item records and donor identity.

| Slot | Type | Required | Notes |
|---|---|---|---|
| `id` | `uriorcurie` | yes | |
| `source_type` | `DonationSourceTypeEnum` | yes | `anonymous_private | corporate | organisation` |
| `anonymous_donor_id` | `uriorcurie` | no | Opaque UUID token — Phase 1 only type populated |
| `corporate_donor_ref` | `string` | no | FK reference — Year 2 |
| `organisation_ref` | `SocialOrganisation` | no | FK — for Share disposal workflow |
| `lifecycle_state` | `DonationSourceLifecycleEnum` | yes | `announced → received → acknowledged` |
| `created_at` | `datetime` | yes | |
| `provenance` | `ProvenanceRecord` | no | Who recorded this source, on what device |

**External grounding:**
- `anonymous_donor_id` `see_also: schema:identifier`
- `see_also: schema:GiveAction` on the donation event concept

**Phase:** Phase 1 (minimal — `anonymous_private` type only)

---

#### `demand_signal.yaml`

Demand-side entity — what an organisation wants. Unifies standing stock interests and time-bounded campaign requests under one model.

| Slot | Type | Required | Notes |
|---|---|---|---|
| `id` | `uriorcurie` | yes | |
| `org` | `SocialOrganisation` | yes | FK |
| `signal_type` | `DemandSignalTypeEnum` | yes | `standing | campaign | specific` |
| `category` | `CategoryEnum` | yes | Matches `src/inkind/schema/categories/` vocabulary |
| `attributes` | `AttributeMap` | no | JSON — category-specific demand attributes (subcategory, demographic, size range, etc.) |
| `quantity_requested` | `integer` | no | null = any amount welcome (standing signals) |
| `quantity_fulfilled` | `integer` | yes | Derived from matched items |
| `campaign` | `Campaign` | no | FK — nullable, set for `campaign` type only |
| `holder` | `string` | no | FK reference — Beneficiary or SocialOrganisation |
| `context_note` | `string` | no | Human-readable context ("Back to school for 30 primary school children") |
| `deadline` | `date` | no | null for standing signals |
| `urgency_tier` | `UrgencyTierEnum` | no | `low | medium | high | critical` — null for standing |
| `lifecycle_state` | `DemandSignalLifecycleEnum` | yes | `active → partially_fulfilled → fulfilled | expired | withdrawn` |
| `registered_at` | `datetime` | yes | |
| `public_visibility` | `boolean` | yes | Whether to expose on public API / donor portal |

**External grounding:**
- Class `see_also: ossn:Goal` (OSSN Ontology of Social Service Needs)
- Class `see_also: schema:Demand`
- `category` `see_also: openeligibility:ServiceTag`
- `urgency_tier` `see_also: openeligibility:HumanSituation`

**Phase:** Phase 1

---

#### `campaign.yaml`

Coordination wrapper grouping related demand signals under a shared public-facing appeal.

| Slot | Type | Required | Notes |
|---|---|---|---|
| `id` | `uriorcurie` | yes | |
| `org` | `SocialOrganisation` | yes | FK |
| `title` | `string` | yes | "Back to School 2026" |
| `description` | `string` | no | |
| `starts_at` | `datetime` | yes | |
| `ends_at` | `datetime` | yes | Propagates as deadline to child DemandSignals |
| `target_beneficiary_group` | `string` | no | "Primary school children starting September" |
| `lifecycle_state` | `CampaignLifecycleEnum` | yes | `planned → active → completed | cancelled` |
| `signals` | `DemandSignal[]` | no | Inverse relation — signals with FK to this campaign |

**External grounding:**
- Class `uri: schema:Event`
- `starts_at` `uri: schema:startDate`
- `ends_at` `uri: schema:endDate`

**Phase:** Phase 1

---

### Group 2 — Lifecycle State Machines (`src/inkind/schema/states/`)

State machine definitions. Each schema declares an enum of valid states and the permitted transition graph. LinkML enums; Django enforces transitions via model `clean()`.

---

#### `collection_lifecycle.yaml`

```
open → processing → closed → archived
```

`arrival` collections: `open` on creation, `processing` when items are being registered, `closed` when all items processed.
`stock` collections: `open` indefinitely — close only when the org explicitly retires the stock.
`working` / `sorted` collections: `processing` during sort episode, `closed` when all items moved to child collections.

**Phase:** Phase 1 (arrival lifecycle only); full semantics in Phase 2+

---

#### `item_lifecycle.yaml`

```
announced → received → sorting_in_progress → sorted → stored
                                                    → disposed    (future)
                                                    → distributed (future)
                                                    → shared      (future)
```

| State | Meaning | Entry condition |
|---|---|---|
| `announced` | Donor indicated intent; item not yet physical | DonationSource created |
| `received` | Physical item arrived and registered | Batch intake completed |
| `sorting_in_progress` | Active sort episode in progress | ProcessEpisode launched |
| `sorted` | Sorting completed, category and attributes assigned | Sort episode terminal step |
| `stored` | Item assigned to a storage location | assign_storage step completed |
| `disposed` | Item unsuitable for redistribution (future) | Disposal episode |
| `distributed` | Item given to beneficiary (future) | Distribution episode |
| `shared` | Item transferred to another org (future) | Share episode |

**Phase:** Phase 1 (`announced → stored`); future states declared as stubs

---

#### `demand_signal_lifecycle.yaml`

```
active → partially_fulfilled → fulfilled
active →                       expired     (deadline passed)
active →                       withdrawn   (org cancelled)
```

`standing` type signals: `active` only — no expiry, no fulfilment terminal state.

**Phase:** Phase 1

---

#### `donation_source_lifecycle.yaml`

```
announced → received → acknowledged
```

**Phase:** Phase 1 (`announced`, `received` only; `acknowledged` stub for Year 2 impact events)

---

#### `campaign_lifecycle.yaml`

```
planned → active → completed
planned → active → cancelled
planned →          cancelled
```

**Phase:** Phase 1

---

#### `process_episode_lifecycle.yaml`

```
in_progress → completed
in_progress → abandoned
```

**Note:** This is a runtime state — defined here for schema completeness but enforced in the Django `ProcessEpisode` model, not loaded into the in-memory engine.

**Phase:** Phase 1

---

### Group 3 — Process (`src/inkind/schema/process/`)

Process configuration schemas — the building blocks that orgs assemble into operational workflows.

---

#### `step_type.yaml`

The catalogue of available step types. These are the atomic operations that appear in process templates. An org cannot invent new step types; it assembles sequences from this catalogue.

| Slot | Type | Required | Notes |
|---|---|---|---|
| `id` | `uriorcurie` | yes | Slug — `assign_category`, `take_photo`, etc. |
| `label` | `string` | yes | |
| `description` | `string` | no | |
| `produces_observations` | `string[]` | no | Which attribute slots this step populates |
| `postcondition` | `ItemLifecycleStateEnum` | no | null for intermediate steps; set for terminal step |
| `default_cost` | `float` | yes | Minutes — used when org has no StepCost override |
| `fragment_bindings` | `UIFragmentBinding[]` | no | Inverse relation |

**Phase 1 step type catalogue:**

*Phase 2 will add collection-oriented step types: `create_sub_collection`, `move_to_collection`, `merge_collections`, `assign_to_stock`. These will be declared as stubs in the Phase 1 knowledge repo to reserve the vocabulary.*

| Step type | Description | Produces | Terminal? |
|---|---|---|---|
| `assign_category` | Select item category and subcategory | `category`, `subcategory` | No |
| `manual_condition_assessment` | Manual assessment of condition and attributes | `condition`, category-specific attributes | No |
| `take_photo` | Capture item photo | `photo_ref` | No |
| `ml_recognition` | Submit photo for ML inference | `ml_category_suggestion`, `ml_condition_suggestion` | No |
| `review_ml_result` | Actor reviews and accepts/adjusts ML output | `category`, `condition` (confirmed) | No |
| `assign_storage` | Assign item to storage location | `storage_unit` | Yes → `stored` |
| `set_category` | Set demand signal category | `category` | No |
| `set_signal_type` | Set demand signal type | `signal_type` | No |
| `set_attributes` | Set demand signal attribute filters | `attributes` | Yes → `active` |
| `assess_need` | Evaluate urgency and context of a specific need | `urgency_tier`, `context_note` | No |
| `set_priority` | Set urgency tier and deadline | `urgency_tier`, `deadline` | Yes → `active` |

**External grounding:** `see_also: p-plan:Activity` (abstract step type as plan component)

**Phase:** Phase 1

---

#### `process_template.yaml`

A named, complete process definition — an ordered sequence of step types that an org can select. Orgs select a template per process type; they do not modify templates.

| Slot | Type | Required | Notes |
|---|---|---|---|
| `id` | `uriorcurie` | yes | Slug — `sort_item_manual`, `sort_item_with_ml`, etc. |
| `process_type` | `ProcessTypeEnum` | yes | `sort_item | register_demand_signal | stock_check` |
| `label` | `string` | yes | Human-readable name shown in org config UI |
| `description` | `string` | no | |
| `is_default` | `boolean` | yes | Used when org has no explicit selection |
| `entity_type` | `EntityTypeEnum` | yes | `donation_item | demand_signal | donation_collection | storage_unit` |
| `launchable_from_states` | `string[]` | yes | Entity lifecycle states from which this process can be launched |
| `steps` | `ProcessTemplateStep[]` | yes | Ordered list |

**`ProcessTemplateStep` (inlined type):**

| Slot | Type | Required | Notes |
|---|---|---|---|
| `step_type` | `StepType` | yes | FK into step type catalogue |
| `sequence` | `integer` | yes | Explicit ordering |
| `is_optional` | `boolean` | yes | |
| `skip_condition` | `AttributeCondition` | no | Auto-skip if condition met |

**External grounding:**
- Class `uri: p-plan:Plan`
- `steps` `see_also: p-plan:wasGeneratedBy`

**Phase 1 templates:**

| Template ID | Process type | Steps | Default? |
|---|---|---|---|
| `sort_item_manual` | `sort_item` | assign_category → manual_condition_assessment → assign_storage | Yes |
| `sort_item_with_ml` | `sort_item` | assign_category → take_photo → ml_recognition → review_ml_result → assign_storage | No |
| `sort_item_rapid_triage` | `sort_item` | assign_category → assign_storage | No |
| `register_demand_signal` | `register_demand_signal` | set_category → set_signal_type → set_attributes | Yes |

**Phase:** Phase 1

---

### Group 4 — UI Fragment Bindings (`src/inkind/schema/ui/`)

Fragment routing configuration — maps process step context to a specific template and field set.

---

#### `fragment_binding.yaml`

The resolution table loaded into the inference engine's in-memory routing index. Resolves `(step_type, category, actor_role, org_id)` → template + fields + postcondition.

| Slot | Type | Required | Notes |
|---|---|---|---|
| `id` | `uriorcurie` | yes | Slug — `sort_clothing_guided`, `sort_furniture_expert` |
| `step_type` | `StepType` | yes | FK into step type catalogue |
| `category` | `CategoryEnum` | no | null = applies to all categories |
| `actor_role` | `ActorRoleEnum` | yes | `volunteer | staff | manager` |
| `precondition_state` | `string` | yes | Entity lifecycle state required — constraint type FS |
| `postcondition_state` | `string` | yes | Entity state produced on completion |
| `template_ref` | `string` | yes | Relative path to Django template file |
| `required_fields` | `string[]` | yes | Which slots the actor must fill in this step |
| `guidance_text` | `string` | no | Helper text shown to volunteer mode actors |
| `emits_event` | `DomainEventEnum` | no | Domain event emitted on completion |
| `mode` | `FragmentModeEnum` | no | `guided | expert` — informational |

**Routing resolution logic:** The engine evaluates bindings in specificity order: category-specific bindings take priority over category-null (catch-all) bindings. Among same-specificity bindings, role-specific takes priority over role-null.

**Phase:** Phase 1

---

### Group 5 — Value Dimensions and Cost (`src/inkind/schema/value/`)

Formal definitions of the `v_λ` scoring functions and the `ω_s` weight vector schema. Phase 1 implements cost only; other dimensions are declared as stubs.

---

#### `step_cost.yaml`

Schema for org-level step cost configuration. Instances live in the Django database (`StepCost` model), not in the knowledge repo. This schema defines the shape of valid configuration.

| Slot | Type | Required | Notes |
|---|---|---|---|
| `org` | `SocialOrganisation` | yes | FK |
| `step_type` | `StepType` | yes | FK |
| `cost_scalar` | `float` | yes | Operational cost in org-defined units (minutes, staff-minutes, or normalised index) |
| `unit` | `CostUnitEnum` | yes | `minutes | staff_minutes | index` |
| `effective_from` | `datetime` | yes | Versioned — org can change costs over time |

**Phase:** Phase 1

---

#### `weight_vector.yaml`

Schema for the `ω_s` weight vector — how an org weighs the four value dimensions. Phase 1 hardcodes `efficiency = 1.0`, all others `= 0.0`. Schema declared now so instances are valid when other dimensions are activated.

| Slot | Type | Required | Notes |
|---|---|---|---|
| `org` | `SocialOrganisation` | yes | |
| `efficiency` | `float` | yes | Default 1.0 in Phase 1 |
| `dignity` | `float` | yes | Default 0.0 — deferred |
| `equity` | `float` | yes | Default 0.0 — deferred |
| `urgency` | `float` | yes | Default 0.0 — deferred |
| `effective_from` | `datetime` | yes | |

**Constraint:** weights must sum to 1.0 — UC on this schema.

**Phase:** Phase 1 stub; fully activated in later phases

---

#### `value_dimension.yaml` *(stub)*

Formal definition of the `v_λ` scoring functions — one class per dimension. Stub declarations only in Phase 1; function bodies deferred until operational data validates functional forms.

```
ValueDimension (abstract)
├── EfficiencyDimension    # v_efficiency(i, b, p) — deferred
├── UrgencyDimension       # v_urgency — deferred  
├── DignityDimension       # v_dignity — deferred
└── EquityDimension        # v_equity — deferred
```

**Phase:** Stub in Phase 1; activated in later phases

---

### Group 6 — Provenance (`src/inkind/schema/provenance.yaml`)

The π(s_k) provenance record — one record per completed process step. Captures the complete context of who did what, when, with what device, and at what cost.

| Slot | Type | Required | Notes |
|---|---|---|---|
| `id` | `uriorcurie` | yes | |
| `episode` | `ProcessEpisode` | yes | FK — which episode this step belongs to |
| `step_type` | `StepType` | yes | |
| `fragment_id` | `UIFragmentBinding` | yes | Which fragment was resolved |
| `actor` | `Actor` | yes | FK |
| `actor_role` | `ActorRoleEnum` | yes | Captured at step time — role may change |
| `org` | `SocialOrganisation` | yes | FK |
| `device` | `DeviceTypeEnum` | yes | `mobile | desktop | scan` |
| `started_at` | `datetime` | yes | When the step fragment was presented |
| `completed_at` | `datetime` | yes | When the actor submitted |
| `duration_seconds` | `integer` | yes | Derived: `completed_at - started_at` |
| `cost_configured` | `float` | yes | `c_s` scalar from StepCost at time of execution |
| `observations` | `ObservationSet` | yes | JSON — field values submitted by the actor |
| `override_flag` | `boolean` | yes | True if actor acknowledged a constraint warning |
| `override_reason` | `string` | no | Free text if override was explicit |

**External grounding:**
- Class `uri: prov:Activity`
- `actor` slot `uri: prov:wasAssociatedWith`
- `completed_at` `uri: prov:endedAtTime`
- `observations` `see_also: prov:generated`
- `episode` `see_also: p-plan:wasGeneratedBy`

**Phase:** Phase 1

---

### Group 7 — Category Schemas (`src/inkind/schema/categories/`)

One YAML file per item type. These are schema definitions — not instances. They define the attribute vocabulary, value map dependencies, and UC constraint rules for a given item type. The fact that they have a different internal structure from standard LinkML class definitions does not make them instances: they are compiled by `gen-json-schema` just like other schemas, and their output goes to `generated/`, not `instances/`. Keeping them under `src/inkind/schema/` means the standard `linkml-validate` glob picks them up without special configuration.

Each category file has three sections: `attributes`, `value_map`, `constraints`, plus a `process_path` reference linking to the fragment binding routing.

---

#### `categories/_base.yaml`

Shared attribute type definitions reused across all category schemas.

| Attribute | Type | Values | Notes |
|---|---|---|---|
| `condition` | `enum` | `new, good, fair, poor` | `uri: schema:itemCondition` |
| `storage_unit` | `ref` | StorageLocation | Used by `assign_storage` step |
| `photo_ref` | `string` | URL/path | Populated by `take_photo` step |
| `notes` | `string` | free text | Actor notes at any step |

---

#### `categories/clothing.yaml`

| Section | Contents |
|---|---|
| `process_path` | `sort_clothing` |
| `attributes` | subcategory, demographic (depends_on: subcategory), size (depends_on: demographic), condition, intact_labels (show_if: subcategory in [tops, bottoms, outerwear]) |
| `value_map` | subcategory → demographic options; demographic → size options |
| `constraints (UC)` | underwear + {fair, poor} condition → block; adult underwear + used condition → block |
| **External grounding** | `see_also: cpi:ClothingAndAccessories`; size `see_also: cpi:ClothingSize`; demographic `see_also: cpi:designatedFor`; size groups `see_also: schema:WearableSizeGroupBaby` etc. |

---

#### `categories/furniture.yaml`

| Section | Contents |
|---|---|
| `process_path` | `sort_furniture` |
| `attributes` | type, material (depends_on: type), condition, structural_integrity (boolean), dimensions_cm (required_if: type in [tables, beds]) |
| `value_map` | furniture type → valid material options |
| `constraints (UC)` | structural_integrity = false → block (suggest disposal); poor condition + seating/beds → warn |
| **External grounding** | `see_also: pto:Furniture`; type values `see_also: pto:Chair`, `pto:Table`, `pto:Bed` etc.; material `see_also: gr:qualitativeProductOrServiceProperty` |

---

#### `categories/food.yaml` *(Phase 1 stub — if food orgs are onboarded)*

| Section | Contents |
|---|---|
| `process_path` | `sort_food` |
| `attributes` | food_type, packaging_intact (boolean), expiry_date (date), storage_requirement |
| `value_map` | food_type → storage_requirement options |
| `constraints (UC)` | expiry_date < today → block (suggest disposal); packaging_intact = false + perishable → block |
| **External grounding** | `see_also: foodon:FoodMaterial`; food_type taxonomy `see_also: foodon:*` terms |

---

### Group 8 — Organisation Instances (`instances/orgs/`)

One YAML file per deployed organisation. Contains org-specific Level 3 configuration: step cost scalars, process template selection, and PC (Policy Constraint) overrides.

#### Schema for org instance files

| Section | Contents | Maps to Django model |
|---|---|---|
| `org_id` | Reference to the organisation | `Enterprise` |
| `step_costs` | List of `{step_type, cost_scalar, unit}` | `StepCost` |
| `process_selections` | List of `{process_type, template_id}` | `OrgProcessConfig` |
| `weight_vector` | `{efficiency, dignity, equity, urgency}` | `OrgWeightVector` |
| `pc_constraints` | List of `{trigger, action, message}` | `PolicyConstraint` |
| `fragment_overrides` | List of `{base_binding_id, override_field, override_value}` | `FragmentBindingOverride` |

**Example (`instances/orgs/org_a.yaml`):**

```yaml
org_id: org-a
step_costs:
  - step_type: assign_category
    cost_scalar: 0.5
    unit: minutes
  - step_type: manual_condition_assessment
    cost_scalar: 2.0
    unit: minutes
  - step_type: assign_storage
    cost_scalar: 0.5
    unit: minutes

process_selections:
  - process_type: sort_item
    template_id: sort_item_manual

weight_vector:
  efficiency: 1.0
  dignity: 0.0
  equity: 0.0
  urgency: 0.0

pc_constraints:
  - id: pc-org-a-labels
    trigger: {category: clothing, subcategory: [tops, bottoms, outerwear]}
    condition: {intact_labels: false}
    action: warn
    message: "Org A prefers items with intact labels — please note condition"
```

---

### Group 9 — Process Workflow Instances (`instances/workflows/`)

Complete process template instances. These are the Level 2 shared workflow definitions loaded by the engine.

The content of these files is the formal YAML encoding of the `ProcessTemplate` schema defined in Group 3. These YAML files are the source; `gen-pydantic` compiles them into the Pydantic package that Django actually loads at runtime. The YAML is the authoritative source; the compiled Pydantic models are the runtime artefact.

**Files:**
- `sort_item_manual.yaml`
- `sort_item_with_ml.yaml`
- `sort_item_rapid_triage.yaml`
- `register_demand_signal.yaml`

---

### Group 10 — Scenarios (`instances/scenarios/`)

Self-contained YAML instances walking through the formal spec's worked examples as real data. Serve simultaneously as funder communication artefacts, regression test fixtures, and CI validation targets.

**Files (Phase 1):**

| File | Formal spec section | What it demonstrates |
|---|---|---|
| `winter_coat.yaml` | §3.3 | Two candidate paths for a winter coat, step costs, net-value comparison |
| `back_to_school_campaign.yaml` | §11.4 | Campaign demand signal lifecycle, urgency escalation, partial fulfilment |
| `clothing_constraint_enforcement.yaml` | §5.2 | UC/PC constraint evaluation — underwear rule, org-specific label policy |

**Phase 2 scenario (stub):**

| File | What it demonstrates |
|---|---|
| `collection_hierarchy_sort.yaml` | Multi-stage sort: arrival collection → condition sort → category sort → stock collections → campaign fulfilment. The most important worked example for the dynamic warehouse concept and funder communication. |

Each scenario file instantiates the full entity graph: a `DonationItem`, a `ProcessEpisode`, a sequence of `ProcessStep` records with observations, and the resulting `ProvenanceRecord` set.

---

## Enum Definitions

All enums are defined inline in their primary schema or in a shared `enums.yaml`. Key enums:

| Enum | Values | Notes |
|---|---|---|
| `CollectionTypeEnum` | `arrival, working, sorted, stock, campaign, disposed` | Phase 1: arrival only |
| `CollectionLifecycleEnum` | `open, processing, closed, archived` | |
| `ItemLifecycleStateEnum` | `announced, received, sorting_in_progress, sorted, stored, disposed, distributed, shared` | |
| `DemandSignalLifecycleEnum` | `active, partially_fulfilled, fulfilled, expired, withdrawn` | |
| `DonationSourceTypeEnum` | `anonymous_private, corporate, organisation` | |
| `DonationSourceLifecycleEnum` | `announced, received, acknowledged` | |
| `CampaignLifecycleEnum` | `planned, active, completed, cancelled` | |
| `ProcessTypeEnum` | `sort_item, register_demand_signal, stock_check` | `stock_check` is stub |
| `ActorRoleEnum` | `volunteer, staff, manager, admin` | |
| `ExperienceLevelEnum` | `novice, experienced, expert` | |
| `UrgencyTierEnum` | `low, medium, high, critical` | null for standing signals |
| `DemandSignalTypeEnum` | `standing, campaign, specific` | |
| `FragmentModeEnum` | `guided, expert` | |
| `ConditionEnum` | `new, good, fair, poor` | `uri: schema:OfferItemCondition` values |
| `DeviceTypeEnum` | `mobile, desktop, scan` | |
| `DomainEventEnum` | `collection_received, item_sorted, item_stored, collection_fulfilled, stock_collection_updated, demand_signal_registered, demand_signal_fulfilled, campaign_launched, campaign_completed` | Declared now; event bus deferred to Year 2 |
| `CostUnitEnum` | `minutes, staff_minutes, index` | |

---

## Schema Dependencies and Load Order

The Django engine loads schemas in dependency order at startup. The load sequence matters because later schemas reference earlier ones.

```
1. enums.yaml                   ← no dependencies
2. entities/organisation.yaml   ← enums only
3. entities/actor.yaml          ← organisation, enums
4. entities/storage_location.yaml ← organisation, enums
5. entities/donation_source.yaml  ← organisation, enums
6. entities/donation_collection.yaml ← organisation, donation_source, enums
7. entities/donation_item.yaml    ← organisation, storage_location, donation_source, donation_collection, enums
20. entities/demand_signal.yaml    ← organisation, enums
20. entities/campaign.yaml         ← organisation, demand_signal, enums
20. states/*.yaml                  ← enums only
20. process/step_type.yaml        ← enums
20. process/process_template.yaml ← step_type, enums
20. ui/fragment_binding.yaml      ← step_type, enums
20. value/step_cost.yaml          ← step_type, organisation, enums
20. value/weight_vector.yaml      ← organisation, enums
20. value/value_dimension.yaml    ← enums (stub)
20. provenance.yaml               ← all entities, process schemas
20. src/inkind/schema/categories/*.yaml  ← enums, src/inkind/schema/categories/_base.yaml
20. instances/workflows/*.yaml    ← process/process_template.yaml
20. instances/orgs/*.yaml         ← all schemas
```

---

## CI Pipeline

`linkml-validate` runs against all schema and instance files on every commit. The CI pipeline also:

1. Runs `gen-pydantic` to produce `generated/pydantic/` — validates that all schemas compile to valid Pydantic v2 models
2. Runs `gen-json-schema` to produce `generated/json-schema/` — validates that all category schemas compile to valid JSON Schema
3. Validates all instance YAML against their schema classes — catches misconfigured org instances before they reach Django
4. Runs scenario instances through the engine in a headless test mode — validates that the inference engine resolves the expected fragments and returns the expected costs

---

## Meta-level Summary

| Level | What it contains | Where | Changed by | Deployment? |
|---|---|---|---|---|
| **L1 — Schema** | Class/slot definitions, enum declarations | `src/inkind/schema/` | Architect via PR | Yes |
| **L2a — Base config** | Category schemas, step type catalogue, workflow templates, fragment bindings | `src/inkind/schema/categories/`, `instances/workflows/` | Domain expert via PR + reload | No (reload) |
| **L2b — Shared rules** | UC constraints (in category schemas), lifecycle transitions | `src/inkind/schema/categories/*.yaml`, `src/inkind/schema/states/*.yaml` | Domain expert / architect via PR + reload | No (reload) |
| **L3 — Org config** | Step costs, process selections, PC constraints, weight vectors | `instances/orgs/` (source) → Django DB (runtime) | Org admin via UI | No (DB write) |
| **Runtime state** | Item states, collection states, episode records, provenance | Django PostgreSQL DB | System at runtime | Never |

**Dynamic warehouse note:** `stock` collections (Phase 2+) bridge Level 3 org config and runtime state — they are org-configured entities (the org defines which stock collections exist) but their `total_item_count` is runtime-derived. This is the same pattern as `DemandSignal.quantity_fulfilled` — configured shape, runtime-populated value.
