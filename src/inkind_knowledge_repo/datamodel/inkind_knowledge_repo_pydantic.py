from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "1.7.0"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )





class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'inkind_knowledge_repo',
     'default_range': 'string',
     'description': 'Formal knowledge representation for in-kind donation '
                    'coordination.\n'
                    'Defines the domain schema, category schemas with constraint '
                    'rules and\n'
                    'dependent field maps, process templates, UI fragment '
                    'bindings, and\n'
                    'organisation configuration instances.',
     'id': 'https://inkind-at.github.io/inkind-knowledge-repo',
     'imports': ['linkml:types',
                 'core',
                 'entities/organisation',
                 'entities/actor',
                 'entities/storage_location',
                 'entities/donation_source',
                 'entities/donation_collection',
                 'entities/donation_item',
                 'entities/demand_signal',
                 'entities/campaign',
                 'categories/_base',
                 'categories/accessories',
                 'categories/clothing',
                 'categories/footwear',
                 'categories/furniture',
                 'categories/bedding_textiles',
                 'categories/household',
                 'categories/electronics',
                 'categories/toys',
                 'categories/sports',
                 'categories/books',
                 'categories/stationery',
                 'categories/personal_care',
                 'categories/mobility_aids',
                 'categories/baby_infant',
                 'categories/food',
                 'provenance'],
     'license': 'MIT',
     'name': 'inkind-knowledge-repo',
     'prefixes': {'inkind_knowledge_repo': {'prefix_prefix': 'inkind_knowledge_repo',
                                            'prefix_reference': 'https://inkind-at.github.io/inkind-knowledge-repo/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'schema': {'prefix_prefix': 'schema',
                             'prefix_reference': 'http://schema.org/'}},
     'see_also': ['https://inkind-at.github.io/inkind-knowledge-repo'],
     'source_file': 'src/inkind_knowledge_repo/schema/inkind_knowledge_repo.yaml',
     'title': 'inkind-knowledge-repo'} )

class ItemUsageEnum(str, Enum):
    """
    Provenance — was the item ever used before donation? Orthogonal to assessment. new does NOT imply no defects. Grounds the top-level split in schema:OfferItemCondition.
    """
    new = "new"
    """
    Never used before donation. Does NOT imply defect-free — manufacturing defects or transit damage are possible. Assessment must still be performed.
    """
    used = "used"
    """
    Previously used before donation. Assessment required.
    """


class UsedConditionGradeEnum(str, Enum):
    """
    Observed wear/quality grade at sorting time. For wear-graded categories. Grounds schema:OfferItemCondition sub-values and schema:itemCondition. Applied regardless of usage — a new item with a defect is graded fair or poor, not assumed like_new. Sorters record what they observe.
    """
    like_new = "like_new"
    """
    No visible wear or defects. As-new appearance and function. Appropriate for new items with no observed defects, or used items showing no signs of wear.
    """
    good = "good"
    """
    Minor wear; fully functional; no significant defects. Most common grade for used items in acceptable condition.
    """
    fair = "fair"
    """
    Visible wear, minor defects, or manufacturing issues. Still suitable for redistribution with appropriate beneficiary matching.
    """
    poor = "poor"
    """
    Significant wear or defects. Redistribution subject to category-specific UC rules — some categories block, others warn and require explicit sorter confirmation.
    """


class AttributeCompletenessEnum(str, Enum):
    """
    Data quality tier for a DonationItem's category-specific attributes. Set by the fragment engine on sorting step completion — not derived from field presence at the schema level.
Design rationale:
  lifecycle_state = sorted means the sorting episode completed (process
  fact). attribute_completeness records the data quality outcome (data
  fact). These are orthogonal:
    - A size label may be missing → item sorted with minimal completeness
    - A structural assessment may be inconclusive → item sorted but routed
      to a hold state, not blocked from progressing in the lifecycle
  The match engine reads attribute_completeness to calibrate which demand
  signals an item can be matched against.

Each category mixin declares field sets for each tier via annotations:
  completeness_minimal:  mandatory fields — must be present at sorted state
  completeness_standard: standard fields — normal redistribution
  completeness_detailed: optional fields — improve match quality
The fragment compiler reads these annotations to configure the sorting UI.
    """
    minimal = "minimal"
    """
    Only mandatory fields recorded. Matches broad demand signals only (e.g. "any adult clothing"). Typical cause: missing labels, inconclusive assessment, rapid triage under time pressure.
    """
    standard = "standard"
    """
    All standard fields recorded. Normal redistribution path. Matches the majority of demand signals.
    """
    detailed = "detailed"
    """
    All optional fields also recorded (colour, style, intact labels, etc.). Maximum match quality. Enables fine-grained demand signal matching.
    """


class ItemLifecycleStateEnum(str, Enum):
    """
    Lifecycle states for a DonationItem. Ordered; transitions enforced by Django model clean(). The fragment engine drives the sorted transition on sorting episode completion; attribute_completeness is set at the same time.
Design rationale for explicit lifecycle states:
  States are enforced by the model (illegal transitions raise validation
  errors). The fragment engine reads lifecycle_state to determine which
  fragment is valid. This replaces implicit UI-flow sequencing with
  explicit data-level sequencing — which is the prerequisite for
  multi-org configuration and concurrent access control.
  No state machine library is needed: a status field with transition
  validation in the model layer is sufficient.

sorted and attribute_completeness are ORTHOGONAL:
  sorted    = the sorting episode completed (process fact)
  minimal   = episode done but limited data captured, e.g. label missing
  An item is always sorted when the episode completes — attribute_completeness
  records how much was captured, not whether the episode was complete.

Transitions:
  announced           → received            (item physically arrives)
  received            → sorting_in_progress (sort episode launched)
  sorting_in_progress → sorted              (sort episode completed;
                                             attribute_completeness set)
  sorted              → stored              (storage assignment made)
  sorted              → disposed            (unsuitable; Phase 2)
  stored              → distributed         (given to beneficiary; Phase 2)
  stored              → shared              (transferred to org; Phase 2)
  stored              → disposed            (culled from stock; Phase 2)
    """
    announced = "announced"
    """
    Donor indicated intent to donate; item not yet physically present. Optional state — used when pre-registration is supported.
    """
    received = "received"
    """
    Item physically arrived and registered against a DonationCollection. usage must be set at this point. Category-specific assessment slots are absent — they are populated during sorting.
    """
    sorting_in_progress = "sorting_in_progress"
    """
    Active sorting episode in progress. Fragment engine sets this on episode launch to prevent concurrent editing of the same item.
    """
    sorted = "sorted"
    """
    Sorting episode completed. Assessment and category attributes recorded. attribute_completeness set by the fragment engine. Item is ready for storage assignment.
    """
    stored = "stored"
    """
    Item assigned to a physical StorageLocation. storage_unit FK is set at this transition.
    """
    disposed = "disposed"
    """
    Item deemed unsuitable for redistribution and disposed of. Terminal state. (Phase 2 stub — declared now for schema completeness.)
    """
    distributed = "distributed"
    """
    Item given to a beneficiary. Terminal state. (Phase 2 stub.)
    """
    shared = "shared"
    """
    Item transferred to another organisation via the Share workflow. Terminal state. (Phase 2 stub.)
    """


class CategoryEnum(str, Enum):
    """
    Canonical registry of all donation item categories. Mirrors the DonationItem subclass URI hierarchy for use in non-item entities: DemandSignal.category, StorageLocation.category_affinity, etc.
DonationItem itself uses designates_type on the category slot; this enum is for other entities that reference categories by value.
Grouping is aligned with COICOP 2018 divisions where applicable, with deviations documented per value:
  Apparel    → COICOP Division 03 (clothing and footwear)
  Home       → COICOP Division 05 (housing, household goods)
  Technology → COICOP Division 09 (recreation and culture)
  Learning   → COICOP Division 09 (recreation and culture)
  Care       → COICOP Divisions 06 (health) and 12 (personal care)
  Life stage → COICOP Divisions 01 (food) and 03/05 (baby items)
    """
    ClothingItem = "ClothingItem"
    """
    Clothing garments: tops, bottoms, outerwear, underwear, nightwear, sportswear → ClothingItem. COICOP 03.1. Separated from accessories because the demographic→size value map and UC rules (underwear condition) do not apply to accessories.
    """
    AccessoriesItem = "AccessoriesItem"
    """
    Fashion accessories: hats, bags, jewellery, scarves, gloves, belts → AccessoriesItem. COICOP 03.1 (grouped with clothing by COICOP; separated here for progressive UI disclosure and schema clarity — no size dimension, simpler demographic vocabulary).
    """
    FootwearItem = "FootwearItem"
    """
    Shoes, boots, sandals, slippers → FootwearItem. COICOP 03.2. Separated from clothing because shoe sizing systems (EU/UK/US/CM) differ from clothing sizes and pair-completeness is footwear-specific.
    """
    FurnitureItem = "FurnitureItem"
    """
    Structural furniture: chairs, tables, beds, wardrobes → FurnitureItem. COICOP 05.1 (furniture and furnishings).
    """
    BeddingTextilesItem = "BeddingTextilesItem"
    """
    Blankets, duvets, mattresses, pillows, towels, curtains → BeddingTextilesItem. COICOP 05.2 (household textiles). Separated from household following COICOP 05.2 and UNHCR NFI kit standards, which list blankets and sleeping mats as core relief items at the same priority level as clothing.
    """
    HouseholdItem = "HouseholdItem"
    """
    Cookware, crockery, small appliances, home decor → HouseholdItem. COICOP 05.3 (household appliances), 05.4 (glassware/tableware/utensils), 05.5 (tools for house and garden).
    """
    ElectronicsItem = "ElectronicsItem"
    """
    Consumer electronics: phones, laptops, cameras, gaming → ElectronicsItem. COICOP 09.1 (audio-visual equipment) and 09.2.
    """
    ToysItem = "ToysItem"
    """
    Toys and games → ToysItem. COICOP 09.3 (games, toys, hobbies). Age-grading follows EU Toy Safety Directive 2009/48/EC.
    """
    SportsItem = "SportsItem"
    """
    Sports and fitness equipment → SportsItem. COICOP 09.4 (sport and recreational equipment). Note: bicycles are placed here by domain convention; COICOP assigns them to Division 07 (Transport).
    """
    BooksItem = "BooksItem"
    """
    Books and educational materials → BooksItem. COICOP 09.5 (newspapers, books, stationery).
    """
    StationeryItem = "StationeryItem"
    """
    Pens, notebooks, art supplies, office equipment → StationeryItem. COICOP 09.5 (newspapers, books, stationery). Separated from books because published content (BooksItem) and consumable/office supplies have different sorting paths, condition vocabularies, and demand signals.
    """
    PersonalCareItem = "PersonalCareItem"
    """
    Personal hygiene, health, and beauty products → PersonalCareItem. Merges COICOP 06.1 (medical products and appliances) and 12.1 (personal care). Merged because the operative safety rules are identical across both: sealed required, used tools blocked, expiry enforced. Open Eligibility uses a single "Personal Care Items" node.
    """
    MobilityAidsItem = "MobilityAidsItem"
    """
    Wheelchairs, crutches, hearing aids, assistive devices → MobilityAidsItem. COICOP 06.1.3 (other medical products) and 06.2 (outpatient services, durable medical equipment). Open Eligibility "Assistive Technology" top-level category.
    """
    BabyInfantItem = "BabyInfantItem"
    """
    Pushchairs, cots, car seats, infant formula, feeding equipment → BabyInfantItem. COICOP distributes baby items across 03 (clothing), 05 (household), and 01 (food). Treated as a first-class top-level category here following Open Eligibility "Baby Supplies" and UNHCR NFI kit practice (nappies and formula are core NFI kit items).
    """
    FoodItem = "FoodItem"
    """
    Food items → FoodItem. COICOP Division 01 (food and non-alcoholic beverages). Phase 1 stub — activated when food-bank organisations are onboarded. Grounded in FoodOn (OBO Foundry).
    """
    OtherItem = "OtherItem"
    """
    Items not fitting any other category → OtherItem. No COICOP alignment. Use sparingly — if a type appears frequently, add a proper subclass.
    """


class ConditionEnum(str, Enum):
    """
    DEPRECATED. Use usage + condition_grade instead.
    """
    new = "new"
    good = "good"
    fair = "fair"
    poor = "poor"


class ActorRoleEnum(str, Enum):
    """
    Valid actor roles within a SocialOrganisation.
    """
    volunteer = "volunteer"
    """
    Volunteer — routed to guided fragment mode by default.
    """
    staff = "staff"
    """
    Staff member — routed to expert mode by default.
    """
    manager = "manager"
    """
    Manager — access to reporting and configuration.
    """
    admin = "admin"
    """
    Organisation administrator — full configuration access.
    """


class ExperienceLevelEnum(str, Enum):
    """
    Actor experience level for fragment mode selection.
    """
    novice = "novice"
    """
    Novice — additional guidance text shown.
    """
    experienced = "experienced"
    """
    Experienced — standard guidance.
    """
    expert = "expert"
    """
    Expert — minimal guidance, fast-path mode.
    """


class DonationSourceTypeEnum(str, Enum):
    """
    Discriminator for the origin type of a donation.
    """
    anonymous_private = "anonymous_private"
    """
    Anonymous private donor.  Only type active in Phase 1. Identity tracked via opaque `anonymous_donor_id` token only.
    """
    corporate = "corporate"
    """
    Corporate donor — linked to CorporateDonor profile. Year 2 feature stub.
    """
    organisation = "organisation"
    """
    Donation from another SocialOrganisation (e.g., a Share workflow transfer).  Phase 2 stub.
    """


class DonationSourceLifecycleEnum(str, Enum):
    """
    Lifecycle states for a DonationSource.
    """
    announced = "announced"
    """
    Donor indicated intent to donate; physical items not yet received.
    """
    received = "received"
    """
    Physical items received and linked to this source.
    """
    acknowledged = "acknowledged"
    """
    Impact notification sent to donor.  Phase 1 stub — activated when items complete their lifecycle and Donor Portal is live.
    """


class CollectionTypeEnum(str, Enum):
    """
    Operational type of a DonationCollection.
    """
    arrival = "arrival"
    """
    Root collection created when a donation arrives.  Replaces DonationBatch.  Phase 1 only type in active use.
    """
    working = "working"
    """
    Temporary intermediate collection during a multi-stage sort pass. Phase 2 stub.
    """
    sorted = "sorted"
    """
    Stable grouping after a sort stage completes.  Phase 2 stub.
    """
    stock = "stock"
    """
    Named standing collection ready for distribution.  Maps to DemandSignal of type `standing`.  Phase 2 stub.
    """
    campaign = "campaign"
    """
    Collection assembled for a specific Campaign entity.  Phase 2 stub.
    """
    disposed = "disposed"
    """
    Items culled during sorting — auditable at collection level. Phase 2 stub.
    """


class CollectionLifecycleEnum(str, Enum):
    """
    Lifecycle states for a DonationCollection.
    """
    open = "open"
    """
    Collection is open for item registration or operations.
    """
    processing = "processing"
    """
    Items are actively being registered or processed.
    """
    closed = "closed"
    """
    All processing complete; collection is closed.
    """
    archived = "archived"
    """
    Collection has been archived for record-keeping.
    """


class SeasonEnum(str, Enum):
    """
    Seasonal suitability of a clothing or footwear item. Used on ClothingCategory (season slot) and FootwearCategory (season slot).
Design notes:
  - Four values only — fine enough for redistribution decisions,
    coarse enough for fast sorting.
  - spring_autumn is a single value because the thermal characteristics
    that define a transitional garment are the same regardless of
    which shoulder season it appears in.
  - all_season covers items with no meaningful seasonal constraint
    (e.g. a plain cotton t-shirt, a lightweight fleece) — distinct from
    "we don't know" (absence of the field) and from "suitable in all
    conditions including winter" (is_winter_suitable=true + all_season).
  - Multivalued: a linen blazer might be both spring_autumn and summer.
    Record all applicable values.
    """
    winter = "winter"
    """
    Primarily suitable for cold weather. Implies is_winter_suitable=true. Examples: heavy winter coat, thermal base layer, fleece-lined trousers, woollen jumper, ski jacket.
    """
    spring_autumn = "spring_autumn"
    """
    Suitable for mild transitional seasons. Thermal weight between winter and summer. is_winter_suitable is sorter's call. Examples: light jacket, cardigan, jeans, hoodie, trench coat.
    """
    summer = "summer"
    """
    Suitable for warm weather; not appropriate for cold conditions. Implies is_winter_suitable=false. Examples: t-shirt, shorts, sundress, swimwear, linen top.
    """
    all_season = "all_season"
    """
    No meaningful seasonal constraint — appropriate across all seasons or in climate-controlled environments. Implies is_winter_suitable=true (all-season items are by definition usable in winter). Examples: underwear, plain cotton t-shirt used as a base layer, school uniform shirt.
    """


class ClothingSubcategoryEnum(str, Enum):
    """
    Clothing garment subcategories. Accessories are NOT here — they are in AccessoriesSubcategoryEnum (accessories.yaml) on a separate item class. Separation enables clean progressive disclosure in the UI.
    """
    tops = "tops"
    """
    T-shirts, shirts, blouses, sweaters, upper-body garments. is_winter_suitable varies widely — a linen shirt and a wool jumper are both tops. Sorter must set explicitly.
    """
    bottoms = "bottoms"
    """
    Trousers, skirts, shorts, leggings, lower-body garments. is_winter_suitable varies — shorts are summer; thermal leggings are winter.
    """
    outerwear = "outerwear"
    """
    Jackets, coats, outer layers. Fragment compiler may pre-fill is_winter_suitable=true; sorter can override for summer-weight jackets.
    """
    underwear = "underwear"
    """
    Underwear and intimate apparel. UC constraints apply. Thermal underwear should be tagged is_winter_suitable=true. Standard underwear → all_season / is_winter_suitable=true (base layer).
    """
    nightwear = "nightwear"
    """
    Pyjamas, nightgowns, dressing gowns, sleep sets. Seasonal weight varies — lightweight vs. fleece nightwear.
    """
    sportswear = "sportswear"
    """
    Athletic wear, gym tops, leggings, swimwear, base layers. Non-specialist — specialist sports clothing (wetsuits, cycling jerseys) belongs in SportsItem. Fragment compiler may pre-fill is_winter_suitable=false for swimwear subcategory context.
    """
    other = "other"
    """
    Clothing garments not fitting above subcategories.
    """


class DemographicEnum(str, Enum):
    """
    Combined age-and-gender demographic for clothing and footwear items. Grounded in cpi:designatedFor and schema.org wearable size groups. Shared with FootwearItem and SportsItem via slot_usage overrides. AccessoriesItem uses the simpler AccessoriesDemographicEnum instead.
    """
    baby = "baby"
    """
    Baby (0-24 months). Valid sizes: baby_0_3m through baby_18_24m.
    """
    child = "child"
    """
    Child (2-14 years). Valid sizes: child_2T through child_14.
    """
    adult_male = "adult_male"
    """
    Adult male / menswear. Valid sizes: xs through one_size.
    """
    adult_female = "adult_female"
    """
    Adult female / womenswear. Valid sizes: xs through one_size.
    """
    unisex = "unisex"
    """
    Unisex / gender-neutral adult. Valid sizes: xs through one_size. Not valid for underwear subcategory.
    """


class ClothingSizeEnum(str, Enum):
    """
    Clothing sizes covering infant, children's, and adult sizing. Grounded in schema.org wearable size groups and CPI ClothingSize. Valid values per demographic are constrained by vm-size-* rules.
    """
    baby_0_3m = "baby_0_3m"
    """
    Baby 0-3 months
    """
    baby_3_6m = "baby_3_6m"
    """
    Baby 3-6 months
    """
    baby_6_12m = "baby_6_12m"
    """
    Baby 6-12 months
    """
    baby_12_18m = "baby_12_18m"
    """
    Baby 12-18 months
    """
    baby_18_24m = "baby_18_24m"
    """
    Baby 18-24 months
    """
    child_2_3T = "child_2_3T"
    """
    Toddler sizes 2 and 3
    """
    child_4_5T = "child_4_5T"
    """
    Toddler sizes 4 and 5
    """
    child_6_7 = "child_6_7"
    """
    Child sizes 6 and 7
    """
    child_8_10 = "child_8_10"
    """
    Child sizes 8-10
    """
    child_12_14 = "child_12_14"
    """
    Child sizes 12-14
    """
    xs_s = "xs_s"
    """
    Extra small or Small (adult)
    """
    m_l = "m_l"
    """
    Medium or Large(adult)
    """
    xl_plus = "xl_plus"
    """
    Extra large or XL+ (adult)
    """
    one_size = "one_size"
    """
    One size fits most.
    """


class AccessoriesSubcategoryEnum(str, Enum):
    """
    Fashion and personal accessories subcategories. Deliberately separate from ClothingSubcategoryEnum to enable clean progressive disclosure in the sorting UI. Grounded in Product Types Ontology (pto:) terms.
    """
    hats_headwear = "hats_headwear"
    """
    Hats, caps, beanies, headscarves, berets.
    """
    scarves = "scarves"
    """
    Scarves and shawls worn at neck or shoulders.
    """
    gloves_mittens = "gloves_mittens"
    """
    Gloves and mittens (all ages).
    """
    belts = "belts"
    """
    Belts, braces, and waist accessories.
    """
    bags_luggage = "bags_luggage"
    """
    Handbags, tote bags, backpacks, shoulder bags, wallets, purses, clutch bags, small luggage items.
    """
    jewellery = "jewellery"
    """
    Necklaces, bracelets, rings, earrings, brooches.
    """
    sunglasses = "sunglasses"
    """
    Sunglasses and fashion spectacle frames.
    """
    watches = "watches"
    """
    Wristwatches and pocket watches.
    """
    other = "other"
    """
    Accessories not fitting above subcategories.
    """


class AccessoriesDemographicEnum(str, Enum):
    """
    Simplified age-group demographic for accessories. Gender split not modelled — gender is not a meaningful dimension for most accessories at the sorting level. This contrasts with DemographicEnum (clothing.yaml) which carries adult_male/adult_female because clothing size systems are gender-differentiated. Use only when the item clearly targets a specific age group (e.g. children's hat, baby mittens).
    """
    baby = "baby"
    """
    Baby (0-24 months). e.g. baby hats, scratch mittens.
    """
    child = "child"
    """
    Child (2-14 years). e.g. children's hats, gloves.
    """
    adult = "adult"
    """
    Adult. Default for most accessories when demographic matters.
    """
    all_ages = "all_ages"
    """
    Suitable for all ages or demographic not applicable.
    """


class FootwearSubcategoryEnum(str, Enum):
    """
    Footwear subcategories. Grounded in Product Types Ontology. is_winter_suitable is the sorter's call — subcategory alone is insufficient (a lightweight canvas boot is not winter-suitable; a fleece-lined boot is). Fragment compiler provides UI hints.
    """
    shoes = "shoes"
    """
    Everyday shoes, trainers/sneakers, loafers, school shoes. is_winter_suitable varies — trainers are spring_autumn/summer; leather Oxford shoes can be all_season.
    """
    boots = "boots"
    """
    Ankle boots, knee-high boots, work boots, winter boots. Fragment compiler pre-fills is_winter_suitable=true; sorter overrides for summer ankle boots, fashion boots without insulation.
    """
    sandals = "sandals"
    """
    Open sandals and flip-flops. Fragment compiler pre-fills is_winter_suitable=false.
    """
    slippers = "slippers"
    """
    Indoor slippers and house shoes. Typically all_season (indoor use, climate-controlled environment).
    """
    sports_footwear = "sports_footwear"
    """
    Football boots, running shoes, cleats, cycling shoes. Specialist sports footwear.
    """
    other = "other"
    """
    Footwear not fitting above subcategories.
    """


class ShoeSizeSystemEnum(str, Enum):
    """
    Shoe size measurement system. Multiple systems in common use across European, UK, US, and children's sizing conventions.
    """
    EU = "EU"
    """
    European sizing (e.g. 36, 38, 42, 46)
    """
    UK = "UK"
    """
    UK sizing (e.g. 3, 5, 8, 11)
    """
    US = "US"
    """
    US sizing (e.g. 6, 7.5, 9, 12)
    """
    CM = "CM"
    """
    Foot length in centimetres — used for infant sizing
    """


class FurnitureAssessmentEnum(str, Enum):
    """
    Structured assessment of furniture structural integrity and quality. Replaces the boolean structural_integrity slot with a richer vocabulary that distinguishes cosmetic damage from structural compromise. Required at sorting regardless of usage — new items can have manufacturing defects. See schema description for full rationale.
    """
    structurally_sound = "structurally_sound"
    """
    All load-bearing components intact; no cracks, wobbling, or unsafe instability. Safe for redistribution without qualification. Appropriate for new items with no observed defects.
    """
    minor_cosmetic_damage = "minor_cosmetic_damage"
    """
    Scratches, scuffs, minor surface damage. Structural integrity unaffected. Fully redistributable. annotations:
      label_en: "Minor Cosmetic Damage"
      label_de: "Geringe Kosmetische Schäden"
    """
    significant_cosmetic_damage = "significant_cosmetic_damage"
    """
    Visible staining, discolouration, or notable surface damage. Structurally sound but appearance significantly affected. action: warn for seating/beds — sorting_notes required.
    """
    functional_with_repairs = "functional_with_repairs"
    """
    Item is usable but benefits from minor repair before redistribution (loose screw, wobbly leg, minor adjustment needed). action: warn — sorting_notes required.
    """
    structurally_compromised = "structurally_compromised"
    """
    Load-bearing components cracked, broken, or unsafe. Must not be redistributed. Applies to new items (manufacturing defect) and used. action: block, suggest: disposal or repair referral.
    """


class FurnitureSubcategoryEnum(str, Enum):
    """
    Furniture subcategories. Grounded in Product Types Ontology.
    """
    seating = "seating"
    """
    Chairs, sofas, armchairs, benches.
    """
    tables = "tables"
    """
    Dining tables, coffee tables, desks. dimensions required.
    """
    beds = "beds"
    """
    Bed frames and divans. dimensions required.
    """
    storage_units = "storage_units"
    """
    Wardrobes, cabinets, chests of drawers.
    """
    shelving = "shelving"
    """
    Shelving units, bookcases, wall-mounted shelves.
    """
    other = "other"
    """
    Furniture not fitting above subcategories.
    """


class FurnitureMaterialEnum(str, Enum):
    """
    Primary furniture construction material. Grounded in schema:material (schema.org property on schema:Product, superseding GoodRelations gr:qualitativeProductOrServiceProperty). Valid values per subcategory constrained by vm-material-* rules.
    """
    wood = "wood"
    """
    Solid wood or wood-composite (MDF, plywood, chipboard).
    """
    metal = "metal"
    """
    Metal frame (steel, aluminium, iron).
    """
    plastic = "plastic"
    """
    Plastic or synthetic polymer primary construction.
    """
    fabric = "fabric"
    """
    Upholstered fabric (sofas, chairs). Not valid for tables or beds.
    """
    glass = "glass"
    """
    Glass panels or surface (glass-top tables). Not valid for beds.
    """
    mixed = "mixed"
    """
    Mixed or composite materials.
    """


class BeddingAssessmentEnum(str, Enum):
    """
    Structured hygiene and condition assessment for bedding and textiles. Replaces former boolean slots has_been_washed and is_mattress_hygienic. Required at sorting regardless of usage.
    """
    clean_unused = "clean_unused"
    """
    Clearly unused/new with original packaging intact or no signs of previous use. No hygiene concerns.
    """
    clean_washed = "clean_washed"
    """
    Previously used but confirmed laundered and clean. No staining, odour, or hygiene concerns. Fully redistributable.
    """
    clean_with_visible_staining = "clean_with_visible_staining"
    """
    Clean and odour-free but with visible staining. Structurally sound. action: warn — sorting_notes required.
    """
    used_not_confirmed_washed = "used_not_confirmed_washed"
    """
    Used item where laundering cannot be confirmed. action: warn — sorting_notes required.
    """
    hygiene_concern = "hygiene_concern"
    """
    Visible contamination, significant staining, odour, infestation, or other hygiene issue. Redistribution unsafe. action: block, suggest: disposal.
    """


class BeddingTextilesSubcategoryEnum(str, Enum):
    """
    Bedding and household textiles subcategories. Aligned with COICOP 05.2. is_winter_suitable is meaningful for the first five subcategories; suppressed by the fragment compiler for the last three.
    """
    blankets = "blankets"
    """
    Blankets, throws, fleece covers. UNHCR NFI core relief item. is_winter_suitable required — a fleece blanket and a cotton throw serve very different needs in cold-weather distribution.
    """
    duvets_quilts = "duvets_quilts"
    """
    Duvets, quilts, continental quilts. is_winter_suitable required — tog rating (if legible) may be noted in sorting_notes.
    """
    pillows = "pillows"
    """
    Pillows and sleeping cushions.
    """
    mattresses = "mattresses"
    """
    Single, double, children's mattresses. Hygiene UC applies. is_winter_suitable typically not meaningful — suppressed in UI.
    """
    sleeping_bags = "sleeping_bags"
    """
    Adult and general sleeping bags and camping bedding. UNHCR NFI core relief item. is_winter_suitable required and UC-enforced — a summer sleeping bag in cold-weather emergency distribution is a safety risk. Thermal rating (e.g. "3-season", "-10°C comfort limit") may be noted in sorting_notes. IMPORTANT: Baby sleeping bags (0-24 months) → BabyInfantItem (subcategory: sleeping_bags). EN 16781:2018 applies — neck and armhole safety assessment required. Do not sort into this category.
    """
    bedsheets = "bedsheets"
    """
    Fitted sheets, flat sheets, pillowcases, duvet covers.
    """
    towels = "towels"
    """
    Bath, hand, face, beach towels. is_winter_suitable not meaningful — suppressed by fragment compiler.
    """
    curtains_blinds = "curtains_blinds"
    """
    Curtains, net curtains, roller blinds. is_winter_suitable not meaningful at item level — suppressed by fragment compiler.
    """
    tablecloths_napkins = "tablecloths_napkins"
    """
    Tablecloths, placemats, cloth napkins. Seasonal not applicable.
    """
    other = "other"
    """
    Household textiles not fitting above subcategories.
    """


class HouseholdSubcategoryEnum(str, Enum):
    """
    Household and kitchen goods subcategories aligned with COICOP 05.3-05.5. Bedding, towels, and curtains (COICOP 05.2) belong in BeddingTextilesSubcategoryEnum.
    """
    cookware = "cookware"
    """
    Pots, pans, baking trays, woks, pressure cookers. COICOP 05.4.
    """
    crockery = "crockery"
    """
    Plates, bowls, mugs, cups, serving dishes. COICOP 05.4.
    """
    cutlery = "cutlery"
    """
    Knives, forks, spoons, serving utensils. COICOP 05.4.
    """
    glassware = "glassware"
    """
    Drinking glasses, jugs, functional glassware. COICOP 05.4.
    """
    small_appliances = "small_appliances"
    """
    Toasters, kettles, blenders, microwaves, irons, hairdryers. COICOP 05.3.
    """
    cleaning = "cleaning"
    """
    Mops, brushes, buckets, vacuum cleaners, brooms. COICOP 05.6.
    """
    storage_organisation = "storage_organisation"
    """
    Storage boxes, baskets, coat hangers, drawer organisers.
    """
    home_decor = "home_decor"
    """
    Picture frames, vases, candles, mirrors, clocks, lamps.
    """
    garden_tools = "garden_tools"
    """
    Spades, trowels, secateurs, watering cans. COICOP 05.5.
    """
    other = "other"
    """
    Household items not fitting above subcategories.
    """


