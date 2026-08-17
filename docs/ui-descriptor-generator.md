# Implementation Guidelines: LinkML UI Descriptor Generator
## `gen-ui-descriptor` — inkind-knowledge-repo
 
**Status:** Implementation ready  
**Scope:** Phase 1 — sorting form UI, no process templates, no fragment bindings  
**Target audience:** AI agent implementing the generator
 
---
 
## 1. Purpose and Context
 
The UI descriptor generator (`gen-ui-descriptor`) is a custom LinkML `Generator` subclass that compiles the domain schema into a set of JSON files consumed by the Django sorting UI. It is a build-time artifact generator, not a runtime component.
 
The generator exists because the two other generated artifacts serve different purposes and different consumers. The JSON Schema files (`gen-json-schema`) serve `ajv` for POST validation in the browser and `jsonschema` for server-side validation in Django — they are validation contracts. The Pydantic models (`gen-pydantic`) serve the Python configuration loader — they are typed data containers. Neither artifact is shaped for the UX need: telling the browser which fields to render, in what order, under what conditions, with what value constraints, and with what inline feedback rules.
 
The UI descriptor fills this gap. It is compiled once from the YAML source, committed to `generated/ui-descriptors/`, loaded by Django at startup, and embedded in the sorting form page. The browser reads it as flat data — no schema machinery, no `$ref` resolution, no `allOf` traversal at runtime.
 
### Relationship to future process templates and fragment bindings
 
Phase 1 does not implement process templates or fragment bindings. The descriptor is designed so that when fragment bindings arrive they slot in cleanly. Each field in the descriptor carries a `required_in_step` flag set from the `completeness_minimal` annotation. A future fragment binding patch mechanism will override this flag per step context without regenerating the schema-derived content. The agent must not conflate the process layer (deferred) with the schema layer (implemented now).
 
---
 
## 2. Repository Placement and Registration
 
The generator lives inside the knowledge repo as a first-class generator alongside `gen-json-schema` and `gen-pydantic`. It is not a script or a post-processor.
 
**File location:** `src/inkind/generators/ui_descriptor.py`
 
**Package registration:** Register as a CLI entry point in `pyproject.toml` under `[project.entry-points."linkml.generators"]` so it is invocable as `gen-ui-descriptor` from the command line, exactly as `gen-json-schema` is invoked.
 
**Invocation pattern:**
```
gen-ui-descriptor src/inkind/schema/donation_item.yaml --output-dir generated/ui-descriptors/
```
 
The entry point schema is `donation_item.yaml` because it is the root schema that imports all category schemas and defines all concrete subclasses. The generator traverses the full imported schema graph via `SchemaView`.
 
**Output location:** `generated/ui-descriptors/` — committed alongside `generated/json-schema/` and `generated/pydantic/`. Django reads from the path specified by the `INKIND_SCHEMA_DIR` environment variable.
 
**Makefile target:** Add alongside the other generator targets. The target depends on `donation_item.yaml` and all `categories/*.yaml` files so that changes to any category schema trigger regeneration.
 
---
 
## 3. Output File Set
 
The generator produces exactly two types of output file:
 
**One base descriptor:** `DonationItem.ui.json`  
Contains only the fields declared directly on `DonationItem` that are universal across all item types. The `category` field in this file carries `dispatches_to` — the map from each category value to its subclass descriptor filename. This file drives the phase 1 UI before any category is selected.
 
**One subclass descriptor per concrete item class:** `ClothingItem.ui.json`, `FurnitureItem.ui.json`, `BabyInfantItem.ui.json`, and so on for all 16 concrete subclasses.  
Each file contains the complete field set for that item type, in slot declaration order, with all rendering metadata attached to each field entry.
 
No other output files. The generator does not produce per-category-mixin files, per-rule files, or any intermediate artifacts.
 
---
 
## 4. Source Schema Structure the Generator Must Understand
 
