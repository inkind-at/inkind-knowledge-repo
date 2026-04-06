# Schema Change Notes: Process Template & Fragment Binding Redesign
# inkind-knowledge-repo — Working Reference
# Status: Design decision record + summary of changes
# Date: April 2026

---

## Overview

This document records the reasoning and structural changes to `process_template.yaml`,
`fragment_binding.yaml`, and the new `org_capabilities.yaml` instance pattern.
It should be read as an amendment to the `inkind_linkml_schema_summary.md` sections
covering Group 3 (Process) and Group 4 (UI).

---

## 1. What Changed and Why

### 1.1 The path-as-optimisation-variable constraint

The formal specification (§5.1) is unambiguous: path `p` is the co-variable in
`net-value(i, b, p) = Σ ω_s(λ) · v_λ(i, b, p) − C_s(p)`. For this to be computable
the engine must know, **before episode launch**, both `C_s(p)` and which observations
the path will produce. These determine the upper bound on achievable reward.

The previous "master template + sub-workflow injection" design violated this: the
condition assessment step — and therefore the observation profile — was not known
until the `assign_category` step completed mid-episode. The engine could not evaluate
net-value across candidate paths before launch.

**Fix:** each `ProcessTemplate` is now a complete, independently-evaluable path.
The category-specific assessment step is part of the template definition, not injected
at runtime.

### 1.2 Technology preconditions as first-class schema

The previous design had no explicit representation of which paths require which
technology. An org without ML would have launched an ml_assisted episode and failed
at the `ml_recognition` step — a runtime error rather than a feasibility decision.

**Fix:** `capability_requirements: CapabilityRequirement[]` on each template.
Hard requirements (`is_required: true`) exclude the template from the candidate set
before net-value evaluation. The engine checks `OrgCapabilityRecord` entries at
`available_processes()` time, not at step execution time.

### 1.3 Category affinity as expected-value prior

The previous design had no representation of the fact that barcode scanning is
valuable for food and books but wasteful for clothing and furniture. Org admins
had to know this implicitly.

**Fix:** `category_affinity: CategoryAffinityEntry[]` on each template. Each entry
carries an `affinity` enum (preferred / neutral / discouraged) and a `rationale`
string documenting why. The engine uses affinity as a tie-breaker when multiple
feasible paths have similar cost; the admin UI surfaces affinity as guidance.

---

## 2. Updated Schema: process_template.yaml

### New slots on ProcessTemplate

| Slot | Type | Purpose |
|---|---|---|
| `process_path_type` | `ProcessPathTypeEnum` | Technique classification (replaces `process_type`) |
| `capability_requirements` | `CapabilityRequirement[]` | Technology preconditions; hard = feasibility gate |
| `category_affinity` | `CategoryAffinityEntry[]` | Per-category expected-value hints |
| `completeness_tier` | `CompletenessTierEnum` | Observation level produced; gates v_λ scoring |
| `estimated_duration_minutes` | `float` | Sum of step default_cost; shown at episode launch |
| `variant_of` | `string` (template ID ref) | Admin UI grouping only; no engine semantics |

### New classes

**`CapabilityRequirement`**
```yaml
attributes:
  capability: OrgCapabilityEnum   # what must be present
  is_required: boolean            # true = hard gate; false = soft preference
```

**`CategoryAffinityEntry`**
```yaml
attributes:
  category: string               # matches category schema name
  affinity: CategoryAffinityEnum  # preferred | neutral | discouraged
  rationale: string              # human-readable explanation
```

**`OrgCapabilityRecord`** (new — lives in instances/orgs/capabilities/)
```yaml
attributes:
  org_id: string
  capability: OrgCapabilityEnum
  is_active: boolean
  config: string                 # JSON blob with capability-specific params
```

### New enums

**`ProcessPathTypeEnum`** (replaces `ProcessTypeEnum`)
```
manual_assessment | ml_assisted | barcode_first | rapid_triage |
demand_signal_standard | demand_signal_urgent
```

**`OrgCapabilityEnum`**
```
ml_model_trained | barcode_scanner | audio_capture |
photo_enabled | trained_staff | data_wipe_station
```

**`CategoryAffinityEnum`**: `preferred | neutral | discouraged`

**`CompletenessTierEnum`**: `minimal | standard | detailed`

### Removed

- `ProcessTypeEnum` — replaced by `ProcessPathTypeEnum`
- The "tier 1 master / tier 2 sub-workflow" conceptual split — replaced by
  complete templates with `variant_of` for grouping
- Dynamic sub-workflow injection mechanism — the `sub_workflow_trigger` and
  `is_sub_workflow` slots are removed; each template is complete

### Template inventory (Phase 1)