class ElectronicsAssessmentEnum(str, Enum):
    """
    Structured functional and cosmetic assessment for electronic items. Combines functional state with cosmetic condition in one vocabulary. Required at sorting regardless of usage — new devices can have defects.
    """
    fully_functional = "fully_functional"
    """
    Powers on; all features operate correctly; cosmetic condition good or better. Ready for redistribution. Appropriate for new items with no observed defects.
    """
    functional_minor_cosmetic = "functional_minor_cosmetic"
    """
    Fully functional but with minor cosmetic issues (light scratches, small scuffs) that do not affect operation. Redistributable.
    """
    functional_significant_cosmetic = "functional_significant_cosmetic"
    """
    Fully functional but with significant cosmetic damage (cracked bezel, major scratches, missing casing components). Functional but appearance notably affected.
    """
    functional_with_issues = "functional_with_issues"
    """
    Powers on but has functional issues (cracked screen still displays, missing key, camera not working, port not functioning). Redistributable with explicit description — sorting_notes required.
    """
    non_functional = "non_functional"
    """
    Does not power on, or major functionality failure rendering it unusable. action: warn — sorting_notes required. Consider repair referral or electronics recycling.
    """
    untested = "untested"
    """
    Not yet tested. Valid only at received state — blocked at sorted state by lc-sorted-electronics-not-untested rule in donation_item.yaml.
    """


class ElectronicsSubcategoryEnum(str, Enum):
    """
    Electronics subcategories. Grounded in Product Types Ontology.
    """
    smartphones = "smartphones"
    """
    Mobile phones and smartphones.
    """
    tablets = "tablets"
    """
    Tablet computers and e-readers.
    """
    laptops = "laptops"
    """
    Laptop and notebook computers.
    """
    desktop_computers = "desktop_computers"
    """
    Desktop computers and all-in-ones.
    """
    monitors = "monitors"
    """
    Computer monitors and display screens.
    """
    cameras = "cameras"
    """
    Digital cameras and camcorders.
    """
    audio = "audio"
    """
    Headphones, speakers, radios, MP3 players.
    """
    cables_chargers = "cables_chargers"
    """
    USB cables, charging adapters, power banks, extension leads.
    """
    peripherals = "peripherals"
    """
    Keyboards, mice, printers, webcams.
    """
    gaming = "gaming"
    """
    Gaming consoles, controllers, handheld gaming devices.
    """
    other = "other"
    """
    Electronics not fitting above subcategories.
    """


class ToysSubcategoryEnum(str, Enum):
    """
    Toys subcategories. Grounded in Product Types Ontology.
    """
    construction = "construction"
    """
    Building blocks, LEGO-style, construction sets.
    """
    dolls_figures = "dolls_figures"
    """
    Dolls, action figures, puppets, plush toys.
    """
    board_games = "board_games"
    """
    Board games, card games, dice games.
    """
    puzzles = "puzzles"
    """
    Jigsaw puzzles, 3D puzzles, shape sorters.
    """
    outdoor_toys = "outdoor_toys"
    """
    Balls, kites, skipping ropes, sandpit toys.
    """
    ride_on = "ride_on"
    """
    Tricycles, balance bikes, scooters, ride-on cars.
    """
    arts_crafts = "arts_crafts"
    """
    Colouring books, craft kits, modelling clay, paint sets.
    """
    educational = "educational"
    """
    Educational games and learning toys.
    """
    plush = "plush"
    """
    Soft toys and stuffed animals.
    """
    other = "other"
    """
    Toys not fitting above subcategories.
    """


class ToyAgeRangeEnum(str, Enum):
    """
    Age suitability for toys. Values aligned with EU Toy Safety Directive 2009/48/EC age-grading categories. The age_0_to_3 value is the critical boundary for the small parts choking hazard rule.
    """
    age_0_to_3 = "age_0_to_3"
    """
    0-3 years. MUST NOT have small parts (EU Toy Safety Directive 2009/48/EC).
    """
    age_3_to_6 = "age_3_to_6"
    """
    3-6 years.
    """
    age_6_to_12 = "age_6_to_12"
    """
    6-12 years.
    """
    age_12_plus = "age_12_plus"
    """
    12 years and above.
    """
    adult = "adult"
    """
    Adult games / collector items; not for children.
    """
    all_ages = "all_ages"
    """
    Suitable for all ages.
    """


class SportsProtectiveAssessmentEnum(str, Enum):
    """
    Structured safety assessment for protective gear (helmets, pads, life jackets, mouth guards). Structural damage may not be visually apparent after impact — a helmet that has absorbed an impact is unsafe even if it looks undamaged. Required regardless of usage.
    """
    safe_to_redistribute = "safe_to_redistribute"
    """
    Visually and physically intact; all components present (straps, buckles, padding); no signs of impact damage; appropriate for redistribution. Appropriate for new items with no observed defects.
    """
    safe_cosmetic_wear_only = "safe_cosmetic_wear_only"
    """
    Minor cosmetic wear (scratches, scuffs) but structurally sound with no impact damage. Safe to redistribute.
    """
    unknown_impact_history = "unknown_impact_history"
    """
    No visible damage but impact history cannot be confirmed. action: warn — sorter must confirm; advise recipient that protective certification cannot be guaranteed.
    """
    visible_structural_damage = "visible_structural_damage"
    """
    Cracks, dents, deformation, or compromised structural components. Must not be redistributed regardless of usage. action: block.
    """
    unsafe_do_not_redistribute = "unsafe_do_not_redistribute"
    """
    Definitively unsafe: confirmed post-impact, recalled model, expired certification, missing critical safety components. action: block — consider specialist recycling.
    """


class SportsSubcategoryEnum(str, Enum):
    """
    Sports equipment subcategories. Grounded in Product Types Ontology.
    """
    balls = "balls"
    """
    Footballs, basketballs, tennis balls, rugby balls.
    """
    rackets_bats = "rackets_bats"
    """
    Tennis/badminton rackets, cricket bats, ping-pong bats.
    """
    protective_gear = "protective_gear"
    """
    Helmets, shin pads, knee pads, life jackets. Structured assessment required.
    """
    fitness_equipment = "fitness_equipment"
    """
    Weights, resistance bands, yoga mats, exercise machines.
    """
    bicycles = "bicycles"
    """
    Bicycles and cycling accessories. Domain convention — COICOP 07 (Transport).
    """
    water_sports = "water_sports"
    """
    Swimming goggles, snorkels, fins, wetsuits.
    """
    winter_sports = "winter_sports"
    """
    Skis, snowboards, ice skates, sleds.
    """
    camping_outdoor = "camping_outdoor"
    """
    Tents, sleeping bags, backpacks, hiking poles.
    """
    other = "other"
    """
    Sports equipment not fitting above subcategories.
    """


class BooksSubcategoryEnum(str, Enum):
    """
    Books and educational materials subcategories.
    """
    fiction = "fiction"
    """
    Novels, short stories, graphic novels, comics.
    """
    non_fiction = "non_fiction"
    """
    Biographies, history, science, self-help, cookbooks.
    """
    childrens_books = "childrens_books"
    """
    Picture books, board books, early readers.
    """
    textbooks = "textbooks"
    """
    School and university textbooks, reference books.
    """
    language_learning = "language_learning"
    """
    Language learning books, dictionaries, phrasebooks.
    """
    religious = "religious"
    """
    Religious texts and devotional books.
    """
    educational_materials = "educational_materials"
    """
    Workbooks, flashcards, educational posters, school supplies.
    """
    other = "other"
    """
    Books and educational materials not fitting above subcategories.
    """


class BookAgeRangeEnum(str, Enum):
    """
    Age suitability for books. Broader and non-gendered compared to DemographicEnum — content suitability does not require gender split.
    """
    children_0_5 = "children_0_5"
    """
    Picture books, board books, early learning (0-5 years)
    """
    children_6_12 = "children_6_12"
    """
    Middle-grade readers, chapter books (6-12 years)
    """
    young_adult = "young_adult"
    """
    Young adult (13-17 years)
    """
    adult = "adult"
    """
    Adult readership
    """
    all_ages = "all_ages"
    """
    Suitable for all ages
    """


class StationerySubcategoryEnum(str, Enum):
    """
    Stationery and office supply subcategories.
    """
    pens_pencils = "pens_pencils"
    """
    Ballpoint pens, pencils, felt-tips, highlighters, markers.
    """
    writing_sets = "writing_sets"
    """
    Pencil cases, pen sets, calligraphy sets.
    """
    notebooks_paper = "notebooks_paper"
    """
    Notebooks, exercise books, loose-leaf paper, drawing pads.
    """
    envelopes_cards = "envelopes_cards"
    """
    Envelopes, postcards, greeting cards.
    """
    folders_binders = "folders_binders"
    """
    Ring binders, lever arch files, document wallets.
    """
    organisers = "organisers"
    """
    Desk organisers, filing trays, clipboards, planners, diaries.
    """
    art_supplies = "art_supplies"
    """
    Paints, brushes, colouring pencils, pastels, canvases.
    """
    craft_supplies = "craft_supplies"
    """
    Scissors, glue, tape, staplers, hole punches, rulers.
    """
    calculators = "calculators"
    """
    Scientific, graphing, and basic calculators.
    """
    office_equipment_small = "office_equipment_small"
    """
    Staplers, hole punches, sharpeners, correction tape.
    """
    storage_supplies = "storage_supplies"
    """
    Labels, sticky notes, index cards, dividers.
    """
    other = "other"
    """
    Stationery not fitting above subcategories.
    """


class PersonalCareSubcategoryEnum(str, Enum):
    """
    Personal care, hygiene, and health product subcategories. Covers COICOP 06.1 (medical products) and 12.1 (personal care).
    """
    soap_body_wash = "soap_body_wash"
    """
    Bar soap, liquid soap, body wash, hand sanitiser. Must be sealed.
    """
    shampoo_conditioner = "shampoo_conditioner"
    """
    Shampoo, conditioner, dry shampoo. Must be sealed.
    """
    dental = "dental"
    """
    Toothpaste, mouthwash, dental floss. Must be sealed. (Toothbrushes → personal_care_tools).
    """
    deodorant = "deodorant"
    """
    Deodorant and antiperspirant. Must be sealed.
    """
    sanitary_products = "sanitary_products"
    """
    Menstrual pads, tampons, menstrual cups. Must be sealed.
    """
    nappies_incontinence = "nappies_incontinence"
    """
    Baby nappies, adult incontinence products. Must be sealed.
    """
    toilet_paper_tissue = "toilet_paper_tissue"
    """
    Toilet paper, facial tissue. Must be sealed/wrapped.
    """
    personal_care_tools = "personal_care_tools"
    """
    Toothbrushes, razors, nail clippers, tweezers, combs. UC block: used → never redistribute.
    """
    skincare = "skincare"
    """
    Moisturisers, sunscreen, face wash, lip balm. Must be sealed.
    """
    cosmetics = "cosmetics"
    """
    Foundation, lipstick, mascara, nail polish. Must be sealed/unused.
    """
    hair_styling = "hair_styling"
    """
    Hair gel, mousse, hairspray, hair dye. Must be sealed.
    """
    otc_medication = "otc_medication"
    """
    OTC pain relief, vitamins, cold medicine. Sealed + expiry enforced. NO prescription medications.
    """
    first_aid = "first_aid"
    """
    First aid kits, plasters, antiseptic, sterile dressings. Sealed required.
    """
    medical_consumables = "medical_consumables"
    """
    Disposable gloves, masks, syringes (sealed). Sealed + expiry.
    """
    medical_devices_small = "medical_devices_small"
    """
    Thermometers, blood pressure monitors, reading glasses. Not durable aids (→ MobilityAidsItem).
    """
    other = "other"
    """
    Personal care products not fitting above subcategories.
    """


class MobilityAssessmentEnum(str, Enum):
    """
    Structured safety and hygiene assessment for mobility aids and assistive devices. Unified vocabulary covering structural soundness, functional state, and body-contact hygiene. Replaces former separate boolean structural_integrity + functional_status slots. Required at sorting regardless of usage.
    """
    safe_to_redistribute = "safe_to_redistribute"
    """
    Structurally sound, fully functional (if powered), and clean. No hygiene concerns for body-contact items. Ready for redistribution. Appropriate for new items with no observed defects.
    """
    safe_cosmetic_wear_only = "safe_cosmetic_wear_only"
    """
    Minor cosmetic wear but structurally sound and fully functional. Safe to redistribute.
    """
    safe_after_cleaning = "safe_after_cleaning"
    """
    Body-contact item (hearing aid, orthotic) that is structurally sound but requires professional cleaning before redistribution. action: warn — sorting_notes required.
    """
    non_functional = "non_functional"
    """
    Powered device does not operate as expected. Consider repair referral. action: warn — sorting_notes required.
    """
    structurally_compromised = "structurally_compromised"
    """
    Load-bearing or structural components unsafe. Applies regardless of usage. action: block, suggest: disposal or specialist repair referral.
    """
    specialist_referral_required = "specialist_referral_required"
    """
    Cannot be assessed by a general sorter — specialist evaluation required (prosthetics, complex orthotics, specialised communication devices). action: block from normal redistribution; flag for specialist organisation.
    """


class MobilityAidsSubcategoryEnum(str, Enum):
    """
    Mobility aids and assistive devices subcategories. Grounded in Product Types Ontology and Open Eligibility taxonomy.
    """
    wheelchairs = "wheelchairs"
    """
    Manual and powered wheelchairs. Structural + functional assessment required.
    """
    crutches = "crutches"
    """
    Axillary and forearm crutches, walking sticks. Structural assessment.
    """
    walking_frames = "walking_frames"
    """
    Walking frames, Zimmer frames, wheeled walkers, rollators.
    """
    mobility_scooters = "mobility_scooters"
    """
    Electric mobility scooters. Full functional + structural assessment.
    """
    hearing_aids = "hearing_aids"
    """
    In-ear and behind-ear hearing aids. Body-contact — safe_after_cleaning minimum.
    """
    visual_aids = "visual_aids"
    """
    Reading glasses (non-prescription), magnifiers, white canes.
    """
    orthotics = "orthotics"
    """
    Splints, braces, supports. Body-contact assessment applies.
    """
    prosthetics = "prosthetics"
    """
    Prosthetic limbs. Specialist referral required.
    """
    daily_living_aids = "daily_living_aids"
    """
    Grab rails, bath seats, reachers, adapted cutlery.
    """
    communication_devices = "communication_devices"
    """
    AAC devices, talking clocks, large-button phones. Functional assessment required.
    """
    other = "other"
    """
    Mobility aids and assistive devices not fitting above subcategories.
    """


class BabyEquipmentAssessmentEnum(str, Enum):
    """
    Structured safety assessment for safety-critical baby equipment (pushchairs, cots, car seats, carriers, high chairs). Required at sorting regardless of usage — new equipment can have manufacturing defects or fail safety age/provenance criteria.
Car seat specific (EN 14344):
  Structural integrity after a collision cannot be verified. Car seats
  over 10 years old or with unknown collision history must receive
  do_not_redistribute. manufacture_year is required for all car seats
  to enable the runtime age check.

Cot specific (EN 716):
  Drop-side cots are banned in the EU. A new-looking dropside cot
  must receive do_not_redistribute.

Baby sleeping bag specific (EN 16781):
  Neck opening must prevent infant from slipping inside. Armhole
  openings must be present and correctly sized. No loose cords,
  drawstrings, or ribbon ties permitted. No small detachable decorative
  parts. is_winter_suitable must be set — thermal weight ranges from
  0.5 tog (summer) to 3.5 tog (winter).
    """
    safe_to_redistribute = "safe_to_redistribute"
    """
    Structurally sound; all components present; manufacture date within acceptable range; no safety concerns. Ready for redistribution. Appropriate for new items with no observed defects.
    """
    safe_minor_wear = "safe_minor_wear"
    """
    Minor cosmetic wear but structurally sound and all safety-relevant components intact. Safe to redistribute.
    """
    requires_specialist_check = "requires_specialist_check"
    """
    Appears functional but sorter cannot fully verify safety (unknown locking mechanism, unfamiliar harness system, unclear provenance). action: warn — redistribution only after specialist confirmation.
    """
    structural_concern = "structural_concern"
    """
    Visible structural damage, cracked components, bent frame, broken harness buckle. Applies to new (manufacturing defect) and used items. action: block.
    """
    do_not_redistribute = "do_not_redistribute"
    """
    Must not be redistributed: car seat over 10 years old or confirmed post-collision (EN 14344), EU-banned dropside cot (EN 716), recalled model, missing critical safety components. action: block.
    """


class BabyInfantSubcategoryEnum(str, Enum):
    """
    Baby and infant supplies subcategories. Grounded in Product Types Ontology. Baby clothing belongs in ClothingItem (demographic=baby).
    """
    pushchairs_prams = "pushchairs_prams"
    """
    Pushchairs, prams, strollers. Structural assessment required (EN 1888).
    """
    car_seats = "car_seats"
    """
    Car and booster seats. Assessment + manufacture_year required (EN 14344).
    """
    cots_cribs = "cots_cribs"
    """
    Cots, cribs, moses baskets. Structural assessment required (EN 716). Dropside cots banned.
    """
    baby_carriers = "baby_carriers"
    """
    Baby slings, carriers, wraps. Structural assessment required.
    """
    infant_formula = "infant_formula"
    """
    Infant formula. Must be sealed + within expiry. UNHCR NFI core item.
    """
    feeding_bottles_teats = "feeding_bottles_teats"
    """
    Feeding bottles and teats. Must be sealed + unused (EN 14350).
    """
    breastfeeding = "breastfeeding"
    """
    Breast pumps, nursing pads, sterilisers.
    """
    bath_equipment = "bath_equipment"
    """
    Baby baths, bath seats, bath thermometers.
    """
    changing = "changing"
    """
    Changing mats, nappy bags, changing bags.
    """
    baby_monitors = "baby_monitors"
    """
    Audio and video baby monitors.
    """
    bouncers_swings = "bouncers_swings"
    """
    Baby bouncers, swings, rockers, play gyms.
    """
    sleeping_bags = "sleeping_bags"
    """
    Baby sleeping bags for home use (0-24 months). Track 1 — structured safety assessment required per EN 16781:2018. Sorter must verify:
      - Neck opening size appropriate (infant cannot slip inside)
      - Armhole openings present and correctly sized
      - No loose cords, drawstrings, or ribbon ties (strangulation hazard)
      - No small decorative parts that could detach (choking hazard)
    is_winter_suitable required — thermal weight varies widely from 0.5 tog (summer) to 3.5 tog (winter). Tog or comfort temperature rating is typically printed on the label. Adult and camping sleeping bags → BeddingTextilesItem.
    """
    other = "other"
    """
    Baby and infant supplies not fitting above subcategories.
    """


class FoodTypeEnum(str, Enum):
    """
    Primary food type classification. Grounded in FoodOn ontology (OBO Foundry). Each value maps to valid storage_requirement values via vm-storage-* rules.
    """
    dry_goods = "dry_goods"
    """
    Non-perishable dry staples: pasta, rice, flour, cereals, pulses. Storage: ambient or dry_cool.
    """
    canned_goods = "canned_goods"
    """
    Factory-sealed tins and cans. Shelf-stable at ambient temperature. Storage: ambient only.
    """
    fresh_produce = "fresh_produce"
    """
    Unprocessed fruit, vegetables, herbs. Perishable. packaging_intact rule applies.
    """
    dairy = "dairy"
    """
    Milk, cheese, yoghurt, and dairy-based products. Perishable — requires refrigeration or freezing.
    """
    frozen = "frozen"
    """
    Items requiring continuous frozen storage. Perishable — frozen storage is the only valid option. Breaking the cold chain makes refreezing unsafe.
    """
    beverages = "beverages"
    """
    Bottled or packaged drinks (non-alcoholic).
    """
    baby_food = "baby_food"
    """
    Commercially prepared infant formula and baby food. Perishable once opened — packaging_intact rule applies. Note: infant formula as a separate donation item belongs in BabyInfantItem (baby_infant category); this value covers baby food donated as part of a food collection.
    """
    condiments = "condiments"
    """
    Sauces, spreads, oils, vinegars, and seasoning products.
    """
    other = "other"
    """
    Food items not fitting above categories.
    """


class StorageRequirementEnum(str, Enum):
    """
    Required storage condition for a food item. Valid values per food_type are constrained by vm-storage-* rules in FoodCategory.
    """
    ambient = "ambient"
    """
    Room temperature (15-25°C), dry conditions. Standard pantry/warehouse shelf.
    """
    refrigerated = "refrigerated"
    """
    Refrigerated storage (0-4°C).
    """
    frozen = "frozen"
    """
    Frozen storage (-18°C or below).
    """
    dry_cool = "dry_cool"
    """
    Cool, dry conditions (8-15°C) — root vegetable or wine-cellar type.
    """


class FoodSubcategoryEnum(str, Enum):
    """
    Optional subcategory for further food classification within a food_type. Used when more granular labelling is operationally useful.
    """
    vegetables = "vegetables"
    """
    Fresh vegetables.
    """
    fruit = "fruit"
    """
    Fresh fruit.
    """
    bread_bakery = "bread_bakery"
    """
    Bread, rolls, and baked goods.
    """
    meat_alternatives = "meat_alternatives"
    """
    Plant-based meat substitutes.
    """
    ready_meals = "ready_meals"
    """
    Prepared meals — ambient, refrigerated, or frozen.
    """
    other = "other"
    """
    Food subcategory not covered above.
    """


class DemandSignalTypeEnum(str, Enum):
    """
    Discriminator for the type of demand signal.
    """
    standing = "standing"
    """
    Permanent standing interest in a category.  No deadline, no quantity target.  Stays active until explicitly withdrawn.
    """
    campaign = "campaign"
    """
    Time-bounded coordinated effort tied to a Campaign.  Has deadline and quantity target.
    """
    specific = "specific"
    """
    Concrete request for a specific beneficiary or holder.  Has urgency tier.
    """


class UrgencyTierEnum(str, Enum):
    """
    Urgency classification for campaign and specific demand signals.
    """
    low = "low"
    """
    Low urgency — no immediate deadline pressure.
    """
    medium = "medium"
    """
    Medium urgency.
    """
    high = "high"
    """
    High urgency — deadline approaching or need is acute.
    """
    critical = "critical"
    """
    Critical — immediate fulfilment required.
    """


class DemandSignalLifecycleEnum(str, Enum):
    """
    Lifecycle states for a DemandSignal.  Standing signals stay `active` permanently; campaign and specific signals follow the full lifecycle.
    """
    active = "active"
    """
    Signal is active and accepting matched items.
    """
    partially_fulfilled = "partially_fulfilled"
    """
    Some items matched but quantity_requested not yet reached.
    """
    fulfilled = "fulfilled"
    """
    All requested items matched.
    """
    expired = "expired"
    """
    Deadline passed without full fulfilment (campaign/specific types only).
    """
    withdrawn = "withdrawn"
    """
    Organisation explicitly cancelled this signal.
    """


class CampaignLifecycleEnum(str, Enum):
    """
    Lifecycle states for a Campaign.
    """
    planned = "planned"
    """
    Campaign is planned but not yet started.
    """
    active = "active"
    """
    Campaign is active and accepting donations.
    """
    completed = "completed"
    """
    Campaign reached its end date with fulfilment achieved.
    """
    cancelled = "cancelled"
    """
    Campaign was cancelled before completion.
    """


class DeviceTypeEnum(str, Enum):
    """
    Device type used to complete a process step.
    """
    mobile = "mobile"
    """
    Mobile phone or tablet.
    """
    desktop = "desktop"
    """
    Desktop or laptop browser.
    """
    scan = "scan"
    """
    Barcode / QR scanner peripheral.
    """



class SocialOrganisation(ConfiguredBaseModel):
    """
    A social organisation deploying the in-kind platform.  Primary operational tenant; hierarchy depth is limited to 4 levels.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'org:Organization',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/organisation',
         'slot_usage': {'parent': {'description': 'FK — parent organisation in the '
                                                  'hierarchy. uri: '
                                                  'org:subOrganizationOf — hierarchy '
                                                  'depth limit 4.',
                                   'name': 'parent',
                                   'range': 'SocialOrganisation',
                                   'required': False}}})

    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    name: Optional[str] = Field(default=None, description="""A human-readable name for a thing.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation', 'NamedThing'], 'slot_uri': 'schema:name'} })
    parent: Optional[str] = Field(default=None, description="""FK — parent organisation in the hierarchy. uri: org:subOrganizationOf — hierarchy depth limit 4.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation', 'StorageLocation', 'DonationCollection']} })
    geo_point: Optional[GeoPoint] = Field(default=None, description="""Geographic coordinates for public map display.  Optional — used by the public org directory.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation']} })
    is_active: bool = Field(default=..., description="""Whether this entity is currently active.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation', 'Actor', 'StorageLocation']} })
    config: Optional[OrgConfig] = Field(default=None, description="""Inlined organisation configuration object (timezone, locale, etc.).""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation']} })


class GeoPoint(ConfiguredBaseModel):
    """
    Geographic coordinates for public map display of an organisation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/organisation'})

    lat: Optional[float] = Field(default=None, description="""Latitude in decimal degrees.""", json_schema_extra = { "linkml_meta": {'domain_of': ['GeoPoint']} })
    long: Optional[float] = Field(default=None, description="""Longitude in decimal degrees.""", json_schema_extra = { "linkml_meta": {'domain_of': ['GeoPoint']} })


class OrgConfig(ConfiguredBaseModel):
    """
    Organisation-specific configuration parameters (timezone, locale, etc.). Full schema to be expanded in Phase 1.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/organisation'})

    timezone: Optional[str] = Field(default=None, description="""IANA timezone identifier (e.g., \"Europe/Vienna\").""", json_schema_extra = { "linkml_meta": {'domain_of': ['OrgConfig']} })
    locale: Optional[str] = Field(default=None, description="""BCP-47 locale code (e.g., \"de-AT\").""", json_schema_extra = { "linkml_meta": {'domain_of': ['OrgConfig']} })


class Actor(ConfiguredBaseModel):
    """
    A person interacting with the system — volunteer, staff, or manager.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/actor',
         'see_also': ['foaf:Person'],
         'slot_usage': {'org': {'name': 'org',
                                'range': 'SocialOrganisation',
                                'required': True}}})

    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    org: str = Field(default=..., description="""Reference to the owning SocialOrganisation. Concrete range applied via slot_usage in each class.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Actor',
                       'StorageLocation',
                       'DonationCollection',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord']} })
    role: ActorRoleEnum = Field(default=..., description="""The actor's role within the organisation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Actor'], 'see_also': ['org:Role']} })
    experience_level: Optional[ExperienceLevelEnum] = Field(default=None, description="""Actor's experience level — informs whether the engine routes to guided or expert fragment mode.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Actor']} })
    is_active: bool = Field(default=..., description="""Whether this entity is currently active.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation', 'Actor', 'StorageLocation']} })


class StorageLocation(ConfiguredBaseModel):
    """
    A physical storage unit within an organisation's warehouse.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/storage_location',
         'slot_usage': {'org': {'name': 'org',
                                'range': 'SocialOrganisation',
                                'required': True},
                        'parent': {'description': 'FK — for hierarchical storage (zone '
                                                  '-> rack -> bin).  Null for '
                                                  'top-level locations.',
                                   'name': 'parent',
                                   'range': 'StorageLocation',
                                   'required': False}}})

    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    org: str = Field(default=..., description="""Reference to the owning SocialOrganisation. Concrete range applied via slot_usage in each class.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Actor',
                       'StorageLocation',
                       'DonationCollection',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord']} })
    label: str = Field(default=..., description="""Human-readable label for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StorageLocation', 'DonationCollection']} })
    parent: Optional[str] = Field(default=None, description="""FK — for hierarchical storage (zone -> rack -> bin).  Null for top-level locations.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation', 'StorageLocation', 'DonationCollection']} })
    capacity: Optional[int] = Field(default=None, description="""Maximum item count for this location.  Null = unlimited.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StorageLocation']} })
    current_occupancy: int = Field(default=..., description="""Current item count — derived from items linked to this location.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StorageLocation']} })
    is_active: bool = Field(default=..., description="""Whether this entity is currently active.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation', 'Actor', 'StorageLocation']} })
    category_affinity: Optional[CategoryEnum] = Field(default=None, description="""Preferred item category — informational hint, not enforced by the engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StorageLocation']} })


class DonationSource(ConfiguredBaseModel):
    """
    Supply-side abstraction representing the origin of a donation. Phase 1 uses `anonymous_private` type only.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_source',
         'slot_usage': {'lifecycle_state': {'name': 'lifecycle_state',
                                            'range': 'DonationSourceLifecycleEnum',
                                            'required': True}}})

    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    source_type: DonationSourceTypeEnum = Field(default=..., description="""Discriminator — `anonymous_private` is the only type used in Phase 1.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource']} })
    anonymous_donor_id: Optional[str] = Field(default=None, description="""Opaque UUID token linking items back to an anonymous donor for impact reporting.  Populated only for `anonymous_private` source type.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource'], 'see_also': ['schema:identifier']} })
    corporate_donor_ref: Optional[str] = Field(default=None, description="""FK reference to CorporateDonor profile — Year 2 feature, nullable in Phase 1.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource']} })
    organisation_ref: Optional[str] = Field(default=None, description="""FK to a SocialOrganisation — set for the Share disposal workflow (Phase 2+).""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource']} })
    lifecycle_state: DonationSourceLifecycleEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    provenance: Optional[str] = Field(default=None, description="""Who recorded this source, on which device, and when.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource']} })


class DonationCollection(ConfiguredBaseModel):
    """
    A general-purpose grouping of items with optional recursive parent-child structure.  Replaces the flat DonationBatch model.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_collection',
         'see_also': ['ceon:Resource'],
         'slot_usage': {'donation_source': {'name': 'donation_source',
                                            'range': 'DonationSource',
                                            'required': False},
                        'lifecycle_state': {'name': 'lifecycle_state',
                                            'range': 'CollectionLifecycleEnum',
                                            'required': True},
                        'org': {'name': 'org',
                                'range': 'SocialOrganisation',
                                'required': True},
                        'parent': {'description': 'FK — null for arrival collections '
                                                  '(root); set for all derived child '
                                                  'collections.',
                                   'name': 'parent',
                                   'range': 'DonationCollection',
                                   'required': False}}})

    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    org: str = Field(default=..., description="""Reference to the owning SocialOrganisation. Concrete range applied via slot_usage in each class.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Actor',
                       'StorageLocation',
                       'DonationCollection',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord']} })
    collection_type: CollectionTypeEnum = Field(default=..., description="""Operational type of this collection.  Phase 1: `arrival` only. Phase 2+: working, sorted, stock, campaign, disposed.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection']} })
    label: str = Field(default=..., description="""Human-readable label for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StorageLocation', 'DonationCollection']} })
    parent: Optional[str] = Field(default=None, description="""FK — null for arrival collections (root); set for all derived child collections.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation', 'StorageLocation', 'DonationCollection']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    lifecycle_state: CollectionLifecycleEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    item_count: int = Field(default=..., description="""Count of items directly registered to this collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection']} })
    total_item_count: int = Field(default=..., description="""Derived count — items in this collection plus all descendant collections (computed by the engine).""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    created_by: str = Field(default=..., description="""FK — the Actor who created this collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })


class FoodCategory(ConfiguredBaseModel):
    """
    Mixin for food-specific slots, value maps, and UC rules. Applied to FoodItem via mixins: [FoodCategory]. Grounded in FoodOn (OBO Foundry): http://purl.obolibrary.org/obo/foodon.owl Does not extend CategoryMixin — see schema description for rationale. Phase 1 stub — sort_food process path activated on food-bank onboarding.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'coicop_division': {'tag': 'coicop_division', 'value': '01'},
                         'completeness_detailed': {'tag': 'completeness_detailed',
                                                   'value': 'food_type, '
                                                            'packaging_intact, '
                                                            'storage_requirement, '
                                                            'expiry_date, quantity, '
                                                            'usage'},
                         'completeness_minimal': {'tag': 'completeness_minimal',
                                                  'value': 'food_type, '
                                                           'packaging_intact, usage'},
                         'completeness_standard': {'tag': 'completeness_standard',
                                                   'value': 'food_type, '
                                                            'packaging_intact, '
                                                            'storage_requirement, '
                                                            'usage'},
                         'phase': {'tag': 'phase', 'value': 'Phase 1 stub'}},
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/categories/food',
         'mixin': True,
         'rules': [{'description': 'Perishable items with compromised packaging must '
                                   'not be redistributed. Food safety principle — '
                                   'perishable items cannot be safely redistributed '
                                   'once packaging integrity is lost. action: block.',
                    'postconditions': {'slot_conditions': {'lifecycle_state': {'name': 'lifecycle_state',
                                                                               'none_of': [{'equals_string': 'stored'},
                                                                                           {'equals_string': 'distributed'}]}}},
                    'preconditions': {'slot_conditions': {'food_type': {'any_of': [{'equals_string': 'fresh_produce'},
                                                                                   {'equals_string': 'dairy'},
                                                                                   {'equals_string': 'frozen'},
                                                                                   {'equals_string': 'baby_food'}],
                                                                        'name': 'food_type'},
                                                          'packaging_intact': {'equals_string': 'false',
                                                                               'name': 'packaging_intact'}}},
                    'title': 'uc-packaging-perishable-block'},
                   {'annotations': {'enforcement': {'tag': 'enforcement',
                                                    'value': 'application_layer'},
                                    'uc_action': {'tag': 'uc_action', 'value': 'block'},
                                    'uc_note': {'tag': 'uc_note',
                                                'value': 'expiry_date < today — '
                                                         'runtime check by Django '
                                                         'model clean()'},
                                    'uc_suggest': {'tag': 'uc_suggest',
                                                   'value': 'disposal'}},
                    'description': 'Items past expiry date must not be redistributed. '
                                   'Runtime check — dynamic date comparison not '
                                   'expressible as a static LinkML rule. Enforced by '
                                   'Django model clean() at save time.',
                    'title': 'uc-expiry-date-past-block'},
                   {'description': 'Frozen food requires frozen storage only. Breaking '
                                   'the cold chain makes frozen food unsafe to '
                                   'refreeze. action: block invalid value.',
                    'postconditions': {'slot_conditions': {'storage_requirement': {'equals_string': 'frozen',
                                                                                   'name': 'storage_requirement'}}},
                    'preconditions': {'slot_conditions': {'food_type': {'equals_string': 'frozen',
                                                                        'name': 'food_type'}}},
                    'title': 'vm-storage-frozen'},
                   {'description': 'Dairy requires refrigerated or frozen storage.',
                    'postconditions': {'slot_conditions': {'storage_requirement': {'any_of': [{'equals_string': 'refrigerated'},
                                                                                              {'equals_string': 'frozen'}],
                                                                                   'name': 'storage_requirement'}}},
                    'preconditions': {'slot_conditions': {'food_type': {'equals_string': 'dairy',
                                                                        'name': 'food_type'}}},
                    'title': 'vm-storage-dairy'},
                   {'description': 'Canned goods are shelf-stable — ambient storage '
                                   'only.',
                    'postconditions': {'slot_conditions': {'storage_requirement': {'equals_string': 'ambient',
                                                                                   'name': 'storage_requirement'}}},
                    'preconditions': {'slot_conditions': {'food_type': {'equals_string': 'canned_goods',
                                                                        'name': 'food_type'}}},
                    'title': 'vm-storage-canned'}],
         'see_also': ['foodon:00001006', 'http://purl.obolibrary.org/obo/foodon.owl'],
         'slot_usage': {'expiry_date': {'annotations': {'uc_action': {'tag': 'uc_action',
                                                                      'value': 'block'},
                                                        'uc_note': {'tag': 'uc_note',
                                                                    'value': 'Dynamic '
                                                                             'date '
                                                                             'comparison '
                                                                             '— '
                                                                             'runtime '
                                                                             'enforcement'},
                                                        'uc_suggest': {'tag': 'uc_suggest',
                                                                       'value': 'disposal'}},
                                        'description': 'Expiry or best-before date as '
                                                       'printed on the packaging. UC '
                                                       'block: expiry_date < today '
                                                       '(runtime check by Django model '
                                                       'clean()).',
                                        'name': 'expiry_date',
                                        'see_also': ['foodon:00001043']},
                        'food_type': {'name': 'food_type', 'required': True},
                        'packaging_intact': {'name': 'packaging_intact',
                                             'required': True},
                        'storage_requirement': {'name': 'storage_requirement',
                                                'required': True}}})

    food_type: FoodTypeEnum = Field(default=..., description="""Primary food type classification. Grounded in FoodOn food product taxonomy. Determines valid storage_requirement values via value map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FoodCategory'], 'see_also': ['foodon:00001017']} })
    expiry_date: Optional[date] = Field(default=None, description="""Expiry or best-before date as printed on the packaging. UC block: expiry_date < today (runtime check by Django model clean()).""", json_schema_extra = { "linkml_meta": {'annotations': {'uc_action': {'tag': 'uc_action', 'value': 'block'},
                         'uc_note': {'tag': 'uc_note',
                                     'value': 'Dynamic date comparison — runtime '
                                              'enforcement'},
                         'uc_suggest': {'tag': 'uc_suggest', 'value': 'disposal'}},
         'domain_of': ['PersonalCareCategory', 'BabyInfantCategory', 'FoodCategory'],
         'see_also': ['foodon:00001043']} })
    packaging_intact: bool = Field(default=..., description="""Whether the item's original packaging is intact and uncompromised. UC block: false + perishable food_type → must not redistribute. Primary safety signal for food items — analogous to is_sealed in PersonalCareCategory.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FoodCategory'], 'see_also': ['foodon:00001043']} })
    storage_requirement: StorageRequirementEnum = Field(default=..., description="""Required storage condition. Valid values constrained by food_type via vm-storage-* rules. Set during sorting to enable correct storage slot assignment and demand signal matching.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FoodCategory']} })
    quantity: Optional[int] = Field(default=None, description="""Quantity in natural units (items, cans, bags, kg, etc.). Optional — detailed completeness tier. Supports demand signal fulfilment tracking.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FoodCategory']} })


class DonationItem(ConfiguredBaseModel):
    """
    Abstract base for all donation items. Never instantiated directly.
    The category slot carries designates_type: true — its value (the class URI of the concrete subclass) selects which subclass schema applies. This is the LinkML mechanism for a discriminated union: category IS the type, not an attribute of the item. Grounded in schema:Product.
    attribute_completeness is set by the fragment engine when the sorting episode completes. It records data quality — NOT whether the episode was complete (lifecycle_state = sorted records that). See AttributeCompletenessEnum in core.yaml for the full rationale.
    The lifecycle state machine is documented in ItemLifecycleStateEnum in core.yaml. Transitions are enforced by Django model clean(). The sorting_in_progress state prevents concurrent editing of the same item by two sorters simultaneously.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True,
         'annotations': {'completeness_detailed': {'tag': 'completeness_detailed',
                                                   'value': 'category, usage, '
                                                            'source_collection, '
                                                            'donation_source, '
                                                            'sorting_notes'},
                         'completeness_minimal': {'tag': 'completeness_minimal',
                                                  'value': 'category, usage'},
                         'completeness_standard': {'tag': 'completeness_standard',
                                                   'value': 'category, usage, '
                                                            'sorting_notes'},
                         'label_de': {'tag': 'label_de', 'value': 'Spendenartikel'},
                         'label_en': {'tag': 'label_en', 'value': 'Donation Item'}},
         'class_uri': 'schema:Product',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_item',
         'see_also': ['schema:Product'],
         'slot_usage': {'attribute_completeness': {'name': 'attribute_completeness',
                                                   'range': 'AttributeCompletenessEnum',
                                                   'required': False},
                        'category': {'designates_type': True,
                                     'name': 'category',
                                     'notes': ['Due to a limitation in LinkML, the '
                                               'designates_type annotation was removed '
                                               'because the range is an Enum and not a '
                                               'string.'],
                                     'range': 'string',
                                     'required': True},
                        'donation_source': {'name': 'donation_source',
                                            'range': 'DonationSource',
                                            'required': False},
                        'lifecycle_state': {'name': 'lifecycle_state',
                                            'range': 'ItemLifecycleStateEnum',
                                            'required': True},
                        'source_collection': {'name': 'source_collection',
                                              'range': 'DonationCollection',
                                              'required': False},
                        'storage_unit': {'name': 'storage_unit',
                                         'range': 'StorageLocation',
                                         'required': False},
                        'usage': {'name': 'usage',
                                  'range': 'ItemUsageEnum',
                                  'required': True}}})

    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    usage: ItemUsageEnum = Field(default=..., description="""Provenance condition — was the item ever used before donation? Orthogonal to condition_grade and assessment_result. Maps to schema:NewCondition / schema:UsedCondition. usage = new does NOT imply no defects — manufacturing defects are possible and assessment must always be performed regardless of usage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Provenance'},
                         'label_en': {'tag': 'label_en', 'value': 'Provenance'}},
         'domain_of': ['DonationItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:NewCondition',
                      'schema:UsedCondition'],
         'slot_uri': 'schema:itemCondition'} })
    category: Literal["DonationItem"] = Field(default="DonationItem", description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'designates_type': True,
         'domain_of': ['DonationItem', 'DemandSignal'],
         'notes': ['Due to a limitation in LinkML, the designates_type annotation was '
                   'removed because the range is an Enum and not a string.'],
         'slot_uri': 'schema:additionalType'} })
    lifecycle_state: ItemLifecycleStateEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    attribute_completeness: Optional[AttributeCompletenessEnum] = Field(default=None, description="""Data quality tier set by the fragment engine on sorting completion. Not derived from field presence. Not a lifecycle gate. Used by the match engine to filter candidates by data quality tier. See AttributeCompletenessEnum for the relationship to lifecycle_state. Set by: fragment_engine. Read by: match_engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    source_collection: Optional[str] = Field(default=None, description="""FK — the DonationCollection (arrival type) this item was registered from. Null for items not arriving as part of a collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    storage_unit: Optional[str] = Field(default=None, description="""FK — set when lifecycle_state transitions to stored. Null until the item reaches stored state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    sorting_notes: Optional[str] = Field(default=None, description="""Free-text notes recorded by the sorter during sorting. Required by UC warn rules to capture explicit sorter confirmation (e.g. incomplete pair, body-contact item, inconclusive assessment).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationItem']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    updated_at: datetime  = Field(default=..., description="""Timestamp when the entity record was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })


class FoodItem(DonationItem, FoodCategory):
    """
    Food donation item. COICOP Division 01 (food and non-alcoholic beverages). Grounded in FoodOn (OBO Foundry food ontology):
      http://purl.obolibrary.org/obo/foodon.owl

    Phase 1 stub — fully declared to establish the schema; the sort_food process path is activated when food-bank organisations are onboarded.
    Assessment: packaging_intact + expiry_date (defined in FoodCategory). No condition_grade or assessment_result — food safety is binary: packaging intact or not, expired or not. FoodCategory does not extend CategoryMixin for this reason.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'label_de': {'tag': 'label_de', 'value': 'Essen'},
                         'label_en': {'tag': 'label_en', 'value': 'Food'}},
         'class_uri': 'foodon:00001006',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_item',
         'mixins': ['FoodCategory'],
         'rules': [{'description': 'storage_requirement required at sorted state.',
                    'postconditions': {'slot_conditions': {'storage_requirement': {'name': 'storage_requirement',
                                                                                   'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-food-storage-required'}],
         'see_also': ['foodon:00001006', 'http://purl.obolibrary.org/obo/foodon.owl']})

    food_type: FoodTypeEnum = Field(default=..., description="""Primary food type classification. Grounded in FoodOn food product taxonomy. Determines valid storage_requirement values via value map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FoodCategory'], 'see_also': ['foodon:00001017']} })
    expiry_date: Optional[date] = Field(default=None, description="""Expiry or best-before date as printed on the packaging. UC block: expiry_date < today (runtime check by Django model clean()).""", json_schema_extra = { "linkml_meta": {'annotations': {'uc_action': {'tag': 'uc_action', 'value': 'block'},
                         'uc_note': {'tag': 'uc_note',
                                     'value': 'Dynamic date comparison — runtime '
                                              'enforcement'},
                         'uc_suggest': {'tag': 'uc_suggest', 'value': 'disposal'}},
         'domain_of': ['PersonalCareCategory', 'BabyInfantCategory', 'FoodCategory'],
         'see_also': ['foodon:00001043']} })
    packaging_intact: bool = Field(default=..., description="""Whether the item's original packaging is intact and uncompromised. UC block: false + perishable food_type → must not redistribute. Primary safety signal for food items — analogous to is_sealed in PersonalCareCategory.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FoodCategory'], 'see_also': ['foodon:00001043']} })
    storage_requirement: StorageRequirementEnum = Field(default=..., description="""Required storage condition. Valid values constrained by food_type via vm-storage-* rules. Set during sorting to enable correct storage slot assignment and demand signal matching.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FoodCategory']} })
    quantity: Optional[int] = Field(default=None, description="""Quantity in natural units (items, cans, bags, kg, etc.). Optional — detailed completeness tier. Supports demand signal fulfilment tracking.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FoodCategory']} })
    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    usage: ItemUsageEnum = Field(default=..., description="""Provenance condition — was the item ever used before donation? Orthogonal to condition_grade and assessment_result. Maps to schema:NewCondition / schema:UsedCondition. usage = new does NOT imply no defects — manufacturing defects are possible and assessment must always be performed regardless of usage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Provenance'},
                         'label_en': {'tag': 'label_en', 'value': 'Provenance'}},
         'domain_of': ['DonationItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:NewCondition',
                      'schema:UsedCondition'],
         'slot_uri': 'schema:itemCondition'} })
    category: Literal["FoodItem"] = Field(default="FoodItem", description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'designates_type': True,
         'domain_of': ['DonationItem', 'DemandSignal'],
         'notes': ['Due to a limitation in LinkML, the designates_type annotation was '
                   'removed because the range is an Enum and not a string.'],
         'slot_uri': 'schema:additionalType'} })
    lifecycle_state: ItemLifecycleStateEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    attribute_completeness: Optional[AttributeCompletenessEnum] = Field(default=None, description="""Data quality tier set by the fragment engine on sorting completion. Not derived from field presence. Not a lifecycle gate. Used by the match engine to filter candidates by data quality tier. See AttributeCompletenessEnum for the relationship to lifecycle_state. Set by: fragment_engine. Read by: match_engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    source_collection: Optional[str] = Field(default=None, description="""FK — the DonationCollection (arrival type) this item was registered from. Null for items not arriving as part of a collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    storage_unit: Optional[str] = Field(default=None, description="""FK — set when lifecycle_state transitions to stored. Null until the item reaches stored state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    sorting_notes: Optional[str] = Field(default=None, description="""Free-text notes recorded by the sorter during sorting. Required by UC warn rules to capture explicit sorter confirmation (e.g. incomplete pair, body-contact item, inconclusive assessment).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationItem']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    updated_at: datetime  = Field(default=..., description="""Timestamp when the entity record was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })


class OtherItem(DonationItem):
    """
    Catch-all for donation items not fitting any other category. No mixin — minimal slots only (item_description + condition_grade). Use sparingly: if a new item type appears frequently in operations, it warrants a proper subclass with a category mixin and dedicated sorting fragment rather than accumulating in OtherItem.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'label_de': {'tag': 'label_de', 'value': 'Sonstiges'},
                         'label_en': {'tag': 'label_en', 'value': 'Other'}},
         'class_uri': 'schema:Product',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_item',
         'rules': [{'description': 'item_description and condition_grade required at '
                                   'sorted state. item_description provides the '
                                   'minimum human-readable record for items with no '
                                   'controlled vocabulary.',
                    'postconditions': {'slot_conditions': {'condition_grade': {'name': 'condition_grade',
                                                                               'required': True},
                                                           'item_description': {'name': 'item_description',
                                                                                'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-other-required-fields'}],
         'slot_usage': {'condition_grade': {'name': 'condition_grade',
                                            'range': 'UsedConditionGradeEnum',
                                            'required': False},
                        'item_description': {'name': 'item_description',
                                             'required': True}}})

    item_description: str = Field(default=..., description="""Free-text description of the item. Required for OtherItem at sorted state — provides the minimum human-readable record where no controlled vocabulary applies.""", json_schema_extra = { "linkml_meta": {'domain_of': ['OtherItem']} })
    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Observed wear/quality grade at sorting time. Grounded in schema:OfferItemCondition and schema:itemCondition. Applied to wear-graded categories: clothing, accessories, footwear, books, stationery, household, toys, general sports equipment.
Required at sorted state regardless of usage:
  new item, no defects           → like_new
  new item, manufacturing defect → fair or poor
  used item, minimal wear        → like_new or good
Sorters record what they observe, not what the label says.
Categories using structured assessment_result enums instead (furniture, electronics, bedding, protective sports gear, mobility aids, baby equipment) do NOT declare this slot.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    usage: ItemUsageEnum = Field(default=..., description="""Provenance condition — was the item ever used before donation? Orthogonal to condition_grade and assessment_result. Maps to schema:NewCondition / schema:UsedCondition. usage = new does NOT imply no defects — manufacturing defects are possible and assessment must always be performed regardless of usage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Provenance'},
                         'label_en': {'tag': 'label_en', 'value': 'Provenance'}},
         'domain_of': ['DonationItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:NewCondition',
                      'schema:UsedCondition'],
         'slot_uri': 'schema:itemCondition'} })
    category: Literal["OtherItem"] = Field(default="OtherItem", description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'designates_type': True,
         'domain_of': ['DonationItem', 'DemandSignal'],
         'notes': ['Due to a limitation in LinkML, the designates_type annotation was '
                   'removed because the range is an Enum and not a string.'],
         'slot_uri': 'schema:additionalType'} })
    lifecycle_state: ItemLifecycleStateEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    attribute_completeness: Optional[AttributeCompletenessEnum] = Field(default=None, description="""Data quality tier set by the fragment engine on sorting completion. Not derived from field presence. Not a lifecycle gate. Used by the match engine to filter candidates by data quality tier. See AttributeCompletenessEnum for the relationship to lifecycle_state. Set by: fragment_engine. Read by: match_engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    source_collection: Optional[str] = Field(default=None, description="""FK — the DonationCollection (arrival type) this item was registered from. Null for items not arriving as part of a collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    storage_unit: Optional[str] = Field(default=None, description="""FK — set when lifecycle_state transitions to stored. Null until the item reaches stored state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    sorting_notes: Optional[str] = Field(default=None, description="""Free-text notes recorded by the sorter during sorting. Required by UC warn rules to capture explicit sorter confirmation (e.g. incomplete pair, body-contact item, inconclusive assessment).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationItem']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    updated_at: datetime  = Field(default=..., description="""Timestamp when the entity record was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })


class AnyValue(ConfiguredBaseModel):
    """
    Current workaround before proper attributes are introduced. Unconstrained value holder for schemaless JSON blobs. Used for DemandSignal.attributes until the Phase 2 typed ItemAttributes refactor.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/demand_signal'})

    subcategory: Optional[str] = Field(default=None, description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    demographic: Optional[DemographicEnum] = Field(default=None, description="""Combined age-and-gender demographic suitability of clothing items. Valid values depend on subcategory (see value_map above). Grounded in cpi:designatedFor and schema.org wearable size groups. Not applicable to AccessoriesItem — accessories use the simpler AccessoriesDemographicEnum (baby/child/adult/all_ages).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Demografie'},
                         'label_en': {'tag': 'label_en', 'value': 'Demographic'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'SportsCategory',
                       'AnyValue'],
         'see_also': ['cpi:designatedFor',
                      'schema:WearableSizeGroupBaby',
                      'schema:WearableSizeGroupChildrens',
                      'schema:WearableSizeGroupAdult']} })
    size: Optional[ClothingSizeEnum] = Field(default=None, description="""Size of the clothing item. Valid values constrained by demographic via value map rules (vm-size-baby, vm-size-child, vm-size-adult). Grounded in cpi:ClothingSize and schema.org size systems.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ClothingCategory', 'AnyValue'],
         'see_also': ['cpi:ClothingSize',
                      'schema:WearableSizeGroupAdult',
                      'schema:WearableSizeSystemEU']} })


class DemandSignal(ConfiguredBaseModel):
    """
    A signal representing demand for a category of items.  Covers standing interests, time-bounded campaigns, and specific beneficiary requests under a single unified model.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/demand_signal',
         'see_also': ['schema:Demand'],
         'slot_usage': {'category': {'name': 'category',
                                     'range': 'CategoryEnum',
                                     'required': True,
                                     'see_also': ['openeligibility:ServiceTag']},
                        'lifecycle_state': {'name': 'lifecycle_state',
                                            'range': 'DemandSignalLifecycleEnum',
                                            'required': True},
                        'org': {'name': 'org',
                                'range': 'SocialOrganisation',
                                'required': True},
                        'urgency_tier': {'name': 'urgency_tier',
                                         'range': 'UrgencyTierEnum',
                                         'required': False,
                                         'see_also': ['openeligibility:HumanSituation']}}})

    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    org: str = Field(default=..., description="""Reference to the owning SocialOrganisation. Concrete range applied via slot_usage in each class.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Actor',
                       'StorageLocation',
                       'DonationCollection',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord']} })
    signal_type: DemandSignalTypeEnum = Field(default=..., description="""Discriminator — standing (permanent interest), campaign (time-bounded), or specific (concrete beneficiary request).""", json_schema_extra = { "linkml_meta": {'domain_of': ['DemandSignal']} })
    category: CategoryEnum = Field(default=..., description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'domain_of': ['DonationItem', 'DemandSignal'],
         'see_also': ['openeligibility:ServiceTag'],
         'slot_uri': 'schema:additionalType'} })
    attributes: Optional[AnyValue] = Field(default=None, description="""Category-specific demand attribute filters. Structure mirrors the attribute vocabulary defined in the category schema for the given category value. Phase 2 refactor: replace Any with typed ItemAttributes subclass hierarchy, moving category mixin slots into *Attributes classes shared between DonationItem and DemandSignal.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DemandSignal']} })
    quantity_requested: Optional[int] = Field(default=None, description="""Target quantity.  Null = any amount welcome (standing signals have no target).""", json_schema_extra = { "linkml_meta": {'domain_of': ['DemandSignal']} })
    quantity_fulfilled: int = Field(default=..., description="""Items matched to this signal — derived at runtime.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DemandSignal']} })
    campaign: Optional[str] = Field(default=None, description="""FK to Campaign — set only for `campaign` signal_type.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DemandSignal']} })
    holder: Optional[str] = Field(default=None, description="""FK reference to Beneficiary or SocialOrganisation — used for `specific` signal_type.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DemandSignal']} })
    context_note: Optional[str] = Field(default=None, description="""Human-readable context note, e.g. \"Back to school for 30 primary school children\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['DemandSignal']} })
    deadline: Optional[date] = Field(default=None, description="""Deadline for fulfilment.  Null for standing signals.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DemandSignal']} })
    urgency_tier: Optional[UrgencyTierEnum] = Field(default=None, description="""Urgency classification.  Null for standing signals; set for campaign and specific types.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DemandSignal'], 'see_also': ['openeligibility:HumanSituation']} })
    lifecycle_state: DemandSignalLifecycleEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    registered_at: datetime  = Field(default=..., description="""Timestamp when this demand signal was registered.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DemandSignal']} })
    public_visibility: bool = Field(default=..., description="""Whether to expose this signal on the public API and Donor Portal.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DemandSignal']} })


class Campaign(ConfiguredBaseModel):
    """
    A public-facing appeal grouping related DemandSignals under a shared title, timeline, and beneficiary group.  Campaign progress is derived from its child signals.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'schema:Event',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/campaign',
         'slot_usage': {'lifecycle_state': {'name': 'lifecycle_state',
                                            'range': 'CampaignLifecycleEnum',
                                            'required': True},
                        'org': {'name': 'org',
                                'range': 'SocialOrganisation',
                                'required': True}}})

    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    org: str = Field(default=..., description="""Reference to the owning SocialOrganisation. Concrete range applied via slot_usage in each class.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Actor',
                       'StorageLocation',
                       'DonationCollection',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord']} })
    title: str = Field(default=..., description="""Human-readable campaign title, e.g. \"Back to School 2026\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['Campaign']} })
    description: Optional[str] = Field(default=None, description="""A human-readable description for a thing.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Campaign', 'NamedThing'], 'slot_uri': 'schema:description'} })
    starts_at: datetime  = Field(default=..., description="""Campaign start date and time.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Campaign'], 'slot_uri': 'schema:startDate'} })
    ends_at: datetime  = Field(default=..., description="""Campaign end date and time.  Propagated as deadline to all child DemandSignals.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Campaign'], 'slot_uri': 'schema:endDate'} })
    target_beneficiary_group: Optional[str] = Field(default=None, description="""Free-text description of the target beneficiary group, e.g. \"Primary school children starting September\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['Campaign']} })
    lifecycle_state: CampaignLifecycleEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    signals: Optional[list[str]] = Field(default=None, description="""Inverse relation — DemandSignals with FK to this Campaign (signal_type = campaign).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Campaign']} })


class CategoryMixin(ConfiguredBaseModel):
    """
    Abstract mixin base for all category classes except FoodCategory.
    Provides shared slots (notes, material) available to all categories. Does NOT declare a condition rule — each category type handles condition differently (see schema description above for full rationale).
    FoodCategory does not extend this mixin because food safety assessment uses packaging_intact + expiry_date rather than condition_grade or assessment_result. Extending CategoryMixin would pull in slots that are semantically incorrect for food items.
    All other concrete category mixins extend CategoryMixin and declare their own condition approach (condition_grade or assessment_result) along with category-specific slots, UC rules, VM rules, and completeness tier annotations.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/categories/_base',
         'mixin': True})

    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class ClothingCategory(CategoryMixin):
    """
    Mixin carrying clothing-specific slots, value maps, and UC rules. Applied to ClothingItem via mixins: [ClothingCategory]. Does NOT include accessories — see AccessoriesCategory (accessories.yaml).
    Domain-level rules only (no lifecycle_state references). Lifecycle-aware rules (lc-*) live on ClothingItem in donation_item.yaml because lifecycle_state is a DonationItem slot invisible to this mixin.
    Value maps grounded in CPI ontology demographic and size vocabularies. Underwear UC constraints reflect real social-sector hygiene policy. Seasonality: is_winter_suitable (boolean, standard tier) + season (SeasonEnum, optional, detailed tier). See schema description above for the full design rationale.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'coicop_division': {'tag': 'coicop_division', 'value': '03.1'},
                         'completeness_detailed': {'tag': 'completeness_detailed',
                                                   'value': 'subcategory, demographic, '
                                                            'size, is_winter_suitable, '
                                                            'season, usage, '
                                                            'condition_grade, '
                                                            'intact_labels'},
                         'completeness_minimal': {'tag': 'completeness_minimal',
                                                  'value': 'subcategory, usage'},
                         'completeness_standard': {'tag': 'completeness_standard',
                                                   'value': 'subcategory, demographic, '
                                                            'size, is_winter_suitable, '
                                                            'usage, condition_grade'},
                         'season_ui_hint': {'tag': 'season_ui_hint',
                                            'value': 'Fragment compiler may pre-fill '
                                                     'is_winter_suitable=true when '
                                                     'subcategory=outerwear and '
                                                     'is_winter_suitable=false when '
                                                     'subcategory=sportswear '
                                                     '(swimwear). Sorter can '
                                                     'override.'}},
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/categories/clothing',
         'mixin': True,
         'rules': [{'description': 'Underwear must be new or like_new condition. fair '
                                   'or poor graded underwear must not be '
                                   'redistributed. Reflects universal hygiene policy '
                                   'across social organisations. action: block, '
                                   'suggest: disposal.',
                    'postconditions': {'slot_conditions': {'lifecycle_state': {'name': 'lifecycle_state',
                                                                               'none_of': [{'equals_string': 'stored'},
                                                                                           {'equals_string': 'distributed'}]}}},
                    'preconditions': {'slot_conditions': {'condition_grade': {'any_of': [{'equals_string': 'fair'},
                                                                                         {'equals_string': 'poor'}],
                                                                              'name': 'condition_grade'},
                                                          'subcategory': {'equals_string': 'underwear',
                                                                          'name': 'subcategory'}}},
                    'title': 'uc-underwear-condition-block'},
                   {'description': 'Used adult underwear (adult_male or adult_female '
                                   'demographic) must not be redistributed. usage must '
                                   'be new. Reflects hygiene and dignity standards '
                                   'applied universally in the social sector. action: '
                                   'block.',
                    'postconditions': {'slot_conditions': {'lifecycle_state': {'name': 'lifecycle_state',
                                                                               'none_of': [{'equals_string': 'stored'},
                                                                                           {'equals_string': 'distributed'}]}}},
                    'preconditions': {'slot_conditions': {'demographic': {'any_of': [{'equals_string': 'adult_male'},
                                                                                     {'equals_string': 'adult_female'}],
                                                                          'name': 'demographic'},
                                                          'subcategory': {'equals_string': 'underwear',
                                                                          'name': 'subcategory'},
                                                          'usage': {'equals_string': 'used',
                                                                    'name': 'usage'}}},
                    'title': 'uc-underwear-adult-used-block'},
                   {'description': 'Items in poor condition should not be distributed. '
                                   'action: block, suggest: disposal.',
                    'postconditions': {'slot_conditions': {'lifecycle_state': {'name': 'lifecycle_state',
                                                                               'none_of': [{'equals_string': 'stored'},
                                                                                           {'equals_string': 'distributed'}]}}},
                    'preconditions': {'slot_conditions': {'condition_grade': {'equals_string': 'poor',
                                                                              'name': 'condition_grade'}}},
                    'title': 'uc-poor-condition-block'},
                   {'description': 'Underwear subcategory restricts demographic to '
                                   'baby, child, adult_male, adult_female. Unisex is '
                                   'not a valid demographic for underwear — underwear '
                                   'is always gender-specific at the redistribution '
                                   'level.',
                    'postconditions': {'slot_conditions': {'demographic': {'any_of': [{'equals_string': 'baby'},
                                                                                      {'equals_string': 'child'},
                                                                                      {'equals_string': 'adult_male'},
                                                                                      {'equals_string': 'adult_female'}],
                                                                           'name': 'demographic'}}},
                    'preconditions': {'slot_conditions': {'subcategory': {'equals_string': 'underwear',
                                                                          'name': 'subcategory'}}},
                    'title': 'vm-demographic-underwear'},
                   {'description': 'baby demographic constrains size to infant size '
                                   'codes.',
                    'postconditions': {'slot_conditions': {'size': {'any_of': [{'equals_string': 'baby_0_3m'},
                                                                               {'equals_string': 'baby_3_6m'},
                                                                               {'equals_string': 'baby_6_12m'},
                                                                               {'equals_string': 'baby_12_18m'},
                                                                               {'equals_string': 'baby_18_24m'}],
                                                                    'name': 'size'}}},
                    'preconditions': {'slot_conditions': {'demographic': {'equals_string': 'baby',
                                                                          'name': 'demographic'}}},
                    'title': 'vm-size-baby'},
                   {'description': "child demographic constrains size to children's "
                                   'size codes.',
                    'postconditions': {'slot_conditions': {'size': {'any_of': [{'equals_string': 'child_2_3T'},
                                                                               {'equals_string': 'child_4_5T'},
                                                                               {'equals_string': 'child_6_7'},
                                                                               {'equals_string': 'child_8_10'},
                                                                               {'equals_string': 'child_12_14'}],
                                                                    'name': 'size'}}},
                    'preconditions': {'slot_conditions': {'demographic': {'equals_string': 'child',
                                                                          'name': 'demographic'}}},
                    'title': 'vm-size-child'},
                   {'description': 'adult/unisex demographics constrain size to adult '
                                   'size codes.',
                    'postconditions': {'slot_conditions': {'size': {'any_of': [{'equals_string': 'xs_s'},
                                                                               {'equals_string': 'm_l'},
                                                                               {'equals_string': 'xl_plus'},
                                                                               {'equals_string': 'one_size'}],
                                                                    'name': 'size'}}},
                    'preconditions': {'slot_conditions': {'demographic': {'any_of': [{'equals_string': 'adult_male'},
                                                                                     {'equals_string': 'adult_female'},
                                                                                     {'equals_string': 'unisex'}],
                                                                          'name': 'demographic'}}},
                    'title': 'vm-size-adult'},
                   {'description': 'season = winter implies is_winter_suitable = true. '
                                   'A garment explicitly tagged winter must be '
                                   'winter-suitable.',
                    'postconditions': {'slot_conditions': {'is_winter_suitable': {'equals_string': 'true',
                                                                                  'name': 'is_winter_suitable'}}},
                    'preconditions': {'slot_conditions': {'season': {'equals_string': 'winter',
                                                                     'name': 'season'}}},
                    'title': 'vm-season-winter'},
                   {'description': 'is_winter_suitable = false implies that season '
                                   'cannot be winter and all season.',
                    'postconditions': {'slot_conditions': {'season': {'any_of': [{'equals_string': 'summer'},
                                                                                 {'equals_string': 'spring_autumn'}],
                                                                      'name': 'season'}}},
                    'preconditions': {'slot_conditions': {'is_winter_suitable': {'equals_string': 'false',
                                                                                 'name': 'is_winter_suitable'}}},
                    'title': 'vm-season-not-winter-suitable'},
                   {'description': 'season = summer implies is_winter_suitable = '
                                   'false. A garment explicitly tagged summer-only is '
                                   'not winter-suitable. Note: if a sorter tags both '
                                   'summer and spring_autumn, the is_winter_suitable '
                                   'value is their explicit call — no rule fires.',
                    'postconditions': {'slot_conditions': {'is_winter_suitable': {'equals_string': 'false',
                                                                                  'name': 'is_winter_suitable'}}},
                    'preconditions': {'slot_conditions': {'season': {'equals_string': 'summer',
                                                                     'name': 'season'}}},
                    'title': 'vm-season-summer'},
                   {'description': 'season = all_season implies is_winter_suitable = '
                                   'true. All-season items are by definition suitable '
                                   'in winter.',
                    'postconditions': {'slot_conditions': {'is_winter_suitable': {'equals_string': 'true',
                                                                                  'name': 'is_winter_suitable'}}},
                    'preconditions': {'slot_conditions': {'season': {'equals_string': 'all_season',
                                                                     'name': 'season'}}},
                    'title': 'vm-season-all'}],
         'see_also': ['http://www.ebusiness-unibw.org/ontologies/cpi/ns#ClothingAndAccessories'],
         'slot_usage': {'condition_grade': {'name': 'condition_grade',
                                            'range': 'UsedConditionGradeEnum',
                                            'required': False},
                        'demographic': {'name': 'demographic',
                                        'range': 'DemographicEnum',
                                        'required': False},
                        'is_winter_suitable': {'description': 'Whether this garment '
                                                              'provides meaningful '
                                                              'warmth in cold-weather '
                                                              'conditions. Required at '
                                                              'standard completeness '
                                                              'for tops, bottoms, '
                                                              'outerwear, nightwear. '
                                                              "The sorter's direct "
                                                              'assessment — not '
                                                              'inferred from '
                                                              'subcategory or '
                                                              'material. The primary '
                                                              'emergency distribution '
                                                              'filter: "all '
                                                              'winter-suitable '
                                                              'clothing for adults."',
                                               'name': 'is_winter_suitable',
                                               'range': 'boolean',
                                               'required': False},
                        'season': {'description': 'Seasonal suitability. Optional — '
                                                  'detailed completeness tier. '
                                                  'Multivalued: a garment may span '
                                                  'seasons (e.g. spring_autumn + '
                                                  'summer). VM rules auto-derive '
                                                  'is_winter_suitable for the extreme '
                                                  'values (winter, summer, '
                                                  'all_season); spring_autumn leaves '
                                                  'the sorter to set '
                                                  'is_winter_suitable explicitly.',
                                   'multivalued': True,
                                   'name': 'season',
                                   'range': 'SeasonEnum',
                                   'required': False},
                        'size': {'name': 'size',
                                 'range': 'ClothingSizeEnum',
                                 'required': False},
                        'subcategory': {'description': 'Subcategory becomes a required '
                                                       'field on DonationItem when '
                                                       "item's lifecycle is sorted.",
                                        'name': 'subcategory',
                                        'range': 'ClothingSubcategoryEnum',
                                        'required': False}}})

    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Observed wear/quality grade at sorting time. Grounded in schema:OfferItemCondition and schema:itemCondition. Applied to wear-graded categories: clothing, accessories, footwear, books, stationery, household, toys, general sports equipment.
Required at sorted state regardless of usage:
  new item, no defects           → like_new
  new item, manufacturing defect → fair or poor
  used item, minimal wear        → like_new or good
Sorters record what they observe, not what the label says.
Categories using structured assessment_result enums instead (furniture, electronics, bedding, protective sports gear, mobility aids, baby equipment) do NOT declare this slot.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    subcategory: Optional[ClothingSubcategoryEnum] = Field(default=None, description="""Subcategory becomes a required field on DonationItem when item's lifecycle is sorted.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    is_winter_suitable: Optional[bool] = Field(default=None, description="""Whether this garment provides meaningful warmth in cold-weather conditions. Required at standard completeness for tops, bottoms, outerwear, nightwear. The sorter's direct assessment — not inferred from subcategory or material. The primary emergency distribution filter: \"all winter-suitable clothing for adults.\"""", json_schema_extra = { "linkml_meta": {'domain_of': ['ClothingCategory',
                       'FootwearCategory',
                       'BeddingTextilesCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:itemCondition']} })
    demographic: Optional[DemographicEnum] = Field(default=None, description="""Combined age-and-gender demographic suitability of clothing items. Valid values depend on subcategory (see value_map above). Grounded in cpi:designatedFor and schema.org wearable size groups. Not applicable to AccessoriesItem — accessories use the simpler AccessoriesDemographicEnum (baby/child/adult/all_ages).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Demografie'},
                         'label_en': {'tag': 'label_en', 'value': 'Demographic'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'SportsCategory',
                       'AnyValue'],
         'see_also': ['cpi:designatedFor',
                      'schema:WearableSizeGroupBaby',
                      'schema:WearableSizeGroupChildrens',
                      'schema:WearableSizeGroupAdult']} })
    size: Optional[ClothingSizeEnum] = Field(default=None, description="""Size of the clothing item. Valid values constrained by demographic via value map rules (vm-size-baby, vm-size-child, vm-size-adult). Grounded in cpi:ClothingSize and schema.org size systems.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ClothingCategory', 'AnyValue'],
         'see_also': ['cpi:ClothingSize',
                      'schema:WearableSizeGroupAdult',
                      'schema:WearableSizeSystemEU']} })
    season: Optional[list[SeasonEnum]] = Field(default=None, description="""Seasonal suitability. Optional — detailed completeness tier. Multivalued: a garment may span seasons (e.g. spring_autumn + summer). VM rules auto-derive is_winter_suitable for the extreme values (winter, summer, all_season); spring_autumn leaves the sorter to set is_winter_suitable explicitly.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Saison'},
                         'label_en': {'tag': 'label_en', 'value': 'Season'}},
         'domain_of': ['ClothingCategory', 'FootwearCategory'],
         'see_also': ['schema:itemCondition']} })
    intact_labels: Optional[bool] = Field(default=None, description="""Whether care and composition labels are present and legible. Improves match quality for beneficiaries with care requirements (e.g. allergy to certain materials). Detailed completeness tier.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de',
                                      'value': 'Unversehrte Pflege- und '
                                               'Materialetiketten'},
                         'label_en': {'tag': 'label_en',
                                      'value': 'Intact care and composition labels'},
                         'show_if': {'tag': 'show_if',
                                     'value': 'subcategory in [tops, bottoms, '
                                              'outerwear, underwear, nightwear, '
                                              'sportswear]'}},
         'domain_of': ['ClothingCategory']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class AccessoriesCategory(CategoryMixin):
    """
    Mixin for fashion and personal accessories. Applied to AccessoriesItem via mixins: [AccessoriesCategory]. Deliberately simpler than ClothingCategory — no size dimension, no demographic→size value map, simpler demographic vocabulary, no underwear UC rules. See schema description above for full rationale.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'coicop_division': {'tag': 'coicop_division', 'value': '03.1'},
                         'completeness_detailed': {'tag': 'completeness_detailed',
                                                   'value': 'subcategory, demographic, '
                                                            'material, usage, '
                                                            'condition_grade'},
                         'completeness_minimal': {'tag': 'completeness_minimal',
                                                  'value': 'subcategory, usage'},
                         'completeness_standard': {'tag': 'completeness_standard',
                                                   'value': 'subcategory, usage, '
                                                            'condition_grade'}},
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/categories/accessories',
         'mixin': True,
         'see_also': ['http://www.productontology.org/id/Fashion_accessory'],
         'slot_usage': {'condition_grade': {'name': 'condition_grade',
                                            'range': 'UsedConditionGradeEnum',
                                            'required': False},
                        'demographic': {'description': 'Optional age group. Not '
                                                       'applicable to most accessories '
                                                       '(bags, jewellery, belts are '
                                                       'generally adult by default). '
                                                       'Use for clearly age-targeted '
                                                       "items: children's hats, baby "
                                                       'mittens, baby carriers (though '
                                                       'carriers belong in '
                                                       'BabyInfantItem).',
                                        'name': 'demographic',
                                        'range': 'AccessoriesDemographicEnum',
                                        'required': False},
                        'material': {'description': 'Primary material (e.g. "leather", '
                                                    '"wool", "cotton", "metal"). Free '
                                                    'text — no controlled vocabulary '
                                                    'at this stage.',
                                     'name': 'material',
                                     'range': 'string',
                                     'required': False},
                        'subcategory': {'name': 'subcategory',
                                        'range': 'AccessoriesSubcategoryEnum',
                                        'required': True}}})

    subcategory: AccessoriesSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    demographic: Optional[AccessoriesDemographicEnum] = Field(default=None, description="""Optional age group. Not applicable to most accessories (bags, jewellery, belts are generally adult by default). Use for clearly age-targeted items: children's hats, baby mittens, baby carriers (though carriers belong in BabyInfantItem).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Demografie'},
                         'label_en': {'tag': 'label_en', 'value': 'Demographic'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'SportsCategory',
                       'AnyValue'],
         'see_also': ['cpi:designatedFor',
                      'schema:WearableSizeGroupBaby',
                      'schema:WearableSizeGroupChildrens',
                      'schema:WearableSizeGroupAdult']} })
    material: Optional[str] = Field(default=None, description="""Primary material (e.g. \"leather\", \"wool\", \"cotton\", \"metal\"). Free text — no controlled vocabulary at this stage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })
    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Observed wear/quality grade at sorting time. Grounded in schema:OfferItemCondition and schema:itemCondition. Applied to wear-graded categories: clothing, accessories, footwear, books, stationery, household, toys, general sports equipment.
Required at sorted state regardless of usage:
  new item, no defects           → like_new
  new item, manufacturing defect → fair or poor
  used item, minimal wear        → like_new or good
Sorters record what they observe, not what the label says.
Categories using structured assessment_result enums instead (furniture, electronics, bedding, protective sports gear, mobility aids, baby equipment) do NOT declare this slot.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })


class FootwearCategory(CategoryMixin):
    """
    Mixin for footwear slots and UC rules. Applied to FootwearItem via mixins: [FootwearCategory]. Uses shoe_size + shoe_size_system instead of ClothingSizeEnum. Reuses DemographicEnum, is_winter_suitable, and SeasonEnum from clothing.yaml. Same VM season auto-derivation rules apply.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'coicop_division': {'tag': 'coicop_division', 'value': '03.2'},
                         'completeness_detailed': {'tag': 'completeness_detailed',
                                                   'value': 'subcategory, demographic, '
                                                            'shoe_size, '
                                                            'shoe_size_system, '
                                                            'is_pair_complete, '
                                                            'is_winter_suitable, '
                                                            'season, usage, '
                                                            'condition_grade'},
                         'completeness_minimal': {'tag': 'completeness_minimal',
                                                  'value': 'subcategory, usage'},
                         'completeness_standard': {'tag': 'completeness_standard',
                                                   'value': 'subcategory, demographic, '
                                                            'shoe_size, '
                                                            'shoe_size_system, '
                                                            'is_pair_complete, '
                                                            'is_winter_suitable, '
                                                            'usage, condition_grade'},
                         'season_ui_hint': {'tag': 'season_ui_hint',
                                            'value': 'Fragment compiler may pre-fill '
                                                     'is_winter_suitable=true for '
                                                     'boots and '
                                                     'is_winter_suitable=false for '
                                                     'sandals. Sorter can override.'}},
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/categories/footwear',
         'mixin': True,
         'rules': [{'description': 'Single shoes require sorter confirmation. Single '
                                   'shoes may still be appropriate for beneficiaries '
                                   'with limb differences. action: warn — '
                                   'sorting_notes required.',
                    'postconditions': {'slot_conditions': {'sorting_notes': {'name': 'sorting_notes',
                                                                             'required': True}}},
                    'preconditions': {'slot_conditions': {'is_pair_complete': {'equals_string': 'false',
                                                                               'name': 'is_pair_complete'}}},
                    'title': 'uc-footwear-pair-incomplete-warn'},
                   {'description': 'season = winter implies is_winter_suitable = true.',
                    'postconditions': {'slot_conditions': {'is_winter_suitable': {'equals_string': 'true',
                                                                                  'name': 'is_winter_suitable'}}},
                    'preconditions': {'slot_conditions': {'season': {'equals_string': 'winter',
                                                                     'name': 'season'}}},
                    'title': 'vm-season-winter'},
                   {'description': 'season = summer implies is_winter_suitable = '
                                   'false.',
                    'postconditions': {'slot_conditions': {'is_winter_suitable': {'equals_string': 'false',
                                                                                  'name': 'is_winter_suitable'}}},
                    'preconditions': {'slot_conditions': {'season': {'equals_string': 'summer',
                                                                     'name': 'season'}}},
                    'title': 'vm-season-summer'},
                   {'description': 'season = all_season implies is_winter_suitable = '
                                   'true.',
                    'postconditions': {'slot_conditions': {'is_winter_suitable': {'equals_string': 'true',
                                                                                  'name': 'is_winter_suitable'}}},
                    'preconditions': {'slot_conditions': {'season': {'equals_string': 'all_season',
                                                                     'name': 'season'}}},
                    'title': 'vm-season-all'}],
         'see_also': ['http://www.productontology.org/id/Footwear'],
         'slot_usage': {'condition_grade': {'name': 'condition_grade',
                                            'range': 'UsedConditionGradeEnum',
                                            'required': False},
                        'demographic': {'name': 'demographic',
                                        'range': 'DemographicEnum',
                                        'required': False},
                        'is_winter_suitable': {'description': 'Whether this footwear '
                                                              'provides meaningful '
                                                              'warmth and weather '
                                                              'protection in cold '
                                                              'conditions. Required at '
                                                              'standard completeness. '
                                                              'Fragment compiler may '
                                                              'pre-fill: boots → true, '
                                                              'sandals → false. Sorter '
                                                              'always overrides (e.g. '
                                                              'a lightweight canvas '
                                                              'boot → false).',
                                               'name': 'is_winter_suitable',
                                               'range': 'boolean',
                                               'required': False},
                        'season': {'description': 'Seasonal suitability. Optional — '
                                                  'detailed completeness tier. Same VM '
                                                  'auto-derivation as '
                                                  'ClothingCategory:\n'
                                                  '  winter → is_winter_suitable = '
                                                  'true\n'
                                                  '  summer → is_winter_suitable = '
                                                  'false\n'
                                                  '  all_season → is_winter_suitable = '
                                                  'true\n'
                                                  '  spring_autumn → sorter decides '
                                                  'is_winter_suitable explicitly.',
                                   'multivalued': True,
                                   'name': 'season',
                                   'range': 'SeasonEnum',
                                   'required': False},
                        'subcategory': {'name': 'subcategory',
                                        'range': 'FootwearSubcategoryEnum',
                                        'required': True}}})

    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Observed wear/quality grade at sorting time. Grounded in schema:OfferItemCondition and schema:itemCondition. Applied to wear-graded categories: clothing, accessories, footwear, books, stationery, household, toys, general sports equipment.