Before implementing, the agent must understand how the schema is organised, because the generator reads across multiple layers simultaneously.
 
### 4.1 The class hierarchy
 
`DonationItem` is declared `abstract: true` in `donation_item.yaml`. It is never instantiated. All 16 concrete subclasses use `is_a: DonationItem`. Most also carry one category mixin via `mixins: [ClothingCategory]`, `mixins: [FurnitureCategory]`, etc. `OtherItem` has no mixin. `FoodItem` is the only subclass whose mixin (`FoodCategory`) does not extend `CategoryMixin`.
 
A concrete subclass is identified by: not abstract, not a mixin, `is_a` ancestor chain includes `DonationItem`, and the class name is not `DonationItem` itself.
 
### 4.2 The `designates_type` slot
 
The `category` slot on `DonationItem` carries `designates_type: true`. This is the semantic marker that makes `category` a type-dispatch field rather than a plain attribute. The generator detects this marker and uses it to build `dispatches_to` in the base descriptor. This is the only annotation the generator relies on for dispatch — no other conventions or annotations are needed.
 
Because of the LinkML limitation that `designates_type` requires the range to be a string referencing a class URI (not an enum), the `category` slot in the actual YAML uses a string range with `designates_type: true`, and the permissible subclass names are listed as the allowed values. The agent must read the slot's permissible values or range restrictions to build the dispatch map — the exact mechanism depends on how the schema is expressed. Verify by inspecting the actual `donation_item.yaml` before implementing this step.
 
### 4.3 Where slots come from
 
When a concrete class like `ClothingItem` is induced by `SchemaView.induced_class()`, the result merges slots from three sources: the base `DonationItem` slots, the mixin's slots (`ClothingCategory`), and any slot_usage overrides. The generator uses the induced class to get the complete, merged slot set. It does not manually union slots from multiple classes.
 
### 4.4 Where rules come from
 
Rules are **not** carried through `induced_class()`. The generator must collect rules separately from two sources and combine them:
 
- **`lc-*` rules** live on the concrete subclass definition in `donation_item.yaml`. They reference `lifecycle_state`, which is a `DonationItem` slot — category mixins cannot see it, so these rules cannot live in the mixin.
- **`vm-*` and `uc-*` rules** live on the category mixin definition in the corresponding `categories/*.yaml` file.
To collect all rules for a given concrete class, the generator walks the class's ancestor list (via `SchemaView.class_ancestors()`), collects rules from each ancestor that is a mixin, and adds the rules from the concrete class itself. The rule title prefix (`lc-`, `vm-`, `uc-`) is the dispatch signal for which output section the rule populates.
 
### 4.5 Where completeness annotations come from
 
The `completeness_minimal`, `completeness_standard`, and `completeness_detailed` annotations live on the **mixin class** definition — for example on `ClothingCategory` in `clothing.yaml`, not on `ClothingItem` in `donation_item.yaml`. Each annotation value is a comma-separated string of slot names belonging to that tier.
 
The generator walks the ancestor list of the concrete class, finds the mixin ancestor, reads its annotations, and parses the comma-separated slot name lists. The base `DonationItem` slots do not have completeness annotations — they are universally required operational fields and are handled separately.
 
---
 
## 5. Field Ordering
 
Field display order in the generated descriptor must match slot declaration order in the YAML source. `SchemaView.induced_class()` returns attributes in declaration order as of current LinkML versions — the generator relies on this. If the order is incorrect in testing, fall back to walking the concrete class's own slots first, then the mixin's slots in declaration order.
 
The `fields` key in the descriptor is a JSON **array**, not an object, to preserve and communicate this order. Field lookup by name in the browser must iterate the array, not rely on key access.
 
The base `DonationItem` slots appear first in the base descriptor in the order they are declared on `DonationItem`. The category-specific slots appear in the subclass descriptor in the order they are declared in the mixin.
 
---
 