| Template ID | Path type | Category | Caps required | Completeness | Default? |
|---|---|---|---|---|---|
| `sort_manual_clothing` | manual | clothing, accessories | none | standard | yes |
| `sort_manual_electronics` | manual | electronics | none | standard | yes |
| `sort_manual_food` | manual | food | none | standard | yes |
| `sort_manual_furniture` | manual | furniture | none | standard | yes |
| `sort_manual_books` | manual | books | none | standard | yes |
| `sort_manual_toys` | manual | toys | none | standard | yes |
| `sort_manual_mobility_aids` | manual | mobility_aids | none | standard | yes |
| `sort_ml_electronics` | ml_assisted | electronics | ml_model_trained, photo_enabled | detailed | no |
| `sort_ml_clothing` | ml_assisted | clothing | ml_model_trained, photo_enabled | detailed | no |
| `sort_barcode_food` | barcode_first | food | barcode_scanner | detailed | no |
| `sort_barcode_books` | barcode_first | books | barcode_scanner | detailed | no |
| `sort_rapid_triage` | rapid_triage | all | none | minimal | no |
| `register_demand_signal` | demand_signal_standard | — | none | standard | yes |
| `register_demand_signal_urgent` | demand_signal_urgent | — | none | minimal | no |

---

## 3. Updated Schema: fragment_binding.yaml

### New slot: `binding_process_path_type`

The resolution key gains a fifth dimension. Previously:
```
(step_type, category, actor_role, org_id) → fragment binding
```
Now:
```
(step_type, category, actor_role, process_path_type, org_id) → fragment binding
```

The new dimension is needed because `review_ml_result` appears in both `ml_assisted`
and `barcode_first` paths but requires different template text (ML suggestion language
vs. barcode lookup language). Null = matches any path type.

### New slot: `optional_fields`

Separates required from optional observation fields per fragment. Previously all
fields were in `required_fields`. The split enables:

- Completeness tier rendering: the fragment template hides optional fields when the
  parent template's `completeness_tier` is `minimal` or `standard`
- Progressive disclosure: optional fields shown collapsed by default in guided mode
- Server-side validation: POST handler validates required_fields as mandatory;
  optional_fields accepted if present but not enforced

### New slot: `completeness_tiers_served`

Declares which completeness tiers this fragment is designed to serve. The engine
selects the binding whose `completeness_tiers_served` includes the template's tier.
This avoids a combinatorial explosion of bindings per tier — one parameterised
template handles multiple tiers.

### Resolution order (updated)

```
1. (step_type, category, role, path_type, org_id)   — org override, most specific
2. (step_type, category, role, path_type, null)      — shared, path+category specific
3. (step_type, category, role, null,      null)      — shared, category specific
4. (step_type, null,     role, null,      null)      — role catch-all
5. (step_type, null,     null, null,      null)      — universal catch-all
```

### Fragment binding inventory summary

Bindings are structured in four groups:

**§A Universal steps** (all categories, all path types, per role): take_photo, take_audio_note,
assign_category, ml_recognition, barcode_scan, confirm_disposal, flag_for_specialist_review,
assign_storage → 2 bindings each (volunteer + staff) = 16 bindings

**§B Category-specific assessment** (per category, per role): assess_condition_clothing,
assess_condition_electronics, perform_data_wipe, assess_condition_food,
assess_condition_furniture, assess_condition_books, assess_condition_toys,
assess_condition_mobility_aids → 2 bindings each = 16 bindings

**§C Path-type-specific review** (review_ml_result, specialised per path_type, per role):
ml_assisted path × 2 roles + barcode_first path × 2 roles = 4 bindings

**§D Demand signal steps** (per role): set_category, set_signal_type, assess_need,
set_attributes, set_priority → 2 bindings each = 10 bindings

**Total: 46 shared fragment bindings** (Phase 1)

---

## 4. New: OrgCapabilityRecord Instances

### Location in repo

```
instances/orgs/capabilities/
  org_a_capabilities.yaml   — or combined in org_capabilities.yaml
  org_b_capabilities.yaml
  ...
```

### How the engine uses them

At startup, the engine builds a capability index:
```python
capability_index: dict[str, set[OrgCapabilityEnum]] = {
    "org-a": {photo_enabled, audio_capture, trained_staff},
    "org-b": {photo_enabled, barcode_scanner, trained_staff, data_wipe_station},
    "org-c": {photo_enabled, audio_capture, ml_model_trained, barcode_scanner,
              trained_staff, data_wipe_station},
}
```

At episode launch:
```python
def available_processes(entity_type, lifecycle_state, org_id) -> list[ProcessTemplate]:
    org_caps = capability_index[org_id]
    return [
        t for t in all_templates
        if t.entity_type == entity_type
        and lifecycle_state in t.launchable_from_states
        and all(
            not req.is_required or req.capability in org_caps
            for req in t.capability_requirements
        )
    ]
```

### Capability unlock effects (by org)

