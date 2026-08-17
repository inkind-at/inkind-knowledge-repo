# Category Descriptor Sync — LinkML Source-Model Design

## Overview

Four descriptor files feed the `inkind-enterprise` categories wizard engine:
`DonationItem.ui.json` (generated from a LinkML schema in a separate knowledge repo) and
`SortedCollection.ui.json`/`StorageCollection.ui.json`/`DemandSignal.ui.json` (hand-curated inside
`inkind-enterprise` today). The three hand-curated files each duplicate all 16 category class blocks
(fields, enums, `uc-*` validation rules) that already live once in the LinkML source, with small,
mostly-uniform-per-root deltas (a `usage`-required flip; `DemandSignal` additionally drops
assessment-related content and has no rules). Every knowledge-repo regeneration has to be manually
re-applied to three more files by hand or it silently drifts — confirmed already drifted in one place
(`DemandSignal`'s `PersonalCareSubcategoryEnum` merges two values that stay separate everywhere else).

**Goal:** model the sharing once, upstream, in LinkML, so the generator emits all four descriptor
files correctly synced and `inkind-enterprise` goes back to purely consuming generated artifacts for
all four files, the way it already does for `DonationItem.ui.json` today.

## Existing LinkML structure (confirmed against the real schema)

- One mixin per category (`ClothingCategory`, `FoodCategory`, etc.) — today these hold both the
  category's descriptive slots (`subcategory`, `material`, `demographic`, `size`, ...) *and* its
  `uc-*`/`vm-*` rules together.
- One concrete subclass per category, used by `DonationItem`'s `designates_type` dispatch —
  `ClothingItem: is_a: DonationItem, mixins: [ClothingCategory]`, etc. These hold `lc-*` rules
  directly (rules that reference `lifecycle_state`, a `DonationItem`-only slot mixins can't see).
- `uc-*`/`vm-*` rules already come from LinkML's native `rules:` construct (confirmed) — not
  generator-side post-processing.
- `SortedCollectionEntry`/`StorageCollectionEntry`/`DemandSignal` don't exist as LinkML classes yet —
  that's the entire reason those three descriptor files are hand-authored in `inkind-enterprise` today.
- The `category` slot uses a **string range with `designates_type: true` and a permissible-values
  list**, not an enum range — a LinkML constraint, not a schema author's choice. Any new root's
  dispatch slot needs the same shape.

## Design decision: new roots dispatch straight to the category mixins — no parallel subclass trees

`SortedCollectionEntry`, `StorageCollectionEntry`, and `DemandSignal` do **not** get their own
`SortedClothingItem`/`StorageClothingItem`/`DemandClothingItem`-style subclass trees. Their
`designates_type` dispatch slot points **directly at the category mixins** (or a mixin variant, see
below) instead. This is a deliberate trade — not the cleanest possible modeling (a mixin becoming a
type-dispatch target isn't the textbook `designates_type` use), but it avoids ~48 near-empty subclasses
(16 categories × 3 new roots) for close to zero functional loss, once rules are reorganized as below.

`DonationItem`'s existing structure (`ClothingItem is_a DonationItem, mixins: [ClothingCategory]`)
**stays as it is** — this design only changes what the three new/newly-modeled roots do, not
`DonationItem` itself, beyond moving where its rules live (see Class 3 below).

## Rule and slot reorganization: three tiers

The core problem this solves: rules and slots that are fine to share broadly (across roots and
categories) need to be separated from ones that are either root-slot-dependent (need `lifecycle_state`/
`usage`, which only `DonationItem`-family roots have) or semantically physical-item-only (assessment
content `DemandSignal` shouldn't carry). Three tiers, not two, because two different LinkML
constraints force two different splits (see the worked example in "Why three tiers, not two" below).

### Tier 1 — category base mixin (existing mixin, trimmed)

Stays as `ClothingCategory`, `FurnitureCategory`, etc. Holds: the category's intrinsic descriptive
slots (`subcategory`, `material`, `demographic`, `size`, `season`, `intact_labels`,
`is_winter_suitable`, and — see below — `condition_grade` on the categories that have it today), plus
`vm-*`-style rules that are genuinely context-independent: `demographic` → `size` options,
`season` → `is_winter_suitable` auto-derivation, `food_type` → `storage_requirement`. These make sense
whether you're describing an actual physical item or a future need, so they're safe to share with
`DemandSignal` too.

**`DemandSignal` dispatches directly to this tier, unmodified, for every category.**

**`condition_grade` stays exactly where it is today — per-category, only on the ~9-10 categories that
currently have it** (`ClothingItem`, `AccessoriesItem`, `FootwearItem`, `HouseholdItem`, `ToysItem`,
`BooksItem`, `StationeryItem`, and the general-equipment branch of `SportsItem`). Don't hoist it to a
universal/root-level slot — it doesn't apply to `FoodItem` at all, and would be redundant alongside the
six categories that already use the more specific `assessment_result` instead (see Tier 2). LinkML
slots are defined once regardless of which classes reference them, so keeping `condition_grade`
per-category costs nothing extra — there's no real duplication being traded away by *not* making it
universal. `SportsItem` is the one deliberate exception with both `condition_grade` (general equipment)
and `assessment_result` (`protective_gear` only) coexisting, gated by `subcategory` — preserve that,
don't treat it as evidence for universalizing `condition_grade`.

### Tier 2 — category-and-context mixins (new, only for the ~6 categories with a category-specific assessment enum)

`assessment_result` isn't one reusable slot — it's six different enum ranges depending on category
(`FurnitureAssessmentEnum`, `BeddingAssessmentEnum`, `ElectronicsAssessmentEnum`,
`SportsProtectiveAssessmentEnum`, `MobilityAssessmentEnum`, `BabyEquipmentAssessmentEnum`). A single
shared mixin can't hold a `slot_usage` override for six different ranges of the same slot name
simultaneously, so this tier has to stay per-category — but only for the six categories that actually
need it: `FurnitureItem`, `BeddingTextilesItem`, `ElectronicsItem`, `SportsItem` (its `protective_gear`
branch), `MobilityAidsItem`, `BabyInfantItem`. Something like `FurnitureAssessmentMixin: mixins:
[FurnitureCategory], slots: [assessment_result], rules: [uc-furniture-compromised-block, ...]` — Tier 1
plus the category's own assessment slot and whichever of its rules don't need root-only slots.

`DonationItem`, `SortedCollectionEntry`, `StorageCollectionEntry` dispatch to this tier (not bare
Tier 1) for these six categories. `DemandSignal` dispatches to bare Tier 1 for them, same as everywhere
else — it never sees `assessment_result` at all.

### Tier 3 — universal context-only rules mixin (new, mixed onto the root classes, not per-category)

Everything that's root-slot-dependent (`lc-*` rules, needing `lifecycle_state`; `uc-*` rules
referencing `usage`, e.g. `uc-underwear-adult-used-block`) plus the `condition_grade`-referencing
validation rules (`uc-poor-condition-block`, `uc-underwear-condition-block`) collects into one shared
mixin — call it `PhysicalItemContextRulesMixin` — mixed onto `DonationItem`, `SortedCollectionEntry`,
and `StorageCollectionEntry` **as whole root classes**, not per category. This is safe to bundle across
every category's rules in one place: a rule referencing `subcategory: underwear` simply never fires
against `FurnitureItem` data, so there's no cross-category collision the way there would be for a slot
range. `DemandSignal` doesn't mix this in at all — that's what makes its rule-free state a direct
consequence of the class structure, not something requiring per-rule exclusion logic.

`usage`'s required-flip (`false` on `DonationItem`, `true` on `SortedCollectionEntry`/
`StorageCollectionEntry`) is unrelated to this rules-sharing mechanism — it's a plain `slot_usage`
override declared directly on each root class, since `usage` is root-owned already.

### Why three tiers, not two

Two different LinkML constraints are at play, and they force the split in different places:
- Tier 1 vs. {Tier 2, Tier 3}: whether `DemandSignal` should see the content at all (semantic — does
  it make sense without a physical item in hand).
- Tier 2 vs. Tier 3: whether the content can be expressed as *one* shared definition across categories
  (Tier 3 can, since rules don't collide) or must stay per-category (Tier 2 must, since
  `assessment_result`'s range genuinely varies by category and a single mixin can't hold six
  conflicting `slot_usage` overrides for the same slot name).

## Generator changes required

1. **New root-rule-folding logic**, specifically for `SortedCollectionEntry`/`StorageCollectionEntry`
   (and `DonationItem`, if migrated to the same uniform mechanism — see point 3): when generating the
   descriptor for a category reached via a root's `designates_type` dispatch, collect rules from
   *both* (a) the dispatched-to mixin's own ancestor chain (existing mechanism, unchanged — walks
   mixin ancestors + the class's own rules) *and* (b) the dispatching root's own directly-mixed-in
   rules (Tier 3, `PhysicalItemContextRulesMixin`). This is genuinely new — the original generator
   only ever walked ancestry within one class's own chain; this adds a second, root-to-dispatch-target
   path that doesn't exist in the current implementation.
2. **Dispatch-map construction per root** needs to route each category to the *right* mixin variant —
   bare Tier 1 for categories without assessment content, the Tier 2 mixin for the six that have it —
   rather than uniformly pointing every category at the same target. This is ordinary `designates_type`
   map-building, no new mechanism, just more careful per-category target selection than
   `DonationItem`'s current single-pattern dispatch.
3. **Open implementation choice for `DonationItem` itself:** its existing per-category subclasses
   (`ClothingItem is_a DonationItem, mixins: [ClothingCategory]`) can absorb Tier 3 content by simply
   adding `PhysicalItemContextRulesMixin` to each subclass's own `mixins:` list — reachable via the
   *existing* mixin-ancestor-walk, no new generator logic needed for `DonationItem` specifically. The
   alternative is migrating `DonationItem` to the same uniform "root + dispatch-target" folding
   mechanism the two new roots need (point 1), trading a small `DonationItem`-side schema change for
   one single generator code path instead of two. Recommend the uniform path for long-term generator
   simplicity, but it's not required — verify which is less churn against the actual generator code
   before deciding.
4. **Fix `DemandSignal`'s `PersonalCareSubcategoryEnum` drift** at the source — realign
   `nappies_incontinence` back to separate `sanitary_products`/`incontinence_products` values, matching
   every other file.
5. **Verify early: does LinkML tolerate rules on `PhysicalItemContextRulesMixin` that reference slot
   names (`subcategory`, `condition_grade`, ...) the mixin itself doesn't declare?** These rules only
   make sense once mixed onto a root and evaluated against whatever the dispatch resolved to — that's
   somewhat unusual LinkML usage (rules normally reference slots visible on the declaring class's own
   induced slot set). If `SchemaView`/the schema loader statically validates rule
   preconditions/postconditions against the declaring class's slots, this pattern would fail to load.
   Test this on one rule before building the full mixin out.

## `donation_source` / `sorting_notes` — fix on the `inkind-enterprise` side, not in LinkML

Unrelated to the rules reorganization above; keep as a separate, independently-shippable fix. These
showed up duplicated into every category block for a specific, findable reason:
`UiEngine.get_field_sequence()` (`apps/categories/ui_engine.py:137-176`) resolves fields for one
`(schema, class)` pair at a time — its dispatch-chaining code that would pull a *dispatched* class's
fields together with the *root* class's fields exists but is commented out (lines 170-174). So once
the wizard dispatches from `DonationItem`'s root into e.g. `ClothingItem`, root-level optional fields
aren't automatically inherited into that step — the per-category duplication in the descriptor is very
likely compensating for that gap, not a deliberate design.

**Recommendation:** keep `donation_source`/`sorting_notes` as root-only slots (as `DonationItem`
already models them), and fix the gap on the consuming side instead — enable the commented-out
chaining (or an equivalent mechanism) so any root's own fields are automatically available in every
dispatched step. Small, self-contained, low-risk, independent of the LinkML work. (Separately:
`sorting_notes` is *also* a real Django model field with its own dedicated wizard step today, causing a
literal duplicate-textarea render bug — independently fixable, unrelated to the descriptor content
itself.)

## Rollout suggestion

1. Smoke-test the Tier 3 rule-visibility question (generator point 5) on a single rule before building
   anything else — it's the one assumption that could invalidate the whole approach.
2. Model one root end-to-end — `StorageCollectionEntry` is a reasonable pick (simplest known delta:
   uniform `usage`-required flip, no other new content). Regenerate, diff against the current
   hand-curated `StorageCollection.ui.json`, confirm it matches modulo the `donation_source`/
   `sorting_notes` removal (expected once the Django-side fix lands separately).
3. Repeat for `SortedCollectionEntry`.
4. Model `DemandSignal` last — verify its Tier-1-only dispatch produces the expected trimmed field set
   per category, and fix the `PersonalCareSubcategoryEnum` drift as part of this pass.
5. Once all four generate correctly, delete the hand-curated `SortedCollection.ui.json`/
   `StorageCollection.ui.json`/`DemandSignal.ui.json` from `inkind-enterprise` and replace them with
   the generated versions — no consuming-side engine changes needed, since the generated files keep
   the same shape (`class`/`fields`/`enums`/`rules` per top-level key) `UiEngine` already reads today.
   Re-run `poetry run python manage.py refresh_schema_test_fixtures` and the `apps.categories`/
   `apps.stock`/`apps.needs` test suites afterward.

## Appendix A — `inkind-enterprise`-side bridge (only if the LinkML work is delayed)

If hand-curation pain needs reducing before the LinkML migration lands, an `extends` primitive inside
`UiEngine.get_class_descriptor()` (`apps/categories/ui_engine.py:199`) can let
`SortedCollection.ui.json`/`StorageCollection.ui.json`/`DemandSignal.ui.json` reference specific
category classes inside `DonationItem.ui.json` by name instead of duplicating them, with a small stub
format (`extends`, `hidden_fields`, `field_overrides`, `additional_fields`, `inherit_rules`). Fully
independent of the LinkML design above — not needed if the LinkML migration is the near-term path,
kept here only as a fallback.

## Open items to verify against the real schema

- Full rule-by-rule audit of which currently-mixin-level `uc-*`/`vm-*` rules are genuinely
  context-independent (Tier 1) vs. need Tier 3 — this doc's examples (demographic→size, season→winter,
  condition_grade validation, usage validation) are illustrative, not exhaustive.
- Whether the Tier 2 mixin list (six categories) is complete, or whether other categories have
  category-specific enums on other slots that hit the same "can't share one `slot_usage`" constraint.
- Generator point 5 (rule-slot-visibility tolerance) — the one hard blocker if LinkML rejects it.
- Whether to migrate `DonationItem` to the uniform root-folding mechanism (generator point 3) or leave
  its existing mixin-ancestor path as-is.