## 6. Internal Slots to Exclude
 
The following slots are managed by the system, not entered by the sorter, and must be excluded from all descriptors:
 
- `id` — system-generated UUID
- `created_at` — set at creation
- `updated_at` — set on save
- `attribute_completeness` — set by the fragment engine at sorting completion
- `storage_unit` — set at the stored lifecycle transition, not during sorting
- `lifecycle_state` — managed by the engine; not a sorter input
`lifecycle_state` deserves special attention: it appears in `visible_when` and `rules` conditions throughout the descriptor, but it is never itself a rendered field. The generator uses it as a condition variable only.
 
---
 
## 7. Base Descriptor: `DonationItem.ui.json`
 
### 7.1 Fields included
 
Include only slots declared directly on `DonationItem` that are not in the exclusion list above. At minimum this covers: `category`, `usage`, `source_collection`, `donation_source`, `sorting_notes`, `material` (where applicable). Verify against the actual `donation_item.yaml`.
 
### 7.2 The `dispatches_to` map on the `category` field
 
When the generator encounters a slot with `designates_type: true`, it builds `dispatches_to` as a dict mapping each permissible value to the filename of the corresponding subclass descriptor. The filename convention is `<ClassName>.ui.json`. The mapping covers every permissible value — all 16 item class names.
 
The `dispatches_to` key is added to the field entry alongside all other field properties. It is not a separate top-level structure.
 
### 7.3 Field structure for base fields
 
Base fields have no `visible_when` condition — they are rendered unconditionally. Each base field entry carries: `name`, `type`, and where applicable `enum` (the enum name, not the values inline) and `required_in_step: true`. For the `category` field, additionally `dispatches_to`. No `completeness` key is emitted for base fields — they are universal operational fields, not tiered by completeness.
 
---
 
## 8. Subclass Descriptors: `<ClassName>.ui.json`
 
### 8.1 Top-level structure
 
Each subclass descriptor is a JSON object with four top-level keys: `class` (the class name string), `fields` (ordered array), `enums` (dict of enum name to values array), and `rules` (array of rule objects).
 
### 8.2 Field entry structure
 
Each entry in the `fields` array is a JSON object with the following keys. All keys are optional except `name` and `type`.
 
**`name`** — the slot name as declared in the YAML. Required.
 
**`type`** — one of: `enum`, `boolean`, `string`, `integer`, `date`. Derived from the slot's `range` declaration. If the range is a declared enum, type is `enum`. If the range is `boolean`, type is `boolean`. If the range is `string` or free text, type is `string`. If the range is `integer`, type is `integer`. If the range is `date` or `datetime`, type is `date`. Required.
 
**`enum`** — the enum name as a string, present only when `type` is `enum`. The enum's values are emitted separately in the top-level `enums` dict. The field entry references by name, not by embedding values inline.
 
**`multivalued`** — boolean, present and `true` only when the slot is declared `multivalued: true` in the YAML. Omit when false.
 
**`completeness`** — one of `minimal`, `standard`, `detailed`. Derived from the mixin's completeness tier annotations. Omit if the slot does not appear in any completeness annotation (this applies to base slots and to any slot not yet annotated). A field with no `visible_when` and no `completeness` is always rendered unconditionally — the generator should emit a warning for any such field, as the schema is underdocumented for that slot.
 
**`visible_when`** — a dict where each key is a field name and each value is a list of permitted values for that field. All conditions in the dict are AND — all must hold simultaneously for the field to be visible. Derived from `lc-*` rules (see section 9.1). Present only on conditionally visible fields. A field with no `visible_when` key is rendered unconditionally within its completeness tier.
 
**`options_depend_on`** — present only on enum fields whose valid option set depends on another field's current value. Derived from `vm-*` rules where the target field is an enum (see section 9.2). The value is a dict with exactly one key: the controlling field name. That key's value is a dict mapping each controlling field value to the list of permitted options for the target field.
 