Required at sorted state regardless of usage:
  new item, no defects           → like_new
  new item, manufacturing defect → fair or poor
  used item, minimal wear        → like_new or good
Sorters record what they observe, not what the label says.
Categories using structured assessment_result enums instead (furniture, electronics, bedding, protective sports gear, mobility aids, baby equipment) do NOT declare this slot.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    subcategory: FootwearSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    is_pair_complete: Optional[bool] = Field(default=None, description="""Whether both shoes of the pair are present. UC warn if false — sorting_notes required.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de',
                                      'value': 'Ist das Paar vollständig?'},
                         'label_en': {'tag': 'label_en', 'value': 'is pair complete'}},
         'domain_of': ['FootwearCategory']} })
    is_winter_suitable: Optional[bool] = Field(default=None, description="""Whether this footwear provides meaningful warmth and weather protection in cold conditions. Required at standard completeness. Fragment compiler may pre-fill: boots → true, sandals → false. Sorter always overrides (e.g. a lightweight canvas boot → false).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ClothingCategory',
                       'FootwearCategory',
                       'BeddingTextilesCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:itemCondition']} })
    demographic: Optional[DemographicEnum] = Field(default=None, description="""Combined age-and-gender demographic suitability of clothing items. Valid values depend on subcategory (see value_map above). Grounded in cpi:designatedFor and schema.org wearable size groups. Not applicable to AccessoriesItem — accessories use the simpler AccessoriesDemographicEnum (baby/child/adult/all_ages).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Demografie'},
                         'label_en': {'tag': 'label_en', 'value': 'Demographic'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'SportsCategory',
                       'AnyValue'],
         'see_also': ['cpi:designatedFor',
                      'schema:WearableSizeGroupBaby',
                      'schema:WearableSizeGroupChildrens',
                      'schema:WearableSizeGroupAdult']} })
    shoe_size: Optional[str] = Field(default=None, description="""Shoe size as a string. Use with shoe_size_system to disambiguate (e.g. \"42\" with system \"EU\", \"8\" with system \"UK\").""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Schuhgröße'},
                         'label_en': {'tag': 'label_en', 'value': 'shoe size'}},
         'domain_of': ['FootwearCategory']} })
    shoe_size_system: Optional[ShoeSizeSystemEnum] = Field(default=None, description="""Sizing system for the shoe_size value.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Schuhgrößen-System'},
                         'label_en': {'tag': 'label_en', 'value': 'shoe size system'}},
         'domain_of': ['FootwearCategory']} })
    season: Optional[list[SeasonEnum]] = Field(default=None, description="""Seasonal suitability. Optional — detailed completeness tier. Same VM auto-derivation as ClothingCategory:
  winter → is_winter_suitable = true
  summer → is_winter_suitable = false
  all_season → is_winter_suitable = true
  spring_autumn → sorter decides is_winter_suitable explicitly.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Saison'},
                         'label_en': {'tag': 'label_en', 'value': 'Season'}},
         'domain_of': ['ClothingCategory', 'FootwearCategory'],
         'see_also': ['schema:itemCondition']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class FurnitureCategory(CategoryMixin):
    """
    Mixin for furniture slots, value maps, and UC rules. Applied to FurnitureItem via mixins: [FurnitureCategory]. Uses FurnitureAssessmentEnum instead of condition_grade — see schema description above for the assessment model rationale. assessment_result required regardless of usage.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'coicop_division': {'tag': 'coicop_division', 'value': '05.1'},
                         'completeness_detailed': {'tag': 'completeness_detailed',
                                                   'value': 'subcategory, material, '
                                                            'assessment_result, '
                                                            'dimensions, style, usage'},
                         'completeness_minimal': {'tag': 'completeness_minimal',
                                                  'value': 'subcategory, '
                                                           'assessment_result, usage'},
                         'completeness_standard': {'tag': 'completeness_standard',
                                                   'value': 'subcategory, material, '
                                                            'assessment_result, '
                                                            'usage'}},
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/categories/furniture',
         'mixin': True,
         'rules': [{'description': 'Items assessed as structurally_compromised must '
                                   'not be redistributed. Applies to both new items '
                                   '(manufacturing defect) and used items. action: '
                                   'block, suggest: disposal or repair referral.',
                    'postconditions': {'slot_conditions': {'lifecycle_state': {'name': 'lifecycle_state',
                                                                               'none_of': [{'equals_string': 'stored'},
                                                                                           {'equals_string': 'distributed'}]}}},
                    'preconditions': {'slot_conditions': {'assessment_result': {'equals_string': 'structurally_compromised',
                                                                                'name': 'assessment_result'}}},
                    'title': 'uc-furniture-compromised-block'},
                   {'description': 'Items assessed as functional_with_repairs require '
                                   'sorter confirmation. action: warn — sorting_notes '
                                   'required.',
                    'postconditions': {'slot_conditions': {'sorting_notes': {'name': 'sorting_notes',
                                                                             'required': True}}},
                    'preconditions': {'slot_conditions': {'assessment_result': {'equals_string': 'functional_with_repairs',
                                                                                'name': 'assessment_result'}}},
                    'title': 'uc-furniture-repairable-warn'},
                   {'description': 'Seating and beds with significant cosmetic damage '
                                   'require sorter confirmation. action: warn — '
                                   'sorting_notes required.',
                    'postconditions': {'slot_conditions': {'sorting_notes': {'name': 'sorting_notes',
                                                                             'required': True}}},
                    'preconditions': {'slot_conditions': {'assessment_result': {'equals_string': 'significant_cosmetic_damage',
                                                                                'name': 'assessment_result'},
                                                          'subcategory': {'any_of': [{'equals_string': 'seating'},
                                                                                     {'equals_string': 'beds'}],
                                                                          'name': 'subcategory'}}},
                    'title': 'uc-furniture-seating-beds-cosmetic-warn'},
                   {'description': 'Beds accept structural materials only (wood, '
                                   'metal, mixed). Fabric and plastic are not valid '
                                   'primary materials for beds.',
                    'postconditions': {'slot_conditions': {'material': {'any_of': [{'equals_string': 'wood'},
                                                                                   {'equals_string': 'metal'},
                                                                                   {'equals_string': 'mixed'}],
                                                                        'name': 'material'}}},
                    'preconditions': {'slot_conditions': {'subcategory': {'equals_string': 'beds',
                                                                          'name': 'subcategory'}}},
                    'title': 'vm-material-beds'},
                   {'description': 'Tables do not use fabric as primary material.',
                    'postconditions': {'slot_conditions': {'material': {'any_of': [{'equals_string': 'wood'},
                                                                                   {'equals_string': 'metal'},
                                                                                   {'equals_string': 'plastic'},
                                                                                   {'equals_string': 'glass'},
                                                                                   {'equals_string': 'mixed'}],
                                                                        'name': 'material'}}},
                    'preconditions': {'slot_conditions': {'subcategory': {'equals_string': 'tables',
                                                                          'name': 'subcategory'}}},
                    'title': 'vm-material-tables'}],
         'see_also': ['http://www.productontology.org/id/Furniture'],
         'slot_usage': {'assessment_result': {'description': 'Structural and quality '
                                                             'assessment. Required '
                                                             'regardless of usage — '
                                                             'new furniture can have '
                                                             'manufacturing defects or '
                                                             'assembly issues.',
                                              'name': 'assessment_result',
                                              'range': 'FurnitureAssessmentEnum',
                                              'required': True},
                        'material': {'name': 'material',
                                     'range': 'FurnitureMaterialEnum',
                                     'required': False},
                        'subcategory': {'name': 'subcategory',
                                        'range': 'FurnitureSubcategoryEnum',
                                        'required': True}}})

    subcategory: FurnitureSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    material: Optional[FurnitureMaterialEnum] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })
    assessment_result: FurnitureAssessmentEnum = Field(default=..., description="""Structural and quality assessment. Required regardless of usage — new furniture can have manufacturing defects or assembly issues.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Bewertungsergebnis'},
                         'label_en': {'tag': 'label_en', 'value': 'Assessment Result'}},
         'domain_of': ['FurnitureCategory',
                       'BeddingTextilesCategory',
                       'ElectronicsCategory',
                       'SportsCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:OfferItemCondition']} })
    dimensions: Optional[str] = Field(default=None, description="""Physical dimensions in centimetres, e.g. \"100*50*75 cm\" (W*D*H). Required for tables and beds to enable storage slot assignment and demand signal matching.""", json_schema_extra = { "linkml_meta": {'annotations': {'required_if': {'tag': 'required_if',
                                         'value': 'subcategory in [tables, beds]'}},
         'domain_of': ['FurnitureCategory'],
         'see_also': ['schema:SizeSpecification']} })
    style: Optional[str] = Field(default=None, description="""Style or design description (e.g. \"Scandinavian\", \"Industrial\", \"Rustic\"). Free text. Optional — detailed completeness tier. Supports demand signal matching for beneficiaries with style preferences.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FurnitureCategory']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })


class BeddingTextilesCategory(CategoryMixin):
    """
    Mixin for bedding and textiles slots and UC rules. Applied to BeddingTextilesItem via mixins: [BeddingTextilesCategory]. Split from HouseholdItem per COICOP 05.2 and UNHCR NFI standards. Uses BeddingAssessmentEnum — hygiene is the primary redistribution signal. is_winter_suitable added for thermal weight signal on blankets, duvets, and sleeping bags. SeasonEnum not declared — binary is sufficient for bedding. See schema description for full rationale.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'coicop_division': {'tag': 'coicop_division', 'value': '05.2'},
                         'completeness_detailed': {'tag': 'completeness_detailed',
                                                   'value': 'subcategory, '
                                                            'is_set_complete, '
                                                            'assessment_result, '
                                                            'is_winter_suitable, '
                                                            'usage'},
                         'completeness_minimal': {'tag': 'completeness_minimal',
                                                  'value': 'subcategory, '
                                                           'assessment_result, usage'},
                         'completeness_standard': {'tag': 'completeness_standard',
                                                   'value': 'subcategory, '
                                                            'is_set_complete, '
                                                            'assessment_result, '
                                                            'is_winter_suitable, '
                                                            'usage'},
                         'unhcr_nfi_category': {'tag': 'unhcr_nfi_category',
                                                'value': 'household_items'},
                         'winter_suitable_subcategories': {'tag': 'winter_suitable_subcategories',
                                                           'value': 'blankets, '
                                                                    'duvets_quilts, '
                                                                    'pillows, '
                                                                    'mattresses, '
                                                                    'sleeping_bags, '
                                                                    'bedsheets'},
                         'winter_suppress_subcategories': {'tag': 'winter_suppress_subcategories',
                                                           'value': 'towels, '
                                                                    'curtains_blinds, '
                                                                    'tablecloths_napkins'}},
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/categories/bedding_textiles',
         'mixin': True,
         'rules': [{'description': 'Items with hygiene concerns must not be '
                                   'redistributed. Covers mattress staining, '
                                   'infestation signs, biological contamination, and '
                                   'packaging damage on new items. Applies regardless '
                                   'of usage. action: block, suggest: disposal.',
                    'postconditions': {'slot_conditions': {'lifecycle_state': {'name': 'lifecycle_state',
                                                                               'none_of': [{'equals_string': 'stored'},
                                                                                           {'equals_string': 'distributed'}]}}},
                    'preconditions': {'slot_conditions': {'assessment_result': {'equals_string': 'hygiene_concern',
                                                                                'name': 'assessment_result'}}},
                    'title': 'uc-bedding-hygiene-concern-block'},
                   {'description': 'Used items where laundering is unconfirmed require '
                                   'sorter confirmation. action: warn — sorting_notes '
                                   'required.',
                    'postconditions': {'slot_conditions': {'sorting_notes': {'name': 'sorting_notes',
                                                                             'required': True}}},
                    'preconditions': {'slot_conditions': {'assessment_result': {'equals_string': 'used_not_confirmed_washed',
                                                                                'name': 'assessment_result'}}},
                    'title': 'uc-bedding-not-washed-warn'},
                   {'description': 'Visibly stained items require sorter confirmation. '
                                   'action: warn — sorting_notes required.',
                    'postconditions': {'slot_conditions': {'sorting_notes': {'name': 'sorting_notes',
                                                                             'required': True}}},
                    'preconditions': {'slot_conditions': {'assessment_result': {'equals_string': 'clean_with_visible_staining',
                                                                                'name': 'assessment_result'}}},
                    'title': 'uc-bedding-stained-warn'},
                   {'description': 'Sleeping bags require is_winter_suitable to be '
                                   'explicitly set. A summer sleeping bag issued in a '
                                   'cold-weather emergency is a genuine safety risk. '
                                   'Sorters must assess the thermal rating. action: '
                                   'warn — is_winter_suitable must be set at sorted '
                                   'state.',
                    'postconditions': {'slot_conditions': {'is_winter_suitable': {'name': 'is_winter_suitable',
                                                                                  'required': True}}},
                    'preconditions': {'slot_conditions': {'subcategory': {'equals_string': 'sleeping_bags',
                                                                          'name': 'subcategory'}}},
                    'title': 'uc-bedding-sleeping-bag-winter-required'}],
         'see_also': ['http://www.productontology.org/id/Bedding',
                      'https://emergency.unhcr.org/emergency-assistance/core-relief-items/kind-non-food-item-distribution'],
         'slot_usage': {'assessment_result': {'description': 'Hygiene and condition '
                                                             'assessment. Required '
                                                             'regardless of usage — '
                                                             'new items may have '
                                                             'packaging damage or '
                                                             'factory soiling.',
                                              'name': 'assessment_result',
                                              'range': 'BeddingAssessmentEnum',
                                              'required': True},
                        'is_winter_suitable': {'description': 'Whether this bedding '
                                                              'item provides '
                                                              'meaningful warmth for '
                                                              'cold conditions. '
                                                              'Required at standard '
                                                              'completeness for '
                                                              'blankets, '
                                                              'duvets_quilts, and '
                                                              'sleeping_bags. Not '
                                                              'meaningful for towels, '
                                                              'curtains, tablecloths. '
                                                              'Suppressed by fragment '
                                                              'compiler for those '
                                                              'subcategories via the '
                                                              'season_relevant_subcategories '
                                                              'annotation.\n'
                                                              'Critical for sleeping '
                                                              'bags — a summer '
                                                              'sleeping bag issued in '
                                                              'a cold-weather '
                                                              'emergency is dangerous. '
                                                              'Thermal rating in tog '
                                                              'or season number may be '
                                                              'noted in sorting_notes '
                                                              'as free text.',
                                               'name': 'is_winter_suitable',
                                               'range': 'boolean',
                                               'required': False},
                        'subcategory': {'name': 'subcategory',
                                        'range': 'BeddingTextilesSubcategoryEnum',
                                        'required': True}}})

    subcategory: BeddingTextilesSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    assessment_result: BeddingAssessmentEnum = Field(default=..., description="""Hygiene and condition assessment. Required regardless of usage — new items may have packaging damage or factory soiling.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Bewertungsergebnis'},
                         'label_en': {'tag': 'label_en', 'value': 'Assessment Result'}},
         'domain_of': ['FurnitureCategory',
                       'BeddingTextilesCategory',
                       'ElectronicsCategory',
                       'SportsCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:OfferItemCondition']} })
    is_set_complete: Optional[bool] = Field(default=None, description="""Whether all components of the set are present. Optional — standard completeness tier.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Set vollständig'},
                         'label_en': {'tag': 'label_en', 'value': 'Set Complete'}},
         'domain_of': ['BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'StationeryCategory']} })
    is_winter_suitable: Optional[bool] = Field(default=None, description="""Whether this bedding item provides meaningful warmth for cold conditions. Required at standard completeness for blankets, duvets_quilts, and sleeping_bags. Not meaningful for towels, curtains, tablecloths. Suppressed by fragment compiler for those subcategories via the season_relevant_subcategories annotation.
Critical for sleeping bags — a summer sleeping bag issued in a cold-weather emergency is dangerous. Thermal rating in tog or season number may be noted in sorting_notes as free text.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ClothingCategory',
                       'FootwearCategory',
                       'BeddingTextilesCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:itemCondition']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class HouseholdCategory(CategoryMixin):
    """
    Mixin for household and kitchen goods slots. Applied to HouseholdItem via mixins: [HouseholdCategory]. COICOP 05.3-05.5. Bedding/textiles (COICOP 05.2) are in BeddingTextilesCategory — not here.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'coicop_divisions': {'tag': 'coicop_divisions',
                                              'value': '05.3, 05.4, 05.5'},
                         'completeness_detailed': {'tag': 'completeness_detailed',
                                                   'value': 'subcategory, material, '
                                                            'is_set_complete, usage, '
                                                            'condition_grade'},
                         'completeness_minimal': {'tag': 'completeness_minimal',
                                                  'value': 'subcategory, usage'},
                         'completeness_standard': {'tag': 'completeness_standard',
                                                   'value': 'subcategory, '
                                                            'is_set_complete, usage, '
                                                            'condition_grade'}},
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/categories/household',
         'mixin': True,
         'see_also': ['http://www.productontology.org/id/Household_goods'],
         'slot_usage': {'condition_grade': {'name': 'condition_grade',
                                            'range': 'UsedConditionGradeEnum',
                                            'required': False},
                        'subcategory': {'name': 'subcategory',
                                        'range': 'HouseholdSubcategoryEnum',
                                        'required': True}}})

    subcategory: HouseholdSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })
    is_set_complete: Optional[bool] = Field(default=None, description="""Whether all components of the set are present. Optional — standard completeness tier.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Set vollständig'},
                         'label_en': {'tag': 'label_en', 'value': 'Set Complete'}},
         'domain_of': ['BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'StationeryCategory']} })
    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Observed wear/quality grade at sorting time. Grounded in schema:OfferItemCondition and schema:itemCondition. Applied to wear-graded categories: clothing, accessories, footwear, books, stationery, household, toys, general sports equipment.
Required at sorted state regardless of usage:
  new item, no defects           → like_new
  new item, manufacturing defect → fair or poor
  used item, minimal wear        → like_new or good
Sorters record what they observe, not what the label says.
Categories using structured assessment_result enums instead (furniture, electronics, bedding, protective sports gear, mobility aids, baby equipment) do NOT declare this slot.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })


class ElectronicsCategory(CategoryMixin):
    """
    Mixin for electronics slots and UC rules. Applied to ElectronicsItem via mixins: [ElectronicsCategory]. Uses ElectronicsAssessmentEnum — see schema description for rationale. assessment_result required regardless of usage.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'coicop_division': {'tag': 'coicop_division', 'value': '09.1'},
                         'completeness_detailed': {'tag': 'completeness_detailed',
                                                   'value': 'subcategory, '
                                                            'assessment_result, '
                                                            'includes_charger, '
                                                            'includes_original_packaging, '
                                                            'usage'},
                         'completeness_minimal': {'tag': 'completeness_minimal',
                                                  'value': 'subcategory, '
                                                           'assessment_result, usage'},
                         'completeness_standard': {'tag': 'completeness_standard',
                                                   'value': 'subcategory, '
                                                            'assessment_result, usage'},
                         'data_wipe_note': {'tag': 'data_wipe_note',
                                            'value': 'Data wiping is enforced by the '
                                                     'sort_electronics process path '
                                                     'fragment step, not by a UC rule '
                                                     'in this schema.'}},
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/categories/electronics',
         'mixin': True,
         'rules': [{'description': 'Non-functional items require sorter confirmation '
                                   'before redistribution. Applies to both new '
                                   '(factory defect) and used items. Sorter should '
                                   'note whether repair referral is appropriate. '
                                   'action: warn — sorting_notes required.',
                    'postconditions': {'slot_conditions': {'sorting_notes': {'name': 'sorting_notes',
                                                                             'required': True}}},
                    'preconditions': {'slot_conditions': {'assessment_result': {'equals_string': 'non_functional',
                                                                                'name': 'assessment_result'}}},
                    'title': 'uc-electronics-non-functional-warn'}],
         'see_also': ['http://www.productontology.org/id/Consumer_electronics'],
         'slot_usage': {'assessment_result': {'description': 'Functional and cosmetic '
                                                             'assessment. Required '
                                                             'regardless of usage — '
                                                             'new devices can have '
                                                             'factory defects or dead '
                                                             'batteries.',
                                              'name': 'assessment_result',
                                              'range': 'ElectronicsAssessmentEnum',
                                              'required': True},
                        'subcategory': {'name': 'subcategory',
                                        'range': 'ElectronicsSubcategoryEnum',
                                        'required': True}}})

    subcategory: ElectronicsSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    assessment_result: ElectronicsAssessmentEnum = Field(default=..., description="""Functional and cosmetic assessment. Required regardless of usage — new devices can have factory defects or dead batteries.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Bewertungsergebnis'},
                         'label_en': {'tag': 'label_en', 'value': 'Assessment Result'}},
         'domain_of': ['FurnitureCategory',
                       'BeddingTextilesCategory',
                       'ElectronicsCategory',
                       'SportsCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:OfferItemCondition']} })
    includes_charger: Optional[bool] = Field(default=None, description="""Whether a compatible charger is included. Affects redistribution value — a device without a charger is significantly less useful. Optional — detailed completeness tier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElectronicsCategory']} })
    includes_original_packaging: Optional[bool] = Field(default=None, description="""Whether original retail packaging is present. Optional — detailed tier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElectronicsCategory']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class ToysCategory(CategoryMixin):
    """
    Mixin for toys and games slots and UC rules. Applied to ToysItem via mixins: [ToysCategory]. Age grading follows EU Toy Safety Directive 2009/48/EC. The small parts rule (uc-toys-small-parts-under3-block) directly implements the Directive's choking hazard requirement.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'coicop_division': {'tag': 'coicop_division', 'value': '09.3'},
                         'completeness_detailed': {'tag': 'completeness_detailed',
                                                   'value': 'subcategory, age_range, '
                                                            'is_set_complete, '
                                                            'has_small_parts, usage, '
                                                            'condition_grade'},
                         'completeness_minimal': {'tag': 'completeness_minimal',
                                                  'value': 'subcategory, usage'},
                         'completeness_standard': {'tag': 'completeness_standard',
                                                   'value': 'subcategory, age_range, '
                                                            'is_set_complete, usage, '
                                                            'condition_grade'},
                         'regulatory_reference': {'tag': 'regulatory_reference',
                                                  'value': 'EU Toy Safety Directive '
                                                           '2009/48/EC; ASTM F963'}},
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/categories/toys',
         'mixin': True,
         'rules': [{'description': 'Toys with small parts must not be assigned to '
                                   'age_0_to_3. Implements EU Toy Safety Directive '
                                   '2009/48/EC choking hazard requirement (also ASTM '
                                   'F963 for US-market toys). action: block.',
                    'postconditions': {'slot_conditions': {'age_range': {'any_of': [{'equals_string': 'age_3_to_6'},
                                                                                    {'equals_string': 'age_6_to_12'},
                                                                                    {'equals_string': 'age_12_plus'},
                                                                                    {'equals_string': 'adult'}],
                                                                         'name': 'age_range'}}},
                    'preconditions': {'slot_conditions': {'has_small_parts': {'equals_string': 'true',
                                                                              'name': 'has_small_parts'}}},
                    'title': 'uc-toys-small-parts-under3-block'},
                   {'description': 'Incomplete sets require sorter confirmation — '
                                   'missing pieces may render the toy unusable or '
                                   'unsafe for its intended purpose. action: warn — '
                                   'sorting_notes required.',
                    'postconditions': {'slot_conditions': {'sorting_notes': {'name': 'sorting_notes',
                                                                             'required': True}}},
                    'preconditions': {'slot_conditions': {'is_set_complete': {'equals_string': 'false',
                                                                              'name': 'is_set_complete'}}},
                    'title': 'uc-toys-incomplete-set-warn'}],
         'see_also': ['http://www.productontology.org/id/Toy',
                      'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009L0048'],
         'slot_usage': {'age_range': {'name': 'age_range',
                                      'range': 'ToyAgeRangeEnum',
                                      'required': False},
                        'condition_grade': {'name': 'condition_grade',
                                            'range': 'UsedConditionGradeEnum',
                                            'required': False},
                        'subcategory': {'name': 'subcategory',
                                        'range': 'ToysSubcategoryEnum',
                                        'required': True}}})

    subcategory: ToysSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    age_range: Optional[ToyAgeRangeEnum] = Field(default=None, description="""Age suitability. Range overridden per class:
  ToysItem  → ToyAgeRangeEnum
  BooksItem → BookAgeRangeEnum""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Altersbereich'},
                         'label_en': {'tag': 'label_en', 'value': 'Age Range'}},
         'domain_of': ['ToysCategory', 'BooksCategory']} })
    is_set_complete: Optional[bool] = Field(default=None, description="""Whether all components of the set are present. Optional — standard completeness tier.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Set vollständig'},
                         'label_en': {'tag': 'label_en', 'value': 'Set Complete'}},
         'domain_of': ['BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'StationeryCategory']} })
    has_small_parts: Optional[bool] = Field(default=None, description="""Whether the item contains small parts posing a choking hazard. UC block: has_small_parts=true → age_range must exclude age_0_to_3. Implements EU Toy Safety Directive 2009/48/EC.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ToysCategory']} })
    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Observed wear/quality grade at sorting time. Grounded in schema:OfferItemCondition and schema:itemCondition. Applied to wear-graded categories: clothing, accessories, footwear, books, stationery, household, toys, general sports equipment.
Required at sorted state regardless of usage:
  new item, no defects           → like_new
  new item, manufacturing defect → fair or poor
  used item, minimal wear        → like_new or good
Sorters record what they observe, not what the label says.
Categories using structured assessment_result enums instead (furniture, electronics, bedding, protective sports gear, mobility aids, baby equipment) do NOT declare this slot.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class SportsCategory(CategoryMixin):
    """
    Mixin for sports equipment slots and UC rules. Applied to SportsItem via mixins: [SportsCategory]. Dual-track assessment: assessment_result for protective_gear, condition_grade for all other subcategories. See schema description for full rationale.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'bicycle_note': {'tag': 'bicycle_note',
                                          'value': 'Bicycles are in this category by '
                                                   'domain convention. COICOP assigns '
                                                   'bicycles to Division 07 '
                                                   '(Transport).'},
                         'coicop_division': {'tag': 'coicop_division', 'value': '09.4'},
                         'completeness_detailed': {'tag': 'completeness_detailed',
                                                   'value': 'subcategory, sport_type, '
                                                            'demographic, '
                                                            'condition_grade, '
                                                            'is_set_complete, usage'},
                         'completeness_minimal': {'tag': 'completeness_minimal',
                                                  'value': 'subcategory, usage'},
                         'completeness_standard': {'tag': 'completeness_standard',
                                                   'value': 'subcategory, '
                                                            'condition_grade, usage'},
                         'protective_gear_standard': {'tag': 'protective_gear_standard',
                                                      'value': 'subcategory, '
                                                               'assessment_result, '
                                                               'usage'}},
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/categories/sports',
         'mixin': True,
         'rules': [{'description': 'Protective gear requires structured safety '
                                   'assessment regardless of usage — new protective '
                                   'gear can have manufacturing defects.',
                    'postconditions': {'slot_conditions': {'assessment_result': {'name': 'assessment_result',
                                                                                 'required': True}}},
                    'preconditions': {'slot_conditions': {'subcategory': {'equals_string': 'protective_gear',
                                                                          'name': 'subcategory'}}},
                    'title': 'uc-sports-protective-gear-assessment-required'},
                   {'description': 'Protective gear assessed as unsafe must not be '
                                   'redistributed. action: block.',
                    'postconditions': {'slot_conditions': {'lifecycle_state': {'name': 'lifecycle_state',
                                                                               'none_of': [{'equals_string': 'stored'},
                                                                                           {'equals_string': 'distributed'}]}}},
                    'preconditions': {'slot_conditions': {'assessment_result': {'equals_string': 'unsafe_do_not_redistribute',
                                                                                'name': 'assessment_result'},
                                                          'subcategory': {'equals_string': 'protective_gear',
                                                                          'name': 'subcategory'}}},
                    'title': 'uc-sports-protective-gear-unsafe-block'},
                   {'description': 'Protective gear with unknown impact history '
                                   'requires confirmation. action: warn — '
                                   'sorting_notes required.',
                    'postconditions': {'slot_conditions': {'sorting_notes': {'name': 'sorting_notes',
                                                                             'required': True}}},
                    'preconditions': {'slot_conditions': {'assessment_result': {'equals_string': 'unknown_impact_history',
                                                                                'name': 'assessment_result'},
                                                          'subcategory': {'equals_string': 'protective_gear',
                                                                          'name': 'subcategory'}}},
                    'title': 'uc-sports-protective-gear-post-impact-warn'},
                   {'description': 'General sports equipment requires condition_grade.',
                    'postconditions': {'slot_conditions': {'condition_grade': {'name': 'condition_grade',
                                                                               'required': True}}},
                    'preconditions': {'slot_conditions': {'subcategory': {'name': 'subcategory',
                                                                          'none_of': [{'equals_string': 'protective_gear'}]}}},
                    'title': 'uc-sports-general-condition-grade-required'},
                   {'description': 'General sports equipment in poor condition '
                                   'requires confirmation. action: warn — '
                                   'sorting_notes required.',
                    'postconditions': {'slot_conditions': {'sorting_notes': {'name': 'sorting_notes',
                                                                             'required': True}}},
                    'preconditions': {'slot_conditions': {'condition_grade': {'equals_string': 'poor',
                                                                              'name': 'condition_grade'},
                                                          'subcategory': {'name': 'subcategory',
                                                                          'none_of': [{'equals_string': 'protective_gear'}]}}},
                    'title': 'uc-sports-general-poor-warn'}],
         'see_also': ['http://www.productontology.org/id/Sporting_goods'],
         'slot_usage': {'assessment_result': {'description': 'Structured safety '
                                                             'assessment for '
                                                             'protective_gear '
                                                             'subcategory only. '
                                                             'Required when '
                                                             'subcategory = '
                                                             'protective_gear; absent '
                                                             'otherwise.',
                                              'name': 'assessment_result',
                                              'range': 'SportsProtectiveAssessmentEnum',
                                              'required': False},
                        'condition_grade': {'description': 'Wear grade for general '
                                                           'sports equipment '
                                                           '(non-protective-gear). '
                                                           'Required when subcategory '
                                                           '≠ protective_gear.',
                                            'name': 'condition_grade',
                                            'range': 'UsedConditionGradeEnum',
                                            'required': False},
                        'demographic': {'description': 'Age/gender demographic (from '
                                                       'DemographicEnum in '
                                                       'clothing.yaml). Optional — '
                                                       'detailed completeness tier for '
                                                       'sports equipment.',
                                        'name': 'demographic',
                                        'range': 'DemographicEnum',
                                        'required': False},
                        'subcategory': {'name': 'subcategory',
                                        'range': 'SportsSubcategoryEnum',
                                        'required': True}}})

    subcategory: SportsSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    assessment_result: Optional[SportsProtectiveAssessmentEnum] = Field(default=None, description="""Structured safety assessment for protective_gear subcategory only. Required when subcategory = protective_gear; absent otherwise.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Bewertungsergebnis'},
                         'label_en': {'tag': 'label_en', 'value': 'Assessment Result'}},
         'domain_of': ['FurnitureCategory',
                       'BeddingTextilesCategory',
                       'ElectronicsCategory',
                       'SportsCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:OfferItemCondition']} })
    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Wear grade for general sports equipment (non-protective-gear). Required when subcategory ≠ protective_gear.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    sport_type: Optional[str] = Field(default=None, description="""Sport or activity type (free text, e.g. \"football\", \"cycling\").""", json_schema_extra = { "linkml_meta": {'domain_of': ['SportsCategory']} })
    demographic: Optional[DemographicEnum] = Field(default=None, description="""Age/gender demographic (from DemographicEnum in clothing.yaml). Optional — detailed completeness tier for sports equipment.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Demografie'},
                         'label_en': {'tag': 'label_en', 'value': 'Demographic'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'SportsCategory',
                       'AnyValue'],
         'see_also': ['cpi:designatedFor',
                      'schema:WearableSizeGroupBaby',
                      'schema:WearableSizeGroupChildrens',
                      'schema:WearableSizeGroupAdult']} })
    is_set_complete: Optional[bool] = Field(default=None, description="""Whether all components of the set are present. Optional — standard completeness tier.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Set vollständig'},
                         'label_en': {'tag': 'label_en', 'value': 'Set Complete'}},
         'domain_of': ['BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'StationeryCategory']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class BooksCategory(CategoryMixin):
    """
    Mixin for books and educational materials slots. Applied to BooksItem via mixins: [BooksCategory]. No UC block rules beyond the cross-cutting condition rule.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'coicop_division': {'tag': 'coicop_division', 'value': '09.5'},
                         'completeness_detailed': {'tag': 'completeness_detailed',
                                                   'value': 'subcategory, age_range, '
                                                            'language, usage, '
                                                            'condition_grade'},
                         'completeness_minimal': {'tag': 'completeness_minimal',
                                                  'value': 'subcategory, usage'},
                         'completeness_standard': {'tag': 'completeness_standard',
                                                   'value': 'subcategory, age_range, '
                                                            'usage, condition_grade'}},
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/categories/books',
         'mixin': True,
         'see_also': ['http://schema.org/Book'],
         'slot_usage': {'age_range': {'name': 'age_range',
                                      'range': 'BookAgeRangeEnum',
                                      'required': False},
                        'condition_grade': {'name': 'condition_grade',
                                            'range': 'UsedConditionGradeEnum',
                                            'required': False},
                        'subcategory': {'name': 'subcategory',
                                        'range': 'BooksSubcategoryEnum',
                                        'required': True}}})

    subcategory: BooksSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    language: Optional[str] = Field(default=None, description="""Language of item content (ISO 639-1 code, e.g. \"de\", \"en\", \"ar\", \"fa\"). Important for demand signal matching — organisations serving specific language communities have targeted language preferences. Optional — detailed completeness tier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['BooksCategory']} })
    age_range: Optional[BookAgeRangeEnum] = Field(default=None, description="""Age suitability. Range overridden per class:
  ToysItem  → ToyAgeRangeEnum
  BooksItem → BookAgeRangeEnum""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Altersbereich'},
                         'label_en': {'tag': 'label_en', 'value': 'Age Range'}},
         'domain_of': ['ToysCategory', 'BooksCategory']} })
    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Observed wear/quality grade at sorting time. Grounded in schema:OfferItemCondition and schema:itemCondition. Applied to wear-graded categories: clothing, accessories, footwear, books, stationery, household, toys, general sports equipment.
Required at sorted state regardless of usage:
  new item, no defects           → like_new
  new item, manufacturing defect → fair or poor
  used item, minimal wear        → like_new or good
Sorters record what they observe, not what the label says.
Categories using structured assessment_result enums instead (furniture, electronics, bedding, protective sports gear, mobility aids, baby equipment) do NOT declare this slot.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class StationeryCategory(CategoryMixin):
    """
    Mixin for stationery and office supply slots. Applied to StationeryItem via mixins: [StationeryCategory]. No UC block rules — condition_grade=poor captures unusable items. Sorters use good judgement for partially-used consumables.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'coicop_division': {'tag': 'coicop_division', 'value': '09.5'},
                         'completeness_detailed': {'tag': 'completeness_detailed',
                                                   'value': 'subcategory, '
                                                            'is_set_complete, usage, '
                                                            'condition_grade'},
                         'completeness_minimal': {'tag': 'completeness_minimal',
                                                  'value': 'subcategory, usage'},
                         'completeness_standard': {'tag': 'completeness_standard',
                                                   'value': 'subcategory, '
                                                            'is_set_complete, usage, '
                                                            'condition_grade'}},
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/categories/stationery',
         'mixin': True,
         'see_also': ['http://www.productontology.org/id/Stationery'],
         'slot_usage': {'condition_grade': {'name': 'condition_grade',
                                            'range': 'UsedConditionGradeEnum',
                                            'required': False},
                        'subcategory': {'name': 'subcategory',
                                        'range': 'StationerySubcategoryEnum',
                                        'required': True}}})

    subcategory: StationerySubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    is_set_complete: Optional[bool] = Field(default=None, description="""Whether all components of the set are present. Optional — standard completeness tier.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Set vollständig'},
                         'label_en': {'tag': 'label_en', 'value': 'Set Complete'}},
         'domain_of': ['BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'StationeryCategory']} })
    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Observed wear/quality grade at sorting time. Grounded in schema:OfferItemCondition and schema:itemCondition. Applied to wear-graded categories: clothing, accessories, footwear, books, stationery, household, toys, general sports equipment.
Required at sorted state regardless of usage:
  new item, no defects           → like_new
  new item, manufacturing defect → fair or poor
  used item, minimal wear        → like_new or good
Sorters record what they observe, not what the label says.
Categories using structured assessment_result enums instead (furniture, electronics, bedding, protective sports gear, mobility aids, baby equipment) do NOT declare this slot.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class PersonalCareCategory(CategoryMixin):
    """
    Mixin for personal care, hygiene, and health product slots and UC rules. Applied to PersonalCareItem via mixins: [PersonalCareCategory]. Merges COICOP 06.1 and 12.1. See schema description for merge rationale. No condition_grade or assessment_result — is_sealed + expiry_date are the complete assessment vocabulary. See schema description.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'coicop_divisions': {'tag': 'coicop_divisions',
                                              'value': '06.1, 12.1'},
                         'completeness_detailed': {'tag': 'completeness_detailed',
                                                   'value': 'subcategory, is_sealed, '
                                                            'expiry_date, usage'},
                         'completeness_minimal': {'tag': 'completeness_minimal',
                                                  'value': 'subcategory, is_sealed, '
                                                           'usage'},
                         'completeness_standard': {'tag': 'completeness_standard',
                                                   'value': 'subcategory, is_sealed, '
                                                            'expiry_date, usage'},
                         'prescription_medication_note': {'tag': 'prescription_medication_note',
                                                          'value': 'Prescription '
                                                                   'medications must '
                                                                   'NOT be accepted. '
                                                                   'Flag for '
                                                                   'pharmaceutical '
                                                                   'disposal. This is '
                                                                   'operational '
                                                                   'procedure — not '
                                                                   'enforceable by '
                                                                   'schema rule.'}},
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/categories/personal_care',
         'mixin': True,
         'rules': [{'description': 'Unsealed consumable personal care products must '
                                   'not be redistributed. A PC (Policy Constraint) '
                                   'override at the org level can permit specific '
                                   'subcategories (e.g. bulk bar soap) if org policy '
                                   'allows. action: block.',
                    'postconditions': {'slot_conditions': {'lifecycle_state': {'name': 'lifecycle_state',
                                                                               'none_of': [{'equals_string': 'stored'},
                                                                                           {'equals_string': 'distributed'}]}}},
                    'preconditions': {'slot_conditions': {'is_sealed': {'equals_string': 'false',
                                                                        'name': 'is_sealed'},
                                                          'subcategory': {'any_of': [{'equals_string': 'soap_body_wash'},
                                                                                     {'equals_string': 'shampoo_conditioner'},
                                                                                     {'equals_string': 'dental'},
                                                                                     {'equals_string': 'deodorant'},
                                                                                     {'equals_string': 'sanitary_products'},
                                                                                     {'equals_string': 'nappies_incontinence'},
                                                                                     {'equals_string': 'skincare'},
                                                                                     {'equals_string': 'cosmetics'},
                                                                                     {'equals_string': 'hair_styling'},
                                                                                     {'equals_string': 'otc_medication'},
                                                                                     {'equals_string': 'first_aid'},
                                                                                     {'equals_string': 'medical_consumables'}],
                                                                          'name': 'subcategory'}}},
                    'title': 'uc-personal-care-unsealed-consumables-block'},
                   {'description': 'Used personal care tools must not be '
                                   'redistributed. Health and sanitary safety — no PC '
                                   'override permitted. action: block.',
                    'postconditions': {'slot_conditions': {'lifecycle_state': {'name': 'lifecycle_state',
                                                                               'none_of': [{'equals_string': 'stored'},
                                                                                           {'equals_string': 'distributed'}]}}},
                    'preconditions': {'slot_conditions': {'subcategory': {'equals_string': 'personal_care_tools',
                                                                          'name': 'subcategory'},
                                                          'usage': {'equals_string': 'used',
                                                                    'name': 'usage'}}},
                    'title': 'uc-personal-care-used-tools-block'},
                   {'annotations': {'enforcement': {'tag': 'enforcement',
                                                    'value': 'application_layer'},
                                    'uc_action': {'tag': 'uc_action', 'value': 'block'},
                                    'uc_note': {'tag': 'uc_note',
                                                'value': 'expiry_date < today — '
                                                         'runtime check by Django '
                                                         'model clean()'},
                                    'uc_suggest': {'tag': 'uc_suggest',
                                                   'value': 'disposal'}},
                    'description': 'Items past expiry date must not be redistributed. '
                                   'Runtime check — dynamic date comparison not '
                                   'expressible as a static LinkML rule. Enforced by '
                                   'Django model clean() at save time.',
                    'title': 'uc-personal-care-expired-block'}],
         'see_also': ['http://www.productontology.org/id/Personal_hygiene',
                      'https://company.auntbertha.com/openeligibility/'],
         'slot_usage': {'expiry_date': {'annotations': {'uc_action': {'tag': 'uc_action',
                                                                      'value': 'block'},
                                                        'uc_note': {'tag': 'uc_note',
                                                                    'value': 'Dynamic '
                                                                             'date '
                                                                             'comparison '
                                                                             '— '
                                                                             'runtime '
                                                                             'enforcement '
                                                                             'by '
                                                                             'Django '
                                                                             'model '
                                                                             'clean()'},
                                                        'uc_suggest': {'tag': 'uc_suggest',
                                                                       'value': 'disposal'}},
                                        'description': 'Expiry or best-before date '
                                                       'from the packaging. UC block: '
                                                       'expiry_date < today (runtime '
                                                       'check by Django model '
                                                       'clean()). Secondary safety '
                                                       'signal — important for '
                                                       'medications, skincare, food.',
                                        'name': 'expiry_date',
                                        'range': 'date'},
                        'is_sealed': {'description': "Whether the item's original "
                                                     'packaging/seal is intact. UC '
                                                     'block for most consumable '
                                                     'subcategories when false. '
                                                     'Primary safety signal for '
                                                     'personal care items — replaces '
                                                     'condition_grade.',
                                      'name': 'is_sealed',
                                      'required': True},
                        'subcategory': {'name': 'subcategory',
                                        'range': 'PersonalCareSubcategoryEnum',
                                        'required': True}}})

    subcategory: PersonalCareSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    is_sealed: bool = Field(default=..., description="""Whether the item's original packaging/seal is intact. UC block for most consumable subcategories when false. Primary safety signal for personal care items — replaces condition_grade.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de',
                                      'value': 'Versiegelte Verpackung'},
                         'label_en': {'tag': 'label_en', 'value': 'Sealed Packaging'}},
         'domain_of': ['PersonalCareCategory', 'BabyInfantCategory']} })
    expiry_date: Optional[date] = Field(default=None, description="""Expiry or best-before date from the packaging. UC block: expiry_date < today (runtime check by Django model clean()). Secondary safety signal — important for medications, skincare, food.""", json_schema_extra = { "linkml_meta": {'annotations': {'uc_action': {'tag': 'uc_action', 'value': 'block'},
                         'uc_note': {'tag': 'uc_note',
                                     'value': 'Dynamic date comparison — runtime '
                                              'enforcement by Django model clean()'},
                         'uc_suggest': {'tag': 'uc_suggest', 'value': 'disposal'}},
         'domain_of': ['PersonalCareCategory', 'BabyInfantCategory', 'FoodCategory']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class MobilityAidsCategory(CategoryMixin):
    """
    Mixin for mobility aids and assistive device slots and UC rules. Applied to MobilityAidsItem via mixins: [MobilityAidsCategory]. Uses MobilityAssessmentEnum — see schema description for rationale. assessment_result required regardless of usage.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'coicop_divisions': {'tag': 'coicop_divisions',
                                              'value': '06.1.3, 06.2'},
                         'completeness_detailed': {'tag': 'completeness_detailed',
                                                   'value': 'subcategory, '
                                                            'assessment_result, usage'},
                         'completeness_minimal': {'tag': 'completeness_minimal',
                                                  'value': 'subcategory, '
                                                           'assessment_result, usage'},
                         'completeness_standard': {'tag': 'completeness_standard',
                                                   'value': 'subcategory, '
                                                            'assessment_result, usage'},
                         'open_eligibility_category': {'tag': 'open_eligibility_category',
                                                       'value': 'Assistive '
                                                                'Technology'}},
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/categories/mobility_aids',
         'mixin': True,
         'rules': [{'description': 'Structurally compromised items must not be '
                                   'redistributed. Safety-critical — applies to new '
                                   '(manufacturing defect) and used items. action: '
                                   'block, suggest: disposal or specialist repair '
                                   'referral.',
                    'postconditions': {'slot_conditions': {'lifecycle_state': {'name': 'lifecycle_state',
                                                                               'none_of': [{'equals_string': 'stored'},
                                                                                           {'equals_string': 'distributed'}]}}},
                    'preconditions': {'slot_conditions': {'assessment_result': {'equals_string': 'structurally_compromised',
                                                                                'name': 'assessment_result'}}},
                    'title': 'uc-mobility-compromised-block'},
                   {'description': 'Items requiring specialist assessment must not '
                                   'enter general redistribution. Flag for specialist '
                                   'organisation referral. action: block from normal '
                                   'redistribution path.',
                    'postconditions': {'slot_conditions': {'lifecycle_state': {'name': 'lifecycle_state',
                                                                               'none_of': [{'equals_string': 'stored'},
                                                                                           {'equals_string': 'distributed'}]}}},
                    'preconditions': {'slot_conditions': {'assessment_result': {'equals_string': 'specialist_referral_required',
                                                                                'name': 'assessment_result'}}},
                    'title': 'uc-mobility-specialist-required-block'},
                   {'description': 'Body-contact items (hearing aids, orthotics) '
                                   'requiring cleaning before redistribution need '
                                   'sorter confirmation. action: warn — sorting_notes '
                                   'required documenting cleaning recommendation.',
                    'postconditions': {'slot_conditions': {'sorting_notes': {'name': 'sorting_notes',
                                                                             'required': True}}},
                    'preconditions': {'slot_conditions': {'assessment_result': {'equals_string': 'safe_after_cleaning',
                                                                                'name': 'assessment_result'}}},
                    'title': 'uc-mobility-safe-after-cleaning-warn'},
                   {'description': 'Non-functional powered devices require sorter '
                                   'confirmation. action: warn — sorting_notes '
                                   'required.',
                    'postconditions': {'slot_conditions': {'sorting_notes': {'name': 'sorting_notes',
                                                                             'required': True}}},
                    'preconditions': {'slot_conditions': {'assessment_result': {'equals_string': 'non_functional',
                                                                                'name': 'assessment_result'}}},
                    'title': 'uc-mobility-non-functional-warn'}],
         'see_also': ['http://www.productontology.org/id/Assistive_technology',
                      'https://company.auntbertha.com/openeligibility/'],
         'slot_usage': {'assessment_result': {'description': 'Safety and hygiene '
                                                             'assessment. Required '
                                                             'regardless of usage — '
                                                             'new mobility aids can '
                                                             'have manufacturing '
                                                             'defects.',
                                              'name': 'assessment_result',
                                              'range': 'MobilityAssessmentEnum',
                                              'required': True},
                        'subcategory': {'name': 'subcategory',
                                        'range': 'MobilityAidsSubcategoryEnum',
                                        'required': True}}})

    subcategory: MobilityAidsSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    assessment_result: MobilityAssessmentEnum = Field(default=..., description="""Safety and hygiene assessment. Required regardless of usage — new mobility aids can have manufacturing defects.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Bewertungsergebnis'},
                         'label_en': {'tag': 'label_en', 'value': 'Assessment Result'}},
         'domain_of': ['FurnitureCategory',
                       'BeddingTextilesCategory',
                       'ElectronicsCategory',
                       'SportsCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:OfferItemCondition']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class BabyInfantCategory(CategoryMixin):
    """
    Mixin for baby and infant supply slots and UC rules. Applied to BabyInfantItem via mixins: [BabyInfantCategory]. Three-track assessment model — see schema description above. EN 1888 (pushchairs), EN 716 (cots), EN 14344 (car seats), EN 14350 (feeding bottles) ground the safety UC rules.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'completeness_detailed': {'tag': 'completeness_detailed',
                                                   'value': 'subcategory, '
                                                            'manufacture_year, '
                                                            'is_complete_with_accessories, '
                                                            'usage'},
                         'completeness_minimal': {'tag': 'completeness_minimal',
                                                  'value': 'subcategory, usage'},
                         'completeness_standard': {'tag': 'completeness_standard',
                                                   'value': 'subcategory, usage'},
                         'regulatory_references': {'tag': 'regulatory_references',
                                                   'value': 'EN 1888, EN 716, EN '
                                                            '14344, EN 14350, EN '
                                                            '16781'},
                         'track_consumable_subcategories': {'tag': 'track_consumable_subcategories',
                                                            'value': 'infant_formula, '
                                                                     'feeding_bottles_teats, '
                                                                     'baby_food'},
                         'track_general_subcategories': {'tag': 'track_general_subcategories',
                                                         'value': 'bath_equipment, '
                                                                  'changing, '
                                                                  'baby_monitors, '
                                                                  'bouncers_swings, '
                                                                  'breastfeeding, '
                                                                  'other'},
                         'track_structural_subcategories': {'tag': 'track_structural_subcategories',
                                                            'value': 'pushchairs_prams, '
                                                                     'cots_cribs, '
                                                                     'baby_carriers, '
                                                                     'high_chairs, '
                                                                     'car_seats, '
                                                                     'sleeping_bags'}},
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/categories/baby_infant',
         'mixin': True,
         'rules': [{'description': 'Safety-critical baby equipment requires a '
                                   'structured assessment. Required regardless of '
                                   'usage — new equipment can have defects. Standards: '
                                   'EN 1888 (pushchairs), EN 716 (cots), EN 14344 (car '
                                   'seats), EN 16781 (baby sleeping bags — '
                                   'neck/armhole openings, no loose cords).',
                    'postconditions': {'slot_conditions': {'assessment_result': {'name': 'assessment_result',
                                                                                 'required': True}}},
                    'preconditions': {'slot_conditions': {'subcategory': {'any_of': [{'equals_string': 'pushchairs_prams'},
                                                                                     {'equals_string': 'cots_cribs'},
                                                                                     {'equals_string': 'baby_carriers'},
                                                                                     {'equals_string': 'high_chairs'},
                                                                                     {'equals_string': 'car_seats'},
                                                                                     {'equals_string': 'sleeping_bags'}],
                                                                          'name': 'subcategory'}}},
                    'title': 'uc-baby-equipment-assessment-required'},
                   {'description': 'Equipment assessed as do_not_redistribute or '
                                   'structural_concern must not be redistributed. '
                                   'action: block.',
                    'postconditions': {'slot_conditions': {'lifecycle_state': {'name': 'lifecycle_state',
                                                                               'none_of': [{'equals_string': 'stored'},
                                                                                           {'equals_string': 'distributed'}]}}},
                    'preconditions': {'slot_conditions': {'assessment_result': {'any_of': [{'equals_string': 'do_not_redistribute'},
                                                                                           {'equals_string': 'structural_concern'}],
                                                                                'name': 'assessment_result'}}},
                    'title': 'uc-baby-equipment-unsafe-block'},
                   {'description': 'Car seats require manufacture_year to enable the '
                                   'runtime age check. EN 14344 standard — car seats '
                                   'over 10 years old or with unknown collision '
                                   'history must not be redistributed. '
                                   'manufacture_year must be recorded for all car '
                                   'seats (new and used) so the runtime check can '
                                   'verify the 10-year limit.',
                    'postconditions': {'slot_conditions': {'manufacture_year': {'name': 'manufacture_year',
                                                                                'required': True}}},
                    'preconditions': {'slot_conditions': {'subcategory': {'equals_string': 'car_seats',
                                                                          'name': 'subcategory'}}},
                    'title': 'uc-baby-car-seat-manufacture-year'},
                   {'description': 'Equipment requiring specialist check before '
                                   'redistribution needs sorter confirmation. action: '
                                   'warn — sorting_notes required.',
                    'postconditions': {'slot_conditions': {'sorting_notes': {'name': 'sorting_notes',
                                                                             'required': True}}},
                    'preconditions': {'slot_conditions': {'assessment_result': {'equals_string': 'requires_specialist_check',
                                                                                'name': 'assessment_result'}}},
                    'title': 'uc-baby-equipment-specialist-warn'},
                   {'description': 'Baby sleeping bags require is_winter_suitable to '
                                   'be explicitly set. A summer-weight baby sleeping '
                                   'bag (e.g. 0.5-1.0 tog) issued in a cold-weather '
                                   'response is a genuine safety risk — infants cannot '
                                   'regulate their own temperature. The thermal rating '
                                   'is typically printed on the label (tog, season '
                                   'number, or comfort temperature). action: warn — '
                                   'is_winter_suitable must be set at sorted state.',
                    'postconditions': {'slot_conditions': {'is_winter_suitable': {'name': 'is_winter_suitable',
                                                                                  'required': True}}},
                    'preconditions': {'slot_conditions': {'subcategory': {'equals_string': 'sleeping_bags',
                                                                          'name': 'subcategory'}}},
                    'title': 'uc-baby-sleeping-bag-winter-required'},
                   {'description': 'Consumable baby items require sealed packaging. '
                                   'Nappies and formula are UNHCR NFI core relief '
                                   'items — hygiene integrity is essential.',
                    'postconditions': {'slot_conditions': {'is_sealed': {'name': 'is_sealed',
                                                                         'required': True}}},
                    'preconditions': {'slot_conditions': {'subcategory': {'any_of': [{'equals_string': 'infant_formula'},
                                                                                     {'equals_string': 'feeding_bottles_teats'},
                                                                                     {'equals_string': 'baby_food'}],
                                                                          'name': 'subcategory'}}},
                    'title': 'uc-baby-consumable-sealed-required'},
                   {'description': 'Unsealed consumable baby items must not be '
                                   'redistributed. action: block.',
                    'postconditions': {'slot_conditions': {'lifecycle_state': {'name': 'lifecycle_state',
                                                                               'none_of': [{'equals_string': 'stored'},
                                                                                           {'equals_string': 'distributed'}]}}},
                    'preconditions': {'slot_conditions': {'is_sealed': {'equals_string': 'false',
                                                                        'name': 'is_sealed'},
                                                          'subcategory': {'any_of': [{'equals_string': 'infant_formula'},
                                                                                     {'equals_string': 'feeding_bottles_teats'},
                                                                                     {'equals_string': 'baby_food'}],
                                                                          'name': 'subcategory'}}},
                    'title': 'uc-baby-consumable-unsealed-block'},
                   {'description': 'Used feeding bottles and teats must not be '
                                   'redistributed. Hygiene and infant safety — EN '
                                   '14350 (drinking equipment for children). action: '
                                   'block — no override.',
                    'postconditions': {'slot_conditions': {'lifecycle_state': {'name': 'lifecycle_state',
                                                                               'none_of': [{'equals_string': 'stored'},
                                                                                           {'equals_string': 'distributed'}]}}},
                    'preconditions': {'slot_conditions': {'subcategory': {'equals_string': 'feeding_bottles_teats',
                                                                          'name': 'subcategory'},
                                                          'usage': {'equals_string': 'used',
                                                                    'name': 'usage'}}},
                    'title': 'uc-baby-feeding-used-block'},
                   {'annotations': {'enforcement': {'tag': 'enforcement',
                                                    'value': 'application_layer'},
                                    'uc_action': {'tag': 'uc_action', 'value': 'block'},
                                    'uc_note': {'tag': 'uc_note',
                                                'value': 'expiry_date < today — '
                                                         'runtime check by Django '
                                                         'model clean()'},
                                    'uc_suggest': {'tag': 'uc_suggest',
                                                   'value': 'disposal'}},
                    'description': 'Consumables past expiry must not be redistributed. '
                                   'Runtime check.',
                    'title': 'uc-baby-consumable-expiry-block'},
                   {'description': 'General baby gear requires condition_grade wear '
                                   'assessment.',
                    'postconditions': {'slot_conditions': {'condition_grade': {'name': 'condition_grade',
                                                                               'required': True}}},
                    'preconditions': {'slot_conditions': {'subcategory': {'any_of': [{'equals_string': 'bath_equipment'},
                                                                                     {'equals_string': 'changing'},
                                                                                     {'equals_string': 'baby_monitors'},
                                                                                     {'equals_string': 'bouncers_swings'},
                                                                                     {'equals_string': 'breastfeeding'},
                                                                                     {'equals_string': 'other'}],
                                                                          'name': 'subcategory'}}},
                    'title': 'uc-baby-general-condition-grade-required'}],
         'see_also': ['http://www.productontology.org/id/Baby_transport',
                      'https://company.auntbertha.com/openeligibility/'],
         'slot_usage': {'assessment_result': {'description': 'Structural/provenance '
                                                             'assessment for Track 1 '
                                                             'safety-critical '
                                                             'equipment. Required when '
                                                             'subcategory in '
                                                             '[pushchairs_prams, '
                                                             'cots_cribs, '
                                                             'baby_carriers, '
                                                             'high_chairs, car_seats, '
                                                             'sleeping_bags].',
                                              'name': 'assessment_result',
                                              'range': 'BabyEquipmentAssessmentEnum',
                                              'required': False},
                        'condition_grade': {'description': 'Wear grade for Track 3 '
                                                           'general baby gear. '
                                                           'Required when subcategory '
                                                           'in [bath_equipment, '
                                                           'changing, baby_monitors, '
                                                           'bouncers_swings, '
                                                           'breastfeeding, other].',
                                            'name': 'condition_grade',
                                            'range': 'UsedConditionGradeEnum',
                                            'required': False},
                        'is_sealed': {'description': 'Packaging/seal integrity for '
                                                     'Track 2 consumables. Required '
                                                     'when subcategory in '
                                                     '[infant_formula, '
                                                     'feeding_bottles_teats, '
                                                     'baby_food].',
                                      'name': 'is_sealed',
                                      'required': False},
                        'is_winter_suitable': {'description': 'Whether this item '
                                                              'provides meaningful '
                                                              'warmth in cold '
                                                              'conditions. Required '
                                                              'for sleeping_bags '
                                                              '(UC-enforced) — a '
                                                              'summer-weight baby '
                                                              'sleeping bag in '
                                                              'cold-weather '
                                                              'distribution is a '
                                                              'safety risk. Thermal '
                                                              'rating (e.g. "2.5 tog", '
                                                              '"0°C comfort limit") '
                                                              'may be noted in '
                                                              'sorting_notes.',
                                               'name': 'is_winter_suitable',
                                               'range': 'boolean',
                                               'required': False},
                        'subcategory': {'name': 'subcategory',
                                        'range': 'BabyInfantSubcategoryEnum',
                                        'required': True}}})

    subcategory: BabyInfantSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    assessment_result: Optional[BabyEquipmentAssessmentEnum] = Field(default=None, description="""Structural/provenance assessment for Track 1 safety-critical equipment. Required when subcategory in [pushchairs_prams, cots_cribs, baby_carriers, high_chairs, car_seats, sleeping_bags].""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Bewertungsergebnis'},
                         'label_en': {'tag': 'label_en', 'value': 'Assessment Result'}},
         'domain_of': ['FurnitureCategory',
                       'BeddingTextilesCategory',
                       'ElectronicsCategory',
                       'SportsCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:OfferItemCondition']} })
    manufacture_year: Optional[int] = Field(default=None, description="""Year of manufacture. Required for car seats (EN 14344 — 10-year redistribution limit). Recommended for cots (EN 716) and pushchairs (EN 1888) to verify age of safety-relevant components.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Herstellungsjahr'},
                         'label_en': {'tag': 'label_en', 'value': 'Manufacture year'},
                         'show_if': {'tag': 'show_if',
                                     'value': 'subcategory in [car_seats, cots_cribs, '
                                              'pushchairs_prams]'}},
         'domain_of': ['BabyInfantCategory']} })
    includes_original_accessories: Optional[bool] = Field(default=None, description="""Whether standard accessories/components are included (e.g. pushchair includes rain cover and harness; cot includes mattress and side rails).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de',
                                      'value': 'Enthält Originalzubehör'},
                         'label_en': {'tag': 'label_en',
                                      'value': 'Includes original accessories'}},
         'domain_of': ['BabyInfantCategory']} })
    is_winter_suitable: Optional[bool] = Field(default=None, description="""Whether this item provides meaningful warmth in cold conditions. Required for sleeping_bags (UC-enforced) — a summer-weight baby sleeping bag in cold-weather distribution is a safety risk. Thermal rating (e.g. \"2.5 tog\", \"0°C comfort limit\") may be noted in sorting_notes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ClothingCategory',
                       'FootwearCategory',
                       'BeddingTextilesCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:itemCondition']} })
    is_sealed: Optional[bool] = Field(default=None, description="""Packaging/seal integrity for Track 2 consumables. Required when subcategory in [infant_formula, feeding_bottles_teats, baby_food].""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de',
                                      'value': 'Versiegelte Verpackung'},
                         'label_en': {'tag': 'label_en', 'value': 'Sealed Packaging'}},
         'domain_of': ['PersonalCareCategory', 'BabyInfantCategory']} })
    expiry_date: Optional[date] = Field(default=None, description="""Expiry or best-before date. UC block: expiry_date < today (runtime check).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Ablaufdatum'},
                         'label_en': {'tag': 'label_en', 'value': 'Expiry Date'},
                         'uc_action': {'tag': 'uc_action', 'value': 'block'},
                         'uc_note': {'tag': 'uc_note',
                                     'value': 'Dynamic date comparison — runtime '
                                              'enforcement'},
                         'uc_suggest': {'tag': 'uc_suggest', 'value': 'disposal'}},
         'domain_of': ['PersonalCareCategory', 'BabyInfantCategory', 'FoodCategory']} })
    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Wear grade for Track 3 general baby gear. Required when subcategory in [bath_equipment, changing, baby_monitors, bouncers_swings, breastfeeding, other].""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class ClothingItem(ClothingCategory, DonationItem):
    """
    Clothing garments: tops, bottoms, outerwear, underwear, nightwear, sportswear. COICOP 03.1 (clothing). Grounded in CPI (Clothing Product Information ontology):
      http://www.ebusiness-unibw.org/ontologies/cpi/ns#ClothingAndAccessories

    Assessment: condition_grade (wear grade). The demographic→size value map and all UC rules (underwear condition, adult underwear must be new) are defined in ClothingCategory (categories/clothing.yaml).
    Lifecycle-aware rules here:
      lc-sorted-clothing-condition-grade-required
      lc-sorted-clothing-demographic-required
      lc-sorted-clothing-size-required
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'label_de': {'tag': 'label_de', 'value': 'Kleidung'},
                         'label_en': {'tag': 'label_en', 'value': 'Clothing'}},
         'class_uri': 'cpi:ClothingAndAccessories',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_item',
         'mixins': ['ClothingCategory'],
         'rules': [{'description': 'is_winter_suitable required at sorted state for '
                                   'tops, bottoms, outerwear, and nightwear. Not '
                                   'required for underwear (thermally neutral base '
                                   'layer) or sportswear (assessed differently by the '
                                   'SportsItem category). The thermal character of a '
                                   'garment is independent of usage — sorters assess '
                                   'what they hold.',
                    'postconditions': {'slot_conditions': {'is_winter_suitable': {'name': 'is_winter_suitable',
                                                                                  'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'},
                                                          'subcategory': {'any_of': [{'equals_string': 'tops'},
                                                                                     {'equals_string': 'bottoms'},
                                                                                     {'equals_string': 'outerwear'},
                                                                                     {'equals_string': 'nightwear'}],
                                                                          'name': 'subcategory'}}},
                    'title': 'lc-sorted-clothing-is-winter-suitable-required'},
                   {'description': 'For used clothing (usage = used), condition_grade '
                                   'is required.',
                    'postconditions': {'slot_conditions': {'condition_grade': {'name': 'condition_grade',
                                                                               'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'},
                                                          'usage': {'equals_string': 'used',
                                                                    'name': 'usage'}}},
                    'title': 'lc-used-clothing-condition-grade-required'},
                   {'description': 'demographic required at sorted state for all '
                                   'ClothingItem instances. Drives demand signal '
                                   'matching (e.g. "adult female tops, size M").',
                    'postconditions': {'slot_conditions': {'demographic': {'name': 'demographic',
                                                                           'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-clothing-demographic-required'},
                   {'description': 'size required at sorted state. Drives demand '
                                   'signal matching and storage slot assignment.',
                    'postconditions': {'slot_conditions': {'size': {'name': 'size',
                                                                    'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-clothing-size-required'},
                   {'description': 'subcategory required at sorted state. Drives '
                                   'demand signal matching, UC rule evaluation '
                                   '(underwear constraints), and storage routing. Not '
                                   'required at received state — category is known but '
                                   'subcategory is determined during sorting.',
                    'postconditions': {'slot_conditions': {'subcategory': {'name': 'subcategory',
                                                                           'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-clothing-subcategory-required'}],
         'see_also': ['http://www.ebusiness-unibw.org/ontologies/cpi/ns#ClothingAndAccessories']})

    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Observed wear/quality grade at sorting time. Grounded in schema:OfferItemCondition and schema:itemCondition. Applied to wear-graded categories: clothing, accessories, footwear, books, stationery, household, toys, general sports equipment.
Required at sorted state regardless of usage:
  new item, no defects           → like_new
  new item, manufacturing defect → fair or poor
  used item, minimal wear        → like_new or good
Sorters record what they observe, not what the label says.
Categories using structured assessment_result enums instead (furniture, electronics, bedding, protective sports gear, mobility aids, baby equipment) do NOT declare this slot.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    subcategory: Optional[ClothingSubcategoryEnum] = Field(default=None, description="""Subcategory becomes a required field on DonationItem when item's lifecycle is sorted.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    is_winter_suitable: Optional[bool] = Field(default=None, description="""Whether this garment provides meaningful warmth in cold-weather conditions. Required at standard completeness for tops, bottoms, outerwear, nightwear. The sorter's direct assessment — not inferred from subcategory or material. The primary emergency distribution filter: \"all winter-suitable clothing for adults.\"""", json_schema_extra = { "linkml_meta": {'domain_of': ['ClothingCategory',
                       'FootwearCategory',
                       'BeddingTextilesCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:itemCondition']} })
    demographic: Optional[DemographicEnum] = Field(default=None, description="""Combined age-and-gender demographic suitability of clothing items. Valid values depend on subcategory (see value_map above). Grounded in cpi:designatedFor and schema.org wearable size groups. Not applicable to AccessoriesItem — accessories use the simpler AccessoriesDemographicEnum (baby/child/adult/all_ages).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Demografie'},
                         'label_en': {'tag': 'label_en', 'value': 'Demographic'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'SportsCategory',
                       'AnyValue'],
         'see_also': ['cpi:designatedFor',
                      'schema:WearableSizeGroupBaby',
                      'schema:WearableSizeGroupChildrens',
                      'schema:WearableSizeGroupAdult']} })
    size: Optional[ClothingSizeEnum] = Field(default=None, description="""Size of the clothing item. Valid values constrained by demographic via value map rules (vm-size-baby, vm-size-child, vm-size-adult). Grounded in cpi:ClothingSize and schema.org size systems.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ClothingCategory', 'AnyValue'],
         'see_also': ['cpi:ClothingSize',
                      'schema:WearableSizeGroupAdult',
                      'schema:WearableSizeSystemEU']} })
    season: Optional[list[SeasonEnum]] = Field(default=None, description="""Seasonal suitability. Optional — detailed completeness tier. Multivalued: a garment may span seasons (e.g. spring_autumn + summer). VM rules auto-derive is_winter_suitable for the extreme values (winter, summer, all_season); spring_autumn leaves the sorter to set is_winter_suitable explicitly.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Saison'},
                         'label_en': {'tag': 'label_en', 'value': 'Season'}},
         'domain_of': ['ClothingCategory', 'FootwearCategory'],
         'see_also': ['schema:itemCondition']} })
    intact_labels: Optional[bool] = Field(default=None, description="""Whether care and composition labels are present and legible. Improves match quality for beneficiaries with care requirements (e.g. allergy to certain materials). Detailed completeness tier.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de',
                                      'value': 'Unversehrte Pflege- und '
                                               'Materialetiketten'},
                         'label_en': {'tag': 'label_en',
                                      'value': 'Intact care and composition labels'},
                         'show_if': {'tag': 'show_if',
                                     'value': 'subcategory in [tops, bottoms, '
                                              'outerwear, underwear, nightwear, '
                                              'sportswear]'}},
         'domain_of': ['ClothingCategory']} })
    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    usage: ItemUsageEnum = Field(default=..., description="""Provenance condition — was the item ever used before donation? Orthogonal to condition_grade and assessment_result. Maps to schema:NewCondition / schema:UsedCondition. usage = new does NOT imply no defects — manufacturing defects are possible and assessment must always be performed regardless of usage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Provenance'},
                         'label_en': {'tag': 'label_en', 'value': 'Provenance'}},
         'domain_of': ['DonationItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:NewCondition',
                      'schema:UsedCondition'],
         'slot_uri': 'schema:itemCondition'} })
    category: Literal["ClothingItem"] = Field(default="ClothingItem", description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'designates_type': True,
         'domain_of': ['DonationItem', 'DemandSignal'],
         'notes': ['Due to a limitation in LinkML, the designates_type annotation was '
                   'removed because the range is an Enum and not a string.'],
         'slot_uri': 'schema:additionalType'} })
    lifecycle_state: ItemLifecycleStateEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    attribute_completeness: Optional[AttributeCompletenessEnum] = Field(default=None, description="""Data quality tier set by the fragment engine on sorting completion. Not derived from field presence. Not a lifecycle gate. Used by the match engine to filter candidates by data quality tier. See AttributeCompletenessEnum for the relationship to lifecycle_state. Set by: fragment_engine. Read by: match_engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    source_collection: Optional[str] = Field(default=None, description="""FK — the DonationCollection (arrival type) this item was registered from. Null for items not arriving as part of a collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    storage_unit: Optional[str] = Field(default=None, description="""FK — set when lifecycle_state transitions to stored. Null until the item reaches stored state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    sorting_notes: Optional[str] = Field(default=None, description="""Free-text notes recorded by the sorter during sorting. Required by UC warn rules to capture explicit sorter confirmation (e.g. incomplete pair, body-contact item, inconclusive assessment).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationItem']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    updated_at: datetime  = Field(default=..., description="""Timestamp when the entity record was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class AccessoriesItem(AccessoriesCategory, DonationItem):
    """
    Fashion and personal accessories: hats, scarves, gloves, belts, bags, jewellery, sunglasses, watches. COICOP 03.1 (grouped with clothing by COICOP; separated here for progressive UI disclosure and schema clarity).
    Separated from ClothingItem because:
      - No demographic→size value map — accessories are not sized XS–XXL
      - Clothing UC rules (underwear condition) do not apply
      - Progressive disclosure: \"clothing or accessory?\" is a clean first
        branch in the sorting UI
      - AccessoriesDemographicEnum uses a simpler age-only vocabulary
        (baby/child/adult/all_ages) — gender is not meaningful for most
        accessories

    Assessment: condition_grade (wear grade).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'label_de': {'tag': 'label_de', 'value': 'Accesoires'},
                         'label_en': {'tag': 'label_en', 'value': 'Accessories'}},
         'class_uri': 'pto:Fashion_accessory',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_item',
         'mixins': ['AccessoriesCategory'],
         'rules': [{'description': 'condition_grade required at sorted state '
                                   'regardless of usage.',
                    'postconditions': {'slot_conditions': {'condition_grade': {'name': 'condition_grade',
                                                                               'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-accessories-condition-grade-required'}],
         'see_also': ['http://www.productontology.org/id/Fashion_accessory']})

    subcategory: AccessoriesSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    demographic: Optional[AccessoriesDemographicEnum] = Field(default=None, description="""Optional age group. Not applicable to most accessories (bags, jewellery, belts are generally adult by default). Use for clearly age-targeted items: children's hats, baby mittens, baby carriers (though carriers belong in BabyInfantItem).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Demografie'},
                         'label_en': {'tag': 'label_en', 'value': 'Demographic'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'SportsCategory',
                       'AnyValue'],
         'see_also': ['cpi:designatedFor',
                      'schema:WearableSizeGroupBaby',
                      'schema:WearableSizeGroupChildrens',
                      'schema:WearableSizeGroupAdult']} })
    material: Optional[str] = Field(default=None, description="""Primary material (e.g. \"leather\", \"wool\", \"cotton\", \"metal\"). Free text — no controlled vocabulary at this stage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })
    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Observed wear/quality grade at sorting time. Grounded in schema:OfferItemCondition and schema:itemCondition. Applied to wear-graded categories: clothing, accessories, footwear, books, stationery, household, toys, general sports equipment.
Required at sorted state regardless of usage:
  new item, no defects           → like_new
  new item, manufacturing defect → fair or poor
  used item, minimal wear        → like_new or good
Sorters record what they observe, not what the label says.
Categories using structured assessment_result enums instead (furniture, electronics, bedding, protective sports gear, mobility aids, baby equipment) do NOT declare this slot.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    usage: ItemUsageEnum = Field(default=..., description="""Provenance condition — was the item ever used before donation? Orthogonal to condition_grade and assessment_result. Maps to schema:NewCondition / schema:UsedCondition. usage = new does NOT imply no defects — manufacturing defects are possible and assessment must always be performed regardless of usage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Provenance'},
                         'label_en': {'tag': 'label_en', 'value': 'Provenance'}},
         'domain_of': ['DonationItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:NewCondition',
                      'schema:UsedCondition'],
         'slot_uri': 'schema:itemCondition'} })
    category: Literal["AccessoriesItem"] = Field(default="AccessoriesItem", description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'designates_type': True,
         'domain_of': ['DonationItem', 'DemandSignal'],
         'notes': ['Due to a limitation in LinkML, the designates_type annotation was '
                   'removed because the range is an Enum and not a string.'],
         'slot_uri': 'schema:additionalType'} })
    lifecycle_state: ItemLifecycleStateEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    attribute_completeness: Optional[AttributeCompletenessEnum] = Field(default=None, description="""Data quality tier set by the fragment engine on sorting completion. Not derived from field presence. Not a lifecycle gate. Used by the match engine to filter candidates by data quality tier. See AttributeCompletenessEnum for the relationship to lifecycle_state. Set by: fragment_engine. Read by: match_engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    source_collection: Optional[str] = Field(default=None, description="""FK — the DonationCollection (arrival type) this item was registered from. Null for items not arriving as part of a collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    storage_unit: Optional[str] = Field(default=None, description="""FK — set when lifecycle_state transitions to stored. Null until the item reaches stored state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    sorting_notes: Optional[str] = Field(default=None, description="""Free-text notes recorded by the sorter during sorting. Required by UC warn rules to capture explicit sorter confirmation (e.g. incomplete pair, body-contact item, inconclusive assessment).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationItem']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    updated_at: datetime  = Field(default=..., description="""Timestamp when the entity record was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })


class FootwearItem(FootwearCategory, DonationItem):
    """
    Footwear: shoes, boots, sandals, slippers. COICOP 03.2 (footwear). Separated from ClothingItem because:
      - Shoe sizing systems (EU/UK/US/CM) differ from clothing sizes
      - Pair-completeness is a footwear-specific assessment concern
    Assessment: condition_grade (wear grade).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'label_de': {'tag': 'label_de', 'value': 'Schuhe'},
                         'label_en': {'tag': 'label_en', 'value': 'Footwear'}},
         'class_uri': 'pto:Footwear',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_item',
         'mixins': ['FootwearCategory'],
         'rules': [{'description': 'condition_grade required at sorted state '
                                   'regardless of usage.',
                    'postconditions': {'slot_conditions': {'condition_grade': {'name': 'condition_grade',
                                                                               'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-footwear-condition-grade-required'},
                   {'description': 'is_winter_suitable required at sorted state. The '
                                   'thermal and weather-protection character of '
                                   'footwear is operationally critical for '
                                   'cold-weather emergency distribution — boots and '
                                   'sandals serve entirely different needs. Sorter '
                                   'makes the call; fragment compiler provides '
                                   'subcategory-based hints only.',
                    'postconditions': {'slot_conditions': {'is_winter_suitable': {'name': 'is_winter_suitable',
                                                                                  'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-footwear-is-winter-suitable-required'},
                   {'description': 'shoe_size and shoe_size_system required at sorted '
                                   'state. System required alongside size to '
                                   'disambiguate EU 42 from UK 8.',
                    'postconditions': {'slot_conditions': {'shoe_size': {'name': 'shoe_size',
                                                                         'required': True},
                                                           'shoe_size_system': {'name': 'shoe_size_system',
                                                                                'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-footwear-size-required'}],
         'see_also': ['http://www.productontology.org/id/Footwear']})

    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Observed wear/quality grade at sorting time. Grounded in schema:OfferItemCondition and schema:itemCondition. Applied to wear-graded categories: clothing, accessories, footwear, books, stationery, household, toys, general sports equipment.
Required at sorted state regardless of usage:
  new item, no defects           → like_new
  new item, manufacturing defect → fair or poor
  used item, minimal wear        → like_new or good
Sorters record what they observe, not what the label says.
Categories using structured assessment_result enums instead (furniture, electronics, bedding, protective sports gear, mobility aids, baby equipment) do NOT declare this slot.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    subcategory: FootwearSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    is_pair_complete: Optional[bool] = Field(default=None, description="""Whether both shoes of the pair are present. UC warn if false — sorting_notes required.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de',
                                      'value': 'Ist das Paar vollständig?'},
                         'label_en': {'tag': 'label_en', 'value': 'is pair complete'}},
         'domain_of': ['FootwearCategory']} })
    is_winter_suitable: Optional[bool] = Field(default=None, description="""Whether this footwear provides meaningful warmth and weather protection in cold conditions. Required at standard completeness. Fragment compiler may pre-fill: boots → true, sandals → false. Sorter always overrides (e.g. a lightweight canvas boot → false).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ClothingCategory',
                       'FootwearCategory',
                       'BeddingTextilesCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:itemCondition']} })
    demographic: Optional[DemographicEnum] = Field(default=None, description="""Combined age-and-gender demographic suitability of clothing items. Valid values depend on subcategory (see value_map above). Grounded in cpi:designatedFor and schema.org wearable size groups. Not applicable to AccessoriesItem — accessories use the simpler AccessoriesDemographicEnum (baby/child/adult/all_ages).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Demografie'},
                         'label_en': {'tag': 'label_en', 'value': 'Demographic'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'SportsCategory',
                       'AnyValue'],
         'see_also': ['cpi:designatedFor',
                      'schema:WearableSizeGroupBaby',
                      'schema:WearableSizeGroupChildrens',
                      'schema:WearableSizeGroupAdult']} })
    shoe_size: Optional[str] = Field(default=None, description="""Shoe size as a string. Use with shoe_size_system to disambiguate (e.g. \"42\" with system \"EU\", \"8\" with system \"UK\").""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Schuhgröße'},
                         'label_en': {'tag': 'label_en', 'value': 'shoe size'}},
         'domain_of': ['FootwearCategory']} })
    shoe_size_system: Optional[ShoeSizeSystemEnum] = Field(default=None, description="""Sizing system for the shoe_size value.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Schuhgrößen-System'},
                         'label_en': {'tag': 'label_en', 'value': 'shoe size system'}},
         'domain_of': ['FootwearCategory']} })
    season: Optional[list[SeasonEnum]] = Field(default=None, description="""Seasonal suitability. Optional — detailed completeness tier. Same VM auto-derivation as ClothingCategory:
  winter → is_winter_suitable = true
  summer → is_winter_suitable = false
  all_season → is_winter_suitable = true
  spring_autumn → sorter decides is_winter_suitable explicitly.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Saison'},
                         'label_en': {'tag': 'label_en', 'value': 'Season'}},
         'domain_of': ['ClothingCategory', 'FootwearCategory'],
         'see_also': ['schema:itemCondition']} })
    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    usage: ItemUsageEnum = Field(default=..., description="""Provenance condition — was the item ever used before donation? Orthogonal to condition_grade and assessment_result. Maps to schema:NewCondition / schema:UsedCondition. usage = new does NOT imply no defects — manufacturing defects are possible and assessment must always be performed regardless of usage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Provenance'},
                         'label_en': {'tag': 'label_en', 'value': 'Provenance'}},
         'domain_of': ['DonationItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:NewCondition',
                      'schema:UsedCondition'],
         'slot_uri': 'schema:itemCondition'} })
    category: Literal["FootwearItem"] = Field(default="FootwearItem", description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'designates_type': True,
         'domain_of': ['DonationItem', 'DemandSignal'],
         'notes': ['Due to a limitation in LinkML, the designates_type annotation was '
                   'removed because the range is an Enum and not a string.'],
         'slot_uri': 'schema:additionalType'} })
    lifecycle_state: ItemLifecycleStateEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    attribute_completeness: Optional[AttributeCompletenessEnum] = Field(default=None, description="""Data quality tier set by the fragment engine on sorting completion. Not derived from field presence. Not a lifecycle gate. Used by the match engine to filter candidates by data quality tier. See AttributeCompletenessEnum for the relationship to lifecycle_state. Set by: fragment_engine. Read by: match_engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    source_collection: Optional[str] = Field(default=None, description="""FK — the DonationCollection (arrival type) this item was registered from. Null for items not arriving as part of a collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    storage_unit: Optional[str] = Field(default=None, description="""FK — set when lifecycle_state transitions to stored. Null until the item reaches stored state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    sorting_notes: Optional[str] = Field(default=None, description="""Free-text notes recorded by the sorter during sorting. Required by UC warn rules to capture explicit sorter confirmation (e.g. incomplete pair, body-contact item, inconclusive assessment).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationItem']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    updated_at: datetime  = Field(default=..., description="""Timestamp when the entity record was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class FurnitureItem(FurnitureCategory, DonationItem):
    """
    Structural furniture: chairs, tables, beds, wardrobes, shelving. COICOP 05.1 (furniture and furnishings). Grounded in Product Types Ontology:
      http://www.productontology.org/id/Furniture

    Assessment: FurnitureAssessmentEnum (structured structural assessment). Structural soundness is the primary redistribution signal for furniture — a scratched but solid chair is redistributable; a wobbly but clean one is not. assessment_result required regardless of usage because new flatpack furniture can have manufacturing defects or assembly issues.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'label_de': {'tag': 'label_de', 'value': 'Mebel'},
                         'label_en': {'tag': 'label_en', 'value': 'Furniture'}},
         'class_uri': 'pto:Furniture',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_item',
         'mixins': ['FurnitureCategory'],
         'rules': [{'description': 'assessment_result required at sorted state '
                                   'regardless of usage. New furniture can have '
                                   'manufacturing defects (cracked panels, defective '
                                   'joints, damaged flatpack components).',
                    'postconditions': {'slot_conditions': {'assessment_result': {'name': 'assessment_result',
                                                                                 'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-furniture-assessment-required'}],
         'see_also': ['http://www.productontology.org/id/Furniture']})

    subcategory: FurnitureSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    material: Optional[FurnitureMaterialEnum] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })
    assessment_result: FurnitureAssessmentEnum = Field(default=..., description="""Structural and quality assessment. Required regardless of usage — new furniture can have manufacturing defects or assembly issues.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Bewertungsergebnis'},
                         'label_en': {'tag': 'label_en', 'value': 'Assessment Result'}},
         'domain_of': ['FurnitureCategory',
                       'BeddingTextilesCategory',
                       'ElectronicsCategory',
                       'SportsCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:OfferItemCondition']} })
    dimensions: Optional[str] = Field(default=None, description="""Physical dimensions in centimetres, e.g. \"100*50*75 cm\" (W*D*H). Required for tables and beds to enable storage slot assignment and demand signal matching.""", json_schema_extra = { "linkml_meta": {'annotations': {'required_if': {'tag': 'required_if',
                                         'value': 'subcategory in [tables, beds]'}},
         'domain_of': ['FurnitureCategory'],
         'see_also': ['schema:SizeSpecification']} })
    style: Optional[str] = Field(default=None, description="""Style or design description (e.g. \"Scandinavian\", \"Industrial\", \"Rustic\"). Free text. Optional — detailed completeness tier. Supports demand signal matching for beneficiaries with style preferences.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FurnitureCategory']} })
    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    usage: ItemUsageEnum = Field(default=..., description="""Provenance condition — was the item ever used before donation? Orthogonal to condition_grade and assessment_result. Maps to schema:NewCondition / schema:UsedCondition. usage = new does NOT imply no defects — manufacturing defects are possible and assessment must always be performed regardless of usage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Provenance'},
                         'label_en': {'tag': 'label_en', 'value': 'Provenance'}},
         'domain_of': ['DonationItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:NewCondition',
                      'schema:UsedCondition'],
         'slot_uri': 'schema:itemCondition'} })
    category: Literal["FurnitureItem"] = Field(default="FurnitureItem", description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'designates_type': True,
         'domain_of': ['DonationItem', 'DemandSignal'],
         'notes': ['Due to a limitation in LinkML, the designates_type annotation was '
                   'removed because the range is an Enum and not a string.'],
         'slot_uri': 'schema:additionalType'} })
    lifecycle_state: ItemLifecycleStateEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    attribute_completeness: Optional[AttributeCompletenessEnum] = Field(default=None, description="""Data quality tier set by the fragment engine on sorting completion. Not derived from field presence. Not a lifecycle gate. Used by the match engine to filter candidates by data quality tier. See AttributeCompletenessEnum for the relationship to lifecycle_state. Set by: fragment_engine. Read by: match_engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    source_collection: Optional[str] = Field(default=None, description="""FK — the DonationCollection (arrival type) this item was registered from. Null for items not arriving as part of a collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    storage_unit: Optional[str] = Field(default=None, description="""FK — set when lifecycle_state transitions to stored. Null until the item reaches stored state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    sorting_notes: Optional[str] = Field(default=None, description="""Free-text notes recorded by the sorter during sorting. Required by UC warn rules to capture explicit sorter confirmation (e.g. incomplete pair, body-contact item, inconclusive assessment).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationItem']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    updated_at: datetime  = Field(default=..., description="""Timestamp when the entity record was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })


class BeddingTextilesItem(BeddingTextilesCategory, DonationItem):
    """
    Bedding and household textiles: blankets, duvets, mattresses, pillows, sleeping bags, towels, curtains. COICOP 05.2 (household textiles).
    Separated from HouseholdItem following COICOP 05.2 and UNHCR NFI kit standards, which list blankets and sleeping mats as core relief items at the same priority level as clothing — not incidental household goods. The hygiene assessment vocabulary (BeddingAssessmentEnum) also differs fundamentally from household item wear grading.
    Assessment: BeddingAssessmentEnum (hygiene and condition assessment). Hygiene state is the primary redistribution signal for bedding — a worn but clean blanket is redistributable; a visually intact but stained mattress is not. assessment_result required regardless of usage because new items may have packaging damage or factory soiling.
    UNHCR NFI standards reference:
      https://emergency.unhcr.org/emergency-assistance/core-relief-items/
      kind-non-food-item-distribution
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'label_de': {'tag': 'label_de',
                                      'value': 'Bettwäsche und Textilien'},
                         'label_en': {'tag': 'label_en',
                                      'value': 'Bedding and Textiles'}},
         'class_uri': 'pto:Bedding',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_item',
         'mixins': ['BeddingTextilesCategory'],
         'rules': [{'description': 'assessment_result required at sorted state '
                                   'regardless of usage. New items may have packaging '
                                   'damage or factory soiling.',
                    'postconditions': {'slot_conditions': {'assessment_result': {'name': 'assessment_result',
                                                                                 'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-bedding-assessment-required'}],
         'see_also': ['http://www.productontology.org/id/Bedding',
                      'https://emergency.unhcr.org/emergency-assistance/core-relief-items/kind-non-food-item-distribution']})

    subcategory: BeddingTextilesSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    assessment_result: BeddingAssessmentEnum = Field(default=..., description="""Hygiene and condition assessment. Required regardless of usage — new items may have packaging damage or factory soiling.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Bewertungsergebnis'},
                         'label_en': {'tag': 'label_en', 'value': 'Assessment Result'}},
         'domain_of': ['FurnitureCategory',
                       'BeddingTextilesCategory',
                       'ElectronicsCategory',
                       'SportsCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:OfferItemCondition']} })
    is_set_complete: Optional[bool] = Field(default=None, description="""Whether all components of the set are present. Optional — standard completeness tier.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Set vollständig'},
                         'label_en': {'tag': 'label_en', 'value': 'Set Complete'}},
         'domain_of': ['BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'StationeryCategory']} })
    is_winter_suitable: Optional[bool] = Field(default=None, description="""Whether this bedding item provides meaningful warmth for cold conditions. Required at standard completeness for blankets, duvets_quilts, and sleeping_bags. Not meaningful for towels, curtains, tablecloths. Suppressed by fragment compiler for those subcategories via the season_relevant_subcategories annotation.
Critical for sleeping bags — a summer sleeping bag issued in a cold-weather emergency is dangerous. Thermal rating in tog or season number may be noted in sorting_notes as free text.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ClothingCategory',
                       'FootwearCategory',
                       'BeddingTextilesCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:itemCondition']} })
    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    usage: ItemUsageEnum = Field(default=..., description="""Provenance condition — was the item ever used before donation? Orthogonal to condition_grade and assessment_result. Maps to schema:NewCondition / schema:UsedCondition. usage = new does NOT imply no defects — manufacturing defects are possible and assessment must always be performed regardless of usage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Provenance'},
                         'label_en': {'tag': 'label_en', 'value': 'Provenance'}},
         'domain_of': ['DonationItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:NewCondition',
                      'schema:UsedCondition'],
         'slot_uri': 'schema:itemCondition'} })
    category: Literal["BeddingTextilesItem"] = Field(default="BeddingTextilesItem", description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'designates_type': True,
         'domain_of': ['DonationItem', 'DemandSignal'],
         'notes': ['Due to a limitation in LinkML, the designates_type annotation was '
                   'removed because the range is an Enum and not a string.'],
         'slot_uri': 'schema:additionalType'} })
    lifecycle_state: ItemLifecycleStateEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    attribute_completeness: Optional[AttributeCompletenessEnum] = Field(default=None, description="""Data quality tier set by the fragment engine on sorting completion. Not derived from field presence. Not a lifecycle gate. Used by the match engine to filter candidates by data quality tier. See AttributeCompletenessEnum for the relationship to lifecycle_state. Set by: fragment_engine. Read by: match_engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    source_collection: Optional[str] = Field(default=None, description="""FK — the DonationCollection (arrival type) this item was registered from. Null for items not arriving as part of a collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    storage_unit: Optional[str] = Field(default=None, description="""FK — set when lifecycle_state transitions to stored. Null until the item reaches stored state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    sorting_notes: Optional[str] = Field(default=None, description="""Free-text notes recorded by the sorter during sorting. Required by UC warn rules to capture explicit sorter confirmation (e.g. incomplete pair, body-contact item, inconclusive assessment).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationItem']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    updated_at: datetime  = Field(default=..., description="""Timestamp when the entity record was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class HouseholdItem(HouseholdCategory, DonationItem):
    """
    Household and kitchen goods: cookware, crockery, small appliances, cleaning tools, home decor, garden tools. COICOP 05.3 (household appliances), 05.4 (glassware, tableware, utensils), 05.5 (tools for house and garden). Note: bedding and textiles (COICOP 05.2) are BeddingTextilesItem, not HouseholdItem — separated per COICOP structure and UNHCR NFI practice. Assessment: condition_grade (wear grade).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'label_de': {'tag': 'label_de', 'value': 'Haustechnik'},
                         'label_en': {'tag': 'label_en', 'value': 'Household'}},
         'class_uri': 'pto:Household_goods',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_item',
         'mixins': ['HouseholdCategory'],
         'rules': [{'description': 'condition_grade required at sorted state '
                                   'regardless of usage.',
                    'postconditions': {'slot_conditions': {'condition_grade': {'name': 'condition_grade',
                                                                               'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-household-condition-grade-required'}],
         'see_also': ['http://www.productontology.org/id/Household_goods']})

    subcategory: HouseholdSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })
    is_set_complete: Optional[bool] = Field(default=None, description="""Whether all components of the set are present. Optional — standard completeness tier.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Set vollständig'},
                         'label_en': {'tag': 'label_en', 'value': 'Set Complete'}},
         'domain_of': ['BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'StationeryCategory']} })
    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Observed wear/quality grade at sorting time. Grounded in schema:OfferItemCondition and schema:itemCondition. Applied to wear-graded categories: clothing, accessories, footwear, books, stationery, household, toys, general sports equipment.
Required at sorted state regardless of usage:
  new item, no defects           → like_new
  new item, manufacturing defect → fair or poor
  used item, minimal wear        → like_new or good
Sorters record what they observe, not what the label says.
Categories using structured assessment_result enums instead (furniture, electronics, bedding, protective sports gear, mobility aids, baby equipment) do NOT declare this slot.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    usage: ItemUsageEnum = Field(default=..., description="""Provenance condition — was the item ever used before donation? Orthogonal to condition_grade and assessment_result. Maps to schema:NewCondition / schema:UsedCondition. usage = new does NOT imply no defects — manufacturing defects are possible and assessment must always be performed regardless of usage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Provenance'},
                         'label_en': {'tag': 'label_en', 'value': 'Provenance'}},
         'domain_of': ['DonationItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:NewCondition',
                      'schema:UsedCondition'],
         'slot_uri': 'schema:itemCondition'} })
    category: Literal["HouseholdItem"] = Field(default="HouseholdItem", description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'designates_type': True,
         'domain_of': ['DonationItem', 'DemandSignal'],
         'notes': ['Due to a limitation in LinkML, the designates_type annotation was '
                   'removed because the range is an Enum and not a string.'],
         'slot_uri': 'schema:additionalType'} })
    lifecycle_state: ItemLifecycleStateEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    attribute_completeness: Optional[AttributeCompletenessEnum] = Field(default=None, description="""Data quality tier set by the fragment engine on sorting completion. Not derived from field presence. Not a lifecycle gate. Used by the match engine to filter candidates by data quality tier. See AttributeCompletenessEnum for the relationship to lifecycle_state. Set by: fragment_engine. Read by: match_engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    source_collection: Optional[str] = Field(default=None, description="""FK — the DonationCollection (arrival type) this item was registered from. Null for items not arriving as part of a collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    storage_unit: Optional[str] = Field(default=None, description="""FK — set when lifecycle_state transitions to stored. Null until the item reaches stored state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    sorting_notes: Optional[str] = Field(default=None, description="""Free-text notes recorded by the sorter during sorting. Required by UC warn rules to capture explicit sorter confirmation (e.g. incomplete pair, body-contact item, inconclusive assessment).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationItem']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    updated_at: datetime  = Field(default=..., description="""Timestamp when the entity record was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })


class ElectronicsItem(ElectronicsCategory, DonationItem):
    """
    Consumer electronics: phones, tablets, laptops, cameras, audio devices, cables, gaming consoles. COICOP 09.1 (audio-visual equipment) and 09.2.
    Assessment: ElectronicsAssessmentEnum (functional and cosmetic state). Functional state is the primary redistribution signal for electronics — a cracked-screen phone that works is more useful than a pristine one that does not. assessment_result required regardless of usage because new devices can have factory defects or dead batteries.
    Data wiping is a process concern (fragment step in sort_electronics process path), not a schema constraint — it is enforced by the fragment engine, not by a UC rule here.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'label_de': {'tag': 'label_de', 'value': 'Elektronik'},
                         'label_en': {'tag': 'label_en', 'value': 'Electronics'}},
         'class_uri': 'pto:Consumer_electronics',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_item',
         'mixins': ['ElectronicsCategory'],
         'rules': [{'description': 'assessment_result required at sorted state '
                                   'regardless of usage. New devices can have factory '
                                   'defects or dead batteries.',
                    'postconditions': {'slot_conditions': {'assessment_result': {'name': 'assessment_result',
                                                                                 'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-electronics-assessment-required'},
                   {'description': 'untested is only valid at received state. At '
                                   'sorted state the sorter must have tested the '
                                   'device and recorded a definitive assessment '
                                   'result.',
                    'postconditions': {'slot_conditions': {'assessment_result': {'name': 'assessment_result',
                                                                                 'none_of': [{'equals_string': 'untested'}]}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-electronics-not-untested'}],
         'see_also': ['http://www.productontology.org/id/Consumer_electronics']})

    subcategory: ElectronicsSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    assessment_result: ElectronicsAssessmentEnum = Field(default=..., description="""Functional and cosmetic assessment. Required regardless of usage — new devices can have factory defects or dead batteries.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Bewertungsergebnis'},
                         'label_en': {'tag': 'label_en', 'value': 'Assessment Result'}},
         'domain_of': ['FurnitureCategory',
                       'BeddingTextilesCategory',
                       'ElectronicsCategory',
                       'SportsCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:OfferItemCondition']} })
    includes_charger: Optional[bool] = Field(default=None, description="""Whether a compatible charger is included. Affects redistribution value — a device without a charger is significantly less useful. Optional — detailed completeness tier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElectronicsCategory']} })
    includes_original_packaging: Optional[bool] = Field(default=None, description="""Whether original retail packaging is present. Optional — detailed tier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElectronicsCategory']} })
    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    usage: ItemUsageEnum = Field(default=..., description="""Provenance condition — was the item ever used before donation? Orthogonal to condition_grade and assessment_result. Maps to schema:NewCondition / schema:UsedCondition. usage = new does NOT imply no defects — manufacturing defects are possible and assessment must always be performed regardless of usage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Provenance'},
                         'label_en': {'tag': 'label_en', 'value': 'Provenance'}},
         'domain_of': ['DonationItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:NewCondition',
                      'schema:UsedCondition'],
         'slot_uri': 'schema:itemCondition'} })
    category: Literal["ElectronicsItem"] = Field(default="ElectronicsItem", description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'designates_type': True,
         'domain_of': ['DonationItem', 'DemandSignal'],
         'notes': ['Due to a limitation in LinkML, the designates_type annotation was '
                   'removed because the range is an Enum and not a string.'],
         'slot_uri': 'schema:additionalType'} })
    lifecycle_state: ItemLifecycleStateEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    attribute_completeness: Optional[AttributeCompletenessEnum] = Field(default=None, description="""Data quality tier set by the fragment engine on sorting completion. Not derived from field presence. Not a lifecycle gate. Used by the match engine to filter candidates by data quality tier. See AttributeCompletenessEnum for the relationship to lifecycle_state. Set by: fragment_engine. Read by: match_engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    source_collection: Optional[str] = Field(default=None, description="""FK — the DonationCollection (arrival type) this item was registered from. Null for items not arriving as part of a collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    storage_unit: Optional[str] = Field(default=None, description="""FK — set when lifecycle_state transitions to stored. Null until the item reaches stored state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    sorting_notes: Optional[str] = Field(default=None, description="""Free-text notes recorded by the sorter during sorting. Required by UC warn rules to capture explicit sorter confirmation (e.g. incomplete pair, body-contact item, inconclusive assessment).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationItem']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    updated_at: datetime  = Field(default=..., description="""Timestamp when the entity record was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class ToysItem(ToysCategory, DonationItem):
    """
    Toys and games. COICOP 09.3 (games, toys, hobbies). Age grading follows EU Toy Safety Directive 2009/48/EC:
      https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009L0048
    UC rule for small parts choking hazard also references ASTM F963 (US standard) for completeness. Assessment: condition_grade (wear grade).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'label_de': {'tag': 'label_de',
                                      'value': 'Spielzeug und Spiele'},
                         'label_en': {'tag': 'label_en', 'value': 'Toys and Games'}},
         'class_uri': 'pto:Toy',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_item',
         'mixins': ['ToysCategory'],
         'rules': [{'description': 'condition_grade required at sorted state '
                                   'regardless of usage.',
                    'postconditions': {'slot_conditions': {'condition_grade': {'name': 'condition_grade',
                                                                               'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-toys-condition-grade-required'}],
         'see_also': ['http://www.productontology.org/id/Toy',
                      'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009L0048']})

    subcategory: ToysSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    age_range: Optional[ToyAgeRangeEnum] = Field(default=None, description="""Age suitability. Range overridden per class:
  ToysItem  → ToyAgeRangeEnum
  BooksItem → BookAgeRangeEnum""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Altersbereich'},
                         'label_en': {'tag': 'label_en', 'value': 'Age Range'}},
         'domain_of': ['ToysCategory', 'BooksCategory']} })
    is_set_complete: Optional[bool] = Field(default=None, description="""Whether all components of the set are present. Optional — standard completeness tier.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Set vollständig'},
                         'label_en': {'tag': 'label_en', 'value': 'Set Complete'}},
         'domain_of': ['BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'StationeryCategory']} })
    has_small_parts: Optional[bool] = Field(default=None, description="""Whether the item contains small parts posing a choking hazard. UC block: has_small_parts=true → age_range must exclude age_0_to_3. Implements EU Toy Safety Directive 2009/48/EC.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ToysCategory']} })
    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Observed wear/quality grade at sorting time. Grounded in schema:OfferItemCondition and schema:itemCondition. Applied to wear-graded categories: clothing, accessories, footwear, books, stationery, household, toys, general sports equipment.
Required at sorted state regardless of usage:
  new item, no defects           → like_new
  new item, manufacturing defect → fair or poor
  used item, minimal wear        → like_new or good
Sorters record what they observe, not what the label says.
Categories using structured assessment_result enums instead (furniture, electronics, bedding, protective sports gear, mobility aids, baby equipment) do NOT declare this slot.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    usage: ItemUsageEnum = Field(default=..., description="""Provenance condition — was the item ever used before donation? Orthogonal to condition_grade and assessment_result. Maps to schema:NewCondition / schema:UsedCondition. usage = new does NOT imply no defects — manufacturing defects are possible and assessment must always be performed regardless of usage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Provenance'},
                         'label_en': {'tag': 'label_en', 'value': 'Provenance'}},
         'domain_of': ['DonationItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:NewCondition',
                      'schema:UsedCondition'],
         'slot_uri': 'schema:itemCondition'} })
    category: Literal["ToysItem"] = Field(default="ToysItem", description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'designates_type': True,
         'domain_of': ['DonationItem', 'DemandSignal'],
         'notes': ['Due to a limitation in LinkML, the designates_type annotation was '
                   'removed because the range is an Enum and not a string.'],
         'slot_uri': 'schema:additionalType'} })
    lifecycle_state: ItemLifecycleStateEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    attribute_completeness: Optional[AttributeCompletenessEnum] = Field(default=None, description="""Data quality tier set by the fragment engine on sorting completion. Not derived from field presence. Not a lifecycle gate. Used by the match engine to filter candidates by data quality tier. See AttributeCompletenessEnum for the relationship to lifecycle_state. Set by: fragment_engine. Read by: match_engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    source_collection: Optional[str] = Field(default=None, description="""FK — the DonationCollection (arrival type) this item was registered from. Null for items not arriving as part of a collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    storage_unit: Optional[str] = Field(default=None, description="""FK — set when lifecycle_state transitions to stored. Null until the item reaches stored state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    sorting_notes: Optional[str] = Field(default=None, description="""Free-text notes recorded by the sorter during sorting. Required by UC warn rules to capture explicit sorter confirmation (e.g. incomplete pair, body-contact item, inconclusive assessment).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationItem']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    updated_at: datetime  = Field(default=..., description="""Timestamp when the entity record was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class SportsItem(SportsCategory, DonationItem):
    """
    Sports and fitness equipment. COICOP 09.4 (sport and recreational equipment). Note: bicycles are placed here by domain convention; COICOP assigns them to Division 07 (Transport). The domain decision reflects how social organisations actually sort and store these items.
    Dual-track assessment (defined in SportsCategory, categories/sports.yaml):
      protective_gear subcategory → SportsProtectiveAssessmentEnum
        Wear grade is insufficient for safety-critical items — structural
        damage may not be visually apparent after impact (e.g. a cracked
        helmet inner shell invisible under an intact outer shell).
      all other subcategories → condition_grade (wear grade)
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'label_de': {'tag': 'label_de', 'value': 'Sport'},
                         'label_en': {'tag': 'label_en', 'value': 'Sports'}},
         'class_uri': 'pto:Sporting_goods',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_item',
         'mixins': ['SportsCategory'],
         'rules': [{'description': 'subcategory required at sorted state. '
                                   'SportsCategory rules then enforce whether '
                                   'assessment_result or condition_grade is required '
                                   'based on the subcategory value (protective_gear '
                                   'vs. other).',
                    'postconditions': {'slot_conditions': {'subcategory': {'name': 'subcategory',
                                                                           'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-sports-subcategory-required'}],
         'see_also': ['http://www.productontology.org/id/Sporting_goods']})

    subcategory: SportsSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    assessment_result: Optional[SportsProtectiveAssessmentEnum] = Field(default=None, description="""Structured safety assessment for protective_gear subcategory only. Required when subcategory = protective_gear; absent otherwise.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Bewertungsergebnis'},
                         'label_en': {'tag': 'label_en', 'value': 'Assessment Result'}},
         'domain_of': ['FurnitureCategory',
                       'BeddingTextilesCategory',
                       'ElectronicsCategory',
                       'SportsCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:OfferItemCondition']} })
    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Wear grade for general sports equipment (non-protective-gear). Required when subcategory ≠ protective_gear.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    sport_type: Optional[str] = Field(default=None, description="""Sport or activity type (free text, e.g. \"football\", \"cycling\").""", json_schema_extra = { "linkml_meta": {'domain_of': ['SportsCategory']} })
    demographic: Optional[DemographicEnum] = Field(default=None, description="""Age/gender demographic (from DemographicEnum in clothing.yaml). Optional — detailed completeness tier for sports equipment.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Demografie'},
                         'label_en': {'tag': 'label_en', 'value': 'Demographic'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'SportsCategory',
                       'AnyValue'],
         'see_also': ['cpi:designatedFor',
                      'schema:WearableSizeGroupBaby',
                      'schema:WearableSizeGroupChildrens',
                      'schema:WearableSizeGroupAdult']} })
    is_set_complete: Optional[bool] = Field(default=None, description="""Whether all components of the set are present. Optional — standard completeness tier.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Set vollständig'},
                         'label_en': {'tag': 'label_en', 'value': 'Set Complete'}},
         'domain_of': ['BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'StationeryCategory']} })
    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    usage: ItemUsageEnum = Field(default=..., description="""Provenance condition — was the item ever used before donation? Orthogonal to condition_grade and assessment_result. Maps to schema:NewCondition / schema:UsedCondition. usage = new does NOT imply no defects — manufacturing defects are possible and assessment must always be performed regardless of usage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Provenance'},
                         'label_en': {'tag': 'label_en', 'value': 'Provenance'}},
         'domain_of': ['DonationItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:NewCondition',
                      'schema:UsedCondition'],
         'slot_uri': 'schema:itemCondition'} })
    category: Literal["SportsItem"] = Field(default="SportsItem", description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'designates_type': True,
         'domain_of': ['DonationItem', 'DemandSignal'],
         'notes': ['Due to a limitation in LinkML, the designates_type annotation was '
                   'removed because the range is an Enum and not a string.'],
         'slot_uri': 'schema:additionalType'} })
    lifecycle_state: ItemLifecycleStateEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    attribute_completeness: Optional[AttributeCompletenessEnum] = Field(default=None, description="""Data quality tier set by the fragment engine on sorting completion. Not derived from field presence. Not a lifecycle gate. Used by the match engine to filter candidates by data quality tier. See AttributeCompletenessEnum for the relationship to lifecycle_state. Set by: fragment_engine. Read by: match_engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    source_collection: Optional[str] = Field(default=None, description="""FK — the DonationCollection (arrival type) this item was registered from. Null for items not arriving as part of a collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    storage_unit: Optional[str] = Field(default=None, description="""FK — set when lifecycle_state transitions to stored. Null until the item reaches stored state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    sorting_notes: Optional[str] = Field(default=None, description="""Free-text notes recorded by the sorter during sorting. Required by UC warn rules to capture explicit sorter confirmation (e.g. incomplete pair, body-contact item, inconclusive assessment).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationItem']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    updated_at: datetime  = Field(default=..., description="""Timestamp when the entity record was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class BooksItem(BooksCategory, DonationItem):
    """
    Books and educational materials. COICOP 09.5 (newspapers, books, stationery). Grounded in schema:Book (schema.org has a first-class Book type distinct from generic Product). No demographic or clothing-style size dimension — age_range (BookAgeRangeEnum) is broader and non-gendered. Assessment: condition_grade (wear grade).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'label_de': {'tag': 'label_de', 'value': 'Bücher'},
                         'label_en': {'tag': 'label_en', 'value': 'Books'}},
         'class_uri': 'schema:Book',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_item',
         'mixins': ['BooksCategory'],
         'rules': [{'description': 'condition_grade required at sorted state '
                                   'regardless of usage.',
                    'postconditions': {'slot_conditions': {'condition_grade': {'name': 'condition_grade',
                                                                               'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-books-condition-grade-required'}],
         'see_also': ['schema:Book']})

    subcategory: BooksSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    language: Optional[str] = Field(default=None, description="""Language of item content (ISO 639-1 code, e.g. \"de\", \"en\", \"ar\", \"fa\"). Important for demand signal matching — organisations serving specific language communities have targeted language preferences. Optional — detailed completeness tier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['BooksCategory']} })
    age_range: Optional[BookAgeRangeEnum] = Field(default=None, description="""Age suitability. Range overridden per class:
  ToysItem  → ToyAgeRangeEnum
  BooksItem → BookAgeRangeEnum""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Altersbereich'},
                         'label_en': {'tag': 'label_en', 'value': 'Age Range'}},
         'domain_of': ['ToysCategory', 'BooksCategory']} })
    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Observed wear/quality grade at sorting time. Grounded in schema:OfferItemCondition and schema:itemCondition. Applied to wear-graded categories: clothing, accessories, footwear, books, stationery, household, toys, general sports equipment.
Required at sorted state regardless of usage:
  new item, no defects           → like_new
  new item, manufacturing defect → fair or poor
  used item, minimal wear        → like_new or good
Sorters record what they observe, not what the label says.
Categories using structured assessment_result enums instead (furniture, electronics, bedding, protective sports gear, mobility aids, baby equipment) do NOT declare this slot.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    usage: ItemUsageEnum = Field(default=..., description="""Provenance condition — was the item ever used before donation? Orthogonal to condition_grade and assessment_result. Maps to schema:NewCondition / schema:UsedCondition. usage = new does NOT imply no defects — manufacturing defects are possible and assessment must always be performed regardless of usage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Provenance'},
                         'label_en': {'tag': 'label_en', 'value': 'Provenance'}},
         'domain_of': ['DonationItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:NewCondition',
                      'schema:UsedCondition'],
         'slot_uri': 'schema:itemCondition'} })
    category: Literal["BooksItem"] = Field(default="BooksItem", description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'designates_type': True,
         'domain_of': ['DonationItem', 'DemandSignal'],
         'notes': ['Due to a limitation in LinkML, the designates_type annotation was '
                   'removed because the range is an Enum and not a string.'],
         'slot_uri': 'schema:additionalType'} })
    lifecycle_state: ItemLifecycleStateEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    attribute_completeness: Optional[AttributeCompletenessEnum] = Field(default=None, description="""Data quality tier set by the fragment engine on sorting completion. Not derived from field presence. Not a lifecycle gate. Used by the match engine to filter candidates by data quality tier. See AttributeCompletenessEnum for the relationship to lifecycle_state. Set by: fragment_engine. Read by: match_engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    source_collection: Optional[str] = Field(default=None, description="""FK — the DonationCollection (arrival type) this item was registered from. Null for items not arriving as part of a collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    storage_unit: Optional[str] = Field(default=None, description="""FK — set when lifecycle_state transitions to stored. Null until the item reaches stored state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    sorting_notes: Optional[str] = Field(default=None, description="""Free-text notes recorded by the sorter during sorting. Required by UC warn rules to capture explicit sorter confirmation (e.g. incomplete pair, body-contact item, inconclusive assessment).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationItem']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    updated_at: datetime  = Field(default=..., description="""Timestamp when the entity record was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class StationeryItem(StationeryCategory, DonationItem):
    """
    Stationery and office supplies: pens, notebooks, art supplies, calculators. COICOP 09.5 (newspapers, books, stationery). Separated from BooksItem because published content (BooksItem) and consumable/office supplies have different sorting paths, condition vocabularies (partially-used pens are not \"poor condition books\"), and demand signal patterns (school supply drives vs. book donations). Assessment: condition_grade (wear grade).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'label_de': {'tag': 'label_de', 'value': 'Schreibwaren'},
                         'label_en': {'tag': 'label_en', 'value': 'Stationery'}},
         'class_uri': 'pto:Stationery',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_item',
         'mixins': ['StationeryCategory'],
         'rules': [{'description': 'condition_grade required at sorted state '
                                   'regardless of usage.',
                    'postconditions': {'slot_conditions': {'condition_grade': {'name': 'condition_grade',
                                                                               'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-stationery-condition-grade-required'}],
         'see_also': ['http://www.productontology.org/id/Stationery']})

    subcategory: StationerySubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    is_set_complete: Optional[bool] = Field(default=None, description="""Whether all components of the set are present. Optional — standard completeness tier.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Set vollständig'},
                         'label_en': {'tag': 'label_en', 'value': 'Set Complete'}},
         'domain_of': ['BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'StationeryCategory']} })
    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Observed wear/quality grade at sorting time. Grounded in schema:OfferItemCondition and schema:itemCondition. Applied to wear-graded categories: clothing, accessories, footwear, books, stationery, household, toys, general sports equipment.
Required at sorted state regardless of usage:
  new item, no defects           → like_new
  new item, manufacturing defect → fair or poor
  used item, minimal wear        → like_new or good
Sorters record what they observe, not what the label says.
Categories using structured assessment_result enums instead (furniture, electronics, bedding, protective sports gear, mobility aids, baby equipment) do NOT declare this slot.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    usage: ItemUsageEnum = Field(default=..., description="""Provenance condition — was the item ever used before donation? Orthogonal to condition_grade and assessment_result. Maps to schema:NewCondition / schema:UsedCondition. usage = new does NOT imply no defects — manufacturing defects are possible and assessment must always be performed regardless of usage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Provenance'},
                         'label_en': {'tag': 'label_en', 'value': 'Provenance'}},
         'domain_of': ['DonationItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:NewCondition',
                      'schema:UsedCondition'],
         'slot_uri': 'schema:itemCondition'} })
    category: Literal["StationeryItem"] = Field(default="StationeryItem", description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'designates_type': True,
         'domain_of': ['DonationItem', 'DemandSignal'],
         'notes': ['Due to a limitation in LinkML, the designates_type annotation was '
                   'removed because the range is an Enum and not a string.'],
         'slot_uri': 'schema:additionalType'} })
    lifecycle_state: ItemLifecycleStateEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    attribute_completeness: Optional[AttributeCompletenessEnum] = Field(default=None, description="""Data quality tier set by the fragment engine on sorting completion. Not derived from field presence. Not a lifecycle gate. Used by the match engine to filter candidates by data quality tier. See AttributeCompletenessEnum for the relationship to lifecycle_state. Set by: fragment_engine. Read by: match_engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    source_collection: Optional[str] = Field(default=None, description="""FK — the DonationCollection (arrival type) this item was registered from. Null for items not arriving as part of a collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    storage_unit: Optional[str] = Field(default=None, description="""FK — set when lifecycle_state transitions to stored. Null until the item reaches stored state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    sorting_notes: Optional[str] = Field(default=None, description="""Free-text notes recorded by the sorter during sorting. Required by UC warn rules to capture explicit sorter confirmation (e.g. incomplete pair, body-contact item, inconclusive assessment).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationItem']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    updated_at: datetime  = Field(default=..., description="""Timestamp when the entity record was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class PersonalCareItem(PersonalCareCategory, DonationItem):
    """
    Personal care, hygiene, and health products. Merges COICOP 06.1 (medical products and appliances) and 12.1 (personal care — toiletries, cosmetics, related appliances). Open Eligibility uses a single \"Personal Care Items\" node for both:
      https://company.auntbertha.com/openeligibility/

    Merged because the operative safety rules are identical across both former categories: sealed required, used tools blocked, expiry enforced. Splitting them would duplicate all three rules with no semantic benefit.
    Assessment: is_sealed + expiry_date (no condition_grade or assessment_result). For personal care products, the relevant safety signals are hygiene integrity (sealed?) and freshness (not expired?). A wear grade is meaningless for a tube of toothpaste — it is either sealed or it is not.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'label_de': {'tag': 'label_de', 'value': 'Personalhygiene'},
                         'label_en': {'tag': 'label_en', 'value': 'Personal Care'}},
         'class_uri': 'pto:Personal_hygiene',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_item',
         'mixins': ['PersonalCareCategory'],
         'rules': [{'description': 'is_sealed required at sorted state regardless of '
                                   'usage. Even new personal care items may have '
                                   'compromised packaging.',
                    'postconditions': {'slot_conditions': {'is_sealed': {'name': 'is_sealed',
                                                                         'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-personal-care-sealed-required'}],
         'see_also': ['http://www.productontology.org/id/Personal_hygiene',
                      'http://www.productontology.org/id/Cosmetics',
                      'https://company.auntbertha.com/openeligibility/']})

    subcategory: PersonalCareSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    is_sealed: bool = Field(default=..., description="""Whether the item's original packaging/seal is intact. UC block for most consumable subcategories when false. Primary safety signal for personal care items — replaces condition_grade.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de',
                                      'value': 'Versiegelte Verpackung'},
                         'label_en': {'tag': 'label_en', 'value': 'Sealed Packaging'}},
         'domain_of': ['PersonalCareCategory', 'BabyInfantCategory']} })
    expiry_date: Optional[date] = Field(default=None, description="""Expiry or best-before date from the packaging. UC block: expiry_date < today (runtime check by Django model clean()). Secondary safety signal — important for medications, skincare, food.""", json_schema_extra = { "linkml_meta": {'annotations': {'uc_action': {'tag': 'uc_action', 'value': 'block'},
                         'uc_note': {'tag': 'uc_note',
                                     'value': 'Dynamic date comparison — runtime '
                                              'enforcement by Django model clean()'},
                         'uc_suggest': {'tag': 'uc_suggest', 'value': 'disposal'}},
         'domain_of': ['PersonalCareCategory', 'BabyInfantCategory', 'FoodCategory']} })
    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    usage: ItemUsageEnum = Field(default=..., description="""Provenance condition — was the item ever used before donation? Orthogonal to condition_grade and assessment_result. Maps to schema:NewCondition / schema:UsedCondition. usage = new does NOT imply no defects — manufacturing defects are possible and assessment must always be performed regardless of usage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Provenance'},
                         'label_en': {'tag': 'label_en', 'value': 'Provenance'}},
         'domain_of': ['DonationItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:NewCondition',
                      'schema:UsedCondition'],
         'slot_uri': 'schema:itemCondition'} })
    category: Literal["PersonalCareItem"] = Field(default="PersonalCareItem", description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'designates_type': True,
         'domain_of': ['DonationItem', 'DemandSignal'],
         'notes': ['Due to a limitation in LinkML, the designates_type annotation was '
                   'removed because the range is an Enum and not a string.'],
         'slot_uri': 'schema:additionalType'} })
    lifecycle_state: ItemLifecycleStateEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    attribute_completeness: Optional[AttributeCompletenessEnum] = Field(default=None, description="""Data quality tier set by the fragment engine on sorting completion. Not derived from field presence. Not a lifecycle gate. Used by the match engine to filter candidates by data quality tier. See AttributeCompletenessEnum for the relationship to lifecycle_state. Set by: fragment_engine. Read by: match_engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    source_collection: Optional[str] = Field(default=None, description="""FK — the DonationCollection (arrival type) this item was registered from. Null for items not arriving as part of a collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    storage_unit: Optional[str] = Field(default=None, description="""FK — set when lifecycle_state transitions to stored. Null until the item reaches stored state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    sorting_notes: Optional[str] = Field(default=None, description="""Free-text notes recorded by the sorter during sorting. Required by UC warn rules to capture explicit sorter confirmation (e.g. incomplete pair, body-contact item, inconclusive assessment).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationItem']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    updated_at: datetime  = Field(default=..., description="""Timestamp when the entity record was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class MobilityAidsItem(MobilityAidsCategory, DonationItem):
    """
    Mobility aids and assistive devices: wheelchairs, crutches, walking frames, hearing aids, orthotics, daily living aids. COICOP 06.1.3 (other medical products) and 06.2 (outpatient services, durable medical equipment). Open Eligibility \"Assistive Technology\" top-level category:
      https://company.auntbertha.com/openeligibility/

    Assessment: MobilityAssessmentEnum (structured safety and hygiene). A single enum captures structural soundness, functional state, and body-contact hygiene (used hearing aids, orthotics) — replacing the former separate boolean structural_integrity + functional_status slots that generated the problematic annotation-based approach. assessment_result required regardless of usage — new mobility aids can have manufacturing defects.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'label_de': {'tag': 'label_de',
                                      'value': 'Mobilitätshilfen und Hilfsgeräte'},
                         'label_en': {'tag': 'label_en',
                                      'value': 'Mobility Aids and Assistive Devices'}},
         'class_uri': 'pto:Assistive_technology',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_item',
         'mixins': ['MobilityAidsCategory'],
         'rules': [{'description': 'assessment_result required at sorted state '
                                   'regardless of usage. New mobility aids can have '
                                   'manufacturing defects.',
                    'postconditions': {'slot_conditions': {'assessment_result': {'name': 'assessment_result',
                                                                                 'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-mobility-assessment-required'}],
         'see_also': ['http://www.productontology.org/id/Assistive_technology',
                      'https://company.auntbertha.com/openeligibility/']})

    subcategory: MobilityAidsSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    assessment_result: MobilityAssessmentEnum = Field(default=..., description="""Safety and hygiene assessment. Required regardless of usage — new mobility aids can have manufacturing defects.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Bewertungsergebnis'},
                         'label_en': {'tag': 'label_en', 'value': 'Assessment Result'}},
         'domain_of': ['FurnitureCategory',
                       'BeddingTextilesCategory',
                       'ElectronicsCategory',
                       'SportsCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:OfferItemCondition']} })
    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    usage: ItemUsageEnum = Field(default=..., description="""Provenance condition — was the item ever used before donation? Orthogonal to condition_grade and assessment_result. Maps to schema:NewCondition / schema:UsedCondition. usage = new does NOT imply no defects — manufacturing defects are possible and assessment must always be performed regardless of usage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Provenance'},
                         'label_en': {'tag': 'label_en', 'value': 'Provenance'}},
         'domain_of': ['DonationItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:NewCondition',
                      'schema:UsedCondition'],
         'slot_uri': 'schema:itemCondition'} })
    category: Literal["MobilityAidsItem"] = Field(default="MobilityAidsItem", description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'designates_type': True,
         'domain_of': ['DonationItem', 'DemandSignal'],
         'notes': ['Due to a limitation in LinkML, the designates_type annotation was '
                   'removed because the range is an Enum and not a string.'],
         'slot_uri': 'schema:additionalType'} })
    lifecycle_state: ItemLifecycleStateEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    attribute_completeness: Optional[AttributeCompletenessEnum] = Field(default=None, description="""Data quality tier set by the fragment engine on sorting completion. Not derived from field presence. Not a lifecycle gate. Used by the match engine to filter candidates by data quality tier. See AttributeCompletenessEnum for the relationship to lifecycle_state. Set by: fragment_engine. Read by: match_engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    source_collection: Optional[str] = Field(default=None, description="""FK — the DonationCollection (arrival type) this item was registered from. Null for items not arriving as part of a collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    storage_unit: Optional[str] = Field(default=None, description="""FK — set when lifecycle_state transitions to stored. Null until the item reaches stored state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    sorting_notes: Optional[str] = Field(default=None, description="""Free-text notes recorded by the sorter during sorting. Required by UC warn rules to capture explicit sorter confirmation (e.g. incomplete pair, body-contact item, inconclusive assessment).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationItem']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    updated_at: datetime  = Field(default=..., description="""Timestamp when the entity record was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class BabyInfantItem(BabyInfantCategory, DonationItem):
    """
    Baby and infant supplies: pushchairs, cots, car seats, infant formula, feeding bottles, baby monitors, bath equipment. Baby clothing belongs in ClothingItem (demographic=baby).
    COICOP distributes baby items across Division 03 (clothing), 05 (household), and 01 (food). Treated as a first-class top-level category here following Open Eligibility \"Baby Supplies\" and UNHCR NFI kit practice (nappies and formula are core NFI kit items):
      https://company.auntbertha.com/openeligibility/
      https://emergency.unhcr.org/emergency-assistance/core-relief-items/

    Three-track assessment model (defined in BabyInfantCategory):
      Track 1 — safety-critical equipment (BabyEquipmentAssessmentEnum):
        pushchairs, cots, car seats, carriers, high chairs, sleeping bags.
        EN 1888 (pushchairs), EN 716 (cots), EN 14344 (car seats),
        EN 16781 (baby sleeping bags — neck/armhole openings, no loose
        cords), all require structured provenance + structural assessment.
        Baby sleeping bags are Track 1, NOT BeddingTextilesItem — the
        EN 16781 safety check differs materially from adult sleeping bag
        hygiene assessment.
      Track 2 — consumables (is_sealed + expiry_date):
        infant_formula, feeding_bottles_teats, baby_food.
      Track 3 — general baby gear (condition_grade):
        bath equipment, changing, monitors, bouncers.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'label_de': {'tag': 'label_de',
                                      'value': 'Baby- und Kleinkindausstattung'},
                         'label_en': {'tag': 'label_en',
                                      'value': 'Baby and Infant Supplies'}},
         'class_uri': 'pto:Baby_transport',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/donation_item',
         'mixins': ['BabyInfantCategory'],
         'rules': [{'description': 'is_winter_suitable required at sorted state for '
                                   'baby sleeping bags. A summer-weight baby sleeping '
                                   'bag (0.5-1.0 tog) issued in cold- weather '
                                   'distribution is a safety risk — infants cannot '
                                   'regulate their own temperature. BabyInfantCategory '
                                   'also carries this rule; the lifecycle rule here '
                                   'ensures it is enforced at the sorted transition.',
                    'postconditions': {'slot_conditions': {'is_winter_suitable': {'name': 'is_winter_suitable',
                                                                                  'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'},
                                                          'subcategory': {'equals_string': 'sleeping_bags',
                                                                          'name': 'subcategory'}}},
                    'title': 'lc-sorted-baby-sleeping-bag-winter-required'},
                   {'description': 'subcategory required at sorted state. '
                                   'BabyInfantCategory rules then enforce the '
                                   'appropriate assessment track for that subcategory.',
                    'postconditions': {'slot_conditions': {'subcategory': {'name': 'subcategory',
                                                                           'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'}}},
                    'title': 'lc-sorted-baby-subcategory-required'},
                   {'description': 'Manufacture year is required for certain '
                                   'subcategories.',
                    'postconditions': {'slot_conditions': {'manufacture_year': {'name': 'manufacture_year',
                                                                                'required': True}}},
                    'preconditions': {'slot_conditions': {'lifecycle_state': {'equals_string': 'sorted',
                                                                              'name': 'lifecycle_state'},
                                                          'subcategory': {'any_of': [{'equals_string': 'cots_cribs'},
                                                                                     {'equals_string': 'car_seats'},
                                                                                     {'equals_string': 'pushchairs_prams'}],
                                                                          'name': 'subcategory'}}},
                    'title': 'lc-manufacture-year-required'}],
         'see_also': ['http://www.productontology.org/id/Baby_transport',
                      'http://www.productontology.org/id/Infant_bed',
                      'https://company.auntbertha.com/openeligibility/',
                      'https://emergency.unhcr.org/emergency-assistance/core-relief-items/kind-non-food-item-distribution']})

    subcategory: BabyInfantSubcategoryEnum = Field(default=..., description="""Subcategory within the item type. Overridden via slot_usage in each concrete DonationItem subclass to a category-specific enum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Unterkategorie'},
                         'label_en': {'tag': 'label_en', 'value': 'Subcategory'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'FurnitureCategory',
                       'BeddingTextilesCategory',
                       'HouseholdCategory',
                       'ElectronicsCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'PersonalCareCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory',
                       'AnyValue']} })
    assessment_result: Optional[BabyEquipmentAssessmentEnum] = Field(default=None, description="""Structural/provenance assessment for Track 1 safety-critical equipment. Required when subcategory in [pushchairs_prams, cots_cribs, baby_carriers, high_chairs, car_seats, sleeping_bags].""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Bewertungsergebnis'},
                         'label_en': {'tag': 'label_en', 'value': 'Assessment Result'}},
         'domain_of': ['FurnitureCategory',
                       'BeddingTextilesCategory',
                       'ElectronicsCategory',
                       'SportsCategory',
                       'MobilityAidsCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:OfferItemCondition']} })
    manufacture_year: Optional[int] = Field(default=None, description="""Year of manufacture. Required for car seats (EN 14344 — 10-year redistribution limit). Recommended for cots (EN 716) and pushchairs (EN 1888) to verify age of safety-relevant components.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Herstellungsjahr'},
                         'label_en': {'tag': 'label_en', 'value': 'Manufacture year'},
                         'show_if': {'tag': 'show_if',
                                     'value': 'subcategory in [car_seats, cots_cribs, '
                                              'pushchairs_prams]'}},
         'domain_of': ['BabyInfantCategory']} })
    includes_original_accessories: Optional[bool] = Field(default=None, description="""Whether standard accessories/components are included (e.g. pushchair includes rain cover and harness; cot includes mattress and side rails).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de',
                                      'value': 'Enthält Originalzubehör'},
                         'label_en': {'tag': 'label_en',
                                      'value': 'Includes original accessories'}},
         'domain_of': ['BabyInfantCategory']} })
    is_winter_suitable: Optional[bool] = Field(default=None, description="""Whether this item provides meaningful warmth in cold conditions. Required for sleeping_bags (UC-enforced) — a summer-weight baby sleeping bag in cold-weather distribution is a safety risk. Thermal rating (e.g. \"2.5 tog\", \"0°C comfort limit\") may be noted in sorting_notes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ClothingCategory',
                       'FootwearCategory',
                       'BeddingTextilesCategory',
                       'BabyInfantCategory'],
         'see_also': ['schema:itemCondition']} })
    is_sealed: Optional[bool] = Field(default=None, description="""Packaging/seal integrity for Track 2 consumables. Required when subcategory in [infant_formula, feeding_bottles_teats, baby_food].""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de',
                                      'value': 'Versiegelte Verpackung'},
                         'label_en': {'tag': 'label_en', 'value': 'Sealed Packaging'}},
         'domain_of': ['PersonalCareCategory', 'BabyInfantCategory']} })
    expiry_date: Optional[date] = Field(default=None, description="""Expiry or best-before date. UC block: expiry_date < today (runtime check).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Ablaufdatum'},
                         'label_en': {'tag': 'label_en', 'value': 'Expiry Date'},
                         'uc_action': {'tag': 'uc_action', 'value': 'block'},
                         'uc_note': {'tag': 'uc_note',
                                     'value': 'Dynamic date comparison — runtime '
                                              'enforcement'},
                         'uc_suggest': {'tag': 'uc_suggest', 'value': 'disposal'}},
         'domain_of': ['PersonalCareCategory', 'BabyInfantCategory', 'FoodCategory']} })
    condition_grade: Optional[UsedConditionGradeEnum] = Field(default=None, description="""Wear grade for Track 3 general baby gear. Required when subcategory in [bath_equipment, changing, baby_monitors, bouncers_swings, breastfeeding, other].""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Abnutzungsgrad'},
                         'label_en': {'tag': 'label_en', 'value': 'Wear Grade'}},
         'domain_of': ['ClothingCategory',
                       'AccessoriesCategory',
                       'FootwearCategory',
                       'HouseholdCategory',
                       'ToysCategory',
                       'SportsCategory',
                       'BooksCategory',
                       'StationeryCategory',
                       'BabyInfantCategory',
                       'OtherItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:LikeNewCondition',
                      'schema:DamagedCondition',
                      'schema:itemCondition']} })
    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    usage: ItemUsageEnum = Field(default=..., description="""Provenance condition — was the item ever used before donation? Orthogonal to condition_grade and assessment_result. Maps to schema:NewCondition / schema:UsedCondition. usage = new does NOT imply no defects — manufacturing defects are possible and assessment must always be performed regardless of usage.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Provenance'},
                         'label_en': {'tag': 'label_en', 'value': 'Provenance'}},
         'domain_of': ['DonationItem'],
         'see_also': ['schema:OfferItemCondition',
                      'schema:NewCondition',
                      'schema:UsedCondition'],
         'slot_uri': 'schema:itemCondition'} })
    category: Literal["BabyInfantItem"] = Field(default="BabyInfantItem", description="""Type-defining slot on DonationItem. Value is the class URI of the concrete subclass (e.g. inkind_knowledge_repo:ClothingItem). linkml-validate, gen-json-schema, and gen-pydantic all use this slot to dispatch to the correct subclass schema and valid slot set. For other entities (DemandSignal, StorageLocation) the range is overridden via slot_usage to CategoryEnum.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Artikeltyp'},
                         'label_en': {'tag': 'label_en', 'value': 'Item Type'}},
         'designates_type': True,
         'domain_of': ['DonationItem', 'DemandSignal'],
         'notes': ['Due to a limitation in LinkML, the designates_type annotation was '
                   'removed because the range is an Enum and not a string.'],
         'slot_uri': 'schema:additionalType'} })
    lifecycle_state: ItemLifecycleStateEnum = Field(default=..., description="""Current lifecycle state of the entity. Concrete enum range applied via slot_usage. Transitions enforced by Django model clean().""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign']} })
    attribute_completeness: Optional[AttributeCompletenessEnum] = Field(default=None, description="""Data quality tier set by the fragment engine on sorting completion. Not derived from field presence. Not a lifecycle gate. Used by the match engine to filter candidates by data quality tier. See AttributeCompletenessEnum for the relationship to lifecycle_state. Set by: fragment_engine. Read by: match_engine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    source_collection: Optional[str] = Field(default=None, description="""FK — the DonationCollection (arrival type) this item was registered from. Null for items not arriving as part of a collection.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    donation_source: Optional[str] = Field(default=None, description="""Reference to the DonationSource — privacy boundary between item records and donor identity. Concrete range applied via slot_usage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationCollection', 'DonationItem'],
         'slot_uri': 'inkind_knowledge_repo:donation_source'} })
    storage_unit: Optional[str] = Field(default=None, description="""FK — set when lifecycle_state transitions to stored. Null until the item reaches stored state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    sorting_notes: Optional[str] = Field(default=None, description="""Free-text notes recorded by the sorter during sorting. Required by UC warn rules to capture explicit sorter confirmation (e.g. incomplete pair, body-contact item, inconclusive assessment).""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationItem']} })
    created_at: datetime  = Field(default=..., description="""Timestamp when the entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationSource', 'DonationCollection', 'DonationItem']} })
    updated_at: datetime  = Field(default=..., description="""Timestamp when the entity record was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DonationItem']} })
    notes: Optional[str] = Field(default=None, description="""Optional free-text notes.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Notizen'},
                         'label_en': {'tag': 'label_en', 'value': 'Notes'}},
         'domain_of': ['DonationCollection', 'CategoryMixin']} })
    material: Optional[str] = Field(default=None, description="""Primary material composition. Range overridden per class.""", json_schema_extra = { "linkml_meta": {'annotations': {'label_de': {'tag': 'label_de', 'value': 'Material'},
                         'label_en': {'tag': 'label_en', 'value': 'Material'}},
         'domain_of': ['AccessoriesCategory',
                       'FurnitureCategory',
                       'HouseholdCategory',
                       'CategoryMixin']} })


class ProvenanceRecord(ConfiguredBaseModel):
    """
    A single provenance record capturing one completed process step — who did it, when, on which device, at what configured cost, and what observations were submitted.  Corresponds to prov:Activity in W3C PROV-O.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'prov:Activity',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo/provenance',
         'slot_usage': {'actor_role_ref': {'name': 'actor_role_ref',
                                           'range': 'ActorRoleEnum',
                                           'required': True},
                        'org': {'name': 'org',
                                'range': 'SocialOrganisation',
                                'required': True}}})

    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    step_type_ref: str = Field(default=..., description="""Slug reference to the StepType that was executed (e.g., `assign_category`).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProvenanceRecord']} })
    actor_ref: str = Field(default=..., description="""UUID reference to the Actor who performed this step.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProvenanceRecord'], 'slot_uri': 'prov:wasAssociatedWith'} })
    actor_role_ref: ActorRoleEnum = Field(default=..., description="""Actor role captured at step time — role may change after the fact so it is snapshotted here.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProvenanceRecord']} })
    org: str = Field(default=..., description="""Reference to the owning SocialOrganisation. Concrete range applied via slot_usage in each class.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Actor',
                       'StorageLocation',
                       'DonationCollection',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord']} })
    device: DeviceTypeEnum = Field(default=..., description="""Device type used to complete this step.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProvenanceRecord']} })
    started_at: datetime  = Field(default=..., description="""Timestamp when the step fragment was presented to the actor.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProvenanceRecord']} })
    completed_at: datetime  = Field(default=..., description="""Timestamp when the actor submitted the step.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProvenanceRecord'], 'slot_uri': 'prov:endedAtTime'} })
    duration_seconds: int = Field(default=..., description="""Derived: completed_at - started_at in whole seconds.  Used for observed vs configured cost comparison.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProvenanceRecord']} })
    cost_configured: float = Field(default=..., description="""The c_s scalar from StepCost at time of execution — the configured cost for this step type under this organisation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProvenanceRecord']} })
    observations_ref: str = Field(default=..., description="""JSON blob of field values submitted by the actor during this step.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProvenanceRecord'], 'see_also': ['prov:generated']} })
    override_flag: bool = Field(default=..., description="""True if the actor acknowledged a constraint warning (UC or PC) and proceeded anyway.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProvenanceRecord']} })
    override_reason: Optional[str] = Field(default=None, description="""Free-text reason provided by the actor when override_flag is true.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProvenanceRecord']} })


class NamedThing(ConfiguredBaseModel):
    """
    A generic grouping for any identifiable entity with an id, name, and description. Provided as a convenience base class; entity schemas are not required to extend it.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'schema:Thing',
         'from_schema': 'https://inkind-at.github.io/inkind-knowledge-repo'})

    id: str = Field(default=..., description="""A unique identifier for the entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation',
                       'Actor',
                       'StorageLocation',
                       'DonationSource',
                       'DonationCollection',
                       'DonationItem',
                       'DemandSignal',
                       'Campaign',
                       'ProvenanceRecord',
                       'NamedThing'],
         'slot_uri': 'schema:identifier'} })
    name: Optional[str] = Field(default=None, description="""A human-readable name for a thing.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SocialOrganisation', 'NamedThing'], 'slot_uri': 'schema:name'} })
    description: Optional[str] = Field(default=None, description="""A human-readable description for a thing.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Campaign', 'NamedThing'], 'slot_uri': 'schema:description'} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
SocialOrganisation.model_rebuild()
GeoPoint.model_rebuild()
OrgConfig.model_rebuild()
Actor.model_rebuild()
StorageLocation.model_rebuild()
DonationSource.model_rebuild()
DonationCollection.model_rebuild()
FoodCategory.model_rebuild()
DonationItem.model_rebuild()
FoodItem.model_rebuild()
OtherItem.model_rebuild()
AnyValue.model_rebuild()
DemandSignal.model_rebuild()
Campaign.model_rebuild()
CategoryMixin.model_rebuild()
ClothingCategory.model_rebuild()
AccessoriesCategory.model_rebuild()
FootwearCategory.model_rebuild()
FurnitureCategory.model_rebuild()
BeddingTextilesCategory.model_rebuild()
HouseholdCategory.model_rebuild()
ElectronicsCategory.model_rebuild()
ToysCategory.model_rebuild()
SportsCategory.model_rebuild()
BooksCategory.model_rebuild()
StationeryCategory.model_rebuild()
PersonalCareCategory.model_rebuild()
MobilityAidsCategory.model_rebuild()
BabyInfantCategory.model_rebuild()
ClothingItem.model_rebuild()
AccessoriesItem.model_rebuild()
FootwearItem.model_rebuild()
FurnitureItem.model_rebuild()
BeddingTextilesItem.model_rebuild()
HouseholdItem.model_rebuild()
ElectronicsItem.model_rebuild()
ToysItem.model_rebuild()
SportsItem.model_rebuild()
BooksItem.model_rebuild()
StationeryItem.model_rebuild()
PersonalCareItem.model_rebuild()
MobilityAidsItem.model_rebuild()
BabyInfantItem.model_rebuild()
ProvenanceRecord.model_rebuild()
NamedThing.model_rebuild()
