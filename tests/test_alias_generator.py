from linkml_runtime.utils.schemaview import SchemaView

from inkind_knowledge_repo.generators.alias_generator import AliasGenerator

SCHEMA_PATH = "src/inkind_knowledge_repo/schema/inkind_knowledge_repo.yaml"

# DonationItem's real concrete subclasses (entities/donation_item.yaml) and
# the Tier 1 category mixin each one mixes in. alias_generator.py reads
# sv.all_classes() directly (no ancestor walk), so each concrete subclass
# must carry its own label_en/label_de/aliases_en/aliases_de — mirroring,
# not inheriting, the Tier 1 mixin's values.
DONATION_ITEM_SUBCLASS_TO_TIER1_MIXIN = {
    "ClothingItem": "ClothingCategory",
    "AccessoriesItem": "AccessoriesCategory",
    "FootwearItem": "FootwearCategory",
    "FurnitureItem": "FurnitureCategory",
    "BeddingTextilesItem": "BeddingTextilesCategory",
    "HouseholdItem": "HouseholdCategory",
    "ElectronicsItem": "ElectronicsCategory",
    "ToysItem": "ToysCategory",
    "SportsItem": "SportsCategory",
    "BooksItem": "BooksCategory",
    "StationeryItem": "StationeryCategory",
    "PersonalCareItem": "PersonalCareCategory",
    "MobilityAidsItem": "MobilityAidsCategory",
    "BabyInfantItem": "BabyInfantCategory",
    "FoodItem": "FoodCategory",
    "OtherItem": "OtherCategory",
}


def test_donation_item_subclasses_carry_label_and_alias_annotations():
    """Every DonationItem concrete subclass must declare label_en/label_de
    directly on itself (not just on its Tier 1 mixin ancestor) — the
    UiDescriptorGenerator resolves labels via an ancestor walk, but
    AliasGenerator reads sv.all_classes() directly and never walks
    ancestors, so a subclass missing these annotations silently drops out
    of the alias output."""
    sv = SchemaView(SCHEMA_PATH)
    missing = []
    for subclass_name in DONATION_ITEM_SUBCLASS_TO_TIER1_MIXIN:
        cls = sv.get_class(subclass_name)
        anns = getattr(cls, "annotations", None) or {}
        for key in ("label_en", "label_de", "aliases_en", "aliases_de"):
            if key not in anns:
                missing.append(f"{subclass_name}.{key}")
    assert not missing, f"Missing label/alias annotations: {missing}"


def test_donation_item_subclass_labels_match_tier1_mixin():
    """A DonationItem subclass's label_en/label_de must match its Tier 1
    category mixin's — they should stay in sync, not drift into two
    different names for the same category."""
    sv = SchemaView(SCHEMA_PATH)
    mismatches = []
    for subclass_name, mixin_name in DONATION_ITEM_SUBCLASS_TO_TIER1_MIXIN.items():
        subclass_anns = getattr(sv.get_class(subclass_name), "annotations", None) or {}
        mixin_anns = getattr(sv.get_class(mixin_name), "annotations", None) or {}
        for key in ("label_en", "label_de"):
            sub_val = subclass_anns.get(key)
            mixin_val = mixin_anns.get(key)
            sub_val = sub_val.value if sub_val is not None else None
            mixin_val = mixin_val.value if mixin_val is not None else None
            if sub_val != mixin_val:
                mismatches.append(f"{subclass_name}.{key}={sub_val!r} != {mixin_name}.{key}={mixin_val!r}")
    assert not mismatches, f"Label drift between subclass and Tier 1 mixin: {mismatches}"


def test_alias_generator_includes_all_donation_item_subclasses():
    """AliasGenerator's output must include every DonationItem concrete
    subclass with a non-empty alias list — this is the actual regression
    the missing annotations caused: the subclasses silently vanished from
    aliases-en.json/aliases-de.json."""
    gen = AliasGenerator(SCHEMA_PATH)
    data = gen.generate()

    for locale in ("en", "de"):
        for subclass_name in DONATION_ITEM_SUBCLASS_TO_TIER1_MIXIN:
            assert subclass_name in data[locale], (
                f"{subclass_name} missing from AliasGenerator's {locale} output"
            )
            assert data[locale][subclass_name], (
                f"{subclass_name} has an empty alias list in {locale} output"
            )


def test_alias_generator_still_includes_tier1_mixins():
    """Tier 1 category mixins keep their own aliases too — the fix restores
    subclass-level annotations without removing the mixin-level ones the UI
    descriptor generator's ancestor walk relies on."""
    gen = AliasGenerator(SCHEMA_PATH)
    data = gen.generate()

    for locale in ("en", "de"):
        for mixin_name in DONATION_ITEM_SUBCLASS_TO_TIER1_MIXIN.values():
            assert mixin_name in data[locale], (
                f"{mixin_name} missing from AliasGenerator's {locale} output"
            )
            assert data[locale][mixin_name], (
                f"{mixin_name} has an empty alias list in {locale} output"
            )