**`auto_set_from`** — present only on boolean or scalar fields that are auto-derived from another field's value. Derived from `vm-*` rules where the target field is boolean or scalar (see section 9.2). The value is a dict with exactly one key: the controlling field name. That key's value is a dict mapping each controlling value to the derived scalar value.
 
**`required_in_step`** — boolean. `true` if the slot appears in the mixin's `completeness_minimal` annotation, `false` otherwise. This is the seam for future fragment binding overrides. Always present.
 
### 8.3 Enum collection
 
The top-level `enums` dict collects all enums referenced by fields in this descriptor. Each entry maps the enum name to the list of permissible value names in declaration order. Only enums actually referenced by a field in this descriptor are included — do not include the full global enum registry. Enum values are strings (the permissible value names), not the full LinkML `PermissibleValue` objects.
 
---
 
## 9. Rule Processing by Prefix
 
### 9.1 `lc-*` rules → `visible_when` on fields
 
Lifecycle-aware rules encode when a field becomes required relative to `lifecycle_state`. For the UI descriptor, this translates to field visibility: a field that is required at `sorted` state should be visible when `lifecycle_state` is `sorting_in_progress` (the state during which the sorter fills in the form).
 
**Important:** The precondition in `lc-*` rules references `lifecycle_state: sorted` — the state at which the field is validated as present. But the UI must show the field *before* that state, during `sorting_in_progress`. The generator therefore maps `lifecycle_state: sorted` in the precondition to `lifecycle_state: sorting_in_progress` in the `visible_when` output. This is the correct translation: show the field during active sorting so it can be filled before the transition to `sorted` is made.
 
**Processing steps:**
1. Read `preconditions.slot_conditions` to extract the triggering conditions.
2. Translate `lifecycle_state: sorted` to `lifecycle_state: sorting_in_progress` in the `visible_when` output.
3. Preserve any other slot conditions in the precondition as additional AND conditions in `visible_when`.
4. Read `postconditions.slot_conditions` to find which fields have `required: true`.
5. For each such field (excluding internal slots), add or merge the `visible_when` condition onto the field entry.
When multiple `lc-*` rules add `visible_when` conditions to the same field, merge them. If all rules have identical conditions, the result is one `visible_when` entry. If rules have different conditions (e.g. one adds a subcategory constraint), the result is the intersection — the field is visible only when all conditions hold simultaneously.
 
### 9.2 `vm-*` rules → `options_depend_on` or `auto_set_from` on the target field
 
Value-map rules encode dependent relationships between fields. The rule's precondition specifies the source field and its triggering values; the postcondition specifies the target field and its permitted values.
 
**Processing steps:**
1. Extract the source field name and its triggering values from `preconditions.slot_conditions`. Each vm-* rule has exactly one source field in the precondition.
2. Extract the target field name and its constrained values from `postconditions.slot_conditions`. Each vm-* rule has exactly one target field in the postcondition.
3. Determine the type of the target field by checking its `range` in the induced class:
   - If the target field's range is a declared enum → emit `options_depend_on` on the target field.
   - If the target field's range is `boolean` or a scalar → emit `auto_set_from` on the target field.
4. For `options_depend_on`: the source field becomes the key in the dict. Each triggering source value maps to the list of permitted target values from the postcondition. Multiple `vm-*` rules with the same source field and target field are merged into a single `options_depend_on` entry (one source value per rule, all accumulated under the same controlling field key).
5. For `auto_set_from`: same structure but the mapped value is a single scalar (e.g. `true` or `false`) rather than a list.
**Important for auto_set_from:** The postcondition in `vm-season-winter` specifies `is_winter_suitable: equals_string: "true"`. The generator must cast this to the appropriate JSON type — `"true"` as a string must become the boolean `true` in the output when the target field's range is `boolean`.
 
### 9.3 `uc-*` rules → `rules` array entries
 