| Org | Active capabilities | Additional feasible paths vs. baseline |
|---|---|---|
| Org A (baseline) | photo_enabled, audio_capture, trained_staff | Manual paths only (all categories) |
| Org B | + barcode_scanner, data_wipe_station | + sort_barcode_food, sort_barcode_books; electronics redistribution enabled |
| Org C | + ml_model_trained (clothing + electronics) | + sort_ml_electronics, sort_ml_clothing |
| Org C (full) | all capabilities | All 11 sort paths feasible |

### Config JSON convention

The `config` field carries capability-specific parameters as a JSON string.
The engine deserialises it into a typed dataclass at startup. Key configs:

```python
# ml_model_trained
@dataclass
class MLModelConfig:
    endpoint_url: str
    model_version: str
    confidence_threshold: float          # e.g. 0.82
    categories_covered: list[str]         # only these categories get ML paths
    fallback_on_low_confidence: str       # "manual_assessment"
    timeout_seconds: int

# barcode_scanner
@dataclass
class BarcodeScannerConfig:
    scanner_type: str                     # "bluetooth" | "camera"
    gs1_enabled: bool
    open_food_facts_enabled: bool
    open_library_enabled: bool
    internal_registry_enabled: bool
    internal_registry_url: str | None
    lookup_timeout_seconds: int
    fallback_on_timeout: str              # "manual"
```

---

## 5. Django Model Implications

### New model: OrgCapability

```python
class OrgCapability(models.Model):
    org = models.ForeignKey(Enterprise, on_delete=models.CASCADE)
    capability = models.CharField(max_length=64, choices=OrgCapabilityEnum.choices)
    is_active = models.BooleanField(default=False)
    config = models.JSONField(null=True, blank=True)

    class Meta:
        unique_together = [("org", "capability")]
```

This is a Django model — not a knowledge repo instance. The knowledge repo
`OrgCapabilityRecord` class defines the *schema* for these records; the Django
model stores the runtime values. Org admins manage capabilities through the
standard Django admin interface.

### Updated: ProcessEpisode.step_sequence

The JSON snapshot stored at episode launch now includes `process_path_type` and
`capability_requirements` from the template. This ensures the episode's capability
context is preserved even if the org later changes its capability configuration.

```python
step_sequence = {
    "template_id": "sort_barcode_food",
    "process_path_type": "barcode_first",
    "completeness_tier": "detailed",
    "capabilities_at_launch": ["barcode_scanner", "photo_enabled"],
    "steps": [...],  # as before
}
```

### Updated: InferenceEngine.available_processes()

```python
def available_processes(
    self,
    entity_type: str,
    lifecycle_state: str,
    org_id: str,
) -> list[ProcessTemplate]:
    """
    Returns feasible templates for this entity type, state, and org.
    Filters out templates with unsatisfied hard capability requirements.
    Sorts remaining templates by:
      1. category_affinity (preferred > neutral > discouraged) for current item category
      2. completeness_tier (detailed > standard > minimal) — higher completeness
         is preferred when cost is similar, to maximise matchable v_λ dimensions
      3. estimated_duration_minutes ascending (lower cost preferred as tiebreaker)
    """
```

### Updated: InferenceEngine.resolve_fragment()

The resolution call gains `process_path_type` as an explicit parameter:

```python
def resolve_fragment(
    self,
    step_type: str,
    category: str | None,
    actor_role: str,
    process_path_type: str | None,
    org_id: str,
) -> UIFragmentBinding:
    """
    Resolves in specificity order:
    (step_type, category, role, path_type, org_id)
    (step_type, category, role, path_type, None)
    (step_type, category, role, None,      None)
    (step_type, None,     role, None,      None)
    (step_type, None,     None, None,      None)
    Raises FragmentNotFound if no binding matches.
    """
```

---

## 6. Open Questions for Phase 2

1. **ML model scope vs. capability**: The `ml_model_trained` capability is currently
   binary (present/absent). The `config.categories_covered` field partially addresses
   per-category ML scope but this is not enforced at the capability requirement level.
   Phase 2 should consider per-category ML capability flags
   (e.g., `ml_model_clothing`, `ml_model_electronics`) so the engine can admit
   `sort_ml_clothing` even when `sort_ml_electronics` is infeasible due to
   insufficient training data.

2. **Affinity as learnable prior**: Category affinity values are currently
   hardcoded in the schema. Phase 3 (provenance-weighted learning) should derive
   affinity from empirical net-value comparisons across orgs — replacing the
   schema-author's prior with observed outcome data.

3. **Soft capability degradation signals**: When a soft capability (audio_capture,
   photo_enabled) is absent, the engine silently skips the step. This is correct
   but produces no provenance signal. Phase 2 should record `capability_absent`
   as a step skip reason in the `ProvenanceRecord`, enabling analytics on how
   often soft capabilities degrade the observation completeness.

4. **`variant_of` for admin UI**: The `variant_of` slot is currently informational.
   Phase 2 should use it to group templates in the org admin UI into "path families"
   (e.g., "Manual assessment" group showing all 7 manual variants) rather than a
   flat list of 14 templates.