Universal constraint rules encode combinations that should be blocked or flagged. These appear in the top-level `rules` array of the subclass descriptor.
 
**Processing steps:**
1. Read `preconditions.slot_conditions` to extract the triggering conditions. Each condition entry maps a field name to a list of triggering values.
2. Build the `when` dict: field name → list of values that trigger the rule.
3. Determine `severity` from the rule's description or annotations. If the description contains the word "block" or "must not", use `"block"`. If it contains "warn" or "should not", use `"warn"`. Default to `"block"` when uncertain.
4. Extract the user-facing `message` from the rule's `description`. Use the first sentence or the content after any prefix like "action: block, suggest: disposal.".
5. Use the rule's `title` as the `id`.
The `rules` array contains **all** uc-* rules that apply to this item class. Rules from the mixin (`uc-*` in `clothing.yaml`) and any uc-like rules on the concrete class are both included. The `vm-*` underwear-no-unisex rule (which functions as a UC constraint blocking unisex demographic for underwear) should be treated as a rule entry if it encodes a blocking combination, not just a value filter — inspect the actual rule postcondition to determine whether it belongs in `options_depend_on` or in `rules`.
 
---
 
## 10. Special Cases
 
### 10.1 `OtherItem`
 
`OtherItem` has no category mixin. Its completeness annotations do not exist. It has only two category-specific fields: `item_description` (required at sorted) and `condition_grade`. The generator handles it by reading only the concrete class's own rules and slots, skipping the mixin ancestor walk.
 
### 10.2 `FoodItem`
 
`FoodItem` uses `FoodCategory`, which does not extend `CategoryMixin`. It has no `condition_grade` and no `assessment_result`. Its field set is entirely distinct: `food_type`, `packaging_intact`, `storage_requirement`, `expiry_date`, `quantity`. The `vm-*` rules encode the `food_type → storage_requirement` value map. Process these identically to the clothing `vm-*` rules via `options_depend_on`.
 
### 10.3 `BabyInfantItem` three-track assessment
 
`BabyInfantItem` uses three distinct assessment tracks driven by `subcategory`:
- Safety-critical equipment subcategories → `assessment_result` (BabyEquipmentAssessmentEnum)
- Consumable subcategories → `is_sealed` + `expiry_date`
- General gear subcategories → `condition_grade`
The three fields (`assessment_result`, `is_sealed`, `condition_grade`) each have `visible_when` conditions on `subcategory` with different value lists. These conditions come from `lc-*` rules on `BabyInfantItem`. The generator produces three separate field entries, each conditionally visible, with non-overlapping subcategory value lists. This is the correct output — no special casing needed beyond the standard `lc-*` rule processing.
 
### 10.4 `SportsItem` dual-track assessment
 
`SportsItem` has `assessment_result` for `protective_gear` subcategory and `condition_grade` for all other subcategories. These two fields are mutually exclusive — when one is visible the other is not. Both get `visible_when` conditions derived from `lc-*` rules. The `condition_grade` rule uses a `not: const: protective_gear` pattern in the precondition. The generator must handle this negation and produce a `visible_when` condition listing all subcategory values *except* `protective_gear`. To build this list, the generator reads the full `SportsSubcategoryEnum` permissible values and subtracts the excluded value.
 
### 10.5 Multivalued fields
 
The `season` slot on `ClothingItem` and `FootwearItem` is `multivalued: true`. The field entry carries `"multivalued": true`. The browser renders this as a multi-select or checkbox group. No other changes to the field entry structure are needed.
 
---
 
## 11. Verification Checklist
 
Before the generator is considered complete, verify the following against the actual schema files:
 
**Structure verification:**
- `DonationItem.ui.json` contains only base slots, no category-specific slots from any mixin.
- The `category` field in `DonationItem.ui.json` has `dispatches_to` with exactly 16 entries, one per concrete subclass.
- Each concrete class produces exactly one `.ui.json` file.
- No abstract class, no mixin class, and no `DonationItem` base class produces a subclass descriptor file.
**Field ordering verification:**
- Fields in `ClothingItem.ui.json` appear in the same order as slots are declared in `clothing.yaml` (for mixin slots) and `donation_item.yaml` (for base slots that appear first).
**Visibility verification:**
- `demographic` in `ClothingItem.ui.json` has `visible_when: { "lifecycle_state": ["sorting_in_progress"] }`.
- `is_winter_suitable` in `ClothingItem.ui.json` has `visible_when` with both `lifecycle_state` and `subcategory` conditions.
- `assessment_result` in `FurnitureItem.ui.json` has `visible_when: { "lifecycle_state": ["sorting_in_progress"] }` (required at sorted → visible during sorting_in_progress).
**Value map verification:**
- `size` in `ClothingItem.ui.json` has `options_depend_on` with key `"demographic"` mapping all five demographic values to their respective size lists.
- `is_winter_suitable` in `ClothingItem.ui.json` has `auto_set_from` with key `"season"` mapping `"winter"` to `true`, `"summer"` to `false`, `"all_season"` to `true`. `"spring_autumn"` is absent (no auto-derivation for this value).
**Rules verification:**
- `ClothingItem.ui.json` contains at least two uc-* rule entries: the underwear condition block and the adult underwear usage block.
- Each rule entry has `id`, `message`, `severity`, and `when`.
**Enum verification:**
- The `enums` dict in `ClothingItem.ui.json` contains only the enums referenced by fields in that descriptor, not the full global enum set.
- `ClothingSizeEnum` values are present in declaration order.
**Exclusion verification:**
- `id`, `created_at`, `updated_at`, `attribute_completeness`, `storage_unit`, and `lifecycle_state` do not appear in any `fields` array.
- `lifecycle_state` does appear correctly as a condition value in `visible_when` dicts.
---
 
## 12. Django Integration (for reference, not implemented by the generator)
 
The generator produces files. Django consumes them. The integration is straightforward:
 
The `SchemaRegistry` class in `inkind/schema_registry.py` loads all `*.ui.json` files from `INKIND_SCHEMA_DIR/ui-descriptors/` at application startup via `AppConfig.ready()`. It stores them in a dict keyed by class name. The sort form view retrieves all descriptors and embeds them as a single JSON blob in the page context. No reload mechanism in Phase 1 — restart the process when schemas change.
 
The browser receives one JSON object containing all descriptors keyed by class name. The `SortingForm` JavaScript class reads `DonationItem` from this object to drive phase 1, then reads the selected category's descriptor to drive phase 2. The `fields` array drives render order. The `dispatches_to` map on the `category` field drives the phase 1 → phase 2 transition.
 
---
 
## 13. What the Generator Must Not Do
 
The agent implementing this generator must not:
 
- Parse rule descriptions as strings to extract semantic content — use the structured `preconditions` and `postconditions` objects.
- Hard-code any category names, field names, enum values, or rule titles — all content must be read from the schema.
- Embed enum values inline in field entries — enum values belong in the top-level `enums` dict, referenced by name from field entries.
- Include `lifecycle_state` as a rendered field in any `fields` array.
- Conflate `visible_when` (field presence) with `options_depend_on` (value filtering) — these are distinct mechanisms for distinct problems.
- Generate any output for abstract classes, mixin classes, or the `DonationItem` base class as a subclass descriptor.
- Use `lifecycle_state: sorted` verbatim in `visible_when` — always translate to `sorting_in_progress` as described in section 9.1.
- Emit an `always_visible` key — this key does not exist in the descriptor format. The absence of `visible_when` already implies unconditional rendering within the field's completeness tier. Adding a redundant flag creates false symmetry with `visible_when` and misleads the browser implementation.
- Implement any Django, JavaScript, or browser-side code — the generator's responsibility ends at writing `.ui.json` files.
 