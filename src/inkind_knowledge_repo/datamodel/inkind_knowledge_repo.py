# Auto generated from inkind_knowledge_repo.yaml by pythongen.py version: 0.0.1
# Generation date: 2026-08-20T22:13:43
# Schema: inkind-knowledge-repo
#
# id: https://inkind-at.github.io/inkind-knowledge-repo
# description: Formal knowledge representation for in-kind donation coordination.
#   Defines the domain schema, category schemas with constraint rules and
#   dependent field maps, process templates, UI fragment bindings, and
#   organisation configuration instances.
# license: MIT

import dataclasses
import re
from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    time
)
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Union
)

from jsonasobj2 import (
    JsonObj,
    as_dict
)
from linkml_runtime.linkml_model.meta import (
    EnumDefinition,
    PermissibleValue,
    PvFormulaOptions
)
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from linkml_runtime.utils.formatutils import (
    camelcase,
    sfx,
    underscore
)
from linkml_runtime.utils.metamodelcore import (
    bnode,
    empty_dict,
    empty_list
)
from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.yamlutils import (
    YAMLRoot,
    extended_float,
    extended_int,
    extended_str
)
from rdflib import (
    Namespace,
    URIRef
)

from linkml_runtime.linkml_model.types import Boolean, Date, Datetime, Decimal, Float, Integer, String, Uriorcurie
from linkml_runtime.utils.metamodelcore import Bool, Decimal, URIorCURIE, XSDDate, XSDDateTime

metamodel_version = "1.7.0"
version = None

# Namespaces
CPI = CurieNamespace('cpi', 'http://www.ebusiness-unibw.org/ontologies/cpi/ns#')
FOODON = CurieNamespace('foodon', 'http://purl.obolibrary.org/obo/FOODON_')
INKIND_KNOWLEDGE_REPO = CurieNamespace('inkind_knowledge_repo', 'https://inkind-at.github.io/inkind-knowledge-repo/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
ORG = CurieNamespace('org', 'http://www.w3.org/ns/org#')
PROV = CurieNamespace('prov', 'http://www.w3.org/ns/prov#')
PTO = CurieNamespace('pto', 'http://www.productontology.org/id/')
SCHEMA = CurieNamespace('schema', 'http://schema.org/')
DEFAULT_ = INKIND_KNOWLEDGE_REPO


# Types

# Class references
class NamedThingId(URIorCURIE):
    pass


class SocialOrganisationId(URIorCURIE):
    pass


class ActorId(URIorCURIE):
    pass


class StorageLocationId(URIorCURIE):
    pass


class DonationSourceId(URIorCURIE):
    pass


class DonationCollectionId(URIorCURIE):
    pass


class DonationItemId(URIorCURIE):
    pass


class ClothingItemId(DonationItemId):
    pass


class AccessoriesItemId(DonationItemId):
    pass


class FootwearItemId(DonationItemId):
    pass


class FurnitureItemId(DonationItemId):
    pass


class BeddingTextilesItemId(DonationItemId):
    pass


class HouseholdItemId(DonationItemId):
    pass


class ElectronicsItemId(DonationItemId):
    pass


class ToysItemId(DonationItemId):
    pass


class SportsItemId(DonationItemId):
    pass


class BooksItemId(DonationItemId):
    pass


class StationeryItemId(DonationItemId):
    pass


class PersonalCareItemId(DonationItemId):
    pass


class MobilityAidsItemId(DonationItemId):
    pass


class BabyInfantItemId(DonationItemId):
    pass


class FoodItemId(DonationItemId):
    pass


class OtherItemId(DonationItemId):
    pass


class DemandSignalId(URIorCURIE):
    pass


class CampaignId(URIorCURIE):
    pass


class ProvenanceRecordId(URIorCURIE):
    pass


@dataclass(repr=False)
class NamedThing(YAMLRoot):
    """
    A generic grouping for any identifiable entity with an id, name, and description. Provided as a convenience base
    class; entity schemas are not required to extend it.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["Thing"]
    class_class_curie: ClassVar[str] = "schema:Thing"
    class_name: ClassVar[str] = "NamedThing"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.NamedThing

    id: Union[str, NamedThingId] = None
    name: Optional[str] = None
    description: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, NamedThingId):
            self.id = NamedThingId(self.id)

        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class SocialOrganisation(YAMLRoot):
    """
    A social organisation deploying the in-kind platform. Primary operational tenant; hierarchy depth is limited to 4
    levels.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = ORG["Organization"]
    class_class_curie: ClassVar[str] = "org:Organization"
    class_name: ClassVar[str] = "SocialOrganisation"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.SocialOrganisation

    id: Union[str, SocialOrganisationId] = None
    is_active: Union[bool, Bool] = None
    name: Optional[str] = None
    parent: Optional[Union[str, SocialOrganisationId]] = None
    geo_point: Optional[Union[dict, "GeoPoint"]] = None
    config: Optional[Union[dict, "OrgConfig"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, SocialOrganisationId):
            self.id = SocialOrganisationId(self.id)

        if self._is_empty(self.is_active):
            self.MissingRequiredField("is_active")
        if not isinstance(self.is_active, Bool):
            self.is_active = Bool(self.is_active)

        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if self.parent is not None and not isinstance(self.parent, SocialOrganisationId):
            self.parent = SocialOrganisationId(self.parent)

        if self.geo_point is not None and not isinstance(self.geo_point, GeoPoint):
            self.geo_point = GeoPoint(**as_dict(self.geo_point))

        if self.config is not None and not isinstance(self.config, OrgConfig):
            self.config = OrgConfig(**as_dict(self.config))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class GeoPoint(YAMLRoot):
    """
    Geographic coordinates for public map display of an organisation.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["GeoPoint"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:GeoPoint"
    class_name: ClassVar[str] = "GeoPoint"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.GeoPoint

    lat: Optional[float] = None
    long: Optional[float] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.lat is not None and not isinstance(self.lat, float):
            self.lat = float(self.lat)

        if self.long is not None and not isinstance(self.long, float):
            self.long = float(self.long)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class OrgConfig(YAMLRoot):
    """
    Organisation-specific configuration parameters (timezone, locale, etc.). Full schema to be expanded in Phase 1.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["OrgConfig"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:OrgConfig"
    class_name: ClassVar[str] = "OrgConfig"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.OrgConfig

    timezone: Optional[str] = None
    locale: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.timezone is not None and not isinstance(self.timezone, str):
            self.timezone = str(self.timezone)

        if self.locale is not None and not isinstance(self.locale, str):
            self.locale = str(self.locale)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Actor(YAMLRoot):
    """
    A person interacting with the system — volunteer, staff, or manager.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["Actor"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:Actor"
    class_name: ClassVar[str] = "Actor"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.Actor

    id: Union[str, ActorId] = None
    org: Union[str, SocialOrganisationId] = None
    role: Union[str, "ActorRoleEnum"] = None
    is_active: Union[bool, Bool] = None
    experience_level: Optional[Union[str, "ExperienceLevelEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ActorId):
            self.id = ActorId(self.id)

        if self._is_empty(self.org):
            self.MissingRequiredField("org")
        if not isinstance(self.org, SocialOrganisationId):
            self.org = SocialOrganisationId(self.org)

        if self._is_empty(self.role):
            self.MissingRequiredField("role")
        if not isinstance(self.role, ActorRoleEnum):
            self.role = ActorRoleEnum(self.role)

        if self._is_empty(self.is_active):
            self.MissingRequiredField("is_active")
        if not isinstance(self.is_active, Bool):
            self.is_active = Bool(self.is_active)

        if self.experience_level is not None and not isinstance(self.experience_level, ExperienceLevelEnum):
            self.experience_level = ExperienceLevelEnum(self.experience_level)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class StorageLocation(YAMLRoot):
    """
    A physical storage unit within an organisation's warehouse.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["StorageLocation"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:StorageLocation"
    class_name: ClassVar[str] = "StorageLocation"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.StorageLocation

    id: Union[str, StorageLocationId] = None
    org: Union[str, SocialOrganisationId] = None
    label: str = None
    current_occupancy: int = None
    is_active: Union[bool, Bool] = None
    parent: Optional[Union[str, StorageLocationId]] = None
    capacity: Optional[int] = None
    category_affinity: Optional[Union[str, "BaseCategoryEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, StorageLocationId):
            self.id = StorageLocationId(self.id)

        if self._is_empty(self.org):
            self.MissingRequiredField("org")
        if not isinstance(self.org, SocialOrganisationId):
            self.org = SocialOrganisationId(self.org)

        if self._is_empty(self.label):
            self.MissingRequiredField("label")
        if not isinstance(self.label, str):
            self.label = str(self.label)

        if self._is_empty(self.current_occupancy):
            self.MissingRequiredField("current_occupancy")
        if not isinstance(self.current_occupancy, int):
            self.current_occupancy = int(self.current_occupancy)

        if self._is_empty(self.is_active):
            self.MissingRequiredField("is_active")
        if not isinstance(self.is_active, Bool):
            self.is_active = Bool(self.is_active)

        if self.parent is not None and not isinstance(self.parent, StorageLocationId):
            self.parent = StorageLocationId(self.parent)

        if self.capacity is not None and not isinstance(self.capacity, int):
            self.capacity = int(self.capacity)

        if self.category_affinity is not None and not isinstance(self.category_affinity, BaseCategoryEnum):
            self.category_affinity = BaseCategoryEnum(self.category_affinity)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DonationSource(YAMLRoot):
    """
    Supply-side abstraction representing the origin of a donation. Phase 1 uses `anonymous_private` type only.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["DonationSource"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:DonationSource"
    class_name: ClassVar[str] = "DonationSource"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.DonationSource

    id: Union[str, DonationSourceId] = None
    source_type: Union[str, "DonationSourceTypeEnum"] = None
    lifecycle_state: Union[str, "DonationSourceLifecycleEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    anonymous_donor_id: Optional[Union[str, URIorCURIE]] = None
    corporate_donor_ref: Optional[str] = None
    organisation_ref: Optional[Union[str, SocialOrganisationId]] = None
    provenance: Optional[Union[str, ProvenanceRecordId]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, DonationSourceId):
            self.id = DonationSourceId(self.id)

        if self._is_empty(self.source_type):
            self.MissingRequiredField("source_type")
        if not isinstance(self.source_type, DonationSourceTypeEnum):
            self.source_type = DonationSourceTypeEnum(self.source_type)

        if self._is_empty(self.lifecycle_state):
            self.MissingRequiredField("lifecycle_state")
        if not isinstance(self.lifecycle_state, DonationSourceLifecycleEnum):
            self.lifecycle_state = DonationSourceLifecycleEnum(self.lifecycle_state)

        if self._is_empty(self.created_at):
            self.MissingRequiredField("created_at")
        if not isinstance(self.created_at, XSDDateTime):
            self.created_at = XSDDateTime(self.created_at)

        if self.anonymous_donor_id is not None and not isinstance(self.anonymous_donor_id, URIorCURIE):
            self.anonymous_donor_id = URIorCURIE(self.anonymous_donor_id)

        if self.corporate_donor_ref is not None and not isinstance(self.corporate_donor_ref, str):
            self.corporate_donor_ref = str(self.corporate_donor_ref)

        if self.organisation_ref is not None and not isinstance(self.organisation_ref, SocialOrganisationId):
            self.organisation_ref = SocialOrganisationId(self.organisation_ref)

        if self.provenance is not None and not isinstance(self.provenance, ProvenanceRecordId):
            self.provenance = ProvenanceRecordId(self.provenance)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DonationCollection(YAMLRoot):
    """
    A general-purpose grouping of items with optional recursive parent-child structure. Replaces the flat
    DonationBatch model.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["DonationCollection"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:DonationCollection"
    class_name: ClassVar[str] = "DonationCollection"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.DonationCollection

    id: Union[str, DonationCollectionId] = None
    org: Union[str, SocialOrganisationId] = None
    collection_type: Union[str, "CollectionTypeEnum"] = None
    label: str = None
    lifecycle_state: Union[str, "CollectionLifecycleEnum"] = None
    item_count: int = None
    total_item_count: int = None
    created_at: Union[str, XSDDateTime] = None
    created_by: Union[str, ActorId] = None
    parent: Optional[Union[str, DonationCollectionId]] = None
    donation_source: Optional[Union[str, DonationSourceId]] = None
    notes: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, DonationCollectionId):
            self.id = DonationCollectionId(self.id)

        if self._is_empty(self.org):
            self.MissingRequiredField("org")
        if not isinstance(self.org, SocialOrganisationId):
            self.org = SocialOrganisationId(self.org)

        if self._is_empty(self.collection_type):
            self.MissingRequiredField("collection_type")
        if not isinstance(self.collection_type, CollectionTypeEnum):
            self.collection_type = CollectionTypeEnum(self.collection_type)

        if self._is_empty(self.label):
            self.MissingRequiredField("label")
        if not isinstance(self.label, str):
            self.label = str(self.label)

        if self._is_empty(self.lifecycle_state):
            self.MissingRequiredField("lifecycle_state")
        if not isinstance(self.lifecycle_state, CollectionLifecycleEnum):
            self.lifecycle_state = CollectionLifecycleEnum(self.lifecycle_state)

        if self._is_empty(self.item_count):
            self.MissingRequiredField("item_count")
        if not isinstance(self.item_count, int):
            self.item_count = int(self.item_count)

        if self._is_empty(self.total_item_count):
            self.MissingRequiredField("total_item_count")
        if not isinstance(self.total_item_count, int):
            self.total_item_count = int(self.total_item_count)

        if self._is_empty(self.created_at):
            self.MissingRequiredField("created_at")
        if not isinstance(self.created_at, XSDDateTime):
            self.created_at = XSDDateTime(self.created_at)

        if self._is_empty(self.created_by):
            self.MissingRequiredField("created_by")
        if not isinstance(self.created_by, ActorId):
            self.created_by = ActorId(self.created_by)

        if self.parent is not None and not isinstance(self.parent, DonationCollectionId):
            self.parent = DonationCollectionId(self.parent)

        if self.donation_source is not None and not isinstance(self.donation_source, DonationSourceId):
            self.donation_source = DonationSourceId(self.donation_source)

        if self.notes is not None and not isinstance(self.notes, str):
            self.notes = str(self.notes)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DonationItem(YAMLRoot):
    """
    Abstract base for all donation items. Never instantiated directly.
    attribute_completeness is set by the fragment engine when a sorting episode completes; it records data quality,
    not episode completion (lifecycle_state = sorted records that — see AttributeCompletenessEnum in core.yaml).
    Lifecycle state machine is documented in ItemLifecycleStateEnum (core.yaml). Transitions are enforced by Django
    model clean(); the sorting_in_progress state prevents concurrent edits by two sorters.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["Product"]
    class_class_curie: ClassVar[str] = "schema:Product"
    class_name: ClassVar[str] = "DonationItem"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.DonationItem

    id: Union[str, DonationItemId] = None
    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None
    lifecycle_state: Union[str, "ItemLifecycleStateEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    updated_at: Union[str, XSDDateTime] = None
    attribute_completeness: Optional[Union[str, "AttributeCompletenessEnum"]] = None
    donation_source: Optional[Union[str, DonationSourceId]] = None
    storage_unit: Optional[Union[str, StorageLocationId]] = None
    sorting_notes: Optional[str] = None
    source_collection: Optional[Union[str, DonationCollectionId]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, DonationItemId):
            self.id = DonationItemId(self.id)

        if self._is_empty(self.usage):
            self.MissingRequiredField("usage")
        if not isinstance(self.usage, ItemUsageEnum):
            self.usage = ItemUsageEnum(self.usage)

        if self._is_empty(self.category):
            self.MissingRequiredField("category")
        if not isinstance(self.category, SortingCategoryEnum):
            self.category = SortingCategoryEnum(self.category)

        if self._is_empty(self.lifecycle_state):
            self.MissingRequiredField("lifecycle_state")
        if not isinstance(self.lifecycle_state, ItemLifecycleStateEnum):
            self.lifecycle_state = ItemLifecycleStateEnum(self.lifecycle_state)

        if self._is_empty(self.created_at):
            self.MissingRequiredField("created_at")
        if not isinstance(self.created_at, XSDDateTime):
            self.created_at = XSDDateTime(self.created_at)

        if self._is_empty(self.updated_at):
            self.MissingRequiredField("updated_at")
        if not isinstance(self.updated_at, XSDDateTime):
            self.updated_at = XSDDateTime(self.updated_at)

        if self.attribute_completeness is not None and not isinstance(self.attribute_completeness, AttributeCompletenessEnum):
            self.attribute_completeness = AttributeCompletenessEnum(self.attribute_completeness)

        if self.donation_source is not None and not isinstance(self.donation_source, DonationSourceId):
            self.donation_source = DonationSourceId(self.donation_source)

        if self.storage_unit is not None and not isinstance(self.storage_unit, StorageLocationId):
            self.storage_unit = StorageLocationId(self.storage_unit)

        if self.sorting_notes is not None and not isinstance(self.sorting_notes, str):
            self.sorting_notes = str(self.sorting_notes)

        if self.source_collection is not None and not isinstance(self.source_collection, DonationCollectionId):
            self.source_collection = DonationCollectionId(self.source_collection)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ClothingItem(DonationItem):
    """
    Clothing garments: tops, bottoms, outerwear, underwear, nightwear, sportswear. COICOP 03.1. Assessment:
    condition_grade (wear grade).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = CPI["ClothingAndAccessories"]
    class_class_curie: ClassVar[str] = "cpi:ClothingAndAccessories"
    class_name: ClassVar[str] = "ClothingItem"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.ClothingItem

    id: Union[str, ClothingItemId] = None
    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None
    lifecycle_state: Union[str, "ItemLifecycleStateEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    updated_at: Union[str, XSDDateTime] = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None
    subcategory: Optional[Union[str, "ClothingSubcategoryEnum"]] = None
    tops_subcategory: Optional[Union[str, "TopsSubcategoryEnum"]] = None
    bottoms_subcategory: Optional[Union[str, "BottomsSubcategoryEnum"]] = None
    material: Optional[Union[str, "ClothingMaterialEnum"]] = None
    is_winter_suitable: Optional[Union[bool, Bool]] = None
    demographic: Optional[Union[str, "DemographicEnum"]] = None
    is_maternity: Optional[Union[bool, Bool]] = None
    size: Optional[Union[Union[str, "ClothingSizeEnum"], list[Union[str, "ClothingSizeEnum"]]]] = empty_list()
    season: Optional[Union[Union[str, "SeasonEnum"], list[Union[str, "SeasonEnum"]]]] = empty_list()
    intact_labels: Optional[Union[bool, Bool]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ClothingItemId):
            self.id = ClothingItemId(self.id)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        if self.subcategory is not None and not isinstance(self.subcategory, ClothingSubcategoryEnum):
            self.subcategory = ClothingSubcategoryEnum(self.subcategory)

        if self.tops_subcategory is not None and not isinstance(self.tops_subcategory, TopsSubcategoryEnum):
            self.tops_subcategory = TopsSubcategoryEnum(self.tops_subcategory)

        if self.bottoms_subcategory is not None and not isinstance(self.bottoms_subcategory, BottomsSubcategoryEnum):
            self.bottoms_subcategory = BottomsSubcategoryEnum(self.bottoms_subcategory)

        if self.material is not None and not isinstance(self.material, ClothingMaterialEnum):
            self.material = ClothingMaterialEnum(self.material)

        if self.is_winter_suitable is not None and not isinstance(self.is_winter_suitable, Bool):
            self.is_winter_suitable = Bool(self.is_winter_suitable)

        if self.demographic is not None and not isinstance(self.demographic, DemographicEnum):
            self.demographic = DemographicEnum(self.demographic)

        if self.is_maternity is not None and not isinstance(self.is_maternity, Bool):
            self.is_maternity = Bool(self.is_maternity)

        if not isinstance(self.size, list):
            self.size = [self.size] if self.size is not None else []
        self.size = [v if isinstance(v, ClothingSizeEnum) else ClothingSizeEnum(v) for v in self.size]

        if not isinstance(self.season, list):
            self.season = [self.season] if self.season is not None else []
        self.season = [v if isinstance(v, SeasonEnum) else SeasonEnum(v) for v in self.season]

        if self.intact_labels is not None and not isinstance(self.intact_labels, Bool):
            self.intact_labels = Bool(self.intact_labels)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class AccessoriesItem(DonationItem):
    """
    Fashion and personal accessories: hats, scarves, gloves, belts, bags, jewellery, sunglasses, watches. COICOP 03.1,
    grouped with clothing but kept separate here — no demographic→size value map, no clothing UC rules, simpler
    age-only AccessoriesDemographicEnum. Assessment: condition_grade (wear grade).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = PTO["Fashion_accessory"]
    class_class_curie: ClassVar[str] = "pto:Fashion_accessory"
    class_name: ClassVar[str] = "AccessoriesItem"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.AccessoriesItem

    id: Union[str, AccessoriesItemId] = None
    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None
    lifecycle_state: Union[str, "ItemLifecycleStateEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    updated_at: Union[str, XSDDateTime] = None
    subcategory: Union[str, "AccessoriesSubcategoryEnum"] = None
    demographic: Optional[Union[str, "AccessoriesDemographicEnum"]] = None
    material: Optional[Union[str, "AccessoriesMaterialEnum"]] = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, AccessoriesItemId):
            self.id = AccessoriesItemId(self.id)

        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, AccessoriesSubcategoryEnum):
            self.subcategory = AccessoriesSubcategoryEnum(self.subcategory)

        if self.demographic is not None and not isinstance(self.demographic, AccessoriesDemographicEnum):
            self.demographic = AccessoriesDemographicEnum(self.demographic)

        if self.material is not None and not isinstance(self.material, AccessoriesMaterialEnum):
            self.material = AccessoriesMaterialEnum(self.material)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class FootwearItem(DonationItem):
    """
    Footwear: shoes, boots, sandals, slippers. COICOP 03.2. Separated from ClothingItem for shoe-specific sizing
    (EU/UK/US/CM) and pair completeness. Assessment: condition_grade (wear grade).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = PTO["Footwear"]
    class_class_curie: ClassVar[str] = "pto:Footwear"
    class_name: ClassVar[str] = "FootwearItem"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.FootwearItem

    id: Union[str, FootwearItemId] = None
    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None
    lifecycle_state: Union[str, "ItemLifecycleStateEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    updated_at: Union[str, XSDDateTime] = None
    subcategory: Union[str, "FootwearSubcategoryEnum"] = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None
    material: Optional[Union[str, "FootwearMaterialEnum"]] = None
    is_pair_complete: Optional[Union[bool, Bool]] = None
    is_winter_suitable: Optional[Union[bool, Bool]] = None
    demographic: Optional[Union[str, "DemographicEnum"]] = None
    shoe_size: Optional[str] = None
    shoe_size_system: Optional[Union[str, "ShoeSizeSystemEnum"]] = None
    season: Optional[Union[Union[str, "SeasonEnum"], list[Union[str, "SeasonEnum"]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, FootwearItemId):
            self.id = FootwearItemId(self.id)

        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, FootwearSubcategoryEnum):
            self.subcategory = FootwearSubcategoryEnum(self.subcategory)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        if self.material is not None and not isinstance(self.material, FootwearMaterialEnum):
            self.material = FootwearMaterialEnum(self.material)

        if self.is_pair_complete is not None and not isinstance(self.is_pair_complete, Bool):
            self.is_pair_complete = Bool(self.is_pair_complete)

        if self.is_winter_suitable is not None and not isinstance(self.is_winter_suitable, Bool):
            self.is_winter_suitable = Bool(self.is_winter_suitable)

        if self.demographic is not None and not isinstance(self.demographic, DemographicEnum):
            self.demographic = DemographicEnum(self.demographic)

        if self.shoe_size is not None and not isinstance(self.shoe_size, str):
            self.shoe_size = str(self.shoe_size)

        if self.shoe_size_system is not None and not isinstance(self.shoe_size_system, ShoeSizeSystemEnum):
            self.shoe_size_system = ShoeSizeSystemEnum(self.shoe_size_system)

        if not isinstance(self.season, list):
            self.season = [self.season] if self.season is not None else []
        self.season = [v if isinstance(v, SeasonEnum) else SeasonEnum(v) for v in self.season]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class FurnitureItem(DonationItem):
    """
    Structural furniture: chairs, tables, beds, wardrobes, shelving. COICOP 05.1. Assessment: FurnitureAssessmentEnum
    — structural soundness is the primary redistribution signal (a scratched but solid chair is redistributable; a
    wobbly but clean one is not). assessment_result required regardless of usage since flatpack furniture can have
    assembly/manufacturing defects.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = PTO["Furniture"]
    class_class_curie: ClassVar[str] = "pto:Furniture"
    class_name: ClassVar[str] = "FurnitureItem"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.FurnitureItem

    id: Union[str, FurnitureItemId] = None
    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None
    lifecycle_state: Union[str, "ItemLifecycleStateEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    updated_at: Union[str, XSDDateTime] = None
    subcategory: Union[str, "FurnitureSubcategoryEnum"] = None
    material: Optional[Union[str, "FurnitureMaterialEnum"]] = None
    dimensions: Optional[str] = None
    style: Optional[str] = None
    assessment_result: Optional[Union[str, "FurnitureAssessmentEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, FurnitureItemId):
            self.id = FurnitureItemId(self.id)

        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, FurnitureSubcategoryEnum):
            self.subcategory = FurnitureSubcategoryEnum(self.subcategory)

        if self.material is not None and not isinstance(self.material, FurnitureMaterialEnum):
            self.material = FurnitureMaterialEnum(self.material)

        if self.dimensions is not None and not isinstance(self.dimensions, str):
            self.dimensions = str(self.dimensions)

        if self.style is not None and not isinstance(self.style, str):
            self.style = str(self.style)

        if self.assessment_result is not None and not isinstance(self.assessment_result, FurnitureAssessmentEnum):
            self.assessment_result = FurnitureAssessmentEnum(self.assessment_result)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class BeddingTextilesItem(DonationItem):
    """
    Bedding and household textiles: blankets, duvets, mattresses, pillows, sleeping bags, towels, curtains. COICOP
    05.2. Separated from HouseholdItem — UNHCR NFI standards list blankets/sleeping mats as core relief items, and
    hygiene assessment differs from wear grading. Assessment: BeddingAssessmentEnum (hygiene primary signal — a worn
    but clean blanket is redistributable, a stained mattress is not). assessment_result required regardless of usage.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = PTO["Bedding"]
    class_class_curie: ClassVar[str] = "pto:Bedding"
    class_name: ClassVar[str] = "BeddingTextilesItem"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.BeddingTextilesItem

    id: Union[str, BeddingTextilesItemId] = None
    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None
    lifecycle_state: Union[str, "ItemLifecycleStateEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    updated_at: Union[str, XSDDateTime] = None
    subcategory: Union[str, "BeddingTextilesSubcategoryEnum"] = None
    material: Optional[Union[str, "BeddingMaterialEnum"]] = None
    is_set_complete: Optional[Union[bool, Bool]] = None
    is_winter_suitable: Optional[Union[bool, Bool]] = None
    assessment_result: Optional[Union[str, "BeddingAssessmentEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, BeddingTextilesItemId):
            self.id = BeddingTextilesItemId(self.id)

        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, BeddingTextilesSubcategoryEnum):
            self.subcategory = BeddingTextilesSubcategoryEnum(self.subcategory)

        if self.material is not None and not isinstance(self.material, BeddingMaterialEnum):
            self.material = BeddingMaterialEnum(self.material)

        if self.is_set_complete is not None and not isinstance(self.is_set_complete, Bool):
            self.is_set_complete = Bool(self.is_set_complete)

        if self.is_winter_suitable is not None and not isinstance(self.is_winter_suitable, Bool):
            self.is_winter_suitable = Bool(self.is_winter_suitable)

        if self.assessment_result is not None and not isinstance(self.assessment_result, BeddingAssessmentEnum):
            self.assessment_result = BeddingAssessmentEnum(self.assessment_result)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class HouseholdItem(DonationItem):
    """
    Household and kitchen goods: cookware, crockery, small appliances, cleaning tools, home decor, garden tools.
    COICOP 05.3–05.5. Bedding and textiles (05.2) are BeddingTextilesItem, not this class. Assessment: condition_grade
    (wear grade).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = PTO["Household_goods"]
    class_class_curie: ClassVar[str] = "pto:Household_goods"
    class_name: ClassVar[str] = "HouseholdItem"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.HouseholdItem

    id: Union[str, HouseholdItemId] = None
    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None
    lifecycle_state: Union[str, "ItemLifecycleStateEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    updated_at: Union[str, XSDDateTime] = None
    subcategory: Union[str, "HouseholdSubcategoryEnum"] = None
    material: Optional[Union[str, "HouseholdMaterialEnum"]] = None
    is_set_complete: Optional[Union[bool, Bool]] = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, HouseholdItemId):
            self.id = HouseholdItemId(self.id)

        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, HouseholdSubcategoryEnum):
            self.subcategory = HouseholdSubcategoryEnum(self.subcategory)

        if self.material is not None and not isinstance(self.material, HouseholdMaterialEnum):
            self.material = HouseholdMaterialEnum(self.material)

        if self.is_set_complete is not None and not isinstance(self.is_set_complete, Bool):
            self.is_set_complete = Bool(self.is_set_complete)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ElectronicsItem(DonationItem):
    """
    Consumer electronics: phones, tablets, laptops, cameras, audio devices, cables, gaming consoles. COICOP 09.1–09.2.
    Assessment: ElectronicsAssessmentEnum — functional state is the primary redistribution signal (a cracked-screen
    phone that works beats a pristine one that doesn't). assessment_result required regardless of usage. Data wiping
    is enforced by the fragment engine, not a schema rule.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = PTO["Consumer_electronics"]
    class_class_curie: ClassVar[str] = "pto:Consumer_electronics"
    class_name: ClassVar[str] = "ElectronicsItem"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.ElectronicsItem

    id: Union[str, ElectronicsItemId] = None
    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None
    lifecycle_state: Union[str, "ItemLifecycleStateEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    updated_at: Union[str, XSDDateTime] = None
    subcategory: Union[str, "ElectronicsSubcategoryEnum"] = None
    assessment_result: Union[str, "ElectronicsAssessmentEnum"] = None
    material: Optional[str] = None
    includes_charger: Optional[Union[bool, Bool]] = None
    includes_original_packaging: Optional[Union[bool, Bool]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ElectronicsItemId):
            self.id = ElectronicsItemId(self.id)

        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, ElectronicsSubcategoryEnum):
            self.subcategory = ElectronicsSubcategoryEnum(self.subcategory)

        if self._is_empty(self.assessment_result):
            self.MissingRequiredField("assessment_result")
        if not isinstance(self.assessment_result, ElectronicsAssessmentEnum):
            self.assessment_result = ElectronicsAssessmentEnum(self.assessment_result)

        if self.material is not None and not isinstance(self.material, str):
            self.material = str(self.material)

        if self.includes_charger is not None and not isinstance(self.includes_charger, Bool):
            self.includes_charger = Bool(self.includes_charger)

        if self.includes_original_packaging is not None and not isinstance(self.includes_original_packaging, Bool):
            self.includes_original_packaging = Bool(self.includes_original_packaging)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ToysItem(DonationItem):
    """
    Toys and games. COICOP 09.3. Age grading follows EU Toy Safety Directive 2009/48/EC; the small-parts
    choking-hazard UC rule also references ASTM F963. Assessment: condition_grade (wear grade).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = PTO["Toy"]
    class_class_curie: ClassVar[str] = "pto:Toy"
    class_name: ClassVar[str] = "ToysItem"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.ToysItem

    id: Union[str, ToysItemId] = None
    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None
    lifecycle_state: Union[str, "ItemLifecycleStateEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    updated_at: Union[str, XSDDateTime] = None
    subcategory: Union[str, "ToysSubcategoryEnum"] = None
    material: Optional[Union[str, "ToysMaterialEnum"]] = None
    age_range: Optional[Union[str, "ToyAgeRangeEnum"]] = None
    is_set_complete: Optional[Union[bool, Bool]] = None
    has_small_parts: Optional[Union[bool, Bool]] = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ToysItemId):
            self.id = ToysItemId(self.id)

        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, ToysSubcategoryEnum):
            self.subcategory = ToysSubcategoryEnum(self.subcategory)

        if self.material is not None and not isinstance(self.material, ToysMaterialEnum):
            self.material = ToysMaterialEnum(self.material)

        if self.age_range is not None and not isinstance(self.age_range, ToyAgeRangeEnum):
            self.age_range = ToyAgeRangeEnum(self.age_range)

        if self.is_set_complete is not None and not isinstance(self.is_set_complete, Bool):
            self.is_set_complete = Bool(self.is_set_complete)

        if self.has_small_parts is not None and not isinstance(self.has_small_parts, Bool):
            self.has_small_parts = Bool(self.has_small_parts)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class SportsItem(DonationItem):
    """
    Sports and fitness equipment. COICOP 09.4. Bicycles are placed here by domain convention (COICOP assigns them to
    Division 07). Dual-track assessment: protective_gear subcategory uses SportsProtectiveAssessmentEnum (wear grade
    can't catch impact damage not visible under an intact shell); everything else uses condition_grade.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = PTO["Sporting_goods"]
    class_class_curie: ClassVar[str] = "pto:Sporting_goods"
    class_name: ClassVar[str] = "SportsItem"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.SportsItem

    id: Union[str, SportsItemId] = None
    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None
    lifecycle_state: Union[str, "ItemLifecycleStateEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    updated_at: Union[str, XSDDateTime] = None
    subcategory: Union[str, "SportsSubcategoryEnum"] = None
    material: Optional[str] = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None
    sport_type: Optional[str] = None
    demographic: Optional[Union[str, "DemographicEnum"]] = None
    is_set_complete: Optional[Union[bool, Bool]] = None
    assessment_result: Optional[Union[str, "SportsProtectiveAssessmentEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, SportsItemId):
            self.id = SportsItemId(self.id)

        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, SportsSubcategoryEnum):
            self.subcategory = SportsSubcategoryEnum(self.subcategory)

        if self.material is not None and not isinstance(self.material, str):
            self.material = str(self.material)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        if self.sport_type is not None and not isinstance(self.sport_type, str):
            self.sport_type = str(self.sport_type)

        if self.demographic is not None and not isinstance(self.demographic, DemographicEnum):
            self.demographic = DemographicEnum(self.demographic)

        if self.is_set_complete is not None and not isinstance(self.is_set_complete, Bool):
            self.is_set_complete = Bool(self.is_set_complete)

        if self.assessment_result is not None and not isinstance(self.assessment_result, SportsProtectiveAssessmentEnum):
            self.assessment_result = SportsProtectiveAssessmentEnum(self.assessment_result)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class BooksItem(DonationItem):
    """
    Books and educational materials. COICOP 09.5. No demographic/size dimension — age_range (BookAgeRangeEnum) is
    broader and non-gendered. Assessment: condition_grade (wear grade).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["Book"]
    class_class_curie: ClassVar[str] = "schema:Book"
    class_name: ClassVar[str] = "BooksItem"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.BooksItem

    id: Union[str, BooksItemId] = None
    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None
    lifecycle_state: Union[str, "ItemLifecycleStateEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    updated_at: Union[str, XSDDateTime] = None
    subcategory: Union[str, "BooksSubcategoryEnum"] = None
    material: Optional[str] = None
    language: Optional[str] = None
    age_range: Optional[Union[str, "BookAgeRangeEnum"]] = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, BooksItemId):
            self.id = BooksItemId(self.id)

        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, BooksSubcategoryEnum):
            self.subcategory = BooksSubcategoryEnum(self.subcategory)

        if self.material is not None and not isinstance(self.material, str):
            self.material = str(self.material)

        if self.language is not None and not isinstance(self.language, str):
            self.language = str(self.language)

        if self.age_range is not None and not isinstance(self.age_range, BookAgeRangeEnum):
            self.age_range = BookAgeRangeEnum(self.age_range)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class StationeryItem(DonationItem):
    """
    Stationery and office supplies: pens, notebooks, art supplies, calculators. COICOP 09.5. Separated from BooksItem
    — different sorting paths, condition vocabulary, and demand patterns. Assessment: condition_grade (wear grade).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = PTO["Stationery"]
    class_class_curie: ClassVar[str] = "pto:Stationery"
    class_name: ClassVar[str] = "StationeryItem"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.StationeryItem

    id: Union[str, StationeryItemId] = None
    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None
    lifecycle_state: Union[str, "ItemLifecycleStateEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    updated_at: Union[str, XSDDateTime] = None
    subcategory: Union[str, "StationerySubcategoryEnum"] = None
    material: Optional[str] = None
    is_set_complete: Optional[Union[bool, Bool]] = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, StationeryItemId):
            self.id = StationeryItemId(self.id)

        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, StationerySubcategoryEnum):
            self.subcategory = StationerySubcategoryEnum(self.subcategory)

        if self.material is not None and not isinstance(self.material, str):
            self.material = str(self.material)

        if self.is_set_complete is not None and not isinstance(self.is_set_complete, Bool):
            self.is_set_complete = Bool(self.is_set_complete)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class PersonalCareItem(DonationItem):
    """
    Personal care, hygiene, and health products. Merges COICOP 06.1 and 12.1 — the operative safety rules (sealed
    required, used tools blocked, expiry enforced) are identical across both. Assessment: is_sealed + expiry_date, no
    condition_grade — a wear grade is meaningless for a tube of toothpaste.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = PTO["Personal_hygiene"]
    class_class_curie: ClassVar[str] = "pto:Personal_hygiene"
    class_name: ClassVar[str] = "PersonalCareItem"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.PersonalCareItem

    id: Union[str, PersonalCareItemId] = None
    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None
    lifecycle_state: Union[str, "ItemLifecycleStateEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    updated_at: Union[str, XSDDateTime] = None
    subcategory: Union[str, "PersonalCareSubcategoryEnum"] = None
    material: Optional[str] = None
    is_sealed: Optional[Union[bool, Bool]] = None
    expiry_date: Optional[Union[str, XSDDate]] = None
    net_content_value: Optional[Decimal] = None
    net_content_unit: Optional[Union[str, "NetContentUnitEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, PersonalCareItemId):
            self.id = PersonalCareItemId(self.id)

        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, PersonalCareSubcategoryEnum):
            self.subcategory = PersonalCareSubcategoryEnum(self.subcategory)

        if self.material is not None and not isinstance(self.material, str):
            self.material = str(self.material)

        if self.is_sealed is not None and not isinstance(self.is_sealed, Bool):
            self.is_sealed = Bool(self.is_sealed)

        if self.expiry_date is not None and not isinstance(self.expiry_date, XSDDate):
            self.expiry_date = XSDDate(self.expiry_date)

        if self.net_content_value is not None and not isinstance(self.net_content_value, Decimal):
            self.net_content_value = Decimal(self.net_content_value)

        if self.net_content_unit is not None and not isinstance(self.net_content_unit, NetContentUnitEnum):
            self.net_content_unit = NetContentUnitEnum(self.net_content_unit)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class MobilityAidsItem(DonationItem):
    """
    Mobility aids and assistive devices: wheelchairs, crutches, walking frames, hearing aids, orthotics, daily living
    aids. COICOP 06.1.3 and 06.2. Assessment: MobilityAssessmentEnum, capturing structural soundness, functional
    state, and body-contact hygiene in one enum. assessment_result required regardless of usage.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = PTO["Assistive_technology"]
    class_class_curie: ClassVar[str] = "pto:Assistive_technology"
    class_name: ClassVar[str] = "MobilityAidsItem"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.MobilityAidsItem

    id: Union[str, MobilityAidsItemId] = None
    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None
    lifecycle_state: Union[str, "ItemLifecycleStateEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    updated_at: Union[str, XSDDateTime] = None
    subcategory: Union[str, "MobilityAidsSubcategoryEnum"] = None
    material: Optional[str] = None
    assessment_result: Optional[Union[str, "MobilityAssessmentEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, MobilityAidsItemId):
            self.id = MobilityAidsItemId(self.id)

        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, MobilityAidsSubcategoryEnum):
            self.subcategory = MobilityAidsSubcategoryEnum(self.subcategory)

        if self.material is not None and not isinstance(self.material, str):
            self.material = str(self.material)

        if self.assessment_result is not None and not isinstance(self.assessment_result, MobilityAssessmentEnum):
            self.assessment_result = MobilityAssessmentEnum(self.assessment_result)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class BabyInfantItem(DonationItem):
    """
    Baby and infant supplies: pushchairs, cots, car seats, infant formula, feeding bottles, baby monitors, bath
    equipment. Baby clothing belongs in ClothingItem (demographic=baby). Treated as a first-class category (COICOP
    otherwise scatters these across Divisions 01/03/05), following Open Eligibility and UNHCR NFI kit practice.
    Three-track assessment: Track 1 — safety-critical equipment (BabyEquipmentAssessmentEnum): pushchairs, cots, car
    seats, carriers, high chairs, sleeping bags (EN 1888/716/14344/16781). Baby sleeping bags are Track 1, not
    BeddingTextilesItem, since EN 16781 differs from adult sleeping-bag hygiene checks. Track 2 — consumables
    (is_sealed + expiry_date): infant formula, feeding bottles/teats, baby food. Track 3 — general gear
    (condition_grade): bath, changing, monitors, bouncers.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = PTO["Baby_transport"]
    class_class_curie: ClassVar[str] = "pto:Baby_transport"
    class_name: ClassVar[str] = "BabyInfantItem"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.BabyInfantItem

    id: Union[str, BabyInfantItemId] = None
    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None
    lifecycle_state: Union[str, "ItemLifecycleStateEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    updated_at: Union[str, XSDDateTime] = None
    subcategory: Union[str, "BabyInfantSubcategoryEnum"] = None
    material: Optional[str] = None
    manufacture_year: Optional[int] = None
    includes_original_accessories: Optional[Union[bool, Bool]] = None
    is_winter_suitable: Optional[Union[bool, Bool]] = None
    is_sealed: Optional[Union[bool, Bool]] = None
    expiry_date: Optional[Union[str, XSDDate]] = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None
    nappy_size: Optional[Union[str, "NappySizeEnum"]] = None
    assessment_result: Optional[Union[str, "BabyEquipmentAssessmentEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, BabyInfantItemId):
            self.id = BabyInfantItemId(self.id)

        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, BabyInfantSubcategoryEnum):
            self.subcategory = BabyInfantSubcategoryEnum(self.subcategory)

        if self.material is not None and not isinstance(self.material, str):
            self.material = str(self.material)

        if self.manufacture_year is not None and not isinstance(self.manufacture_year, int):
            self.manufacture_year = int(self.manufacture_year)

        if self.includes_original_accessories is not None and not isinstance(self.includes_original_accessories, Bool):
            self.includes_original_accessories = Bool(self.includes_original_accessories)

        if self.is_winter_suitable is not None and not isinstance(self.is_winter_suitable, Bool):
            self.is_winter_suitable = Bool(self.is_winter_suitable)

        if self.is_sealed is not None and not isinstance(self.is_sealed, Bool):
            self.is_sealed = Bool(self.is_sealed)

        if self.expiry_date is not None and not isinstance(self.expiry_date, XSDDate):
            self.expiry_date = XSDDate(self.expiry_date)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        if self.nappy_size is not None and not isinstance(self.nappy_size, NappySizeEnum):
            self.nappy_size = NappySizeEnum(self.nappy_size)

        if self.assessment_result is not None and not isinstance(self.assessment_result, BabyEquipmentAssessmentEnum):
            self.assessment_result = BabyEquipmentAssessmentEnum(self.assessment_result)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class FoodItem(DonationItem):
    """
    Food donation item. COICOP Division 01. Phase 1 stub — fully declared to establish the schema; the sort_food
    process path activates once food-bank organisations are onboarded. Assessment: packaging_intact + expiry_date —
    food safety is binary, no condition_grade.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = FOODON["00001006"]
    class_class_curie: ClassVar[str] = "foodon:00001006"
    class_name: ClassVar[str] = "FoodItem"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.FoodItem

    id: Union[str, FoodItemId] = None
    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None
    lifecycle_state: Union[str, "ItemLifecycleStateEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    updated_at: Union[str, XSDDateTime] = None
    subcategory: Union[str, "FoodTypeEnum"] = None
    packaging_intact: Union[bool, Bool] = None
    storage_requirement: Union[str, "StorageRequirementEnum"] = None
    expiry_date: Optional[Union[str, XSDDate]] = None
    net_content_value: Optional[Decimal] = None
    net_content_unit: Optional[Union[str, "NetContentUnitEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, FoodItemId):
            self.id = FoodItemId(self.id)

        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, FoodTypeEnum):
            self.subcategory = FoodTypeEnum(self.subcategory)

        if self._is_empty(self.packaging_intact):
            self.MissingRequiredField("packaging_intact")
        if not isinstance(self.packaging_intact, Bool):
            self.packaging_intact = Bool(self.packaging_intact)

        if self._is_empty(self.storage_requirement):
            self.MissingRequiredField("storage_requirement")
        if not isinstance(self.storage_requirement, StorageRequirementEnum):
            self.storage_requirement = StorageRequirementEnum(self.storage_requirement)

        if self.expiry_date is not None and not isinstance(self.expiry_date, XSDDate):
            self.expiry_date = XSDDate(self.expiry_date)

        if self.net_content_value is not None and not isinstance(self.net_content_value, Decimal):
            self.net_content_value = Decimal(self.net_content_value)

        if self.net_content_unit is not None and not isinstance(self.net_content_unit, NetContentUnitEnum):
            self.net_content_unit = NetContentUnitEnum(self.net_content_unit)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class OtherItem(DonationItem):
    """
    Catch-all for donation items not fitting any other category. Minimal slots only (item_description +
    condition_grade), via OtherCategory (categories/other.yaml). Use sparingly: if a new item type appears frequently
    in operations, it warrants a proper subclass with a category mixin and dedicated sorting fragment rather than
    accumulating in OtherItem.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["Product"]
    class_class_curie: ClassVar[str] = "schema:Product"
    class_name: ClassVar[str] = "OtherItem"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.OtherItem

    id: Union[str, OtherItemId] = None
    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None
    lifecycle_state: Union[str, "ItemLifecycleStateEnum"] = None
    created_at: Union[str, XSDDateTime] = None
    updated_at: Union[str, XSDDateTime] = None
    item_description: str = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, OtherItemId):
            self.id = OtherItemId(self.id)

        if self._is_empty(self.item_description):
            self.MissingRequiredField("item_description")
        if not isinstance(self.item_description, str):
            self.item_description = str(self.item_description)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class StorageCollection(YAMLRoot):
    """
    A physical donation item assigned to storage. Parallel to DonationItem but reached via a different lifecycle entry
    point — items already sorted and stored, tracked here for stock/storage purposes.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["Product"]
    class_class_curie: ClassVar[str] = "schema:Product"
    class_name: ClassVar[str] = "StorageCollection"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.StorageCollection

    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "BaseCategoryEnum"] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.usage):
            self.MissingRequiredField("usage")
        if not isinstance(self.usage, ItemUsageEnum):
            self.usage = ItemUsageEnum(self.usage)

        if self._is_empty(self.category):
            self.MissingRequiredField("category")
        if not isinstance(self.category, BaseCategoryEnum):
            self.category = BaseCategoryEnum(self.category)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class SortedCollection(YAMLRoot):
    """
    A physical donation item that has completed sorting. Parallel to DonationItem and StorageCollection but reached
    via a different lifecycle entry point.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["Product"]
    class_class_curie: ClassVar[str] = "schema:Product"
    class_name: ClassVar[str] = "SortedCollection"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.SortedCollection

    usage: Union[str, "ItemUsageEnum"] = None
    category: Union[str, "SortingCategoryEnum"] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.usage):
            self.MissingRequiredField("usage")
        if not isinstance(self.usage, ItemUsageEnum):
            self.usage = ItemUsageEnum(self.usage)

        if self._is_empty(self.category):
            self.MissingRequiredField("category")
        if not isinstance(self.category, SortingCategoryEnum):
            self.category = SortingCategoryEnum(self.category)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DemandSignal(YAMLRoot):
    """
    A signal representing demand for a category of items. Covers standing interests, time-bounded campaigns, and
    specific beneficiary requests under a single unified model.
    category's range is BaseCategoryEnum (core.yaml) — dispatch_to resolves to the bare Tier 1 category mixin only,
    since a demand signal describes what's wanted, not a physical item in hand: assessment_result and
    lifecycle_state-gated visibility never apply here.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["DemandSignal"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:DemandSignal"
    class_name: ClassVar[str] = "DemandSignal"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.DemandSignal

    id: Union[str, DemandSignalId] = None
    category: Union[str, "BaseCategoryEnum"] = None
    lifecycle_state: Union[str, "DemandSignalLifecycleEnum"] = None
    org: Union[str, SocialOrganisationId] = None
    urgency_tier: Optional[Union[str, "UrgencyTierEnum"]] = None
    household_situation: Optional[Union[str, "HouseholdSituationEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, DemandSignalId):
            self.id = DemandSignalId(self.id)

        if self._is_empty(self.category):
            self.MissingRequiredField("category")
        if not isinstance(self.category, BaseCategoryEnum):
            self.category = BaseCategoryEnum(self.category)

        if self._is_empty(self.lifecycle_state):
            self.MissingRequiredField("lifecycle_state")
        if not isinstance(self.lifecycle_state, DemandSignalLifecycleEnum):
            self.lifecycle_state = DemandSignalLifecycleEnum(self.lifecycle_state)

        if self._is_empty(self.org):
            self.MissingRequiredField("org")
        if not isinstance(self.org, SocialOrganisationId):
            self.org = SocialOrganisationId(self.org)

        if self.urgency_tier is not None and not isinstance(self.urgency_tier, UrgencyTierEnum):
            self.urgency_tier = UrgencyTierEnum(self.urgency_tier)

        if self.household_situation is not None and not isinstance(self.household_situation, HouseholdSituationEnum):
            self.household_situation = HouseholdSituationEnum(self.household_situation)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Campaign(YAMLRoot):
    """
    A public-facing appeal grouping related DemandSignals under a shared title, timeline, and beneficiary group.
    Campaign progress is derived from its child signals.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["Event"]
    class_class_curie: ClassVar[str] = "schema:Event"
    class_name: ClassVar[str] = "Campaign"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.Campaign

    id: Union[str, CampaignId] = None
    org: Union[str, SocialOrganisationId] = None
    title: str = None
    starts_at: Union[str, XSDDateTime] = None
    ends_at: Union[str, XSDDateTime] = None
    lifecycle_state: Union[str, "CampaignLifecycleEnum"] = None
    description: Optional[str] = None
    target_beneficiary_group: Optional[str] = None
    signals: Optional[Union[Union[str, DemandSignalId], list[Union[str, DemandSignalId]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, CampaignId):
            self.id = CampaignId(self.id)

        if self._is_empty(self.org):
            self.MissingRequiredField("org")
        if not isinstance(self.org, SocialOrganisationId):
            self.org = SocialOrganisationId(self.org)

        if self._is_empty(self.title):
            self.MissingRequiredField("title")
        if not isinstance(self.title, str):
            self.title = str(self.title)

        if self._is_empty(self.starts_at):
            self.MissingRequiredField("starts_at")
        if not isinstance(self.starts_at, XSDDateTime):
            self.starts_at = XSDDateTime(self.starts_at)

        if self._is_empty(self.ends_at):
            self.MissingRequiredField("ends_at")
        if not isinstance(self.ends_at, XSDDateTime):
            self.ends_at = XSDDateTime(self.ends_at)

        if self._is_empty(self.lifecycle_state):
            self.MissingRequiredField("lifecycle_state")
        if not isinstance(self.lifecycle_state, CampaignLifecycleEnum):
            self.lifecycle_state = CampaignLifecycleEnum(self.lifecycle_state)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if self.target_beneficiary_group is not None and not isinstance(self.target_beneficiary_group, str):
            self.target_beneficiary_group = str(self.target_beneficiary_group)

        if not isinstance(self.signals, list):
            self.signals = [self.signals] if self.signals is not None else []
        self.signals = [v if isinstance(v, DemandSignalId) else DemandSignalId(v) for v in self.signals]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class CategoryMixin(YAMLRoot):
    """
    Abstract mixin base for all category classes except FoodCategory (see schema description above for why). Provides
    shared slots (material). Does not declare a condition rule — each category type handles condition differently.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["CategoryMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:CategoryMixin"
    class_name: ClassVar[str] = "CategoryMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.CategoryMixin

    material: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.material is not None and not isinstance(self.material, str):
            self.material = str(self.material)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class AccessoriesCategory(CategoryMixin):
    """
    Mixin for fashion and personal accessories. Applied to AccessoriesItem via mixins: [AccessoriesCategory].
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["AccessoriesCategory"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:AccessoriesCategory"
    class_name: ClassVar[str] = "AccessoriesCategory"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.AccessoriesCategory

    subcategory: Union[str, "AccessoriesSubcategoryEnum"] = None
    demographic: Optional[Union[str, "AccessoriesDemographicEnum"]] = None
    material: Optional[Union[str, "AccessoriesMaterialEnum"]] = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, AccessoriesSubcategoryEnum):
            self.subcategory = AccessoriesSubcategoryEnum(self.subcategory)

        if self.demographic is not None and not isinstance(self.demographic, AccessoriesDemographicEnum):
            self.demographic = AccessoriesDemographicEnum(self.demographic)

        if self.material is not None and not isinstance(self.material, AccessoriesMaterialEnum):
            self.material = AccessoriesMaterialEnum(self.material)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class AccessoriesPhysicalItemMixin(AccessoriesCategory):
    """
    Shared physical-item dispatch target for the Accessories category, used identically by DonationItem,
    StorageCollection, and SortedCollection. Pure composition — no slots or rules of its own.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["AccessoriesPhysicalItemMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:AccessoriesPhysicalItemMixin"
    class_name: ClassVar[str] = "AccessoriesPhysicalItemMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.AccessoriesPhysicalItemMixin

    subcategory: Union[str, "AccessoriesSubcategoryEnum"] = None

@dataclass(repr=False)
class ClothingCategory(CategoryMixin):
    """
    Mixin carrying clothing-specific slots, value maps, and UC rules. Applied to ClothingItem via mixins:
    [ClothingCategory]. Does NOT include accessories — see AccessoriesCategory (accessories.yaml). Domain-level rules
    only; lifecycle-aware (lc-*) rules live in ClothingContextRulesMixin (categories/_context_rules.yaml).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["ClothingCategory"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:ClothingCategory"
    class_name: ClassVar[str] = "ClothingCategory"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.ClothingCategory

    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None
    subcategory: Optional[Union[str, "ClothingSubcategoryEnum"]] = None
    tops_subcategory: Optional[Union[str, "TopsSubcategoryEnum"]] = None
    bottoms_subcategory: Optional[Union[str, "BottomsSubcategoryEnum"]] = None
    material: Optional[Union[str, "ClothingMaterialEnum"]] = None
    is_winter_suitable: Optional[Union[bool, Bool]] = None
    demographic: Optional[Union[str, "DemographicEnum"]] = None
    is_maternity: Optional[Union[bool, Bool]] = None
    size: Optional[Union[Union[str, "ClothingSizeEnum"], list[Union[str, "ClothingSizeEnum"]]]] = empty_list()
    season: Optional[Union[Union[str, "SeasonEnum"], list[Union[str, "SeasonEnum"]]]] = empty_list()
    intact_labels: Optional[Union[bool, Bool]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        if self.subcategory is not None and not isinstance(self.subcategory, ClothingSubcategoryEnum):
            self.subcategory = ClothingSubcategoryEnum(self.subcategory)

        if self.tops_subcategory is not None and not isinstance(self.tops_subcategory, TopsSubcategoryEnum):
            self.tops_subcategory = TopsSubcategoryEnum(self.tops_subcategory)

        if self.bottoms_subcategory is not None and not isinstance(self.bottoms_subcategory, BottomsSubcategoryEnum):
            self.bottoms_subcategory = BottomsSubcategoryEnum(self.bottoms_subcategory)

        if self.material is not None and not isinstance(self.material, ClothingMaterialEnum):
            self.material = ClothingMaterialEnum(self.material)

        if self.is_winter_suitable is not None and not isinstance(self.is_winter_suitable, Bool):
            self.is_winter_suitable = Bool(self.is_winter_suitable)

        if self.demographic is not None and not isinstance(self.demographic, DemographicEnum):
            self.demographic = DemographicEnum(self.demographic)

        if self.is_maternity is not None and not isinstance(self.is_maternity, Bool):
            self.is_maternity = Bool(self.is_maternity)

        if not isinstance(self.size, list):
            self.size = [self.size] if self.size is not None else []
        self.size = [v if isinstance(v, ClothingSizeEnum) else ClothingSizeEnum(v) for v in self.size]

        if not isinstance(self.season, list):
            self.season = [self.season] if self.season is not None else []
        self.season = [v if isinstance(v, SeasonEnum) else SeasonEnum(v) for v in self.season]

        if self.intact_labels is not None and not isinstance(self.intact_labels, Bool):
            self.intact_labels = Bool(self.intact_labels)

        super().__post_init__(**kwargs)


class ClothingPhysicalItemMixin(ClothingCategory):
    """
    Shared physical-item dispatch target for the Clothing category, used identically by DonationItem,
    StorageCollection, and SortedCollection. Pure composition — no slots or rules of its own.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["ClothingPhysicalItemMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:ClothingPhysicalItemMixin"
    class_name: ClassVar[str] = "ClothingPhysicalItemMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.ClothingPhysicalItemMixin


@dataclass(repr=False)
class FootwearCategory(CategoryMixin):
    """
    Mixin for footwear slots and UC rules. Applied to FootwearItem via mixins: [FootwearCategory].
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["FootwearCategory"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:FootwearCategory"
    class_name: ClassVar[str] = "FootwearCategory"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.FootwearCategory

    subcategory: Union[str, "FootwearSubcategoryEnum"] = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None
    material: Optional[Union[str, "FootwearMaterialEnum"]] = None
    is_pair_complete: Optional[Union[bool, Bool]] = None
    is_winter_suitable: Optional[Union[bool, Bool]] = None
    demographic: Optional[Union[str, "DemographicEnum"]] = None
    shoe_size: Optional[str] = None
    shoe_size_system: Optional[Union[str, "ShoeSizeSystemEnum"]] = None
    season: Optional[Union[Union[str, "SeasonEnum"], list[Union[str, "SeasonEnum"]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, FootwearSubcategoryEnum):
            self.subcategory = FootwearSubcategoryEnum(self.subcategory)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        if self.material is not None and not isinstance(self.material, FootwearMaterialEnum):
            self.material = FootwearMaterialEnum(self.material)

        if self.is_pair_complete is not None and not isinstance(self.is_pair_complete, Bool):
            self.is_pair_complete = Bool(self.is_pair_complete)

        if self.is_winter_suitable is not None and not isinstance(self.is_winter_suitable, Bool):
            self.is_winter_suitable = Bool(self.is_winter_suitable)

        if self.demographic is not None and not isinstance(self.demographic, DemographicEnum):
            self.demographic = DemographicEnum(self.demographic)

        if self.shoe_size is not None and not isinstance(self.shoe_size, str):
            self.shoe_size = str(self.shoe_size)

        if self.shoe_size_system is not None and not isinstance(self.shoe_size_system, ShoeSizeSystemEnum):
            self.shoe_size_system = ShoeSizeSystemEnum(self.shoe_size_system)

        if not isinstance(self.season, list):
            self.season = [self.season] if self.season is not None else []
        self.season = [v if isinstance(v, SeasonEnum) else SeasonEnum(v) for v in self.season]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class FootwearPhysicalItemMixin(FootwearCategory):
    """
    Shared physical-item dispatch target for the Footwear category, used identically by DonationItem,
    StorageCollection, and SortedCollection. Pure composition — no slots or rules of its own.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["FootwearPhysicalItemMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:FootwearPhysicalItemMixin"
    class_name: ClassVar[str] = "FootwearPhysicalItemMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.FootwearPhysicalItemMixin

    subcategory: Union[str, "FootwearSubcategoryEnum"] = None

@dataclass(repr=False)
class FurnitureCategory(CategoryMixin):
    """
    Mixin for furniture slots, value maps, and UC rules. Applied to FurnitureItem via mixins: [FurnitureCategory].
    assessment_result and its UC rules live on FurnitureAssessmentMixin (below) so DemandSignal can dispatch to this
    bare mixin without assessment content that only applies to a physical item in hand.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["FurnitureCategory"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:FurnitureCategory"
    class_name: ClassVar[str] = "FurnitureCategory"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.FurnitureCategory

    subcategory: Union[str, "FurnitureSubcategoryEnum"] = None
    material: Optional[Union[str, "FurnitureMaterialEnum"]] = None
    dimensions: Optional[str] = None
    style: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, FurnitureSubcategoryEnum):
            self.subcategory = FurnitureSubcategoryEnum(self.subcategory)

        if self.material is not None and not isinstance(self.material, FurnitureMaterialEnum):
            self.material = FurnitureMaterialEnum(self.material)

        if self.dimensions is not None and not isinstance(self.dimensions, str):
            self.dimensions = str(self.dimensions)

        if self.style is not None and not isinstance(self.style, str):
            self.style = str(self.style)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class FurnitureAssessmentMixin(FurnitureCategory):
    """
    Shared physical-item dispatch target for Furniture — used identically by DonationItem, StorageCollection, and
    SortedCollection. Adds assessment_result and its UC rules on top of FurnitureCategory. Never used by DemandSignal.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["FurnitureAssessmentMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:FurnitureAssessmentMixin"
    class_name: ClassVar[str] = "FurnitureAssessmentMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.FurnitureAssessmentMixin

    subcategory: Union[str, "FurnitureSubcategoryEnum"] = None
    assessment_result: Optional[Union[str, "FurnitureAssessmentEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.assessment_result is not None and not isinstance(self.assessment_result, FurnitureAssessmentEnum):
            self.assessment_result = FurnitureAssessmentEnum(self.assessment_result)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class BeddingTextilesCategory(CategoryMixin):
    """
    Mixin for bedding and textiles slots and UC rules. Applied to BeddingTextilesItem via mixins:
    [BeddingTextilesCategory]. assessment_result and its hygiene UC rules live on BeddingAssessmentMixin (below) so
    DemandSignal can dispatch to this bare mixin without assessment content that only applies to a physical item in
    hand.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["BeddingTextilesCategory"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:BeddingTextilesCategory"
    class_name: ClassVar[str] = "BeddingTextilesCategory"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.BeddingTextilesCategory

    subcategory: Union[str, "BeddingTextilesSubcategoryEnum"] = None
    material: Optional[Union[str, "BeddingMaterialEnum"]] = None
    is_set_complete: Optional[Union[bool, Bool]] = None
    is_winter_suitable: Optional[Union[bool, Bool]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, BeddingTextilesSubcategoryEnum):
            self.subcategory = BeddingTextilesSubcategoryEnum(self.subcategory)

        if self.material is not None and not isinstance(self.material, BeddingMaterialEnum):
            self.material = BeddingMaterialEnum(self.material)

        if self.is_set_complete is not None and not isinstance(self.is_set_complete, Bool):
            self.is_set_complete = Bool(self.is_set_complete)

        if self.is_winter_suitable is not None and not isinstance(self.is_winter_suitable, Bool):
            self.is_winter_suitable = Bool(self.is_winter_suitable)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class BeddingAssessmentMixin(BeddingTextilesCategory):
    """
    Shared physical-item dispatch target for Bedding and Textiles — used identically by DonationItem,
    StorageCollection, and SortedCollection. Adds assessment_result and its UC rules on top of
    BeddingTextilesCategory. Never used by DemandSignal.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["BeddingAssessmentMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:BeddingAssessmentMixin"
    class_name: ClassVar[str] = "BeddingAssessmentMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.BeddingAssessmentMixin

    subcategory: Union[str, "BeddingTextilesSubcategoryEnum"] = None
    assessment_result: Optional[Union[str, "BeddingAssessmentEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.assessment_result is not None and not isinstance(self.assessment_result, BeddingAssessmentEnum):
            self.assessment_result = BeddingAssessmentEnum(self.assessment_result)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class HouseholdCategory(CategoryMixin):
    """
    Mixin for household and kitchen goods slots. Applied to HouseholdItem via mixins: [HouseholdCategory].
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["HouseholdCategory"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:HouseholdCategory"
    class_name: ClassVar[str] = "HouseholdCategory"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.HouseholdCategory

    subcategory: Union[str, "HouseholdSubcategoryEnum"] = None
    material: Optional[Union[str, "HouseholdMaterialEnum"]] = None
    is_set_complete: Optional[Union[bool, Bool]] = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, HouseholdSubcategoryEnum):
            self.subcategory = HouseholdSubcategoryEnum(self.subcategory)

        if self.material is not None and not isinstance(self.material, HouseholdMaterialEnum):
            self.material = HouseholdMaterialEnum(self.material)

        if self.is_set_complete is not None and not isinstance(self.is_set_complete, Bool):
            self.is_set_complete = Bool(self.is_set_complete)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class HouseholdPhysicalItemMixin(HouseholdCategory):
    """
    Shared physical-item dispatch target for the Household category, used identically by DonationItem,
    StorageCollection, and SortedCollection. Pure composition — no slots or rules of its own.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["HouseholdPhysicalItemMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:HouseholdPhysicalItemMixin"
    class_name: ClassVar[str] = "HouseholdPhysicalItemMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.HouseholdPhysicalItemMixin

    subcategory: Union[str, "HouseholdSubcategoryEnum"] = None

@dataclass(repr=False)
class ElectronicsCategory(CategoryMixin):
    """
    Mixin for electronics slots and UC rules. Applied to ElectronicsItem via mixins: [ElectronicsCategory].
    assessment_result and its UC rule live on ElectronicsAssessmentMixin (below) so DemandSignal can dispatch to this
    bare mixin without assessment content that only applies to a physical item in hand.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["ElectronicsCategory"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:ElectronicsCategory"
    class_name: ClassVar[str] = "ElectronicsCategory"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.ElectronicsCategory

    subcategory: Union[str, "ElectronicsSubcategoryEnum"] = None
    includes_charger: Optional[Union[bool, Bool]] = None
    includes_original_packaging: Optional[Union[bool, Bool]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, ElectronicsSubcategoryEnum):
            self.subcategory = ElectronicsSubcategoryEnum(self.subcategory)

        if self.includes_charger is not None and not isinstance(self.includes_charger, Bool):
            self.includes_charger = Bool(self.includes_charger)

        if self.includes_original_packaging is not None and not isinstance(self.includes_original_packaging, Bool):
            self.includes_original_packaging = Bool(self.includes_original_packaging)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ElectronicsAssessmentMixin(ElectronicsCategory):
    """
    Shared physical-item dispatch target for Electronics — used identically by DonationItem, StorageCollection, and
    SortedCollection. Adds assessment_result and its UC rule on top of ElectronicsCategory. Never used by
    DemandSignal.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["ElectronicsAssessmentMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:ElectronicsAssessmentMixin"
    class_name: ClassVar[str] = "ElectronicsAssessmentMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.ElectronicsAssessmentMixin

    subcategory: Union[str, "ElectronicsSubcategoryEnum"] = None
    assessment_result: Union[str, "ElectronicsAssessmentEnum"] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.assessment_result):
            self.MissingRequiredField("assessment_result")
        if not isinstance(self.assessment_result, ElectronicsAssessmentEnum):
            self.assessment_result = ElectronicsAssessmentEnum(self.assessment_result)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ToysCategory(CategoryMixin):
    """
    Mixin for toys and games slots and UC rules. Applied to ToysItem via mixins: [ToysCategory].
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["ToysCategory"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:ToysCategory"
    class_name: ClassVar[str] = "ToysCategory"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.ToysCategory

    subcategory: Union[str, "ToysSubcategoryEnum"] = None
    material: Optional[Union[str, "ToysMaterialEnum"]] = None
    age_range: Optional[Union[str, "ToyAgeRangeEnum"]] = None
    is_set_complete: Optional[Union[bool, Bool]] = None
    has_small_parts: Optional[Union[bool, Bool]] = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, ToysSubcategoryEnum):
            self.subcategory = ToysSubcategoryEnum(self.subcategory)

        if self.material is not None and not isinstance(self.material, ToysMaterialEnum):
            self.material = ToysMaterialEnum(self.material)

        if self.age_range is not None and not isinstance(self.age_range, ToyAgeRangeEnum):
            self.age_range = ToyAgeRangeEnum(self.age_range)

        if self.is_set_complete is not None and not isinstance(self.is_set_complete, Bool):
            self.is_set_complete = Bool(self.is_set_complete)

        if self.has_small_parts is not None and not isinstance(self.has_small_parts, Bool):
            self.has_small_parts = Bool(self.has_small_parts)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ToysPhysicalItemMixin(ToysCategory):
    """
    Shared physical-item dispatch target for the Toys category, used identically by DonationItem, StorageCollection,
    and SortedCollection. Pure composition — no slots or rules of its own.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["ToysPhysicalItemMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:ToysPhysicalItemMixin"
    class_name: ClassVar[str] = "ToysPhysicalItemMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.ToysPhysicalItemMixin

    subcategory: Union[str, "ToysSubcategoryEnum"] = None

@dataclass(repr=False)
class SportsCategory(CategoryMixin):
    """
    Mixin for sports equipment slots and UC rules. Applied to SportsItem via mixins: [SportsCategory]. condition_grade
    for general (non-protective-gear) subcategories lives here; assessment_result for protective_gear and its UC rules
    live on SportsProtectiveAssessmentMixin (below), so DemandSignal can dispatch to this bare mixin without that
    assessment content.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["SportsCategory"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:SportsCategory"
    class_name: ClassVar[str] = "SportsCategory"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.SportsCategory

    subcategory: Union[str, "SportsSubcategoryEnum"] = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None
    sport_type: Optional[str] = None
    demographic: Optional[Union[str, "DemographicEnum"]] = None
    is_set_complete: Optional[Union[bool, Bool]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, SportsSubcategoryEnum):
            self.subcategory = SportsSubcategoryEnum(self.subcategory)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        if self.sport_type is not None and not isinstance(self.sport_type, str):
            self.sport_type = str(self.sport_type)

        if self.demographic is not None and not isinstance(self.demographic, DemographicEnum):
            self.demographic = DemographicEnum(self.demographic)

        if self.is_set_complete is not None and not isinstance(self.is_set_complete, Bool):
            self.is_set_complete = Bool(self.is_set_complete)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class SportsProtectiveAssessmentMixin(SportsCategory):
    """
    Shared physical-item dispatch target for Sports — used identically by DonationItem, StorageCollection, and
    SortedCollection. Adds assessment_result (protective_gear only) and its UC rules on top of SportsCategory. Never
    used by DemandSignal.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["SportsProtectiveAssessmentMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:SportsProtectiveAssessmentMixin"
    class_name: ClassVar[str] = "SportsProtectiveAssessmentMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.SportsProtectiveAssessmentMixin

    subcategory: Union[str, "SportsSubcategoryEnum"] = None
    assessment_result: Optional[Union[str, "SportsProtectiveAssessmentEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.assessment_result is not None and not isinstance(self.assessment_result, SportsProtectiveAssessmentEnum):
            self.assessment_result = SportsProtectiveAssessmentEnum(self.assessment_result)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class BooksCategory(CategoryMixin):
    """
    Mixin for books and educational materials slots. Applied to BooksItem via mixins: [BooksCategory]. No UC block
    rules beyond the cross-cutting condition rule.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["BooksCategory"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:BooksCategory"
    class_name: ClassVar[str] = "BooksCategory"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.BooksCategory

    subcategory: Union[str, "BooksSubcategoryEnum"] = None
    language: Optional[str] = None
    age_range: Optional[Union[str, "BookAgeRangeEnum"]] = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, BooksSubcategoryEnum):
            self.subcategory = BooksSubcategoryEnum(self.subcategory)

        if self.language is not None and not isinstance(self.language, str):
            self.language = str(self.language)

        if self.age_range is not None and not isinstance(self.age_range, BookAgeRangeEnum):
            self.age_range = BookAgeRangeEnum(self.age_range)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class BooksPhysicalItemMixin(BooksCategory):
    """
    Shared physical-item dispatch target for the Books category, used identically by DonationItem, StorageCollection,
    and SortedCollection. Pure composition — no slots or rules of its own.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["BooksPhysicalItemMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:BooksPhysicalItemMixin"
    class_name: ClassVar[str] = "BooksPhysicalItemMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.BooksPhysicalItemMixin

    subcategory: Union[str, "BooksSubcategoryEnum"] = None

@dataclass(repr=False)
class StationeryCategory(CategoryMixin):
    """
    Mixin for stationery and office supply slots. Applied to StationeryItem via mixins: [StationeryCategory].
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["StationeryCategory"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:StationeryCategory"
    class_name: ClassVar[str] = "StationeryCategory"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.StationeryCategory

    subcategory: Union[str, "StationerySubcategoryEnum"] = None
    is_set_complete: Optional[Union[bool, Bool]] = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, StationerySubcategoryEnum):
            self.subcategory = StationerySubcategoryEnum(self.subcategory)

        if self.is_set_complete is not None and not isinstance(self.is_set_complete, Bool):
            self.is_set_complete = Bool(self.is_set_complete)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class StationeryPhysicalItemMixin(StationeryCategory):
    """
    Shared physical-item dispatch target for the Stationery category, used identically by DonationItem,
    StorageCollection, and SortedCollection. Pure composition — no slots or rules of its own.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["StationeryPhysicalItemMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:StationeryPhysicalItemMixin"
    class_name: ClassVar[str] = "StationeryPhysicalItemMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.StationeryPhysicalItemMixin

    subcategory: Union[str, "StationerySubcategoryEnum"] = None

@dataclass(repr=False)
class PersonalCareCategory(CategoryMixin):
    """
    Mixin for personal care, hygiene, and health product slots and UC rules. Applied to PersonalCareItem via mixins:
    [PersonalCareCategory].
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["PersonalCareCategory"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:PersonalCareCategory"
    class_name: ClassVar[str] = "PersonalCareCategory"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.PersonalCareCategory

    subcategory: Union[str, "PersonalCareSubcategoryEnum"] = None
    is_sealed: Optional[Union[bool, Bool]] = None
    expiry_date: Optional[Union[str, XSDDate]] = None
    net_content_value: Optional[Decimal] = None
    net_content_unit: Optional[Union[str, "NetContentUnitEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, PersonalCareSubcategoryEnum):
            self.subcategory = PersonalCareSubcategoryEnum(self.subcategory)

        if self.is_sealed is not None and not isinstance(self.is_sealed, Bool):
            self.is_sealed = Bool(self.is_sealed)

        if self.expiry_date is not None and not isinstance(self.expiry_date, XSDDate):
            self.expiry_date = XSDDate(self.expiry_date)

        if self.net_content_value is not None and not isinstance(self.net_content_value, Decimal):
            self.net_content_value = Decimal(self.net_content_value)

        if self.net_content_unit is not None and not isinstance(self.net_content_unit, NetContentUnitEnum):
            self.net_content_unit = NetContentUnitEnum(self.net_content_unit)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class PersonalCarePhysicalItemMixin(PersonalCareCategory):
    """
    Shared physical-item dispatch target for the Personal Care category, used identically by DonationItem,
    StorageCollection, and SortedCollection. Pure composition — no slots or rules of its own.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["PersonalCarePhysicalItemMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:PersonalCarePhysicalItemMixin"
    class_name: ClassVar[str] = "PersonalCarePhysicalItemMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.PersonalCarePhysicalItemMixin

    subcategory: Union[str, "PersonalCareSubcategoryEnum"] = None

@dataclass(repr=False)
class MobilityAidsCategory(CategoryMixin):
    """
    Mixin for mobility aids and assistive device slots and UC rules. Applied to MobilityAidsItem via mixins:
    [MobilityAidsCategory]. assessment_result and its UC rules live on MobilityAssessmentMixin (below) so DemandSignal
    can dispatch to this bare mixin without assessment content that only applies to a physical item in hand.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["MobilityAidsCategory"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:MobilityAidsCategory"
    class_name: ClassVar[str] = "MobilityAidsCategory"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.MobilityAidsCategory

    subcategory: Union[str, "MobilityAidsSubcategoryEnum"] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, MobilityAidsSubcategoryEnum):
            self.subcategory = MobilityAidsSubcategoryEnum(self.subcategory)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class MobilityAssessmentMixin(MobilityAidsCategory):
    """
    Shared physical-item dispatch target for Mobility Aids — used identically by DonationItem, StorageCollection, and
    SortedCollection. Adds assessment_result and its UC rules on top of MobilityAidsCategory. Never used by
    DemandSignal.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["MobilityAssessmentMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:MobilityAssessmentMixin"
    class_name: ClassVar[str] = "MobilityAssessmentMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.MobilityAssessmentMixin

    subcategory: Union[str, "MobilityAidsSubcategoryEnum"] = None
    assessment_result: Optional[Union[str, "MobilityAssessmentEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.assessment_result is not None and not isinstance(self.assessment_result, MobilityAssessmentEnum):
            self.assessment_result = MobilityAssessmentEnum(self.assessment_result)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class BabyInfantCategory(CategoryMixin):
    """
    Mixin for baby and infant supply slots and UC rules — Tracks 2/3, see schema description above. Applied to
    BabyInfantItem via mixins: [BabyInfantCategory]. Track 1 assessment_result and its UC rules live on
    BabyEquipmentAssessmentMixin (below), so DemandSignal can dispatch to this bare mixin without that assessment
    content.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["BabyInfantCategory"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:BabyInfantCategory"
    class_name: ClassVar[str] = "BabyInfantCategory"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.BabyInfantCategory

    subcategory: Union[str, "BabyInfantSubcategoryEnum"] = None
    manufacture_year: Optional[int] = None
    includes_original_accessories: Optional[Union[bool, Bool]] = None
    is_winter_suitable: Optional[Union[bool, Bool]] = None
    is_sealed: Optional[Union[bool, Bool]] = None
    expiry_date: Optional[Union[str, XSDDate]] = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None
    nappy_size: Optional[Union[str, "NappySizeEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, BabyInfantSubcategoryEnum):
            self.subcategory = BabyInfantSubcategoryEnum(self.subcategory)

        if self.manufacture_year is not None and not isinstance(self.manufacture_year, int):
            self.manufacture_year = int(self.manufacture_year)

        if self.includes_original_accessories is not None and not isinstance(self.includes_original_accessories, Bool):
            self.includes_original_accessories = Bool(self.includes_original_accessories)

        if self.is_winter_suitable is not None and not isinstance(self.is_winter_suitable, Bool):
            self.is_winter_suitable = Bool(self.is_winter_suitable)

        if self.is_sealed is not None and not isinstance(self.is_sealed, Bool):
            self.is_sealed = Bool(self.is_sealed)

        if self.expiry_date is not None and not isinstance(self.expiry_date, XSDDate):
            self.expiry_date = XSDDate(self.expiry_date)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        if self.nappy_size is not None and not isinstance(self.nappy_size, NappySizeEnum):
            self.nappy_size = NappySizeEnum(self.nappy_size)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class BabyEquipmentAssessmentMixin(BabyInfantCategory):
    """
    Shared physical-item dispatch target for Baby & Infant Supplies — used identically by DonationItem,
    StorageCollection, and SortedCollection. Adds Track 1 assessment_result and its UC rules on top of
    BabyInfantCategory. Never used by DemandSignal.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["BabyEquipmentAssessmentMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:BabyEquipmentAssessmentMixin"
    class_name: ClassVar[str] = "BabyEquipmentAssessmentMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.BabyEquipmentAssessmentMixin

    subcategory: Union[str, "BabyInfantSubcategoryEnum"] = None
    assessment_result: Optional[Union[str, "BabyEquipmentAssessmentEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.assessment_result is not None and not isinstance(self.assessment_result, BabyEquipmentAssessmentEnum):
            self.assessment_result = BabyEquipmentAssessmentEnum(self.assessment_result)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class FoodCategory(YAMLRoot):
    """
    Mixin for food-specific slots, value maps, and UC rules. Applied to FoodItem via mixins: [FoodCategory].
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["FoodCategory"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:FoodCategory"
    class_name: ClassVar[str] = "FoodCategory"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.FoodCategory

    subcategory: Union[str, "FoodTypeEnum"] = None
    packaging_intact: Union[bool, Bool] = None
    storage_requirement: Union[str, "StorageRequirementEnum"] = None
    expiry_date: Optional[Union[str, XSDDate]] = None
    net_content_value: Optional[Decimal] = None
    net_content_unit: Optional[Union[str, "NetContentUnitEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.subcategory):
            self.MissingRequiredField("subcategory")
        if not isinstance(self.subcategory, FoodTypeEnum):
            self.subcategory = FoodTypeEnum(self.subcategory)

        if self._is_empty(self.packaging_intact):
            self.MissingRequiredField("packaging_intact")
        if not isinstance(self.packaging_intact, Bool):
            self.packaging_intact = Bool(self.packaging_intact)

        if self._is_empty(self.storage_requirement):
            self.MissingRequiredField("storage_requirement")
        if not isinstance(self.storage_requirement, StorageRequirementEnum):
            self.storage_requirement = StorageRequirementEnum(self.storage_requirement)

        if self.expiry_date is not None and not isinstance(self.expiry_date, XSDDate):
            self.expiry_date = XSDDate(self.expiry_date)

        if self.net_content_value is not None and not isinstance(self.net_content_value, Decimal):
            self.net_content_value = Decimal(self.net_content_value)

        if self.net_content_unit is not None and not isinstance(self.net_content_unit, NetContentUnitEnum):
            self.net_content_unit = NetContentUnitEnum(self.net_content_unit)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class FoodPhysicalItemMixin(FoodCategory):
    """
    Shared physical-item dispatch target for the Food category, used identically by DonationItem, StorageCollection,
    and SortedCollection. Pure composition — no slots or rules of its own.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["FoodPhysicalItemMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:FoodPhysicalItemMixin"
    class_name: ClassVar[str] = "FoodPhysicalItemMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.FoodPhysicalItemMixin

    subcategory: Union[str, "FoodTypeEnum"] = None
    packaging_intact: Union[bool, Bool] = None
    storage_requirement: Union[str, "StorageRequirementEnum"] = None

@dataclass(repr=False)
class OtherCategory(YAMLRoot):
    """
    Mixin for the catch-all OtherItem category. Minimal slots only (item_description + condition_grade) — no
    category-specific value maps or UC rules. Deliberately no completeness tier annotations.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["Product"]
    class_class_curie: ClassVar[str] = "schema:Product"
    class_name: ClassVar[str] = "OtherCategory"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.OtherCategory

    item_description: str = None
    condition_grade: Optional[Union[str, "UsedConditionGradeEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.item_description):
            self.MissingRequiredField("item_description")
        if not isinstance(self.item_description, str):
            self.item_description = str(self.item_description)

        if self.condition_grade is not None and not isinstance(self.condition_grade, UsedConditionGradeEnum):
            self.condition_grade = UsedConditionGradeEnum(self.condition_grade)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class OtherPhysicalItemMixin(OtherCategory):
    """
    Shared physical-item dispatch target for the Other category, used identically by DonationItem, StorageCollection,
    and SortedCollection. Pure composition — no slots or rules of its own.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["OtherPhysicalItemMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:OtherPhysicalItemMixin"
    class_name: ClassVar[str] = "OtherPhysicalItemMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.OtherPhysicalItemMixin

    item_description: str = None

@dataclass(repr=False)
class ProvenanceRecord(YAMLRoot):
    """
    A single provenance record capturing one completed process step — who did it, when, on which device, at what
    configured cost, and what observations were submitted. Corresponds to prov:Activity in W3C PROV-O.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = PROV["Activity"]
    class_class_curie: ClassVar[str] = "prov:Activity"
    class_name: ClassVar[str] = "ProvenanceRecord"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.ProvenanceRecord

    id: Union[str, ProvenanceRecordId] = None
    step_type_ref: str = None
    actor_ref: str = None
    actor_role_ref: Union[str, "ActorRoleEnum"] = None
    org: Union[str, SocialOrganisationId] = None
    device: Union[str, "DeviceTypeEnum"] = None
    started_at: Union[str, XSDDateTime] = None
    completed_at: Union[str, XSDDateTime] = None
    duration_seconds: int = None
    cost_configured: float = None
    observations_ref: str = None
    override_flag: Union[bool, Bool] = None
    override_reason: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ProvenanceRecordId):
            self.id = ProvenanceRecordId(self.id)

        if self._is_empty(self.step_type_ref):
            self.MissingRequiredField("step_type_ref")
        if not isinstance(self.step_type_ref, str):
            self.step_type_ref = str(self.step_type_ref)

        if self._is_empty(self.actor_ref):
            self.MissingRequiredField("actor_ref")
        if not isinstance(self.actor_ref, str):
            self.actor_ref = str(self.actor_ref)

        if self._is_empty(self.actor_role_ref):
            self.MissingRequiredField("actor_role_ref")
        if not isinstance(self.actor_role_ref, ActorRoleEnum):
            self.actor_role_ref = ActorRoleEnum(self.actor_role_ref)

        if self._is_empty(self.org):
            self.MissingRequiredField("org")
        if not isinstance(self.org, SocialOrganisationId):
            self.org = SocialOrganisationId(self.org)

        if self._is_empty(self.device):
            self.MissingRequiredField("device")
        if not isinstance(self.device, DeviceTypeEnum):
            self.device = DeviceTypeEnum(self.device)

        if self._is_empty(self.started_at):
            self.MissingRequiredField("started_at")
        if not isinstance(self.started_at, XSDDateTime):
            self.started_at = XSDDateTime(self.started_at)

        if self._is_empty(self.completed_at):
            self.MissingRequiredField("completed_at")
        if not isinstance(self.completed_at, XSDDateTime):
            self.completed_at = XSDDateTime(self.completed_at)

        if self._is_empty(self.duration_seconds):
            self.MissingRequiredField("duration_seconds")
        if not isinstance(self.duration_seconds, int):
            self.duration_seconds = int(self.duration_seconds)

        if self._is_empty(self.cost_configured):
            self.MissingRequiredField("cost_configured")
        if not isinstance(self.cost_configured, float):
            self.cost_configured = float(self.cost_configured)

        if self._is_empty(self.observations_ref):
            self.MissingRequiredField("observations_ref")
        if not isinstance(self.observations_ref, str):
            self.observations_ref = str(self.observations_ref)

        if self._is_empty(self.override_flag):
            self.MissingRequiredField("override_flag")
        if not isinstance(self.override_flag, Bool):
            self.override_flag = Bool(self.override_flag)

        if self.override_reason is not None and not isinstance(self.override_reason, str):
            self.override_reason = str(self.override_reason)

        super().__post_init__(**kwargs)


class ClothingContextRulesMixin(YAMLRoot):
    """
    lc-* rules for the Clothing category only. Mixed into ClothingPhysicalItemMixin (categories/clothing.yaml) and
    DonationItem's real ClothingItem subclass (entities/donation_item.yaml).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["ClothingContextRulesMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:ClothingContextRulesMixin"
    class_name: ClassVar[str] = "ClothingContextRulesMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.ClothingContextRulesMixin


class AccessoriesContextRulesMixin(YAMLRoot):
    """
    lc-* rules for the Accessories category only. Mixed into AccessoriesPhysicalItemMixin
    (categories/accessories.yaml) and DonationItem's real AccessoriesItem subclass.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["AccessoriesContextRulesMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:AccessoriesContextRulesMixin"
    class_name: ClassVar[str] = "AccessoriesContextRulesMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.AccessoriesContextRulesMixin


class FootwearContextRulesMixin(YAMLRoot):
    """
    lc-* rules for the Footwear category only. Mixed into FootwearPhysicalItemMixin (categories/footwear.yaml) and
    DonationItem's real FootwearItem subclass.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["FootwearContextRulesMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:FootwearContextRulesMixin"
    class_name: ClassVar[str] = "FootwearContextRulesMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.FootwearContextRulesMixin


class FurnitureContextRulesMixin(YAMLRoot):
    """
    lc-* rules for the Furniture category only. Mixed into FurnitureAssessmentMixin (categories/furniture.yaml) and
    DonationItem's real FurnitureItem subclass.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["FurnitureContextRulesMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:FurnitureContextRulesMixin"
    class_name: ClassVar[str] = "FurnitureContextRulesMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.FurnitureContextRulesMixin


class BeddingContextRulesMixin(YAMLRoot):
    """
    lc-* rules for the Bedding and Textiles category only. Mixed into BeddingAssessmentMixin
    (categories/bedding_textiles.yaml) and DonationItem's real BeddingTextilesItem subclass.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["BeddingContextRulesMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:BeddingContextRulesMixin"
    class_name: ClassVar[str] = "BeddingContextRulesMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.BeddingContextRulesMixin


class HouseholdContextRulesMixin(YAMLRoot):
    """
    lc-* rules for the Household category only. Mixed into HouseholdPhysicalItemMixin (categories/household.yaml) and
    DonationItem's real HouseholdItem subclass.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["HouseholdContextRulesMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:HouseholdContextRulesMixin"
    class_name: ClassVar[str] = "HouseholdContextRulesMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.HouseholdContextRulesMixin


class ElectronicsContextRulesMixin(YAMLRoot):
    """
    lc-* rules for the Electronics category only. Mixed into ElectronicsAssessmentMixin (categories/electronics.yaml)
    and DonationItem's real ElectronicsItem subclass.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["ElectronicsContextRulesMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:ElectronicsContextRulesMixin"
    class_name: ClassVar[str] = "ElectronicsContextRulesMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.ElectronicsContextRulesMixin


class ToysContextRulesMixin(YAMLRoot):
    """
    lc-* rules for the Toys category only. Mixed into ToysPhysicalItemMixin (categories/toys.yaml) and DonationItem's
    real ToysItem subclass.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["ToysContextRulesMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:ToysContextRulesMixin"
    class_name: ClassVar[str] = "ToysContextRulesMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.ToysContextRulesMixin


class SportsContextRulesMixin(YAMLRoot):
    """
    lc-* rules for the Sports category only. Mixed into SportsProtectiveAssessmentMixin (categories/sports.yaml) and
    DonationItem's real SportsItem subclass.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["SportsContextRulesMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:SportsContextRulesMixin"
    class_name: ClassVar[str] = "SportsContextRulesMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.SportsContextRulesMixin


class BooksContextRulesMixin(YAMLRoot):
    """
    lc-* rules for the Books category only. Mixed into BooksPhysicalItemMixin (categories/books.yaml) and
    DonationItem's real BooksItem subclass.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["BooksContextRulesMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:BooksContextRulesMixin"
    class_name: ClassVar[str] = "BooksContextRulesMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.BooksContextRulesMixin


class StationeryContextRulesMixin(YAMLRoot):
    """
    lc-* rules for the Stationery category only. Mixed into StationeryPhysicalItemMixin (categories/stationery.yaml)
    and DonationItem's real StationeryItem subclass.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["StationeryContextRulesMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:StationeryContextRulesMixin"
    class_name: ClassVar[str] = "StationeryContextRulesMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.StationeryContextRulesMixin


class PersonalCareContextRulesMixin(YAMLRoot):
    """
    lc-* rules for the Personal Care category only. Mixed into PersonalCarePhysicalItemMixin
    (categories/personal_care.yaml) and DonationItem's real PersonalCareItem subclass.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["PersonalCareContextRulesMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:PersonalCareContextRulesMixin"
    class_name: ClassVar[str] = "PersonalCareContextRulesMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.PersonalCareContextRulesMixin


class MobilityAidsContextRulesMixin(YAMLRoot):
    """
    lc-* rules for the Mobility Aids category only. Mixed into MobilityAssessmentMixin (categories/mobility_aids.yaml)
    and DonationItem's real MobilityAidsItem subclass.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["MobilityAidsContextRulesMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:MobilityAidsContextRulesMixin"
    class_name: ClassVar[str] = "MobilityAidsContextRulesMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.MobilityAidsContextRulesMixin


class BabyInfantContextRulesMixin(YAMLRoot):
    """
    lc-* rules for the Baby & Infant Supplies category only. Mixed into BabyEquipmentAssessmentMixin
    (categories/baby_infant.yaml) and DonationItem's real BabyInfantItem subclass.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["BabyInfantContextRulesMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:BabyInfantContextRulesMixin"
    class_name: ClassVar[str] = "BabyInfantContextRulesMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.BabyInfantContextRulesMixin


class FoodContextRulesMixin(YAMLRoot):
    """
    lc-* rules for the Food category only. Mixed into FoodPhysicalItemMixin (categories/food.yaml) and DonationItem's
    real FoodItem subclass.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["FoodContextRulesMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:FoodContextRulesMixin"
    class_name: ClassVar[str] = "FoodContextRulesMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.FoodContextRulesMixin


class OtherContextRulesMixin(YAMLRoot):
    """
    lc-* rules for the Other (catch-all) category only. Mixed into OtherPhysicalItemMixin (categories/other.yaml) and
    DonationItem's real OtherItem subclass.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO["OtherContextRulesMixin"]
    class_class_curie: ClassVar[str] = "inkind_knowledge_repo:OtherContextRulesMixin"
    class_name: ClassVar[str] = "OtherContextRulesMixin"
    class_model_uri: ClassVar[URIRef] = INKIND_KNOWLEDGE_REPO.OtherContextRulesMixin


# Enumerations
class ItemUsageEnum(EnumDefinitionImpl):
    """
    Provenance — was the item ever used before donation? Orthogonal to assessment. new does NOT imply no defects.
    Grounds the top-level split in schema:OfferItemCondition.
    """
    new = PermissibleValue(
        text="new",
        description="""Never used before donation. Does NOT imply defect-free — manufacturing defects or transit damage are possible. Assessment must still be performed.""",
        meaning=SCHEMA["NewCondition"])
    used = PermissibleValue(
        text="used",
        description="Previously used before donation. Assessment required.",
        meaning=SCHEMA["UsedCondition"])

    _defn = EnumDefinition(
        name="ItemUsageEnum",
        description="""Provenance — was the item ever used before donation? Orthogonal to assessment. new does NOT imply no defects. Grounds the top-level split in schema:OfferItemCondition.""",
    )

class UsedConditionGradeEnum(EnumDefinitionImpl):
    """
    Observed wear/quality grade at sorting time. For wear-graded categories. Grounds schema:OfferItemCondition
    sub-values and schema:itemCondition. Applied regardless of usage — a new item with a defect is graded fair or
    poor, not assumed like_new. Sorters record what they observe.
    """
    like_new = PermissibleValue(
        text="like_new",
        description="""No visible wear or defects. As-new appearance and function. Appropriate for new items with no observed defects, or used items showing no signs of wear.""",
        meaning=SCHEMA["LikeNewCondition"])
    good = PermissibleValue(
        text="good",
        description="""Minor wear; fully functional; no significant defects. Most common grade for used items in acceptable condition.""")
    fair = PermissibleValue(
        text="fair",
        description="""Visible wear, minor defects, or manufacturing issues. Still suitable for redistribution with appropriate beneficiary matching.""")
    poor = PermissibleValue(
        text="poor",
        description="""Significant wear or defects. Redistribution subject to category-specific UC rules — some categories block, others warn and require explicit sorter confirmation.""",
        meaning=SCHEMA["DamagedCondition"])

    _defn = EnumDefinition(
        name="UsedConditionGradeEnum",
        description="""Observed wear/quality grade at sorting time. For wear-graded categories. Grounds schema:OfferItemCondition sub-values and schema:itemCondition. Applied regardless of usage — a new item with a defect is graded fair or poor, not assumed like_new. Sorters record what they observe.""",
    )

class NetContentUnitEnum(EnumDefinitionImpl):
    """
    Unit of measure for a single packaged item's net content (net_content_value). Values correspond to UN/CEFACT
    Recommendation 20 unit-of-measure codes, the same code list referenced by schema:unitCode and GS1's netContent
    property for packaged goods.
    """
    milliliter = PermissibleValue(
        text="milliliter",
        description="""Millilitres. UN/CEFACT code MLT. Liquids in small packaging (shampoo, cough syrup, hand sanitiser).""")
    litre = PermissibleValue(
        text="litre",
        description="Litres. UN/CEFACT code LTR. Liquids in larger packaging (juice, laundry detergent).")
    gram = PermissibleValue(
        text="gram",
        description="Grams. UN/CEFACT code GRM. Solids in small packaging (bar soap, spice sachet).")
    kilogram = PermissibleValue(
        text="kilogram",
        description="Kilograms. UN/CEFACT code KGM. Solids in larger packaging (rice, flour, dry pet food).")
    piece = PermissibleValue(
        text="piece",
        description="Discrete count as printed on the pack. UN/CEFACT code H87. Tablets, pads, sheets, rolls.")
    other = PermissibleValue(
        text="other",
        description="Unit not covered by the values above.")

    _defn = EnumDefinition(
        name="NetContentUnitEnum",
        description="""Unit of measure for a single packaged item's net content (net_content_value). Values correspond to UN/CEFACT Recommendation 20 unit-of-measure codes, the same code list referenced by schema:unitCode and GS1's netContent property for packaged goods.""",
    )

class AttributeCompletenessEnum(EnumDefinitionImpl):
    """
    Data quality tier for a DonationItem's category-specific attributes. Set by the fragment engine on sorting step
    completion — not derived from field presence at the schema level.
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
    minimal = PermissibleValue(
        text="minimal",
        description="""Only mandatory fields recorded. Matches broad demand signals only (e.g. \"any adult clothing\"). Typical cause: missing labels, inconclusive assessment, rapid triage under time pressure.""")
    standard = PermissibleValue(
        text="standard",
        description="""All standard fields recorded. Normal redistribution path. Matches the majority of demand signals.""")
    detailed = PermissibleValue(
        text="detailed",
        description="""All optional fields also recorded (colour, style, intact labels, etc.). Maximum match quality. Enables fine-grained demand signal matching.""")

    _defn = EnumDefinition(
        name="AttributeCompletenessEnum",
        description="""Data quality tier for a DonationItem's category-specific attributes. Set by the fragment engine on sorting step completion — not derived from field presence at the schema level.
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
The fragment compiler reads these annotations to configure the sorting UI.""",
    )

class ItemLifecycleStateEnum(EnumDefinitionImpl):
    """
    Lifecycle states for a DonationItem. Ordered; transitions enforced by Django model clean(). The fragment engine
    drives the sorted transition on sorting episode completion; attribute_completeness is set at the same time.
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
    announced = PermissibleValue(
        text="announced",
        description="""Donor indicated intent to donate; item not yet physically present. Optional state — used when pre-registration is supported.""")
    received = PermissibleValue(
        text="received",
        description="""Item physically arrived and registered against a DonationCollection. usage must be set at this point. Category-specific assessment slots are absent — they are populated during sorting.""")
    sorting_in_progress = PermissibleValue(
        text="sorting_in_progress",
        description="""Active sorting episode in progress. Fragment engine sets this on episode launch to prevent concurrent editing of the same item.""")
    sorted = PermissibleValue(
        text="sorted",
        description="""Sorting episode completed. Assessment and category attributes recorded. attribute_completeness set by the fragment engine. Item is ready for storage assignment.""")
    stored = PermissibleValue(
        text="stored",
        description="Item assigned to a physical StorageLocation. storage_unit FK is set at this transition.")
    disposed = PermissibleValue(
        text="disposed",
        description="""Item deemed unsuitable for redistribution and disposed of. Terminal state. (Phase 2 stub — declared now for schema completeness.)""")
    distributed = PermissibleValue(
        text="distributed",
        description="Item given to a beneficiary. Terminal state. (Phase 2 stub.)")
    shared = PermissibleValue(
        text="shared",
        description="""Item transferred to another organisation via the Share workflow. Terminal state. (Phase 2 stub.)""")

    _defn = EnumDefinition(
        name="ItemLifecycleStateEnum",
        description="""Lifecycle states for a DonationItem. Ordered; transitions enforced by Django model clean(). The fragment engine drives the sorted transition on sorting episode completion; attribute_completeness is set at the same time.
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
  stored              → disposed            (culled from stock; Phase 2)""",
    )

class BaseCategoryEnum(EnumDefinitionImpl):
    """
    Canonical registry of all donation item categories. Each permissible value carries a dispatch_to annotation naming
    the bare category mixin (categories/*.yaml) for that category — no assessment content, no lifecycle-gated fields.
    See SortingCategoryEnum below for the parallel enum used where that content is needed.
    The UI descriptor generator (generators/ui_descriptor.py) treats any slot whose range is an enum with dispatch_to
    annotations as a dispatch field, and builds its dispatch map directly from those annotations.
    Grouping is aligned with COICOP 2018 divisions where applicable, with deviations documented per value:
    Apparel    → COICOP Division 03 (clothing and footwear)
    Home       → COICOP Division 05 (housing, household goods)
    Technology → COICOP Division 09 (recreation and culture)
    Learning   → COICOP Division 09 (recreation and culture)
    Care       → COICOP Divisions 06 (health) and 12 (personal care)
    Life stage → COICOP Divisions 01 (food) and 03/05 (baby items)
    """
    ClothingItem = PermissibleValue(
        text="ClothingItem",
        description="""Clothing garments: tops, bottoms, outerwear, underwear, nightwear, sportswear → ClothingItem. COICOP 03.1. Separated from accessories because the demographic→size value map and UC rules (underwear condition) do not apply to accessories.""",
        meaning=INKIND_KNOWLEDGE_REPO["ClothingItem"])
    AccessoriesItem = PermissibleValue(
        text="AccessoriesItem",
        description="""Fashion accessories: hats, bags, jewellery, scarves, gloves, belts → AccessoriesItem. COICOP 03.1 (grouped with clothing by COICOP; separated here for progressive UI disclosure and schema clarity — no size dimension, simpler demographic vocabulary).""",
        meaning=INKIND_KNOWLEDGE_REPO["AccessoriesItem"])
    FootwearItem = PermissibleValue(
        text="FootwearItem",
        description="""Shoes, boots, sandals, slippers → FootwearItem. COICOP 03.2. Separated from clothing because shoe sizing systems (EU/UK/US/CM) differ from clothing sizes and pair-completeness is footwear-specific.""",
        meaning=INKIND_KNOWLEDGE_REPO["FootwearItem"])
    FurnitureItem = PermissibleValue(
        text="FurnitureItem",
        description="""Structural furniture: chairs, tables, beds, wardrobes → FurnitureItem. COICOP 05.1 (furniture and furnishings).""",
        meaning=INKIND_KNOWLEDGE_REPO["FurnitureItem"])
    BeddingTextilesItem = PermissibleValue(
        text="BeddingTextilesItem",
        description="""Blankets, duvets, mattresses, pillows, towels, curtains → BeddingTextilesItem. COICOP 05.2 (household textiles). Separated from household following COICOP 05.2 and UNHCR NFI kit standards, which list blankets and sleeping mats as core relief items at the same priority level as clothing.""",
        meaning=INKIND_KNOWLEDGE_REPO["BeddingTextilesItem"])
    HouseholdItem = PermissibleValue(
        text="HouseholdItem",
        description="""Cookware, crockery, small appliances, home decor → HouseholdItem. COICOP 05.3 (household appliances), 05.4 (glassware/tableware/utensils), 05.5 (tools for house and garden).""",
        meaning=INKIND_KNOWLEDGE_REPO["HouseholdItem"])
    ElectronicsItem = PermissibleValue(
        text="ElectronicsItem",
        description="""Consumer electronics: phones, laptops, cameras, gaming → ElectronicsItem. COICOP 09.1 (audio-visual equipment) and 09.2.""",
        meaning=INKIND_KNOWLEDGE_REPO["ElectronicsItem"])
    ToysItem = PermissibleValue(
        text="ToysItem",
        description="""Toys and games → ToysItem. COICOP 09.3 (games, toys, hobbies). Age-grading follows EU Toy Safety Directive 2009/48/EC.""",
        meaning=INKIND_KNOWLEDGE_REPO["ToysItem"])
    SportsItem = PermissibleValue(
        text="SportsItem",
        description="""Sports and fitness equipment → SportsItem. COICOP 09.4 (sport and recreational equipment). Note: bicycles are placed here by domain convention; COICOP assigns them to Division 07 (Transport).""",
        meaning=INKIND_KNOWLEDGE_REPO["SportsItem"])
    BooksItem = PermissibleValue(
        text="BooksItem",
        description="Books and educational materials → BooksItem. COICOP 09.5 (newspapers, books, stationery).",
        meaning=INKIND_KNOWLEDGE_REPO["BooksItem"])
    StationeryItem = PermissibleValue(
        text="StationeryItem",
        description="""Pens, notebooks, art supplies, office equipment → StationeryItem. COICOP 09.5 (newspapers, books, stationery). Separated from books because published content (BooksItem) and consumable/office supplies have different sorting paths, condition vocabularies, and demand signals.""",
        meaning=INKIND_KNOWLEDGE_REPO["StationeryItem"])
    PersonalCareItem = PermissibleValue(
        text="PersonalCareItem",
        description="""Personal hygiene, health, and beauty products → PersonalCareItem. Merges COICOP 06.1 (medical products and appliances) and 12.1 (personal care). Merged because the operative safety rules are identical across both: sealed required, used tools blocked, expiry enforced. Open Eligibility uses a single \"Personal Care Items\" node.""",
        meaning=INKIND_KNOWLEDGE_REPO["PersonalCareItem"])
    MobilityAidsItem = PermissibleValue(
        text="MobilityAidsItem",
        description="""Wheelchairs, crutches, hearing aids, assistive devices → MobilityAidsItem. COICOP 06.1.3 (other medical products) and 06.2 (outpatient services, durable medical equipment). Open Eligibility \"Assistive Technology\" top-level category.""",
        meaning=INKIND_KNOWLEDGE_REPO["MobilityAidsItem"])
    BabyInfantItem = PermissibleValue(
        text="BabyInfantItem",
        description="""Pushchairs, cots, car seats, infant formula, feeding equipment → BabyInfantItem. COICOP distributes baby items across 03 (clothing), 05 (household), and 01 (food). Treated as a first-class top-level category here following Open Eligibility \"Baby Supplies\" and UNHCR NFI kit practice (nappies and formula are core NFI kit items).""",
        meaning=INKIND_KNOWLEDGE_REPO["BabyInfantItem"])
    FoodItem = PermissibleValue(
        text="FoodItem",
        description="""Food items → FoodItem. COICOP Division 01 (food and non-alcoholic beverages). Phase 1 stub — activated when food-bank organisations are onboarded. Grounded in FoodOn (OBO Foundry).""",
        meaning=INKIND_KNOWLEDGE_REPO["FoodItem"])
    OtherItem = PermissibleValue(
        text="OtherItem",
        description="""Items not fitting any other category → OtherItem. No COICOP alignment. Use sparingly — if a type appears frequently, add a proper subclass.""",
        meaning=INKIND_KNOWLEDGE_REPO["OtherItem"])

    _defn = EnumDefinition(
        name="BaseCategoryEnum",
        description="""Canonical registry of all donation item categories. Each permissible value carries a dispatch_to annotation naming the bare category mixin (categories/*.yaml) for that category — no assessment content, no lifecycle-gated fields. See SortingCategoryEnum below for the parallel enum used where that content is needed.
The UI descriptor generator (generators/ui_descriptor.py) treats any slot whose range is an enum with dispatch_to annotations as a dispatch field, and builds its dispatch map directly from those annotations.
Grouping is aligned with COICOP 2018 divisions where applicable, with deviations documented per value:
  Apparel    → COICOP Division 03 (clothing and footwear)
  Home       → COICOP Division 05 (housing, household goods)
  Technology → COICOP Division 09 (recreation and culture)
  Learning   → COICOP Division 09 (recreation and culture)
  Care       → COICOP Divisions 06 (health) and 12 (personal care)
  Life stage → COICOP Divisions 01 (food) and 03/05 (baby items)""",
    )

class SortingCategoryEnum(EnumDefinitionImpl):
    """
    Same 16 category identities as BaseCategoryEnum (see that enum for COICOP grounding, not repeated here), but each
    dispatch_to annotation points to the category's physical-item mixin — Tier 1/2 category mixin plus that category's
    lc-* rules (categories/_context_rules.yaml) — instead of the bare mixin. Used by roots describing an actual
    physical item with a real lifecycle_state.
    """
    ClothingItem = PermissibleValue(
        text="ClothingItem",
        meaning=INKIND_KNOWLEDGE_REPO["ClothingItem"])
    AccessoriesItem = PermissibleValue(
        text="AccessoriesItem",
        meaning=INKIND_KNOWLEDGE_REPO["AccessoriesItem"])
    FootwearItem = PermissibleValue(
        text="FootwearItem",
        meaning=INKIND_KNOWLEDGE_REPO["FootwearItem"])
    FurnitureItem = PermissibleValue(
        text="FurnitureItem",
        meaning=INKIND_KNOWLEDGE_REPO["FurnitureItem"])
    BeddingTextilesItem = PermissibleValue(
        text="BeddingTextilesItem",
        meaning=INKIND_KNOWLEDGE_REPO["BeddingTextilesItem"])
    HouseholdItem = PermissibleValue(
        text="HouseholdItem",
        meaning=INKIND_KNOWLEDGE_REPO["HouseholdItem"])
    ElectronicsItem = PermissibleValue(
        text="ElectronicsItem",
        meaning=INKIND_KNOWLEDGE_REPO["ElectronicsItem"])
    ToysItem = PermissibleValue(
        text="ToysItem",
        meaning=INKIND_KNOWLEDGE_REPO["ToysItem"])
    SportsItem = PermissibleValue(
        text="SportsItem",
        meaning=INKIND_KNOWLEDGE_REPO["SportsItem"])
    BooksItem = PermissibleValue(
        text="BooksItem",
        meaning=INKIND_KNOWLEDGE_REPO["BooksItem"])
    StationeryItem = PermissibleValue(
        text="StationeryItem",
        meaning=INKIND_KNOWLEDGE_REPO["StationeryItem"])
    PersonalCareItem = PermissibleValue(
        text="PersonalCareItem",
        meaning=INKIND_KNOWLEDGE_REPO["PersonalCareItem"])
    MobilityAidsItem = PermissibleValue(
        text="MobilityAidsItem",
        meaning=INKIND_KNOWLEDGE_REPO["MobilityAidsItem"])
    BabyInfantItem = PermissibleValue(
        text="BabyInfantItem",
        meaning=INKIND_KNOWLEDGE_REPO["BabyInfantItem"])
    FoodItem = PermissibleValue(
        text="FoodItem",
        meaning=INKIND_KNOWLEDGE_REPO["FoodItem"])
    OtherItem = PermissibleValue(
        text="OtherItem",
        meaning=INKIND_KNOWLEDGE_REPO["OtherItem"])

    _defn = EnumDefinition(
        name="SortingCategoryEnum",
        description="""Same 16 category identities as BaseCategoryEnum (see that enum for COICOP grounding, not repeated here), but each dispatch_to annotation points to the category's physical-item mixin — Tier 1/2 category mixin plus that category's lc-* rules (categories/_context_rules.yaml) — instead of the bare mixin. Used by roots describing an actual physical item with a real lifecycle_state.""",
    )

class ConditionEnum(EnumDefinitionImpl):
    """
    DEPRECATED. Use usage + condition_grade instead.
    """
    new = PermissibleValue(
        text="new",
        meaning=SCHEMA["NewCondition"])
    good = PermissibleValue(
        text="good",
        meaning=SCHEMA["UsedCondition"])
    fair = PermissibleValue(
        text="fair",
        meaning=SCHEMA["UsedCondition"])
    poor = PermissibleValue(
        text="poor",
        meaning=SCHEMA["DamagedCondition"])

    _defn = EnumDefinition(
        name="ConditionEnum",
        description="DEPRECATED. Use usage + condition_grade instead.",
    )

class ActorRoleEnum(EnumDefinitionImpl):
    """
    Valid actor roles within a SocialOrganisation.
    """
    volunteer = PermissibleValue(
        text="volunteer",
        description="Volunteer — routed to guided fragment mode by default.")
    staff = PermissibleValue(
        text="staff",
        description="Staff member — routed to expert mode by default.")
    manager = PermissibleValue(
        text="manager",
        description="Manager — access to reporting and configuration.")
    admin = PermissibleValue(
        text="admin",
        description="Organisation administrator — full configuration access.")

    _defn = EnumDefinition(
        name="ActorRoleEnum",
        description="Valid actor roles within a SocialOrganisation.",
    )

class ExperienceLevelEnum(EnumDefinitionImpl):
    """
    Actor experience level for fragment mode selection.
    """
    novice = PermissibleValue(
        text="novice",
        description="Novice — additional guidance text shown.")
    experienced = PermissibleValue(
        text="experienced",
        description="Experienced — standard guidance.")
    expert = PermissibleValue(
        text="expert",
        description="Expert — minimal guidance, fast-path mode.")

    _defn = EnumDefinition(
        name="ExperienceLevelEnum",
        description="Actor experience level for fragment mode selection.",
    )

class DonationSourceTypeEnum(EnumDefinitionImpl):
    """
    Discriminator for the origin type of a donation.
    """
    anonymous_private = PermissibleValue(
        text="anonymous_private",
        description="""Anonymous private donor.  Only type active in Phase 1. Identity tracked via opaque `anonymous_donor_id` token only.""")
    corporate = PermissibleValue(
        text="corporate",
        description="Corporate donor — linked to CorporateDonor profile. Year 2 feature stub.")
    organisation = PermissibleValue(
        text="organisation",
        description="Donation from another SocialOrganisation (e.g., a Share workflow transfer).  Phase 2 stub.")

    _defn = EnumDefinition(
        name="DonationSourceTypeEnum",
        description="Discriminator for the origin type of a donation.",
    )

class DonationSourceLifecycleEnum(EnumDefinitionImpl):
    """
    Lifecycle states for a DonationSource.
    """
    announced = PermissibleValue(
        text="announced",
        description="Donor indicated intent to donate; physical items not yet received.")
    received = PermissibleValue(
        text="received",
        description="Physical items received and linked to this source.")
    acknowledged = PermissibleValue(
        text="acknowledged",
        description="""Impact notification sent to donor.  Phase 1 stub — activated when items complete their lifecycle and Donor Portal is live.""")

    _defn = EnumDefinition(
        name="DonationSourceLifecycleEnum",
        description="Lifecycle states for a DonationSource.",
    )

class CollectionTypeEnum(EnumDefinitionImpl):
    """
    Operational type of a DonationCollection.
    """
    arrival = PermissibleValue(
        text="arrival",
        description="""Root collection created when a donation arrives.  Replaces DonationBatch.  Phase 1 only type in active use.""")
    working = PermissibleValue(
        text="working",
        description="Temporary intermediate collection during a multi-stage sort pass. Phase 2 stub.")
    sorted = PermissibleValue(
        text="sorted",
        description="Stable grouping after a sort stage completes.  Phase 2 stub.")
    stock = PermissibleValue(
        text="stock",
        description="""Named standing collection ready for distribution.  Maps to DemandSignal of type `standing`.  Phase 2 stub.""")
    campaign = PermissibleValue(
        text="campaign",
        description="Collection assembled for a specific Campaign entity.  Phase 2 stub.")
    disposed = PermissibleValue(
        text="disposed",
        description="Items culled during sorting — auditable at collection level. Phase 2 stub.")

    _defn = EnumDefinition(
        name="CollectionTypeEnum",
        description="Operational type of a DonationCollection.",
    )

class CollectionLifecycleEnum(EnumDefinitionImpl):
    """
    Lifecycle states for a DonationCollection.
    """
    open = PermissibleValue(
        text="open",
        description="Collection is open for item registration or operations.")
    processing = PermissibleValue(
        text="processing",
        description="Items are actively being registered or processed.")
    closed = PermissibleValue(
        text="closed",
        description="All processing complete; collection is closed.")
    archived = PermissibleValue(
        text="archived",
        description="Collection has been archived for record-keeping.")

    _defn = EnumDefinition(
        name="CollectionLifecycleEnum",
        description="Lifecycle states for a DonationCollection.",
    )

class ItemCountRangeEnum(EnumDefinitionImpl):
    """
    Categorical ranges for item counts in a collection or for defining the tracking tier.
    """
    single = PermissibleValue(
        text="single",
        description="A single, identifiable item")
    small_pile = PermissibleValue(
        text="small_pile",
        description="2-10 items")
    medium_pile = PermissibleValue(
        text="medium_pile",
        description="11-50 items")
    large_pile = PermissibleValue(
        text="large_pile",
        description="51+ items")

    _defn = EnumDefinition(
        name="ItemCountRangeEnum",
        description="Categorical ranges for item counts in a collection or for defining the tracking tier.",
    )

class DemandSignalTypeEnum(EnumDefinitionImpl):
    """
    Discriminator for the type of demand signal.
    """
    standing = PermissibleValue(
        text="standing",
        description="""Permanent standing interest in a category.  No deadline, no quantity target.  Stays active until explicitly withdrawn.""")
    campaign = PermissibleValue(
        text="campaign",
        description="Time-bounded coordinated effort tied to a Campaign.  Has deadline and quantity target.")
    specific = PermissibleValue(
        text="specific",
        description="Concrete request for a specific beneficiary or holder.  Has urgency tier.")

    _defn = EnumDefinition(
        name="DemandSignalTypeEnum",
        description="Discriminator for the type of demand signal.",
    )

class UrgencyTierEnum(EnumDefinitionImpl):
    """
    Urgency classification for campaign and specific demand signals.
    """
    low = PermissibleValue(
        text="low",
        description="Low urgency — no immediate deadline pressure.")
    medium = PermissibleValue(
        text="medium",
        description="Medium urgency.")
    high = PermissibleValue(
        text="high",
        description="High urgency — deadline approaching or need is acute.")
    critical = PermissibleValue(
        text="critical",
        description="Critical — immediate fulfilment required.")

    _defn = EnumDefinition(
        name="UrgencyTierEnum",
        description="Urgency classification for campaign and specific demand signals.",
    )

class HouseholdSituationEnum(EnumDefinitionImpl):
    """
    Household composition classification for a demand signal.
    """
    single_adult = PermissibleValue(
        text="single_adult",
        description="Single adult household.")
    couple_no_children = PermissibleValue(
        text="couple_no_children",
        description="Couple without children.")
    single_parent = PermissibleValue(
        text="single_parent",
        description="Single parent with one or more children.")
    family_with_children = PermissibleValue(
        text="family_with_children",
        description="Family with two parents/carers and one or more children.")
    multigenerational = PermissibleValue(
        text="multigenerational",
        description="Household spanning multiple generations.")
    other = PermissibleValue(
        text="other",
        description="Household composition not covered by the above.")

    _defn = EnumDefinition(
        name="HouseholdSituationEnum",
        description="Household composition classification for a demand signal.",
    )

class DemandSignalLifecycleEnum(EnumDefinitionImpl):
    """
    Lifecycle states for a DemandSignal. Standing signals stay `active` permanently; campaign and specific signals
    follow the full lifecycle.
    """
    active = PermissibleValue(
        text="active",
        description="Signal is active and accepting matched items.")
    partially_fulfilled = PermissibleValue(
        text="partially_fulfilled",
        description="Some items matched but quantity_requested not yet reached.")
    fulfilled = PermissibleValue(
        text="fulfilled",
        description="All requested items matched.")
    expired = PermissibleValue(
        text="expired",
        description="Deadline passed without full fulfilment (campaign/specific types only).")
    withdrawn = PermissibleValue(
        text="withdrawn",
        description="Organisation explicitly cancelled this signal.")

    _defn = EnumDefinition(
        name="DemandSignalLifecycleEnum",
        description="""Lifecycle states for a DemandSignal.  Standing signals stay `active` permanently; campaign and specific signals follow the full lifecycle.""",
    )

class CampaignLifecycleEnum(EnumDefinitionImpl):
    """
    Lifecycle states for a Campaign.
    """
    planned = PermissibleValue(
        text="planned",
        description="Campaign is planned but not yet started.")
    active = PermissibleValue(
        text="active",
        description="Campaign is active and accepting donations.")
    completed = PermissibleValue(
        text="completed",
        description="Campaign reached its end date with fulfilment achieved.")
    cancelled = PermissibleValue(
        text="cancelled",
        description="Campaign was cancelled before completion.")

    _defn = EnumDefinition(
        name="CampaignLifecycleEnum",
        description="Lifecycle states for a Campaign.",
    )

class AccessoriesSubcategoryEnum(EnumDefinitionImpl):
    """
    Fashion and personal accessories subcategories. Deliberately separate from ClothingSubcategoryEnum to enable clean
    progressive disclosure in the sorting UI. Grounded in Product Types Ontology (pto:) terms.
    """
    hats_headwear = PermissibleValue(
        text="hats_headwear",
        description="Hats, caps, beanies, headscarves, berets.")
    scarves = PermissibleValue(
        text="scarves",
        description="Scarves and shawls worn at neck or shoulders.")
    gloves_mittens = PermissibleValue(
        text="gloves_mittens",
        description="Gloves and mittens (all ages).")
    belts = PermissibleValue(
        text="belts",
        description="Belts, braces, and waist accessories.")
    bags_luggage = PermissibleValue(
        text="bags_luggage",
        description="""Handbags, tote bags, backpacks, shoulder bags, wallets, purses, clutch bags, small luggage items.""")
    jewellery = PermissibleValue(
        text="jewellery",
        description="Necklaces, bracelets, rings, earrings, brooches.")
    sunglasses = PermissibleValue(
        text="sunglasses",
        description="Sunglasses and fashion spectacle frames.")
    watches = PermissibleValue(
        text="watches",
        description="Wristwatches and pocket watches.")
    other = PermissibleValue(
        text="other",
        description="Accessories not fitting above subcategories.")

    _defn = EnumDefinition(
        name="AccessoriesSubcategoryEnum",
        description="""Fashion and personal accessories subcategories. Deliberately separate from ClothingSubcategoryEnum to enable clean progressive disclosure in the sorting UI. Grounded in Product Types Ontology (pto:) terms.""",
    )

class AccessoriesMaterialEnum(EnumDefinitionImpl):
    """
    Primary construction material of a fashion or personal accessory. Records the dominant material the sorter can
    identify quickly (e.g. a watch has metal case + leather strap + glass face — record the most prominent element).
    Grounded in Product Types Ontology (pto:), aligned with ClothingMaterialEnum's fibre values for consistency.
    """
    leather = PermissibleValue(
        text="leather",
        description="""Genuine or faux leather (PU/synthetic leather). Predominant material for bags, belts, wallets, and some gloves and watch straps. Requires specialist conditioning care.""")
    wool = PermissibleValue(
        text="wool",
        description="""Wool, merino, cashmere, or wool-dominant blend. Primary material for scarves, hats, and gloves. Allergen signal for wool-sensitive beneficiaries.""")
    cotton = PermissibleValue(
        text="cotton",
        description="""Cotton or cotton-dominant woven fabric. Common in fabric hats, canvas bags, and some gloves and scarves. All-season versatile.""")
    silk = PermissibleValue(
        text="silk",
        description="""Silk or silk-blend. Typical for elegant scarves and ties. Requires specialist care (hand wash or dry clean).""")
    metal = PermissibleValue(
        text="metal",
        description="""Metal (gold, silver, base metal, stainless steel, or alloy). Predominant for jewellery, watch cases, belt buckles, and eyewear frames. Nickel in base metal alloys is a common allergen.""")
    plastic = PermissibleValue(
        text="plastic",
        description="""Plastic or acrylic. Common for sunglasses frames, costume jewellery, and some bags. Wide range of types — record specifics in sorting_notes if relevant (e.g. recycled plastic, BPA-free for baby accessories).""")
    synthetic = PermissibleValue(
        text="synthetic",
        description="""Synthetic fabric or material — nylon, polyester, or other man-made fibres. Common in nylon bags, polyester scarves, and synthetic gloves. Distinct from leather_faux_leather (which mimics leather texture).""")
    natural_fibre = PermissibleValue(
        text="natural_fibre",
        description="""Natural plant-based fibres other than cotton — straw, raffia, jute, bamboo, rattan, wicker. Common in summer hats and baskets.""")
    glass_crystal = PermissibleValue(
        text="glass_crystal",
        description="""Glass or crystal elements. Common in costume jewellery (glass beads, crystal pendants) and some decorative accessories.""")
    other = PermissibleValue(
        text="other",
        description="Materials not covered above. Record the specific material in sorting_notes when known.")

    _defn = EnumDefinition(
        name="AccessoriesMaterialEnum",
        description="""Primary construction material of a fashion or personal accessory. Records the dominant material the sorter can identify quickly (e.g. a watch has metal case + leather strap + glass face — record the most prominent element). Grounded in Product Types Ontology (pto:), aligned with ClothingMaterialEnum's fibre values for consistency.""",
    )

class AccessoriesDemographicEnum(EnumDefinitionImpl):
    """
    Simplified age-group demographic for accessories. Gender split not modelled — gender is not a meaningful dimension
    for most accessories at the sorting level. This contrasts with DemographicEnum (clothing.yaml) which carries
    adult_male/adult_female because clothing size systems are gender-differentiated. Use only when the item clearly
    targets a specific age group (e.g. children's hat, baby mittens).
    """
    baby = PermissibleValue(
        text="baby",
        description="Baby (0-24 months). e.g. baby hats, scratch mittens.")
    child = PermissibleValue(
        text="child",
        description="Child (2-14 years). e.g. children's hats, gloves.")
    adult = PermissibleValue(
        text="adult",
        description="Adult. Default for most accessories when demographic matters.")
    all_ages = PermissibleValue(
        text="all_ages",
        description="Suitable for all ages or demographic not applicable.")

    _defn = EnumDefinition(
        name="AccessoriesDemographicEnum",
        description="""Simplified age-group demographic for accessories. Gender split not modelled — gender is not a meaningful dimension for most accessories at the sorting level. This contrasts with DemographicEnum (clothing.yaml) which carries adult_male/adult_female because clothing size systems are gender-differentiated. Use only when the item clearly targets a specific age group (e.g. children's hat, baby mittens).""",
    )

class SeasonEnum(EnumDefinitionImpl):
    """
    Seasonal suitability of a clothing or footwear item. Used on ClothingCategory (season slot) and FootwearCategory
    (season slot).
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
    winter = PermissibleValue(
        text="winter",
        description="""Primarily suitable for cold weather. Implies is_winter_suitable=true. Examples: heavy winter coat, thermal base layer, fleece-lined trousers, woollen jumper, ski jacket.""")
    spring_autumn = PermissibleValue(
        text="spring_autumn",
        description="""Suitable for mild transitional seasons. Thermal weight between winter and summer. is_winter_suitable is sorter's call. Examples: light jacket, cardigan, jeans, hoodie, trench coat.""")
    summer = PermissibleValue(
        text="summer",
        description="""Suitable for warm weather; not appropriate for cold conditions. Implies is_winter_suitable=false. Examples: t-shirt, shorts, sundress, swimwear, linen top.""")
    all_season = PermissibleValue(
        text="all_season",
        description="""No meaningful seasonal constraint — appropriate across all seasons or in climate-controlled environments. Implies is_winter_suitable=true (all-season items are by definition usable in winter). Examples: underwear, plain cotton t-shirt used as a base layer, school uniform shirt.""")

    _defn = EnumDefinition(
        name="SeasonEnum",
        description="""Seasonal suitability of a clothing or footwear item. Used on ClothingCategory (season slot) and FootwearCategory (season slot).
Design notes:
  - Four values only — fine enough for redistribution decisions,
    coarse enough for fast sorting.
  - spring_autumn is a single value because the thermal characteristics
    that define a transitional garment are the same regardless of
    which shoulder season it appears in.
  - all_season covers items with no meaningful seasonal constraint
    (e.g. a plain cotton t-shirt, a lightweight fleece) — distinct from
    \"we don't know\" (absence of the field) and from \"suitable in all
    conditions including winter\" (is_winter_suitable=true + all_season).
  - Multivalued: a linen blazer might be both spring_autumn and summer.
    Record all applicable values.""",
    )

class ClothingSubcategoryEnum(EnumDefinitionImpl):
    """
    Clothing garment subcategories. Accessories are NOT here — they are in AccessoriesSubcategoryEnum
    (accessories.yaml) on a separate item class. Separation enables clean progressive disclosure in the UI.
    """
    tops = PermissibleValue(
        text="tops",
        description="""T-shirts, shirts, blouses, sweaters, upper-body garments. is_winter_suitable varies widely — a linen shirt and a wool jumper are both tops. Sorter must set explicitly.""")
    bottoms = PermissibleValue(
        text="bottoms",
        description="""Trousers, skirts, shorts, leggings, lower-body garments. is_winter_suitable varies — shorts are summer; thermal leggings are winter.""")
    one_piece = PermissibleValue(
        text="one_piece",
        description="One-piece garments: dresses, jumpsuits, rompers, overalls.")
    outerwear = PermissibleValue(
        text="outerwear",
        description="""Jackets, coats, outer layers. Fragment compiler may pre-fill is_winter_suitable=true; sorter can override for summer-weight jackets.""")
    underwear = PermissibleValue(
        text="underwear",
        description="""Underwear and intimate apparel. UC constraints apply. Thermal underwear should be tagged is_winter_suitable=true. Standard underwear → all_season / is_winter_suitable=true (base layer).""")
    nightwear = PermissibleValue(
        text="nightwear",
        description="""Pyjamas, nightgowns, dressing gowns, sleep sets. Seasonal weight varies — lightweight vs. fleece nightwear.""")
    sportswear = PermissibleValue(
        text="sportswear",
        description="""Athletic wear, gym tops, leggings, base layers. Non-specialist — specialist sports clothing (wetsuits, cycling jerseys) belongs in SportsItem. Swimwear is a separate subcategory — see swimwear.""")
    swimwear = PermissibleValue(
        text="swimwear",
        description="""Swimwear and bathing garments: swimsuits, bikinis, swim trunks, board shorts. Always summer-only (see SeasonEnum) — unlike sportswear's other examples (e.g. thermal base layers), which can be winter-suitable. Separated from sportswear for hygiene handling: worn against skin like underwear, so the same UC condition/usage rules apply (uc-swimwear-condition-block, uc-swimwear-adult-used-block).""")
    other = PermissibleValue(
        text="other",
        description="Clothing garments not fitting above subcategories.")

    _defn = EnumDefinition(
        name="ClothingSubcategoryEnum",
        description="""Clothing garment subcategories. Accessories are NOT here — they are in AccessoriesSubcategoryEnum (accessories.yaml) on a separate item class. Separation enables clean progressive disclosure in the UI.""",
    )

class TopsSubcategoryEnum(EnumDefinitionImpl):
    """
    Finer-grained garment type within the tops subcategory. UI-only refinement of ClothingSubcategoryEnum's tops value
    — not a separate hierarchy level, no UC/VM rules reference it.
    """
    t_shirt = PermissibleValue(
        text="t_shirt",
        description="T-shirts, tank tops.")
    shirt_blouse = PermissibleValue(
        text="shirt_blouse",
        description="Button-up shirts, blouses.")
    sweater_hoodie = PermissibleValue(
        text="sweater_hoodie",
        description="Sweaters, jumpers, hoodies, sweatshirts.")
    other = PermissibleValue(
        text="other",
        description="Tops not fitting above types.")

    _defn = EnumDefinition(
        name="TopsSubcategoryEnum",
        description="""Finer-grained garment type within the tops subcategory. UI-only refinement of ClothingSubcategoryEnum's tops value — not a separate hierarchy level, no UC/VM rules reference it.""",
    )

class BottomsSubcategoryEnum(EnumDefinitionImpl):
    """
    Finer-grained garment type within the bottoms subcategory. UI-only refinement of ClothingSubcategoryEnum's bottoms
    value — not a separate hierarchy level, no UC/VM rules reference it.
    """
    trousers = PermissibleValue(
        text="trousers",
        description="Trousers, pants, jeans.")
    shorts = PermissibleValue(
        text="shorts",
        description="Shorts.")
    skirt = PermissibleValue(
        text="skirt",
        description="Skirts.")
    leggings = PermissibleValue(
        text="leggings",
        description="Leggings, tights.")
    other = PermissibleValue(
        text="other",
        description="Bottoms not fitting above types.")

    _defn = EnumDefinition(
        name="BottomsSubcategoryEnum",
        description="""Finer-grained garment type within the bottoms subcategory. UI-only refinement of ClothingSubcategoryEnum's bottoms value — not a separate hierarchy level, no UC/VM rules reference it.""",
    )

class DemographicEnum(EnumDefinitionImpl):
    """
    Combined age-and-gender demographic for clothing and footwear items. Grounded in cpi:designatedFor and schema.org
    wearable size groups. Shared with FootwearItem and SportsItem via slot_usage overrides. AccessoriesItem uses the
    simpler AccessoriesDemographicEnum instead.
    """
    baby = PermissibleValue(
        text="baby",
        description="Baby (0-24 months). Valid sizes: baby_0_3m through baby_18_24m.")
    child = PermissibleValue(
        text="child",
        description="Child (2-14 years). Valid sizes: child_2T through child_14.")
    adult_male = PermissibleValue(
        text="adult_male",
        description="Adult male / menswear. Valid sizes: xs through one_size.")
    adult_female = PermissibleValue(
        text="adult_female",
        description="Adult female / womenswear. Valid sizes: xs through one_size.")
    unisex = PermissibleValue(
        text="unisex",
        description="""Unisex / gender-neutral adult. Valid sizes: xs through one_size. Not valid for underwear subcategory.""")

    _defn = EnumDefinition(
        name="DemographicEnum",
        description="""Combined age-and-gender demographic for clothing and footwear items. Grounded in cpi:designatedFor and schema.org wearable size groups. Shared with FootwearItem and SportsItem via slot_usage overrides. AccessoriesItem uses the simpler AccessoriesDemographicEnum instead.""",
    )

class ClothingSizeEnum(EnumDefinitionImpl):
    """
    Clothing sizes covering infant, children's, and adult sizing. Grounded in schema.org wearable size groups and CPI
    ClothingSize. Valid values per demographic are constrained by vm-size-* rules.
    """
    baby_50 = PermissibleValue(
        text="baby_50",
        description="Baby Size 45-50. Age Newborn.")
    baby_56 = PermissibleValue(
        text="baby_56",
        description="Baby Size 51-56. Age 1 month.")
    baby_62 = PermissibleValue(
        text="baby_62",
        description="Baby Size 57-62. Age 2-4 months.")
    baby_68 = PermissibleValue(
        text="baby_68",
        description="Baby Size 63-68. Age 5-7 months.")
    baby_74 = PermissibleValue(
        text="baby_74",
        description="Baby Size 69-74. Age 8-11 months.")
    baby_80 = PermissibleValue(
        text="baby_80",
        description="Baby Size 75-80. Age 12-15 months.")
    baby_86 = PermissibleValue(
        text="baby_86",
        description="Baby Size 81-86. Age 16-21 months.")
    baby_92 = PermissibleValue(
        text="baby_92",
        description="Baby Size 87-92. Age 22-24 months.")
    child_98 = PermissibleValue(
        text="child_98",
        description="Toddler 93-98. Age 2-3 years.")
    child_104 = PermissibleValue(
        text="child_104",
        description="Toddler 99-104. Age 3-4 years.")
    child_110 = PermissibleValue(
        text="child_110",
        description="Child 105-110. Age 4-5 years.")
    child_116 = PermissibleValue(
        text="child_116",
        description="Child 111-116. Age 5-6 years.")
    child_122 = PermissibleValue(
        text="child_122",
        description="Child 117-122. Age 6-7 years.")
    child_128 = PermissibleValue(
        text="child_128",
        description="Child 123-128. Age 7-8 years.")
    child_134 = PermissibleValue(
        text="child_134",
        description="Child 129-134. Age 8-9 years.")
    child_140 = PermissibleValue(
        text="child_140",
        description="Child 135-140. Age 9-10 years.")
    child_146 = PermissibleValue(
        text="child_146",
        description="Child 141-146. Age 10-11 years.")
    child_152 = PermissibleValue(
        text="child_152",
        description="Child 147-152. Age 11-12 years.")
    child_158 = PermissibleValue(
        text="child_158",
        description="Child 153-158. Age 12-13 years.")
    child_164 = PermissibleValue(
        text="child_164",
        description="Child 159-164. Age 13-14 years.")
    child_170 = PermissibleValue(
        text="child_170",
        description="Child 165-170. Age 14-16 years.")
    size_xs = PermissibleValue(
        text="size_xs",
        description="Adult Extra Small")
    size_s = PermissibleValue(
        text="size_s",
        description="Adult Small")
    size_m = PermissibleValue(
        text="size_m",
        description="Adult Medium")
    size_l = PermissibleValue(
        text="size_l",
        description="Adult Large")
    size_xl = PermissibleValue(
        text="size_xl",
        description="Adult Extra Large")
    size_xxl_plus = PermissibleValue(
        text="size_xxl_plus",
        description="Adult Extra Extra Large and Plus")
    baby_0_3m = PermissibleValue(
        text="baby_0_3m",
        description="Baby 0-3 months")
    baby_3_6m = PermissibleValue(
        text="baby_3_6m",
        description="Baby 3-6 months")
    baby_6_12m = PermissibleValue(
        text="baby_6_12m",
        description="Baby 6-12 months")
    baby_12_18m = PermissibleValue(
        text="baby_12_18m",
        description="Baby 12-18 months")
    baby_18_24m = PermissibleValue(
        text="baby_18_24m",
        description="Baby 18-24 months")
    child_2_3T = PermissibleValue(
        text="child_2_3T",
        description="Toddler sizes 2 and 3")
    child_4_5T = PermissibleValue(
        text="child_4_5T",
        description="Toddler sizes 4 and 5")
    child_6_7 = PermissibleValue(
        text="child_6_7",
        description="Child sizes 6 and 7")
    child_8_10 = PermissibleValue(
        text="child_8_10",
        description="Child sizes 8-10")
    child_12_14 = PermissibleValue(
        text="child_12_14",
        description="Child sizes 12-14")
    xs_s = PermissibleValue(
        text="xs_s",
        description="Extra small or Small (adult)")
    m_l = PermissibleValue(
        text="m_l",
        description="Medium or Large(adult)")
    xl_plus = PermissibleValue(
        text="xl_plus",
        description="Extra large or XL+ (adult)")
    one_size = PermissibleValue(
        text="one_size",
        description="One size fits most.")

    _defn = EnumDefinition(
        name="ClothingSizeEnum",
        description="""Clothing sizes covering infant, children's, and adult sizing. Grounded in schema.org wearable size groups and CPI ClothingSize. Valid values per demographic are constrained by vm-size-* rules.""",
    )

class ClothingMaterialEnum(EnumDefinitionImpl):
    """
    Primary fibre or fabric composition of a clothing item. Records the predominant material; for blends, select the
    dominant fibre or use synthetic_blend. Grounded in Product Types Ontology (pto:) per-value IRIs and
    schema:material as the fallback anchor. See file header for the allergen-filtering / seasonality-hinting /
    care-matching use cases.
    """
    cotton = PermissibleValue(
        text="cotton",
        description="""Cotton or cotton-dominant blend (>50% cotton). The most common natural fibre. All-season versatile; thermal weight varies by weave and weight (a thin cotton t-shirt vs. a heavy flannel shirt).""")
    wool = PermissibleValue(
        text="wool",
        description="""Wool, merino, lambswool, cashmere, or wool-dominant blend. Primary natural indicator of winter suitability.""")
    linen = PermissibleValue(
        text="linen",
        description="Linen (flax) fabric. Lightweight and breathable natural fibre. Primarily summer-weight.")
    silk = PermissibleValue(
        text="silk",
        description="""Silk or silk-blend. Lightweight natural fibre; typically summer or formal wear. Requires specialist care (dry clean or hand wash). Fragment compiler may pre-fill is_winter_suitable=false.""")
    denim = PermissibleValue(
        text="denim",
        description="""Denim (woven cotton twill). Used for jeans, jackets, and skirts. Seasonality varies by weight — standard denim is spring_autumn; heavy or lined denim may be winter-suitable. Sorter decides.""")
    leather = PermissibleValue(
        text="leather",
        description="""Leather or leather-look (genuine, PU, or faux leather). Primarily for outerwear (jackets, coats). Typically spring_autumn or winter-suitable depending on lining. Requires specialist care.""")
    fleece = PermissibleValue(
        text="fleece",
        description="""Polar fleece or other synthetic-pile insulating fabric. Warm and lightweight. Fragment compiler may pre-fill is_winter_suitable=true. This value covers synthetic-pile fleece only — use wool for merino or lambswool fleece.""")
    down = PermissibleValue(
        text="down",
        description="""Down-filled or feather-filled insulating garments (puffer jackets, gilets, down coats). Fragment compiler may pre-fill is_winter_suitable=true.""")
    polyester = PermissibleValue(
        text="polyester",
        description="""Polyester or polyester-dominant synthetic. Common in sportswear, activewear, and everyday garments. All-season; thermal weight varies by fabric construction.""")
    nylon = PermissibleValue(
        text="nylon",
        description="""Nylon (polyamide) fabric. Common in sportswear, windbreakers, and tights. Strong, lightweight, and moisture-resistant.""")
    synthetic_blend = PermissibleValue(
        text="synthetic_blend",
        description="""Mixed synthetic fibres or a synthetic + natural blend where no single fibre dominates and a more specific value does not apply. Examples: polyester/spandex (activewear), nylon/cotton blends, acrylic/polyester blends.""")
    other = PermissibleValue(
        text="other",
        description="""Materials not covered above — e.g. viscose/rayon, bamboo, modal, technical fabrics, specialty textiles. Record the specific material in sorting_notes when known and intact_labels=true.""")

    _defn = EnumDefinition(
        name="ClothingMaterialEnum",
        description="""Primary fibre or fabric composition of a clothing item. Records the predominant material; for blends, select the dominant fibre or use synthetic_blend. Grounded in Product Types Ontology (pto:) per-value IRIs and schema:material as the fallback anchor. See file header for the allergen-filtering / seasonality-hinting / care-matching use cases.""",
    )

class FootwearSubcategoryEnum(EnumDefinitionImpl):
    """
    Footwear subcategories. Grounded in Product Types Ontology. is_winter_suitable is the sorter's call — subcategory
    alone is insufficient (a lightweight canvas boot is not winter-suitable; a fleece-lined boot is). Fragment
    compiler provides UI hints.
    """
    shoes = PermissibleValue(
        text="shoes",
        description="""Everyday shoes, trainers/sneakers, loafers, school shoes. is_winter_suitable varies — trainers are spring_autumn/summer; leather Oxford shoes can be all_season.""")
    boots = PermissibleValue(
        text="boots",
        description="""Ankle boots, knee-high boots, work boots, winter boots. Fragment compiler pre-fills is_winter_suitable=true; sorter overrides for summer ankle boots, fashion boots without insulation.""")
    sandals = PermissibleValue(
        text="sandals",
        description="Open sandals and flip-flops. Fragment compiler pre-fills is_winter_suitable=false.")
    slippers = PermissibleValue(
        text="slippers",
        description="""Indoor slippers and house shoes. Typically all_season (indoor use, climate-controlled environment).""")
    sports_footwear = PermissibleValue(
        text="sports_footwear",
        description="Football boots, running shoes, cleats, cycling shoes. Specialist sports footwear.")
    other = PermissibleValue(
        text="other",
        description="Footwear not fitting above subcategories.")

    _defn = EnumDefinition(
        name="FootwearSubcategoryEnum",
        description="""Footwear subcategories. Grounded in Product Types Ontology. is_winter_suitable is the sorter's call — subcategory alone is insufficient (a lightweight canvas boot is not winter-suitable; a fleece-lined boot is). Fragment compiler provides UI hints.""",
    )

class FootwearMaterialEnum(EnumDefinitionImpl):
    """
    Primary upper-material of a footwear item (excluding the sole). Grounded in Product Types Ontology (pto:) where
    distinct IRIs exist, schema:material as fallback anchor; aligned with ClothingMaterialEnum for shared values
    (leather, suede, wool). Used for care-requirement matching, allergen filtering (latex rubber), and seasonality
    hinting.
    """
    leather = PermissibleValue(
        text="leather",
        description="""Genuine or polished leather upper. The most common material for dress shoes, leather boots, loafers, and classic Oxford shoes. Requires conditioning and polishing; not machine-washable.""")
    suede = PermissibleValue(
        text="suede",
        description="""Suede or nubuck upper. Brushed, napped leather surface. Common for ankle boots, desert boots, and casual shoes. Requires specialist suede brush and waterproofing spray.""")
    synthetic_leather = PermissibleValue(
        text="synthetic_leather",
        description="""PU or synthetic leather (faux leather) upper. Common in budget shoes, trainers, and fashion boots. Easier care than genuine leather but less durable over time.""")
    canvas = PermissibleValue(
        text="canvas",
        description="""Canvas or cotton-based textile upper. Typical for casual trainers (e.g. classic low-top sneakers), espadrilles, and deck shoes. Usually machine-washable. Primarily spring-autumn or summer use.""")
    synthetic_mesh = PermissibleValue(
        text="synthetic_mesh",
        description="""Breathable synthetic mesh or knit upper. Standard material for running shoes, athletic trainers, and performance footwear. Lightweight and quick-drying. Primarily spring-autumn or summer.""")
    rubber = PermissibleValue(
        text="rubber",
        description="""Rubber or PVC. Primary material for Wellington boots, rain boots, and some sandal soles. Fully waterproof; can be wiped clean. Natural rubber is a known allergen — record in sorting_notes if identifiable as natural rubber (often marked on the boot).""")
    wool_felt = PermissibleValue(
        text="wool_felt",
        description="""Wool, felt, or boiled-wool upper. Most common in warm indoor slippers and some traditional boots. Allergen signal for wool-sensitive beneficiaries.""")
    textile = PermissibleValue(
        text="textile",
        description="""Woven or knitted textile upper that is not canvas or synthetic mesh — e.g. fabric mules, woven espadrille-style shoes, textile slip-ons.""")
    other = PermissibleValue(
        text="other",
        description="""Materials not covered above (e.g. cork, wood clogs, exotic leather). Record the specific material in sorting_notes when known.""")

    _defn = EnumDefinition(
        name="FootwearMaterialEnum",
        description="""Primary upper-material of a footwear item (excluding the sole). Grounded in Product Types Ontology (pto:) where distinct IRIs exist, schema:material as fallback anchor; aligned with ClothingMaterialEnum for shared values (leather, suede, wool). Used for care-requirement matching, allergen filtering (latex rubber), and seasonality hinting.""",
    )

class ShoeSizeSystemEnum(EnumDefinitionImpl):
    """
    Shoe size measurement system. Multiple systems in common use across European, UK, US, and children's sizing
    conventions.
    """
    EU = PermissibleValue(
        text="EU",
        description="European sizing (e.g. 36, 38, 42, 46)")
    UK = PermissibleValue(
        text="UK",
        description="UK sizing (e.g. 3, 5, 8, 11)")
    US = PermissibleValue(
        text="US",
        description="US sizing (e.g. 6, 7.5, 9, 12)")
    CM = PermissibleValue(
        text="CM",
        description="Foot length in centimetres — used for infant sizing")

    _defn = EnumDefinition(
        name="ShoeSizeSystemEnum",
        description="""Shoe size measurement system. Multiple systems in common use across European, UK, US, and children's sizing conventions.""",
    )

class FurnitureAssessmentEnum(EnumDefinitionImpl):
    """
    Structured assessment of furniture structural integrity and quality, distinguishing cosmetic damage from
    structural compromise. Required at sorting regardless of usage.
    """
    structurally_sound = PermissibleValue(
        text="structurally_sound",
        description="""All load-bearing components intact; no cracks, wobbling, or unsafe instability. Safe for redistribution without qualification. Appropriate for new items with no observed defects.""")
    minor_cosmetic_damage = PermissibleValue(
        text="minor_cosmetic_damage",
        description="""Scratches, scuffs, minor surface damage. Structural integrity unaffected. Fully redistributable.""")
    significant_cosmetic_damage = PermissibleValue(
        text="significant_cosmetic_damage",
        description="""Visible staining, discolouration, or notable surface damage. Structurally sound but appearance significantly affected. action: warn for seating/beds — sorting_notes required.""")
    functional_with_repairs = PermissibleValue(
        text="functional_with_repairs",
        description="""Item is usable but benefits from minor repair before redistribution (loose screw, wobbly leg, minor adjustment needed). action: warn — sorting_notes required.""")
    structurally_compromised = PermissibleValue(
        text="structurally_compromised",
        description="""Load-bearing components cracked, broken, or unsafe. Must not be redistributed. Applies to new items (manufacturing defect) and used. action: block, suggest: disposal or repair referral.""")

    _defn = EnumDefinition(
        name="FurnitureAssessmentEnum",
        description="""Structured assessment of furniture structural integrity and quality, distinguishing cosmetic damage from structural compromise. Required at sorting regardless of usage.""",
    )

class FurnitureSubcategoryEnum(EnumDefinitionImpl):
    """
    Furniture subcategories. Grounded in Product Types Ontology.
    """
    seating = PermissibleValue(
        text="seating",
        description="Chairs, sofas, armchairs, benches.")
    tables = PermissibleValue(
        text="tables",
        description="Dining tables, coffee tables, desks. dimensions required.")
    beds = PermissibleValue(
        text="beds",
        description="Bed frames and divans. dimensions required.")
    storage_units = PermissibleValue(
        text="storage_units",
        description="Wardrobes, cabinets, chests of drawers.")
    shelving = PermissibleValue(
        text="shelving",
        description="Shelving units, bookcases, wall-mounted shelves.")
    other = PermissibleValue(
        text="other",
        description="Furniture not fitting above subcategories.")

    _defn = EnumDefinition(
        name="FurnitureSubcategoryEnum",
        description="Furniture subcategories. Grounded in Product Types Ontology.",
    )

class FurnitureMaterialEnum(EnumDefinitionImpl):
    """
    Primary furniture construction material. Grounded in schema:material (schema.org property on schema:Product,
    superseding GoodRelations gr:qualitativeProductOrServiceProperty). Valid values per subcategory constrained by
    vm-material-* rules.
    """
    wood = PermissibleValue(
        text="wood",
        description="Solid wood or wood-composite (MDF, plywood, chipboard).")
    metal = PermissibleValue(
        text="metal",
        description="Metal frame (steel, aluminium, iron).")
    plastic = PermissibleValue(
        text="plastic",
        description="Plastic or synthetic polymer primary construction.")
    fabric = PermissibleValue(
        text="fabric",
        description="Upholstered fabric (sofas, chairs). Not valid for tables or beds.")
    glass = PermissibleValue(
        text="glass",
        description="Glass panels or surface (glass-top tables). Not valid for beds.")
    mixed = PermissibleValue(
        text="mixed",
        description="Mixed or composite materials.")

    _defn = EnumDefinition(
        name="FurnitureMaterialEnum",
        description="""Primary furniture construction material. Grounded in schema:material (schema.org property on schema:Product, superseding GoodRelations gr:qualitativeProductOrServiceProperty). Valid values per subcategory constrained by vm-material-* rules.""",
    )

class BeddingMaterialEnum(EnumDefinitionImpl):
    """
    Primary fibre or fabric composition of a bedding or textile item. Records the dominant fibre; use synthetic_blend
    when no single synthetic dominates. Grounded in Product Types Ontology (pto:), aligned with ClothingMaterialEnum's
    natural-fibre values for consistency. Used for allergen filtering, winter-suitability hinting (winter_hint
    annotation per value), and care-requirement matching.
    """
    cotton = PermissibleValue(
        text="cotton",
        description="""Cotton or cotton-dominant. The most common natural fibre for sheets, pillowcases, and towels. All-season versatile; thermal weight varies by thread count and weave.""")
    polyester = PermissibleValue(
        text="polyester",
        description="""Polyester or polyester-dominant synthetic. Common in budget blankets, pillows, and duvet covers. All-season; easy-care.""")
    wool = PermissibleValue(
        text="wool",
        description="""Wool, merino, or wool-dominant blend. Primary signal of winter suitability in blankets and duvets. Fragment compiler may pre-fill is_winter_suitable=true. Allergen signal for wool-sensitive beneficiaries.""")
    linen = PermissibleValue(
        text="linen",
        description="""Linen (flax) fabric. Lightweight and breathable. Typical for summer-weight sheets and tablecloths. Fragment compiler may pre-fill is_winter_suitable=false.""")
    fleece = PermissibleValue(
        text="fleece",
        description="""Polar fleece or other synthetic-pile fabric. Common in lightweight throws and entry-level blankets. Warm for its weight. Fragment compiler may pre-fill is_winter_suitable=true.""")
    down_feather = PermissibleValue(
        text="down_feather",
        description="""Down-filled or feather-filled duvets and pillows. Classic winter-weight fill. Fragment compiler may pre-fill is_winter_suitable=true. Allergen signal for feather/down allergy and asthma sufferers. Requires low-heat tumble drying.""")
    silk = PermissibleValue(
        text="silk",
        description="""Silk. Lightweight and temperature-regulating. Common in premium bedding sets. Requires dry-clean or specialist gentle wash. Fragment compiler may pre-fill is_winter_suitable=false.""")
    microfibre = PermissibleValue(
        text="microfibre",
        description="""Microfibre (ultra-fine synthetic) fabric. Common in microfibre towels, soft sheets, and lightweight blankets. Quick-drying and easy-care.""")
    synthetic_blend = PermissibleValue(
        text="synthetic_blend",
        description="""Mixed synthetic fibres or a synthetic + natural blend where no single fibre dominates. Covers polyester/cotton blends (polycotton), acrylic blends, and other mixed compositions.""")
    other = PermissibleValue(
        text="other",
        description="Materials not covered above. Record the specific material in sorting_notes when known.")

    _defn = EnumDefinition(
        name="BeddingMaterialEnum",
        description="""Primary fibre or fabric composition of a bedding or textile item. Records the dominant fibre; use synthetic_blend when no single synthetic dominates. Grounded in Product Types Ontology (pto:), aligned with ClothingMaterialEnum's natural-fibre values for consistency. Used for allergen filtering, winter-suitability hinting (winter_hint annotation per value), and care-requirement matching.""",
    )

class BeddingAssessmentEnum(EnumDefinitionImpl):
    """
    Structured hygiene and condition assessment for bedding and textiles. Replaces former boolean slots
    has_been_washed and is_mattress_hygienic. Required at sorting regardless of usage.
    """
    clean_unused = PermissibleValue(
        text="clean_unused",
        description="""Clearly unused/new with original packaging intact or no signs of previous use. No hygiene concerns.""")
    clean_washed = PermissibleValue(
        text="clean_washed",
        description="""Previously used but confirmed laundered and clean. No staining, odour, or hygiene concerns. Fully redistributable.""")
    clean_with_visible_staining = PermissibleValue(
        text="clean_with_visible_staining",
        description="""Clean and odour-free but with visible staining. Structurally sound. action: warn — sorting_notes required.""")
    used_not_confirmed_washed = PermissibleValue(
        text="used_not_confirmed_washed",
        description="Used item where laundering cannot be confirmed. action: warn — sorting_notes required.")
    hygiene_concern = PermissibleValue(
        text="hygiene_concern",
        description="""Visible contamination, significant staining, odour, infestation, or other hygiene issue. Redistribution unsafe. action: block, suggest: disposal.""")

    _defn = EnumDefinition(
        name="BeddingAssessmentEnum",
        description="""Structured hygiene and condition assessment for bedding and textiles. Replaces former boolean slots has_been_washed and is_mattress_hygienic. Required at sorting regardless of usage.""",
    )

class BeddingTextilesSubcategoryEnum(EnumDefinitionImpl):
    """
    Bedding and household textiles subcategories. Aligned with COICOP 05.2. is_winter_suitable is meaningful for the
    first five subcategories; suppressed by the fragment compiler for the last three.
    """
    blankets = PermissibleValue(
        text="blankets",
        description="""Blankets, throws, fleece covers. UNHCR NFI core relief item. is_winter_suitable required — a fleece blanket and a cotton throw serve very different needs in cold-weather distribution.""")
    duvets_quilts = PermissibleValue(
        text="duvets_quilts",
        description="""Duvets, quilts, continental quilts. is_winter_suitable required — tog rating (if legible) may be noted in sorting_notes.""")
    pillows = PermissibleValue(
        text="pillows",
        description="Pillows and sleeping cushions.")
    mattresses = PermissibleValue(
        text="mattresses",
        description="""Single, double, children's mattresses. Hygiene UC applies. is_winter_suitable typically not meaningful — suppressed in UI.""")
    sleeping_bags = PermissibleValue(
        text="sleeping_bags",
        description="""Adult and general sleeping bags and camping bedding. UNHCR NFI core relief item. is_winter_suitable required and UC-enforced — a summer sleeping bag in cold-weather emergency distribution is a safety risk. Thermal rating (e.g. \"3-season\", \"-10°C comfort limit\") may be noted in sorting_notes. IMPORTANT: Baby sleeping bags (0-24 months) → BabyInfantItem (subcategory: sleeping_bags). EN 16781:2018 applies — neck and armhole safety assessment required. Do not sort into this category.""")
    bedsheets = PermissibleValue(
        text="bedsheets",
        description="Fitted sheets, flat sheets, pillowcases, duvet covers.")
    towels = PermissibleValue(
        text="towels",
        description="""Bath, hand, face, beach towels. is_winter_suitable not meaningful — suppressed by fragment compiler.""")
    curtains_blinds = PermissibleValue(
        text="curtains_blinds",
        description="""Curtains, net curtains, roller blinds. is_winter_suitable not meaningful at item level — suppressed by fragment compiler.""")
    tablecloths_napkins = PermissibleValue(
        text="tablecloths_napkins",
        description="Tablecloths, placemats, cloth napkins. Seasonal not applicable.")
    other = PermissibleValue(
        text="other",
        description="Household textiles not fitting above subcategories.")

    _defn = EnumDefinition(
        name="BeddingTextilesSubcategoryEnum",
        description="""Bedding and household textiles subcategories. Aligned with COICOP 05.2. is_winter_suitable is meaningful for the first five subcategories; suppressed by the fragment compiler for the last three.""",
    )

class HouseholdMaterialEnum(EnumDefinitionImpl):
    """
    Primary construction material of a household or kitchen item. Records the dominant material; use mixed when none
    dominates. Grounded in Product Types Ontology (pto:), consistent with FurnitureMaterialEnum. Used for allergen
    filtering (nickel, copper) and care-requirement matching (cast iron, copper, wood, non-stick).
    """
    stainless_steel = PermissibleValue(
        text="stainless_steel",
        description="Stainless steel. Most common material for cutlery, pots, pans, kettles, and small appliances.")
    wood = PermissibleValue(
        text="wood",
        description="""Solid wood or wood-composite (including bamboo, which is functionally similar). Common for utensils, chopping boards, salad bowls, and home decor. Requires periodic oiling; not dishwasher-safe.""")
    ceramic = PermissibleValue(
        text="ceramic",
        description="""Ceramic, earthenware, stoneware, or porcelain. Predominant for crockery (plates, bowls, mugs), baking dishes, and decorative items. May include a glazed finish.""")
    glass = PermissibleValue(
        text="glass",
        description="""Glass (borosilicate or soda-lime). Used for drinking glasses, storage jars, glass baking dishes, and glass decor items. Fragility relevant to packaging during storage and distribution.""")
    cast_iron = PermissibleValue(
        text="cast_iron",
        description="""Cast iron cookware (frying pans, casseroles, trivets). Requires seasoning and cannot be soaked or put in the dishwasher. Heavy — relevant for storage slot load-bearing assessment.""")
    copper = PermissibleValue(
        text="copper",
        description="Copper or copper-clad cookware and decor. Requires specialist polishing to prevent tarnishing.")
    aluminium = PermissibleValue(
        text="aluminium",
        description="""Aluminium cookware and baking trays. Lightweight and common in baking trays, roasting pans, and budget cookware.""")
    non_stick = PermissibleValue(
        text="non_stick",
        description="""Non-stick coated cookware (PTFE/Teflon or ceramic-coated pans). Requires specific care: no metal utensils, hand-wash only. Record the base material in sorting_notes when visible (typically aluminium or stainless steel with non-stick coating).""")
    plastic = PermissibleValue(
        text="plastic",
        description="""Plastic (various types). Common for containers, food storage boxes, some appliances, and kitchen organisation items.""")
    silicone = PermissibleValue(
        text="silicone",
        description="""Silicone. Used for baking molds, spatulas, oven gloves, and ice cube trays. Heat-resistant and dishwasher-safe.""")
    mixed = PermissibleValue(
        text="mixed",
        description="""Mixed or composite materials where no single material dominates — e.g. a saucepan with a stainless steel body and plastic handle.""")
    other = PermissibleValue(
        text="other",
        description="Materials not covered above. Record the specific material in sorting_notes when known.")

    _defn = EnumDefinition(
        name="HouseholdMaterialEnum",
        description="""Primary construction material of a household or kitchen item. Records the dominant material; use mixed when none dominates. Grounded in Product Types Ontology (pto:), consistent with FurnitureMaterialEnum. Used for allergen filtering (nickel, copper) and care-requirement matching (cast iron, copper, wood, non-stick).""",
    )

class HouseholdSubcategoryEnum(EnumDefinitionImpl):
    """
    Household and kitchen goods subcategories aligned with COICOP 05.3-05.5. Bedding, towels, and curtains (COICOP
    05.2) belong in BeddingTextilesSubcategoryEnum.
    """
    cookware = PermissibleValue(
        text="cookware",
        description="Pots, pans, baking trays, woks, pressure cookers. COICOP 05.4.")
    crockery = PermissibleValue(
        text="crockery",
        description="Plates, bowls, mugs, cups, serving dishes. COICOP 05.4.")
    cutlery = PermissibleValue(
        text="cutlery",
        description="Knives, forks, spoons, serving utensils. COICOP 05.4.")
    glassware = PermissibleValue(
        text="glassware",
        description="Drinking glasses, jugs, functional glassware. COICOP 05.4.")
    small_appliances = PermissibleValue(
        text="small_appliances",
        description="Toasters, kettles, blenders, microwaves, irons, hairdryers. COICOP 05.3.")
    cleaning = PermissibleValue(
        text="cleaning",
        description="Mops, brushes, buckets, vacuum cleaners, brooms. COICOP 05.6.")
    storage_organisation = PermissibleValue(
        text="storage_organisation",
        description="Storage boxes, baskets, coat hangers, drawer organisers.")
    home_decor = PermissibleValue(
        text="home_decor",
        description="Picture frames, vases, candles, mirrors, clocks, lamps.")
    garden_tools = PermissibleValue(
        text="garden_tools",
        description="Spades, trowels, secateurs, watering cans. COICOP 05.5.")
    other = PermissibleValue(
        text="other",
        description="Household items not fitting above subcategories.")

    _defn = EnumDefinition(
        name="HouseholdSubcategoryEnum",
        description="""Household and kitchen goods subcategories aligned with COICOP 05.3-05.5. Bedding, towels, and curtains (COICOP 05.2) belong in BeddingTextilesSubcategoryEnum.""",
    )

class ElectronicsAssessmentEnum(EnumDefinitionImpl):
    """
    Structured functional and cosmetic assessment for electronic items. Combines functional state with cosmetic
    condition in one vocabulary. Required at sorting regardless of usage — new devices can have defects.
    """
    fully_functional = PermissibleValue(
        text="fully_functional",
        description="""Powers on; all features operate correctly; cosmetic condition good or better. Ready for redistribution. Appropriate for new items with no observed defects.""")
    functional_minor_cosmetic = PermissibleValue(
        text="functional_minor_cosmetic",
        description="""Fully functional but with minor cosmetic issues (light scratches, small scuffs) that do not affect operation. Redistributable.""")
    functional_significant_cosmetic = PermissibleValue(
        text="functional_significant_cosmetic",
        description="""Fully functional but with significant cosmetic damage (cracked bezel, major scratches, missing casing components). Functional but appearance notably affected.""")
    functional_with_issues = PermissibleValue(
        text="functional_with_issues",
        description="""Powers on but has functional issues (cracked screen still displays, missing key, camera not working, port not functioning). Redistributable with explicit description — sorting_notes required.""")
    non_functional = PermissibleValue(
        text="non_functional",
        description="""Does not power on, or major functionality failure rendering it unusable. action: warn — sorting_notes required. Consider repair referral or electronics recycling.""")
    untested = PermissibleValue(
        text="untested",
        description="""Not yet tested. Valid only at received state — blocked at sorted state by lc-sorted-electronics-not-untested rule in donation_item.yaml.""")

    _defn = EnumDefinition(
        name="ElectronicsAssessmentEnum",
        description="""Structured functional and cosmetic assessment for electronic items. Combines functional state with cosmetic condition in one vocabulary. Required at sorting regardless of usage — new devices can have defects.""",
    )

class ElectronicsSubcategoryEnum(EnumDefinitionImpl):
    """
    Electronics subcategories. Grounded in Product Types Ontology.
    """
    smartphones = PermissibleValue(
        text="smartphones",
        description="Mobile phones and smartphones.")
    tablets = PermissibleValue(
        text="tablets",
        description="Tablet computers and e-readers.")
    laptops = PermissibleValue(
        text="laptops",
        description="Laptop and notebook computers.")
    desktop_computers = PermissibleValue(
        text="desktop_computers",
        description="Desktop computers and all-in-ones.")
    monitors = PermissibleValue(
        text="monitors",
        description="Computer monitors and display screens.")
    cameras = PermissibleValue(
        text="cameras",
        description="Digital cameras and camcorders.")
    audio = PermissibleValue(
        text="audio",
        description="Headphones, speakers, radios, MP3 players.")
    cables_chargers = PermissibleValue(
        text="cables_chargers",
        description="USB cables, charging adapters, power banks, extension leads.")
    peripherals = PermissibleValue(
        text="peripherals",
        description="Keyboards, mice, printers, webcams.")
    gaming = PermissibleValue(
        text="gaming",
        description="Gaming consoles, controllers, handheld gaming devices.")
    other = PermissibleValue(
        text="other",
        description="Electronics not fitting above subcategories.")

    _defn = EnumDefinition(
        name="ElectronicsSubcategoryEnum",
        description="Electronics subcategories. Grounded in Product Types Ontology.",
    )

class ToysMaterialEnum(EnumDefinitionImpl):
    """
    Primary construction material of a toy or game item. Operationally relevant under EU Toy Safety Directive
    2009/48/EC Annex II (hazardous substance restrictions) — see per-value descriptions for specific chemical/allergen
    concerns. Grounded in pto:Wood/pto:Rubber where discrete IRIs exist, schema:material as fallback anchor.
    """
    plastic = PermissibleValue(
        text="plastic",
        description="""Plastic (various types — ABS, PP, HDPE, PVC). The most common primary toy material. PVC is of particular concern under the Directive (phthalate restrictions for toys for under-3s). Sorters should note in sorting_notes if item appears to be vintage PVC (typically pre-2005 soft plastic with characteristic flexibility and smell).""")
    wood = PermissibleValue(
        text="wood",
        description="""Solid wood or wood composite. Positive signal for durability and repairability. Common in building blocks, puzzles, pull toys, and wooden vehicles. Supports demand matching for natural-material toy preferences.""")
    fabric_plush = PermissibleValue(
        text="fabric_plush",
        description="""Soft fabric or plush textile. Primary material for stuffed animals, cloth dolls, fabric books, and cloth puzzles. Dust-mite allergen signal — laundering before redistribution is recommended best practice. Check that soft toys do not have small detachable decorative parts (choking hazard for age_0_to_3 — see has_small_parts).""")
    rubber_silicone = PermissibleValue(
        text="rubber_silicone",
        description="""Rubber or silicone. Common in bath toys, teething rings, and some bouncy balls. Natural rubber is a known latex allergen — relevant for teething rings and squeeze toys for very young children (age_0_to_3). Synthetic rubber (TPR, TPE, silicone) is latex-free. Record in sorting_notes if natural rubber is identifiable.""")
    metal = PermissibleValue(
        text="metal",
        description="""Metal (steel, aluminium, tin, die-cast alloy). Common in die-cast model vehicles, metal construction toys, and some board game pieces. Older die-cast toys may contain lead alloys — sorters should note in sorting_notes for visibly very old metal toys.""")
    cardboard_paper = PermissibleValue(
        text="cardboard_paper",
        description="""Cardboard or paper. Primary material for board games, jigsaw puzzles, card games, memory games, and paper craft kits. Condition signal: check for water damage, missing pieces.""")
    foam = PermissibleValue(
        text="foam",
        description="""Foam (EVA, polyurethane, or other foam). Common in foam building blocks, play mats, foam sports toys, and puzzle mats. Check for crumbling or deterioration — degraded foam can produce small particles.""")
    mixed = PermissibleValue(
        text="mixed",
        description="""Mixed or composite materials where no single material dominates — e.g. a board game with a cardboard board, plastic pieces, and paper cards.""")
    other = PermissibleValue(
        text="other",
        description="Materials not covered above. Record the specific material in sorting_notes when known.")

    _defn = EnumDefinition(
        name="ToysMaterialEnum",
        description="""Primary construction material of a toy or game item. Operationally relevant under EU Toy Safety Directive 2009/48/EC Annex II (hazardous substance restrictions) — see per-value descriptions for specific chemical/allergen concerns. Grounded in pto:Wood/pto:Rubber where discrete IRIs exist, schema:material as fallback anchor.""",
    )

class ToysSubcategoryEnum(EnumDefinitionImpl):
    """
    Toys subcategories. Grounded in Product Types Ontology.
    """
    construction = PermissibleValue(
        text="construction",
        description="Building blocks, LEGO-style, construction sets.")
    dolls_figures = PermissibleValue(
        text="dolls_figures",
        description="Dolls, action figures, puppets, plush toys.")
    board_games = PermissibleValue(
        text="board_games",
        description="Board games, card games, dice games.")
    puzzles = PermissibleValue(
        text="puzzles",
        description="Jigsaw puzzles, 3D puzzles, shape sorters.")
    outdoor_toys = PermissibleValue(
        text="outdoor_toys",
        description="Balls, kites, skipping ropes, sandpit toys.")
    ride_on = PermissibleValue(
        text="ride_on",
        description="Tricycles, balance bikes, scooters, ride-on cars.")
    arts_crafts = PermissibleValue(
        text="arts_crafts",
        description="Colouring books, craft kits, modelling clay, paint sets.")
    educational = PermissibleValue(
        text="educational",
        description="Educational games and learning toys.")
    plush = PermissibleValue(
        text="plush",
        description="Soft toys and stuffed animals.")
    other = PermissibleValue(
        text="other",
        description="Toys not fitting above subcategories.")

    _defn = EnumDefinition(
        name="ToysSubcategoryEnum",
        description="Toys subcategories. Grounded in Product Types Ontology.",
    )

class ToyAgeRangeEnum(EnumDefinitionImpl):
    """
    Age suitability for toys. Values aligned with EU Toy Safety Directive 2009/48/EC age-grading categories. The
    age_0_to_3 value is the critical boundary for the small parts choking hazard rule.
    """
    age_0_to_3 = PermissibleValue(
        text="age_0_to_3",
        description="0-3 years. MUST NOT have small parts (EU Toy Safety Directive 2009/48/EC).")
    age_3_to_6 = PermissibleValue(
        text="age_3_to_6",
        description="3-6 years.")
    age_6_to_12 = PermissibleValue(
        text="age_6_to_12",
        description="6-12 years.")
    age_12_plus = PermissibleValue(
        text="age_12_plus",
        description="12 years and above.")
    adult = PermissibleValue(
        text="adult",
        description="Adult games / collector items; not for children.")
    all_ages = PermissibleValue(
        text="all_ages",
        description="Suitable for all ages.")

    _defn = EnumDefinition(
        name="ToyAgeRangeEnum",
        description="""Age suitability for toys. Values aligned with EU Toy Safety Directive 2009/48/EC age-grading categories. The age_0_to_3 value is the critical boundary for the small parts choking hazard rule.""",
    )

class SportsProtectiveAssessmentEnum(EnumDefinitionImpl):
    """
    Structured safety assessment for protective gear (helmets, pads, life jackets, mouth guards). Structural damage
    may not be visually apparent after impact — a helmet that has absorbed an impact is unsafe even if it looks
    undamaged. Required regardless of usage.
    """
    safe_to_redistribute = PermissibleValue(
        text="safe_to_redistribute",
        description="""Visually and physically intact; all components present (straps, buckles, padding); no signs of impact damage; appropriate for redistribution. Appropriate for new items with no observed defects.""")
    safe_cosmetic_wear_only = PermissibleValue(
        text="safe_cosmetic_wear_only",
        description="""Minor cosmetic wear (scratches, scuffs) but structurally sound with no impact damage. Safe to redistribute.""")
    unknown_impact_history = PermissibleValue(
        text="unknown_impact_history",
        description="""No visible damage but impact history cannot be confirmed. action: warn — sorter must confirm; advise recipient that protective certification cannot be guaranteed.""")
    visible_structural_damage = PermissibleValue(
        text="visible_structural_damage",
        description="""Cracks, dents, deformation, or compromised structural components. Must not be redistributed regardless of usage. action: block.""")
    unsafe_do_not_redistribute = PermissibleValue(
        text="unsafe_do_not_redistribute",
        description="""Definitively unsafe: confirmed post-impact, recalled model, expired certification, missing critical safety components. action: block — consider specialist recycling.""")

    _defn = EnumDefinition(
        name="SportsProtectiveAssessmentEnum",
        description="""Structured safety assessment for protective gear (helmets, pads, life jackets, mouth guards). Structural damage may not be visually apparent after impact — a helmet that has absorbed an impact is unsafe even if it looks undamaged. Required regardless of usage.""",
    )

class SportsSubcategoryEnum(EnumDefinitionImpl):
    """
    Sports equipment subcategories. Grounded in Product Types Ontology.
    """
    balls = PermissibleValue(
        text="balls",
        description="Footballs, basketballs, tennis balls, rugby balls.")
    rackets_bats = PermissibleValue(
        text="rackets_bats",
        description="Tennis/badminton rackets, cricket bats, ping-pong bats.")
    protective_gear = PermissibleValue(
        text="protective_gear",
        description="Helmets, shin pads, knee pads, life jackets. Structured assessment required.")
    fitness_equipment = PermissibleValue(
        text="fitness_equipment",
        description="Weights, resistance bands, yoga mats, exercise machines.")
    bicycles = PermissibleValue(
        text="bicycles",
        description="Bicycles and cycling accessories. Domain convention — COICOP 07 (Transport).")
    water_sports = PermissibleValue(
        text="water_sports",
        description="Swimming goggles, snorkels, fins, wetsuits.")
    winter_sports = PermissibleValue(
        text="winter_sports",
        description="Skis, snowboards, ice skates, sleds.")
    camping_outdoor = PermissibleValue(
        text="camping_outdoor",
        description="Tents, sleeping bags, backpacks, hiking poles.")
    other = PermissibleValue(
        text="other",
        description="Sports equipment not fitting above subcategories.")

    _defn = EnumDefinition(
        name="SportsSubcategoryEnum",
        description="Sports equipment subcategories. Grounded in Product Types Ontology.",
    )

class BooksSubcategoryEnum(EnumDefinitionImpl):
    """
    Books and educational materials subcategories.
    """
    fiction = PermissibleValue(
        text="fiction",
        description="Novels, short stories, graphic novels, comics.")
    non_fiction = PermissibleValue(
        text="non_fiction",
        description="Biographies, history, science, self-help, cookbooks.")
    childrens_books = PermissibleValue(
        text="childrens_books",
        description="Picture books, board books, early readers.")
    textbooks = PermissibleValue(
        text="textbooks",
        description="School and university textbooks, reference books.")
    language_learning = PermissibleValue(
        text="language_learning",
        description="Language learning books, dictionaries, phrasebooks.")
    religious = PermissibleValue(
        text="religious",
        description="Religious texts and devotional books.")
    educational_materials = PermissibleValue(
        text="educational_materials",
        description="Workbooks, flashcards, educational posters, school supplies.")
    other = PermissibleValue(
        text="other",
        description="Books and educational materials not fitting above subcategories.")

    _defn = EnumDefinition(
        name="BooksSubcategoryEnum",
        description="Books and educational materials subcategories.",
    )

class BookAgeRangeEnum(EnumDefinitionImpl):
    """
    Age suitability for books. Broader and non-gendered compared to DemographicEnum — content suitability does not
    require gender split.
    """
    children_0_5 = PermissibleValue(
        text="children_0_5",
        description="Picture books, board books, early learning (0-5 years)")
    children_6_12 = PermissibleValue(
        text="children_6_12",
        description="Middle-grade readers, chapter books (6-12 years)")
    young_adult = PermissibleValue(
        text="young_adult",
        description="Young adult (13-17 years)")
    adult = PermissibleValue(
        text="adult",
        description="Adult readership")
    all_ages = PermissibleValue(
        text="all_ages",
        description="Suitable for all ages")

    _defn = EnumDefinition(
        name="BookAgeRangeEnum",
        description="""Age suitability for books. Broader and non-gendered compared to DemographicEnum — content suitability does not require gender split.""",
    )

class StationerySubcategoryEnum(EnumDefinitionImpl):
    """
    Stationery and office supply subcategories.
    """
    pens_pencils = PermissibleValue(
        text="pens_pencils",
        description="Ballpoint pens, pencils, felt-tips, highlighters, markers.")
    writing_sets = PermissibleValue(
        text="writing_sets",
        description="Pencil cases, pen sets, calligraphy sets.")
    notebooks_paper = PermissibleValue(
        text="notebooks_paper",
        description="Notebooks, exercise books, loose-leaf paper, drawing pads.")
    envelopes_cards = PermissibleValue(
        text="envelopes_cards",
        description="Envelopes, postcards, greeting cards.")
    folders_binders = PermissibleValue(
        text="folders_binders",
        description="Ring binders, lever arch files, document wallets.")
    organisers = PermissibleValue(
        text="organisers",
        description="Desk organisers, filing trays, clipboards, planners, diaries.")
    art_supplies = PermissibleValue(
        text="art_supplies",
        description="Paints, brushes, colouring pencils, pastels, canvases.")
    craft_supplies = PermissibleValue(
        text="craft_supplies",
        description="Scissors, glue, tape, staplers, hole punches, rulers.")
    calculators = PermissibleValue(
        text="calculators",
        description="Scientific, graphing, and basic calculators.")
    office_equipment_small = PermissibleValue(
        text="office_equipment_small",
        description="Staplers, hole punches, sharpeners, correction tape.")
    storage_supplies = PermissibleValue(
        text="storage_supplies",
        description="Labels, sticky notes, index cards, dividers.")
    other = PermissibleValue(
        text="other",
        description="Stationery not fitting above subcategories.")

    _defn = EnumDefinition(
        name="StationerySubcategoryEnum",
        description="Stationery and office supply subcategories.",
    )

class PersonalCareSubcategoryEnum(EnumDefinitionImpl):
    """
    Personal care, hygiene, and health product subcategories. Covers COICOP 06.1 (medical products) and 12.1 (personal
    care).
    """
    soap_body_wash = PermissibleValue(
        text="soap_body_wash",
        description="""Bar soap, liquid soap, body wash, hand sanitiser. Must be sealed. (Baby wash → BabyInfantItem, see baby_care subcategory.)""")
    shampoo_conditioner = PermissibleValue(
        text="shampoo_conditioner",
        description="""Shampoo, conditioner, dry shampoo. Must be sealed. (Baby shampoo → BabyInfantItem, see baby_care subcategory.)""")
    dental = PermissibleValue(
        text="dental",
        description="Toothpaste, mouthwash, dental floss. Must be sealed. (Toothbrushes → personal_care_tools).")
    deodorant = PermissibleValue(
        text="deodorant",
        description="Deodorant and antiperspirant. Must be sealed.")
    sanitary_products = PermissibleValue(
        text="sanitary_products",
        description="Menstrual pads, tampons, menstrual cups. Must be sealed.")
    incontinence_products = PermissibleValue(
        text="incontinence_products",
        description="""Adult incontinence pads, pull-ups, bed pads. Must be sealed. (Baby nappies → BabyInfantItem, see nappies subcategory.)""")
    toilet_paper_tissue = PermissibleValue(
        text="toilet_paper_tissue",
        description="Toilet paper, facial tissue. Must be sealed/wrapped.")
    personal_care_tools = PermissibleValue(
        text="personal_care_tools",
        description="Toothbrushes, razors, nail clippers, tweezers, combs. UC block: used → never redistribute.")
    skincare = PermissibleValue(
        text="skincare",
        description="""Moisturisers, sunscreen, face wash, lip balm. Must be sealed. (Baby lotion/oil/powder/rash cream/sunscreen → BabyInfantItem, see baby_care subcategory.)""")
    cosmetics = PermissibleValue(
        text="cosmetics",
        description="Foundation, lipstick, mascara, nail polish. Must be sealed/unused.")
    hair_styling = PermissibleValue(
        text="hair_styling",
        description="Hair gel, mousse, hairspray, hair dye. Must be sealed.")
    otc_medication = PermissibleValue(
        text="otc_medication",
        description="""OTC pain relief, vitamins, cold medicine. Sealed + expiry enforced. NO prescription medications.""")
    first_aid = PermissibleValue(
        text="first_aid",
        description="First aid kits, plasters, antiseptic, sterile dressings. Sealed required.")
    medical_consumables = PermissibleValue(
        text="medical_consumables",
        description="Disposable gloves, masks, syringes (sealed). Sealed + expiry.")
    medical_devices_small = PermissibleValue(
        text="medical_devices_small",
        description="Thermometers, blood pressure monitors, reading glasses. Not durable aids (→ MobilityAidsItem).")
    other = PermissibleValue(
        text="other",
        description="Personal care products not fitting above subcategories.")

    _defn = EnumDefinition(
        name="PersonalCareSubcategoryEnum",
        description="""Personal care, hygiene, and health product subcategories. Covers COICOP 06.1 (medical products) and 12.1 (personal care).""",
    )

class MobilityAssessmentEnum(EnumDefinitionImpl):
    """
    Structured safety and hygiene assessment for mobility aids and assistive devices, covering structural soundness,
    functional state, and body-contact hygiene in one vocabulary. Required at sorting regardless of usage.
    """
    safe_to_redistribute = PermissibleValue(
        text="safe_to_redistribute",
        description="""Structurally sound, fully functional (if powered), and clean. No hygiene concerns for body-contact items. Ready for redistribution. Appropriate for new items with no observed defects.""")
    safe_cosmetic_wear_only = PermissibleValue(
        text="safe_cosmetic_wear_only",
        description="Minor cosmetic wear but structurally sound and fully functional. Safe to redistribute.")
    safe_after_cleaning = PermissibleValue(
        text="safe_after_cleaning",
        description="""Body-contact item (hearing aid, orthotic) that is structurally sound but requires professional cleaning before redistribution. action: warn — sorting_notes required.""")
    non_functional = PermissibleValue(
        text="non_functional",
        description="""Powered device does not operate as expected. Consider repair referral. action: warn — sorting_notes required.""")
    structurally_compromised = PermissibleValue(
        text="structurally_compromised",
        description="""Load-bearing or structural components unsafe. Applies regardless of usage. action: block, suggest: disposal or specialist repair referral.""")
    specialist_referral_required = PermissibleValue(
        text="specialist_referral_required",
        description="""Cannot be assessed by a general sorter — specialist evaluation required (prosthetics, complex orthotics, specialised communication devices). action: block from normal redistribution; flag for specialist organisation.""")

    _defn = EnumDefinition(
        name="MobilityAssessmentEnum",
        description="""Structured safety and hygiene assessment for mobility aids and assistive devices, covering structural soundness, functional state, and body-contact hygiene in one vocabulary. Required at sorting regardless of usage.""",
    )

class MobilityAidsSubcategoryEnum(EnumDefinitionImpl):
    """
    Mobility aids and assistive devices subcategories. Grounded in Product Types Ontology and Open Eligibility
    taxonomy.
    """
    wheelchairs = PermissibleValue(
        text="wheelchairs",
        description="Manual and powered wheelchairs. Structural + functional assessment required.")
    crutches = PermissibleValue(
        text="crutches",
        description="Axillary and forearm crutches, walking sticks. Structural assessment.")
    walking_frames = PermissibleValue(
        text="walking_frames",
        description="Walking frames, Zimmer frames, wheeled walkers, rollators.")
    mobility_scooters = PermissibleValue(
        text="mobility_scooters",
        description="Electric mobility scooters. Full functional + structural assessment.")
    hearing_aids = PermissibleValue(
        text="hearing_aids",
        description="In-ear and behind-ear hearing aids. Body-contact — safe_after_cleaning minimum.")
    visual_aids = PermissibleValue(
        text="visual_aids",
        description="Reading glasses (non-prescription), magnifiers, white canes.")
    orthotics = PermissibleValue(
        text="orthotics",
        description="Splints, braces, supports. Body-contact assessment applies.")
    prosthetics = PermissibleValue(
        text="prosthetics",
        description="Prosthetic limbs. Specialist referral required.")
    daily_living_aids = PermissibleValue(
        text="daily_living_aids",
        description="Grab rails, bath seats, reachers, adapted cutlery.")
    communication_devices = PermissibleValue(
        text="communication_devices",
        description="AAC devices, talking clocks, large-button phones. Functional assessment required.")
    other = PermissibleValue(
        text="other",
        description="Mobility aids and assistive devices not fitting above subcategories.")

    _defn = EnumDefinition(
        name="MobilityAidsSubcategoryEnum",
        description="""Mobility aids and assistive devices subcategories. Grounded in Product Types Ontology and Open Eligibility taxonomy.""",
    )

class BabyEquipmentAssessmentEnum(EnumDefinitionImpl):
    """
    Structured safety assessment for safety-critical baby equipment (pushchairs, cots, car seats, carriers, high
    chairs). Required at sorting regardless of usage.
    Car seats (EN 14344): collision history can't be verified visually — over 10 years old or unknown history must
    receive do_not_redistribute; manufacture_year is required to enable the age check. Cots (EN 716): drop-side cots
    are EU-banned, always do_not_redistribute. Baby sleeping bags (EN 16781): verify neck/armhole opening safety, no
    loose cords/ties, no detachable decorative parts; is_winter_suitable must also be set.
    """
    safe_to_redistribute = PermissibleValue(
        text="safe_to_redistribute",
        description="""Structurally sound; all components present; manufacture date within acceptable range; no safety concerns. Ready for redistribution. Appropriate for new items with no observed defects.""")
    safe_minor_wear = PermissibleValue(
        text="safe_minor_wear",
        description="""Minor cosmetic wear but structurally sound and all safety-relevant components intact. Safe to redistribute.""")
    requires_specialist_check = PermissibleValue(
        text="requires_specialist_check",
        description="""Appears functional but sorter cannot fully verify safety (unknown locking mechanism, unfamiliar harness system, unclear provenance). action: warn — redistribution only after specialist confirmation.""")
    structural_concern = PermissibleValue(
        text="structural_concern",
        description="""Visible structural damage, cracked components, bent frame, broken harness buckle. Applies to new (manufacturing defect) and used items. action: block.""")
    do_not_redistribute = PermissibleValue(
        text="do_not_redistribute",
        description="""Must not be redistributed: car seat over 10 years old or confirmed post-collision (EN 14344), EU-banned dropside cot (EN 716), recalled model, missing critical safety components. action: block.""")

    _defn = EnumDefinition(
        name="BabyEquipmentAssessmentEnum",
        description="""Structured safety assessment for safety-critical baby equipment (pushchairs, cots, car seats, carriers, high chairs). Required at sorting regardless of usage.
Car seats (EN 14344): collision history can't be verified visually — over 10 years old or unknown history must receive do_not_redistribute; manufacture_year is required to enable the age check. Cots (EN 716): drop-side cots are EU-banned, always do_not_redistribute. Baby sleeping bags (EN 16781): verify neck/armhole opening safety, no loose cords/ties, no detachable decorative parts; is_winter_suitable must also be set.""",
    )

class BabyInfantSubcategoryEnum(EnumDefinitionImpl):
    """
    Baby and infant supplies subcategories. Grounded in Product Types Ontology. Baby clothing belongs in ClothingItem
    (demographic=baby).
    """
    pushchairs_prams = PermissibleValue(
        text="pushchairs_prams",
        description="Pushchairs, prams, strollers. Structural assessment required (EN 1888).")
    car_seats = PermissibleValue(
        text="car_seats",
        description="Car and booster seats. Assessment + manufacture_year required (EN 14344).")
    cots_cribs = PermissibleValue(
        text="cots_cribs",
        description="Cots, cribs, moses baskets. Structural assessment required (EN 716). Dropside cots banned.")
    baby_carriers = PermissibleValue(
        text="baby_carriers",
        description="Baby slings, carriers, wraps. Structural assessment required.")
    infant_formula = PermissibleValue(
        text="infant_formula",
        description="Infant formula. Must be sealed + within expiry. UNHCR NFI core item.")
    feeding_bottles_teats = PermissibleValue(
        text="feeding_bottles_teats",
        description="Feeding bottles and teats. Must be sealed + unused (EN 14350).")
    nappies = PermissibleValue(
        text="nappies",
        description="Baby nappies/diapers. Must be sealed. UNHCR NFI core item. nappy_size required.")
    baby_care = PermissibleValue(
        text="baby_care",
        description="""Baby wipes, powder, lotion, oil, wash, shampoo, diaper rash cream, teething gel, baby sunscreen. Must be sealed. (Adult-equivalent toiletries → PersonalCareItem.)""")
    breastfeeding = PermissibleValue(
        text="breastfeeding",
        description="Breast pumps, nursing pads, sterilisers.")
    bath_equipment = PermissibleValue(
        text="bath_equipment",
        description="Baby baths, bath seats, bath thermometers.")
    changing = PermissibleValue(
        text="changing",
        description="Changing mats, nappy bags, changing bags.")
    baby_monitors = PermissibleValue(
        text="baby_monitors",
        description="Audio and video baby monitors.")
    bouncers_swings = PermissibleValue(
        text="bouncers_swings",
        description="Baby bouncers, swings, rockers, play gyms.")
    sleeping_bags = PermissibleValue(
        text="sleeping_bags",
        description="""Baby sleeping bags for home use (0-24 months). Track 1 — structured safety assessment required per EN 16781:2018. Sorter must verify:
  - Neck opening size appropriate (infant cannot slip inside)
  - Armhole openings present and correctly sized
  - No loose cords, drawstrings, or ribbon ties (strangulation hazard)
  - No small decorative parts that could detach (choking hazard)
is_winter_suitable required — thermal weight varies widely from 0.5 tog (summer) to 3.5 tog (winter). Tog or comfort temperature rating is typically printed on the label. Adult and camping sleeping bags → BeddingTextilesItem.""")
    other = PermissibleValue(
        text="other",
        description="Baby and infant supplies not fitting above subcategories.")

    _defn = EnumDefinition(
        name="BabyInfantSubcategoryEnum",
        description="""Baby and infant supplies subcategories. Grounded in Product Types Ontology. Baby clothing belongs in ClothingItem (demographic=baby).""",
    )

class NappySizeEnum(EnumDefinitionImpl):
    """
    Weight-banded nappy sizing, matching how nappies are sized and labeled by manufacturers. Distinct from
    ClothingSizeEnum's age-banded baby sizes, since nappy fit tracks infant weight rather than age. Bands are
    approximate and vary slightly by brand — the weight range printed on the pack is authoritative; sorters should
    match to the closest band.
    """
    newborn = PermissibleValue(
        text="newborn",
        description="Newborn, up to ~4kg.")
    size_1 = PermissibleValue(
        text="size_1",
        description="Size 1, ~2-5kg.")
    size_2 = PermissibleValue(
        text="size_2",
        description="Size 2, ~3-6kg.")
    size_3 = PermissibleValue(
        text="size_3",
        description="Size 3, ~4-9kg.")
    size_4 = PermissibleValue(
        text="size_4",
        description="Size 4, ~7-18kg.")
    size_5 = PermissibleValue(
        text="size_5",
        description="Size 5, ~11-25kg.")
    size_6 = PermissibleValue(
        text="size_6",
        description="Size 6, ~16kg and up.")
    other = PermissibleValue(
        text="other",
        description="Size not fitting the standard bands, or unlabeled/unknown.")

    _defn = EnumDefinition(
        name="NappySizeEnum",
        description="""Weight-banded nappy sizing, matching how nappies are sized and labeled by manufacturers. Distinct from ClothingSizeEnum's age-banded baby sizes, since nappy fit tracks infant weight rather than age. Bands are approximate and vary slightly by brand — the weight range printed on the pack is authoritative; sorters should match to the closest band.""",
    )

class FoodTypeEnum(EnumDefinitionImpl):
    """
    Primary food type classification. Grounded in FoodOn ontology (OBO Foundry). Each value maps to valid
    storage_requirement values via vm-storage-* rules.
    """
    bread_bakery = PermissibleValue(
        text="bread_bakery",
        description="Bread, rolls, pastries, cakes, and other baked goods. Storage: ambient or frozen.")
    fruit_vegetables = PermissibleValue(
        text="fruit_vegetables",
        description="""Fresh fruit, vegetables, and herbs. Perishable — packaging_intact rule applies. May be stored ambient, refrigerated, or frozen.""")
    meat_fish = PermissibleValue(
        text="meat_fish",
        description="""Fresh or frozen meat, poultry, sausage, fish, and seafood. Perishable — packaging_intact rule applies. Requires refrigerated or frozen storage.""")
    dairy_eggs = PermissibleValue(
        text="dairy_eggs",
        description="Milk, cheese, yoghurt, and eggs. Perishable — requires refrigeration or freezing.")
    dry_goods = PermissibleValue(
        text="dry_goods",
        description="Non-perishable dry staples: pasta, rice, flour, cereals, pulses. Storage: ambient or dry_cool.")
    canned_goods = PermissibleValue(
        text="canned_goods",
        description="Factory-sealed tins and cans. Shelf-stable at ambient temperature. Storage: ambient only.")
    beverages = PermissibleValue(
        text="beverages",
        description="Bottled or packaged drinks (non-alcoholic).")
    snacks_confectionery = PermissibleValue(
        text="snacks_confectionery",
        description="""Sweet snacks (chocolate, sweets, candy, desserts) and savory snacks (crisps/chips, pretzels, popcorn, savory crackers, salted nuts). Merged into one bucket following DACH retail/food-bank sorting practice, where sweet and savory snacks share one shelf (\"Süß & Salzig\"). Storage: ambient.""")
    ready_meals = PermissibleValue(
        text="ready_meals",
        description="Prepared meals — ambient (shelf-stable), refrigerated, or frozen.")
    baby_food = PermissibleValue(
        text="baby_food",
        description="""Commercially prepared solid baby food (purées, jars, pouches). Perishable once opened — packaging_intact rule applies. Note: infant formula belongs in BabyInfantItem (subcategory=infant_formula), not here; this value covers baby food donated as part of a food collection.""")
    condiments = PermissibleValue(
        text="condiments",
        description="Sauces, spreads, oils, vinegars, and seasoning products.")
    other = PermissibleValue(
        text="other",
        description="Food items not fitting above categories.")

    _defn = EnumDefinition(
        name="FoodTypeEnum",
        description="""Primary food type classification. Grounded in FoodOn ontology (OBO Foundry). Each value maps to valid storage_requirement values via vm-storage-* rules.""",
    )

class StorageRequirementEnum(EnumDefinitionImpl):
    """
    Required storage condition for a food item. Valid values per subcategory are constrained by vm-storage-* rules in
    FoodCategory.
    """
    ambient = PermissibleValue(
        text="ambient",
        description="Room temperature (15-25°C), dry conditions. Standard pantry/warehouse shelf.")
    refrigerated = PermissibleValue(
        text="refrigerated",
        description="Refrigerated storage (0-4°C).")
    frozen = PermissibleValue(
        text="frozen",
        description="Frozen storage (-18°C or below).")
    dry_cool = PermissibleValue(
        text="dry_cool",
        description="Cool, dry conditions (8-15°C) — root vegetable or wine-cellar type.")

    _defn = EnumDefinition(
        name="StorageRequirementEnum",
        description="""Required storage condition for a food item. Valid values per subcategory are constrained by vm-storage-* rules in FoodCategory.""",
    )

class DeviceTypeEnum(EnumDefinitionImpl):
    """
    Device type used to complete a process step.
    """
    mobile = PermissibleValue(
        text="mobile",
        description="Mobile phone or tablet.")
    desktop = PermissibleValue(
        text="desktop",
        description="Desktop or laptop browser.")
    scan = PermissibleValue(
        text="scan",
        description="Barcode / QR scanner peripheral.")

    _defn = EnumDefinition(
        name="DeviceTypeEnum",
        description="Device type used to complete a process step.",
    )

# Slots
class slots:
    pass

slots.id = Slot(uri=SCHEMA.identifier, name="id", curie=SCHEMA.curie('identifier'),
                   model_uri=INKIND_KNOWLEDGE_REPO.id, domain=None, range=URIRef)

slots.name = Slot(uri=SCHEMA.name, name="name", curie=SCHEMA.curie('name'),
                   model_uri=INKIND_KNOWLEDGE_REPO.name, domain=None, range=Optional[str])

slots.description = Slot(uri=SCHEMA.description, name="description", curie=SCHEMA.curie('description'),
                   model_uri=INKIND_KNOWLEDGE_REPO.description, domain=None, range=Optional[str])

slots.label = Slot(uri=INKIND_KNOWLEDGE_REPO.label, name="label", curie=INKIND_KNOWLEDGE_REPO.curie('label'),
                   model_uri=INKIND_KNOWLEDGE_REPO.label, domain=None, range=str)

slots.org = Slot(uri=INKIND_KNOWLEDGE_REPO.org, name="org", curie=INKIND_KNOWLEDGE_REPO.curie('org'),
                   model_uri=INKIND_KNOWLEDGE_REPO.org, domain=None, range=str)

slots.lifecycle_state = Slot(uri=INKIND_KNOWLEDGE_REPO.lifecycle_state, name="lifecycle_state", curie=INKIND_KNOWLEDGE_REPO.curie('lifecycle_state'),
                   model_uri=INKIND_KNOWLEDGE_REPO.lifecycle_state, domain=None, range=str)

slots.created_at = Slot(uri=INKIND_KNOWLEDGE_REPO.created_at, name="created_at", curie=INKIND_KNOWLEDGE_REPO.curie('created_at'),
                   model_uri=INKIND_KNOWLEDGE_REPO.created_at, domain=None, range=Union[str, XSDDateTime])

slots.updated_at = Slot(uri=INKIND_KNOWLEDGE_REPO.updated_at, name="updated_at", curie=INKIND_KNOWLEDGE_REPO.curie('updated_at'),
                   model_uri=INKIND_KNOWLEDGE_REPO.updated_at, domain=None, range=Union[str, XSDDateTime])

slots.donation_source = Slot(uri=INKIND_KNOWLEDGE_REPO.donation_source, name="donation_source", curie=INKIND_KNOWLEDGE_REPO.curie('donation_source'),
                   model_uri=INKIND_KNOWLEDGE_REPO.donation_source, domain=None, range=Optional[str])

slots.is_active = Slot(uri=INKIND_KNOWLEDGE_REPO.is_active, name="is_active", curie=INKIND_KNOWLEDGE_REPO.curie('is_active'),
                   model_uri=INKIND_KNOWLEDGE_REPO.is_active, domain=None, range=Union[bool, Bool])

slots.parent = Slot(uri=INKIND_KNOWLEDGE_REPO.parent, name="parent", curie=INKIND_KNOWLEDGE_REPO.curie('parent'),
                   model_uri=INKIND_KNOWLEDGE_REPO.parent, domain=None, range=Optional[str])

slots.category = Slot(uri=SCHEMA.additionalType, name="category", curie=SCHEMA.curie('additionalType'),
                   model_uri=INKIND_KNOWLEDGE_REPO.category, domain=None, range=Union[str, "BaseCategoryEnum"])

slots.notes = Slot(uri=INKIND_KNOWLEDGE_REPO.notes, name="notes", curie=INKIND_KNOWLEDGE_REPO.curie('notes'),
                   model_uri=INKIND_KNOWLEDGE_REPO.notes, domain=None, range=Optional[str])

slots.sorting_notes = Slot(uri=INKIND_KNOWLEDGE_REPO.sorting_notes, name="sorting_notes", curie=INKIND_KNOWLEDGE_REPO.curie('sorting_notes'),
                   model_uri=INKIND_KNOWLEDGE_REPO.sorting_notes, domain=None, range=Optional[str])

slots.item_description = Slot(uri=INKIND_KNOWLEDGE_REPO.item_description, name="item_description", curie=INKIND_KNOWLEDGE_REPO.curie('item_description'),
                   model_uri=INKIND_KNOWLEDGE_REPO.item_description, domain=None, range=Optional[str])

slots.material = Slot(uri=INKIND_KNOWLEDGE_REPO.material, name="material", curie=INKIND_KNOWLEDGE_REPO.curie('material'),
                   model_uri=INKIND_KNOWLEDGE_REPO.material, domain=None, range=Optional[str])

slots.net_content_value = Slot(uri=INKIND_KNOWLEDGE_REPO.net_content_value, name="net_content_value", curie=INKIND_KNOWLEDGE_REPO.curie('net_content_value'),
                   model_uri=INKIND_KNOWLEDGE_REPO.net_content_value, domain=None, range=Optional[Decimal])

slots.net_content_unit = Slot(uri=INKIND_KNOWLEDGE_REPO.net_content_unit, name="net_content_unit", curie=INKIND_KNOWLEDGE_REPO.curie('net_content_unit'),
                   model_uri=INKIND_KNOWLEDGE_REPO.net_content_unit, domain=None, range=Optional[Union[str, "NetContentUnitEnum"]])

slots.subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.subcategory, name="subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.subcategory, domain=None, range=Optional[str])

slots.usage = Slot(uri=SCHEMA.itemCondition, name="usage", curie=SCHEMA.curie('itemCondition'),
                   model_uri=INKIND_KNOWLEDGE_REPO.usage, domain=None, range=Union[str, "ItemUsageEnum"])

slots.condition_grade = Slot(uri=INKIND_KNOWLEDGE_REPO.condition_grade, name="condition_grade", curie=INKIND_KNOWLEDGE_REPO.curie('condition_grade'),
                   model_uri=INKIND_KNOWLEDGE_REPO.condition_grade, domain=None, range=Optional[Union[str, "UsedConditionGradeEnum"]])

slots.assessment_result = Slot(uri=INKIND_KNOWLEDGE_REPO.assessment_result, name="assessment_result", curie=INKIND_KNOWLEDGE_REPO.curie('assessment_result'),
                   model_uri=INKIND_KNOWLEDGE_REPO.assessment_result, domain=None, range=Optional[str])

slots.attribute_completeness = Slot(uri=INKIND_KNOWLEDGE_REPO.attribute_completeness, name="attribute_completeness", curie=INKIND_KNOWLEDGE_REPO.curie('attribute_completeness'),
                   model_uri=INKIND_KNOWLEDGE_REPO.attribute_completeness, domain=None, range=Optional[Union[str, "AttributeCompletenessEnum"]])

slots.geo_point = Slot(uri=INKIND_KNOWLEDGE_REPO.geo_point, name="geo_point", curie=INKIND_KNOWLEDGE_REPO.curie('geo_point'),
                   model_uri=INKIND_KNOWLEDGE_REPO.geo_point, domain=None, range=Optional[Union[dict, GeoPoint]])

slots.config = Slot(uri=INKIND_KNOWLEDGE_REPO.config, name="config", curie=INKIND_KNOWLEDGE_REPO.curie('config'),
                   model_uri=INKIND_KNOWLEDGE_REPO.config, domain=None, range=Optional[Union[dict, OrgConfig]])

slots.role = Slot(uri=INKIND_KNOWLEDGE_REPO.role, name="role", curie=INKIND_KNOWLEDGE_REPO.curie('role'),
                   model_uri=INKIND_KNOWLEDGE_REPO.role, domain=None, range=Union[str, "ActorRoleEnum"])

slots.experience_level = Slot(uri=INKIND_KNOWLEDGE_REPO.experience_level, name="experience_level", curie=INKIND_KNOWLEDGE_REPO.curie('experience_level'),
                   model_uri=INKIND_KNOWLEDGE_REPO.experience_level, domain=None, range=Optional[Union[str, "ExperienceLevelEnum"]])

slots.capacity = Slot(uri=INKIND_KNOWLEDGE_REPO.capacity, name="capacity", curie=INKIND_KNOWLEDGE_REPO.curie('capacity'),
                   model_uri=INKIND_KNOWLEDGE_REPO.capacity, domain=None, range=Optional[int])

slots.current_occupancy = Slot(uri=INKIND_KNOWLEDGE_REPO.current_occupancy, name="current_occupancy", curie=INKIND_KNOWLEDGE_REPO.curie('current_occupancy'),
                   model_uri=INKIND_KNOWLEDGE_REPO.current_occupancy, domain=None, range=int)

slots.category_affinity = Slot(uri=INKIND_KNOWLEDGE_REPO.category_affinity, name="category_affinity", curie=INKIND_KNOWLEDGE_REPO.curie('category_affinity'),
                   model_uri=INKIND_KNOWLEDGE_REPO.category_affinity, domain=None, range=Optional[Union[str, "BaseCategoryEnum"]])

slots.source_type = Slot(uri=INKIND_KNOWLEDGE_REPO.source_type, name="source_type", curie=INKIND_KNOWLEDGE_REPO.curie('source_type'),
                   model_uri=INKIND_KNOWLEDGE_REPO.source_type, domain=None, range=Union[str, "DonationSourceTypeEnum"])

slots.anonymous_donor_id = Slot(uri=INKIND_KNOWLEDGE_REPO.anonymous_donor_id, name="anonymous_donor_id", curie=INKIND_KNOWLEDGE_REPO.curie('anonymous_donor_id'),
                   model_uri=INKIND_KNOWLEDGE_REPO.anonymous_donor_id, domain=None, range=Optional[Union[str, URIorCURIE]])

slots.corporate_donor_ref = Slot(uri=INKIND_KNOWLEDGE_REPO.corporate_donor_ref, name="corporate_donor_ref", curie=INKIND_KNOWLEDGE_REPO.curie('corporate_donor_ref'),
                   model_uri=INKIND_KNOWLEDGE_REPO.corporate_donor_ref, domain=None, range=Optional[str])

slots.organisation_ref = Slot(uri=INKIND_KNOWLEDGE_REPO.organisation_ref, name="organisation_ref", curie=INKIND_KNOWLEDGE_REPO.curie('organisation_ref'),
                   model_uri=INKIND_KNOWLEDGE_REPO.organisation_ref, domain=None, range=Optional[Union[str, SocialOrganisationId]])

slots.provenance = Slot(uri=INKIND_KNOWLEDGE_REPO.provenance, name="provenance", curie=INKIND_KNOWLEDGE_REPO.curie('provenance'),
                   model_uri=INKIND_KNOWLEDGE_REPO.provenance, domain=None, range=Optional[Union[str, ProvenanceRecordId]])

slots.collection_type = Slot(uri=INKIND_KNOWLEDGE_REPO.collection_type, name="collection_type", curie=INKIND_KNOWLEDGE_REPO.curie('collection_type'),
                   model_uri=INKIND_KNOWLEDGE_REPO.collection_type, domain=None, range=Union[str, "CollectionTypeEnum"])

slots.item_count = Slot(uri=INKIND_KNOWLEDGE_REPO.item_count, name="item_count", curie=INKIND_KNOWLEDGE_REPO.curie('item_count'),
                   model_uri=INKIND_KNOWLEDGE_REPO.item_count, domain=None, range=int)

slots.total_item_count = Slot(uri=INKIND_KNOWLEDGE_REPO.total_item_count, name="total_item_count", curie=INKIND_KNOWLEDGE_REPO.curie('total_item_count'),
                   model_uri=INKIND_KNOWLEDGE_REPO.total_item_count, domain=None, range=int)

slots.created_by = Slot(uri=INKIND_KNOWLEDGE_REPO.created_by, name="created_by", curie=INKIND_KNOWLEDGE_REPO.curie('created_by'),
                   model_uri=INKIND_KNOWLEDGE_REPO.created_by, domain=None, range=Union[str, ActorId])

slots.source_collection = Slot(uri=INKIND_KNOWLEDGE_REPO.source_collection, name="source_collection", curie=INKIND_KNOWLEDGE_REPO.curie('source_collection'),
                   model_uri=INKIND_KNOWLEDGE_REPO.source_collection, domain=None, range=Optional[Union[str, DonationCollectionId]])

slots.storage_unit = Slot(uri=INKIND_KNOWLEDGE_REPO.storage_unit, name="storage_unit", curie=INKIND_KNOWLEDGE_REPO.curie('storage_unit'),
                   model_uri=INKIND_KNOWLEDGE_REPO.storage_unit, domain=None, range=Optional[Union[str, StorageLocationId]])

slots.signal_type = Slot(uri=INKIND_KNOWLEDGE_REPO.signal_type, name="signal_type", curie=INKIND_KNOWLEDGE_REPO.curie('signal_type'),
                   model_uri=INKIND_KNOWLEDGE_REPO.signal_type, domain=None, range=Union[str, "DemandSignalTypeEnum"])

slots.urgency_tier = Slot(uri=INKIND_KNOWLEDGE_REPO.urgency_tier, name="urgency_tier", curie=INKIND_KNOWLEDGE_REPO.curie('urgency_tier'),
                   model_uri=INKIND_KNOWLEDGE_REPO.urgency_tier, domain=None, range=Optional[Union[str, "UrgencyTierEnum"]])

slots.household_situation = Slot(uri=INKIND_KNOWLEDGE_REPO.household_situation, name="household_situation", curie=INKIND_KNOWLEDGE_REPO.curie('household_situation'),
                   model_uri=INKIND_KNOWLEDGE_REPO.household_situation, domain=None, range=Optional[Union[str, "HouseholdSituationEnum"]])

slots.title = Slot(uri=INKIND_KNOWLEDGE_REPO.title, name="title", curie=INKIND_KNOWLEDGE_REPO.curie('title'),
                   model_uri=INKIND_KNOWLEDGE_REPO.title, domain=None, range=str)

slots.starts_at = Slot(uri=SCHEMA.startDate, name="starts_at", curie=SCHEMA.curie('startDate'),
                   model_uri=INKIND_KNOWLEDGE_REPO.starts_at, domain=None, range=Union[str, XSDDateTime])

slots.ends_at = Slot(uri=SCHEMA.endDate, name="ends_at", curie=SCHEMA.curie('endDate'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ends_at, domain=None, range=Union[str, XSDDateTime])

slots.target_beneficiary_group = Slot(uri=INKIND_KNOWLEDGE_REPO.target_beneficiary_group, name="target_beneficiary_group", curie=INKIND_KNOWLEDGE_REPO.curie('target_beneficiary_group'),
                   model_uri=INKIND_KNOWLEDGE_REPO.target_beneficiary_group, domain=None, range=Optional[str])

slots.signals = Slot(uri=INKIND_KNOWLEDGE_REPO.signals, name="signals", curie=INKIND_KNOWLEDGE_REPO.curie('signals'),
                   model_uri=INKIND_KNOWLEDGE_REPO.signals, domain=None, range=Optional[Union[Union[str, DemandSignalId], list[Union[str, DemandSignalId]]]])

slots.demographic = Slot(uri=INKIND_KNOWLEDGE_REPO.demographic, name="demographic", curie=INKIND_KNOWLEDGE_REPO.curie('demographic'),
                   model_uri=INKIND_KNOWLEDGE_REPO.demographic, domain=None, range=Optional[Union[str, "DemographicEnum"]])

slots.is_set_complete = Slot(uri=INKIND_KNOWLEDGE_REPO.is_set_complete, name="is_set_complete", curie=INKIND_KNOWLEDGE_REPO.curie('is_set_complete'),
                   model_uri=INKIND_KNOWLEDGE_REPO.is_set_complete, domain=None, range=Optional[Union[bool, Bool]])

slots.age_range = Slot(uri=INKIND_KNOWLEDGE_REPO.age_range, name="age_range", curie=INKIND_KNOWLEDGE_REPO.curie('age_range'),
                   model_uri=INKIND_KNOWLEDGE_REPO.age_range, domain=None, range=Optional[str])

slots.expiry_date = Slot(uri=INKIND_KNOWLEDGE_REPO.expiry_date, name="expiry_date", curie=INKIND_KNOWLEDGE_REPO.curie('expiry_date'),
                   model_uri=INKIND_KNOWLEDGE_REPO.expiry_date, domain=None, range=Optional[Union[str, XSDDate]])

slots.is_sealed = Slot(uri=INKIND_KNOWLEDGE_REPO.is_sealed, name="is_sealed", curie=INKIND_KNOWLEDGE_REPO.curie('is_sealed'),
                   model_uri=INKIND_KNOWLEDGE_REPO.is_sealed, domain=None, range=Optional[Union[bool, Bool]])

slots.tops_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.tops_subcategory, name="tops_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('tops_subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.tops_subcategory, domain=None, range=Optional[Union[str, "TopsSubcategoryEnum"]])

slots.bottoms_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.bottoms_subcategory, name="bottoms_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('bottoms_subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.bottoms_subcategory, domain=None, range=Optional[Union[str, "BottomsSubcategoryEnum"]])

slots.size = Slot(uri=INKIND_KNOWLEDGE_REPO.size, name="size", curie=INKIND_KNOWLEDGE_REPO.curie('size'),
                   model_uri=INKIND_KNOWLEDGE_REPO.size, domain=None, range=Optional[Union[str, "ClothingSizeEnum"]])

slots.is_winter_suitable = Slot(uri=INKIND_KNOWLEDGE_REPO.is_winter_suitable, name="is_winter_suitable", curie=INKIND_KNOWLEDGE_REPO.curie('is_winter_suitable'),
                   model_uri=INKIND_KNOWLEDGE_REPO.is_winter_suitable, domain=None, range=Optional[Union[bool, Bool]])

slots.season = Slot(uri=INKIND_KNOWLEDGE_REPO.season, name="season", curie=INKIND_KNOWLEDGE_REPO.curie('season'),
                   model_uri=INKIND_KNOWLEDGE_REPO.season, domain=None, range=Optional[Union[Union[str, "SeasonEnum"], list[Union[str, "SeasonEnum"]]]])

slots.intact_labels = Slot(uri=INKIND_KNOWLEDGE_REPO.intact_labels, name="intact_labels", curie=INKIND_KNOWLEDGE_REPO.curie('intact_labels'),
                   model_uri=INKIND_KNOWLEDGE_REPO.intact_labels, domain=None, range=Optional[Union[bool, Bool]])

slots.is_maternity = Slot(uri=INKIND_KNOWLEDGE_REPO.is_maternity, name="is_maternity", curie=INKIND_KNOWLEDGE_REPO.curie('is_maternity'),
                   model_uri=INKIND_KNOWLEDGE_REPO.is_maternity, domain=None, range=Optional[Union[bool, Bool]])

slots.shoe_size = Slot(uri=INKIND_KNOWLEDGE_REPO.shoe_size, name="shoe_size", curie=INKIND_KNOWLEDGE_REPO.curie('shoe_size'),
                   model_uri=INKIND_KNOWLEDGE_REPO.shoe_size, domain=None, range=Optional[str])

slots.shoe_size_system = Slot(uri=INKIND_KNOWLEDGE_REPO.shoe_size_system, name="shoe_size_system", curie=INKIND_KNOWLEDGE_REPO.curie('shoe_size_system'),
                   model_uri=INKIND_KNOWLEDGE_REPO.shoe_size_system, domain=None, range=Optional[Union[str, "ShoeSizeSystemEnum"]])

slots.is_pair_complete = Slot(uri=INKIND_KNOWLEDGE_REPO.is_pair_complete, name="is_pair_complete", curie=INKIND_KNOWLEDGE_REPO.curie('is_pair_complete'),
                   model_uri=INKIND_KNOWLEDGE_REPO.is_pair_complete, domain=None, range=Optional[Union[bool, Bool]])

slots.dimensions = Slot(uri=INKIND_KNOWLEDGE_REPO.dimensions, name="dimensions", curie=INKIND_KNOWLEDGE_REPO.curie('dimensions'),
                   model_uri=INKIND_KNOWLEDGE_REPO.dimensions, domain=None, range=Optional[str])

slots.style = Slot(uri=INKIND_KNOWLEDGE_REPO.style, name="style", curie=INKIND_KNOWLEDGE_REPO.curie('style'),
                   model_uri=INKIND_KNOWLEDGE_REPO.style, domain=None, range=Optional[str])

slots.includes_charger = Slot(uri=INKIND_KNOWLEDGE_REPO.includes_charger, name="includes_charger", curie=INKIND_KNOWLEDGE_REPO.curie('includes_charger'),
                   model_uri=INKIND_KNOWLEDGE_REPO.includes_charger, domain=None, range=Optional[Union[bool, Bool]])

slots.includes_original_packaging = Slot(uri=INKIND_KNOWLEDGE_REPO.includes_original_packaging, name="includes_original_packaging", curie=INKIND_KNOWLEDGE_REPO.curie('includes_original_packaging'),
                   model_uri=INKIND_KNOWLEDGE_REPO.includes_original_packaging, domain=None, range=Optional[Union[bool, Bool]])

slots.has_small_parts = Slot(uri=INKIND_KNOWLEDGE_REPO.has_small_parts, name="has_small_parts", curie=INKIND_KNOWLEDGE_REPO.curie('has_small_parts'),
                   model_uri=INKIND_KNOWLEDGE_REPO.has_small_parts, domain=None, range=Optional[Union[bool, Bool]])

slots.sport_type = Slot(uri=INKIND_KNOWLEDGE_REPO.sport_type, name="sport_type", curie=INKIND_KNOWLEDGE_REPO.curie('sport_type'),
                   model_uri=INKIND_KNOWLEDGE_REPO.sport_type, domain=None, range=Optional[str])

slots.language = Slot(uri=INKIND_KNOWLEDGE_REPO.language, name="language", curie=INKIND_KNOWLEDGE_REPO.curie('language'),
                   model_uri=INKIND_KNOWLEDGE_REPO.language, domain=None, range=Optional[str])

slots.manufacture_year = Slot(uri=INKIND_KNOWLEDGE_REPO.manufacture_year, name="manufacture_year", curie=INKIND_KNOWLEDGE_REPO.curie('manufacture_year'),
                   model_uri=INKIND_KNOWLEDGE_REPO.manufacture_year, domain=None, range=Optional[int])

slots.includes_original_accessories = Slot(uri=INKIND_KNOWLEDGE_REPO.includes_original_accessories, name="includes_original_accessories", curie=INKIND_KNOWLEDGE_REPO.curie('includes_original_accessories'),
                   model_uri=INKIND_KNOWLEDGE_REPO.includes_original_accessories, domain=None, range=Optional[Union[bool, Bool]])

slots.nappy_size = Slot(uri=INKIND_KNOWLEDGE_REPO.nappy_size, name="nappy_size", curie=INKIND_KNOWLEDGE_REPO.curie('nappy_size'),
                   model_uri=INKIND_KNOWLEDGE_REPO.nappy_size, domain=None, range=Optional[Union[str, "NappySizeEnum"]])

slots.packaging_intact = Slot(uri=INKIND_KNOWLEDGE_REPO.packaging_intact, name="packaging_intact", curie=INKIND_KNOWLEDGE_REPO.curie('packaging_intact'),
                   model_uri=INKIND_KNOWLEDGE_REPO.packaging_intact, domain=None, range=Union[bool, Bool])

slots.storage_requirement = Slot(uri=INKIND_KNOWLEDGE_REPO.storage_requirement, name="storage_requirement", curie=INKIND_KNOWLEDGE_REPO.curie('storage_requirement'),
                   model_uri=INKIND_KNOWLEDGE_REPO.storage_requirement, domain=None, range=Union[str, "StorageRequirementEnum"])

slots.step_type_ref = Slot(uri=INKIND_KNOWLEDGE_REPO.step_type_ref, name="step_type_ref", curie=INKIND_KNOWLEDGE_REPO.curie('step_type_ref'),
                   model_uri=INKIND_KNOWLEDGE_REPO.step_type_ref, domain=None, range=str)

slots.actor_ref = Slot(uri=PROV.wasAssociatedWith, name="actor_ref", curie=PROV.curie('wasAssociatedWith'),
                   model_uri=INKIND_KNOWLEDGE_REPO.actor_ref, domain=None, range=str)

slots.actor_role_ref = Slot(uri=INKIND_KNOWLEDGE_REPO.actor_role_ref, name="actor_role_ref", curie=INKIND_KNOWLEDGE_REPO.curie('actor_role_ref'),
                   model_uri=INKIND_KNOWLEDGE_REPO.actor_role_ref, domain=None, range=str)

slots.device = Slot(uri=INKIND_KNOWLEDGE_REPO.device, name="device", curie=INKIND_KNOWLEDGE_REPO.curie('device'),
                   model_uri=INKIND_KNOWLEDGE_REPO.device, domain=None, range=Union[str, "DeviceTypeEnum"])

slots.started_at = Slot(uri=INKIND_KNOWLEDGE_REPO.started_at, name="started_at", curie=INKIND_KNOWLEDGE_REPO.curie('started_at'),
                   model_uri=INKIND_KNOWLEDGE_REPO.started_at, domain=None, range=Union[str, XSDDateTime])

slots.completed_at = Slot(uri=PROV.endedAtTime, name="completed_at", curie=PROV.curie('endedAtTime'),
                   model_uri=INKIND_KNOWLEDGE_REPO.completed_at, domain=None, range=Union[str, XSDDateTime])

slots.duration_seconds = Slot(uri=INKIND_KNOWLEDGE_REPO.duration_seconds, name="duration_seconds", curie=INKIND_KNOWLEDGE_REPO.curie('duration_seconds'),
                   model_uri=INKIND_KNOWLEDGE_REPO.duration_seconds, domain=None, range=int)

slots.cost_configured = Slot(uri=INKIND_KNOWLEDGE_REPO.cost_configured, name="cost_configured", curie=INKIND_KNOWLEDGE_REPO.curie('cost_configured'),
                   model_uri=INKIND_KNOWLEDGE_REPO.cost_configured, domain=None, range=float)

slots.observations_ref = Slot(uri=INKIND_KNOWLEDGE_REPO.observations_ref, name="observations_ref", curie=INKIND_KNOWLEDGE_REPO.curie('observations_ref'),
                   model_uri=INKIND_KNOWLEDGE_REPO.observations_ref, domain=None, range=str)

slots.override_flag = Slot(uri=INKIND_KNOWLEDGE_REPO.override_flag, name="override_flag", curie=INKIND_KNOWLEDGE_REPO.curie('override_flag'),
                   model_uri=INKIND_KNOWLEDGE_REPO.override_flag, domain=None, range=Union[bool, Bool])

slots.override_reason = Slot(uri=INKIND_KNOWLEDGE_REPO.override_reason, name="override_reason", curie=INKIND_KNOWLEDGE_REPO.curie('override_reason'),
                   model_uri=INKIND_KNOWLEDGE_REPO.override_reason, domain=None, range=Optional[str])

slots.geoPoint__lat = Slot(uri=INKIND_KNOWLEDGE_REPO.lat, name="geoPoint__lat", curie=INKIND_KNOWLEDGE_REPO.curie('lat'),
                   model_uri=INKIND_KNOWLEDGE_REPO.geoPoint__lat, domain=None, range=Optional[float])

slots.geoPoint__long = Slot(uri=INKIND_KNOWLEDGE_REPO.long, name="geoPoint__long", curie=INKIND_KNOWLEDGE_REPO.curie('long'),
                   model_uri=INKIND_KNOWLEDGE_REPO.geoPoint__long, domain=None, range=Optional[float])

slots.orgConfig__timezone = Slot(uri=INKIND_KNOWLEDGE_REPO.timezone, name="orgConfig__timezone", curie=INKIND_KNOWLEDGE_REPO.curie('timezone'),
                   model_uri=INKIND_KNOWLEDGE_REPO.orgConfig__timezone, domain=None, range=Optional[str])

slots.orgConfig__locale = Slot(uri=INKIND_KNOWLEDGE_REPO.locale, name="orgConfig__locale", curie=INKIND_KNOWLEDGE_REPO.curie('locale'),
                   model_uri=INKIND_KNOWLEDGE_REPO.orgConfig__locale, domain=None, range=Optional[str])

slots.SocialOrganisation_parent = Slot(uri=INKIND_KNOWLEDGE_REPO.parent, name="SocialOrganisation_parent", curie=INKIND_KNOWLEDGE_REPO.curie('parent'),
                   model_uri=INKIND_KNOWLEDGE_REPO.SocialOrganisation_parent, domain=SocialOrganisation, range=Optional[Union[str, SocialOrganisationId]])

slots.Actor_org = Slot(uri=INKIND_KNOWLEDGE_REPO.org, name="Actor_org", curie=INKIND_KNOWLEDGE_REPO.curie('org'),
                   model_uri=INKIND_KNOWLEDGE_REPO.Actor_org, domain=Actor, range=Union[str, SocialOrganisationId])

slots.StorageLocation_org = Slot(uri=INKIND_KNOWLEDGE_REPO.org, name="StorageLocation_org", curie=INKIND_KNOWLEDGE_REPO.curie('org'),
                   model_uri=INKIND_KNOWLEDGE_REPO.StorageLocation_org, domain=StorageLocation, range=Union[str, SocialOrganisationId])

slots.StorageLocation_parent = Slot(uri=INKIND_KNOWLEDGE_REPO.parent, name="StorageLocation_parent", curie=INKIND_KNOWLEDGE_REPO.curie('parent'),
                   model_uri=INKIND_KNOWLEDGE_REPO.StorageLocation_parent, domain=StorageLocation, range=Optional[Union[str, StorageLocationId]])

slots.DonationSource_lifecycle_state = Slot(uri=INKIND_KNOWLEDGE_REPO.lifecycle_state, name="DonationSource_lifecycle_state", curie=INKIND_KNOWLEDGE_REPO.curie('lifecycle_state'),
                   model_uri=INKIND_KNOWLEDGE_REPO.DonationSource_lifecycle_state, domain=DonationSource, range=Union[str, "DonationSourceLifecycleEnum"])

slots.DonationCollection_org = Slot(uri=INKIND_KNOWLEDGE_REPO.org, name="DonationCollection_org", curie=INKIND_KNOWLEDGE_REPO.curie('org'),
                   model_uri=INKIND_KNOWLEDGE_REPO.DonationCollection_org, domain=DonationCollection, range=Union[str, SocialOrganisationId])

slots.DonationCollection_lifecycle_state = Slot(uri=INKIND_KNOWLEDGE_REPO.lifecycle_state, name="DonationCollection_lifecycle_state", curie=INKIND_KNOWLEDGE_REPO.curie('lifecycle_state'),
                   model_uri=INKIND_KNOWLEDGE_REPO.DonationCollection_lifecycle_state, domain=DonationCollection, range=Union[str, "CollectionLifecycleEnum"])

slots.DonationCollection_donation_source = Slot(uri=INKIND_KNOWLEDGE_REPO.donation_source, name="DonationCollection_donation_source", curie=INKIND_KNOWLEDGE_REPO.curie('donation_source'),
                   model_uri=INKIND_KNOWLEDGE_REPO.DonationCollection_donation_source, domain=DonationCollection, range=Optional[Union[str, DonationSourceId]])

slots.DonationCollection_parent = Slot(uri=INKIND_KNOWLEDGE_REPO.parent, name="DonationCollection_parent", curie=INKIND_KNOWLEDGE_REPO.curie('parent'),
                   model_uri=INKIND_KNOWLEDGE_REPO.DonationCollection_parent, domain=DonationCollection, range=Optional[Union[str, DonationCollectionId]])

slots.DonationItem_category = Slot(uri=SCHEMA.additionalType, name="DonationItem_category", curie=SCHEMA.curie('additionalType'),
                   model_uri=INKIND_KNOWLEDGE_REPO.DonationItem_category, domain=DonationItem, range=Union[str, "SortingCategoryEnum"])

slots.DonationItem_lifecycle_state = Slot(uri=INKIND_KNOWLEDGE_REPO.lifecycle_state, name="DonationItem_lifecycle_state", curie=INKIND_KNOWLEDGE_REPO.curie('lifecycle_state'),
                   model_uri=INKIND_KNOWLEDGE_REPO.DonationItem_lifecycle_state, domain=DonationItem, range=Union[str, "ItemLifecycleStateEnum"])

slots.DonationItem_usage = Slot(uri=SCHEMA.itemCondition, name="DonationItem_usage", curie=SCHEMA.curie('itemCondition'),
                   model_uri=INKIND_KNOWLEDGE_REPO.DonationItem_usage, domain=DonationItem, range=Union[str, "ItemUsageEnum"])

slots.DonationItem_attribute_completeness = Slot(uri=INKIND_KNOWLEDGE_REPO.attribute_completeness, name="DonationItem_attribute_completeness", curie=INKIND_KNOWLEDGE_REPO.curie('attribute_completeness'),
                   model_uri=INKIND_KNOWLEDGE_REPO.DonationItem_attribute_completeness, domain=DonationItem, range=Optional[Union[str, "AttributeCompletenessEnum"]])

slots.DonationItem_source_collection = Slot(uri=INKIND_KNOWLEDGE_REPO.source_collection, name="DonationItem_source_collection", curie=INKIND_KNOWLEDGE_REPO.curie('source_collection'),
                   model_uri=INKIND_KNOWLEDGE_REPO.DonationItem_source_collection, domain=DonationItem, range=Optional[Union[str, DonationCollectionId]])

slots.DonationItem_donation_source = Slot(uri=INKIND_KNOWLEDGE_REPO.donation_source, name="DonationItem_donation_source", curie=INKIND_KNOWLEDGE_REPO.curie('donation_source'),
                   model_uri=INKIND_KNOWLEDGE_REPO.DonationItem_donation_source, domain=DonationItem, range=Optional[Union[str, DonationSourceId]])

slots.DonationItem_storage_unit = Slot(uri=INKIND_KNOWLEDGE_REPO.storage_unit, name="DonationItem_storage_unit", curie=INKIND_KNOWLEDGE_REPO.curie('storage_unit'),
                   model_uri=INKIND_KNOWLEDGE_REPO.DonationItem_storage_unit, domain=DonationItem, range=Optional[Union[str, StorageLocationId]])

slots.StorageCollection_usage = Slot(uri=SCHEMA.itemCondition, name="StorageCollection_usage", curie=SCHEMA.curie('itemCondition'),
                   model_uri=INKIND_KNOWLEDGE_REPO.StorageCollection_usage, domain=StorageCollection, range=Union[str, "ItemUsageEnum"])

slots.StorageCollection_category = Slot(uri=SCHEMA.additionalType, name="StorageCollection_category", curie=SCHEMA.curie('additionalType'),
                   model_uri=INKIND_KNOWLEDGE_REPO.StorageCollection_category, domain=StorageCollection, range=Union[str, "BaseCategoryEnum"])

slots.SortedCollection_usage = Slot(uri=SCHEMA.itemCondition, name="SortedCollection_usage", curie=SCHEMA.curie('itemCondition'),
                   model_uri=INKIND_KNOWLEDGE_REPO.SortedCollection_usage, domain=SortedCollection, range=Union[str, "ItemUsageEnum"])

slots.SortedCollection_category = Slot(uri=SCHEMA.additionalType, name="SortedCollection_category", curie=SCHEMA.curie('additionalType'),
                   model_uri=INKIND_KNOWLEDGE_REPO.SortedCollection_category, domain=SortedCollection, range=Union[str, "SortingCategoryEnum"])

slots.DemandSignal_org = Slot(uri=INKIND_KNOWLEDGE_REPO.org, name="DemandSignal_org", curie=INKIND_KNOWLEDGE_REPO.curie('org'),
                   model_uri=INKIND_KNOWLEDGE_REPO.DemandSignal_org, domain=DemandSignal, range=Union[str, SocialOrganisationId])

slots.DemandSignal_category = Slot(uri=SCHEMA.additionalType, name="DemandSignal_category", curie=SCHEMA.curie('additionalType'),
                   model_uri=INKIND_KNOWLEDGE_REPO.DemandSignal_category, domain=DemandSignal, range=Union[str, "BaseCategoryEnum"])

slots.DemandSignal_lifecycle_state = Slot(uri=INKIND_KNOWLEDGE_REPO.lifecycle_state, name="DemandSignal_lifecycle_state", curie=INKIND_KNOWLEDGE_REPO.curie('lifecycle_state'),
                   model_uri=INKIND_KNOWLEDGE_REPO.DemandSignal_lifecycle_state, domain=DemandSignal, range=Union[str, "DemandSignalLifecycleEnum"])

slots.DemandSignal_urgency_tier = Slot(uri=INKIND_KNOWLEDGE_REPO.urgency_tier, name="DemandSignal_urgency_tier", curie=INKIND_KNOWLEDGE_REPO.curie('urgency_tier'),
                   model_uri=INKIND_KNOWLEDGE_REPO.DemandSignal_urgency_tier, domain=DemandSignal, range=Optional[Union[str, "UrgencyTierEnum"]])

slots.Campaign_org = Slot(uri=INKIND_KNOWLEDGE_REPO.org, name="Campaign_org", curie=INKIND_KNOWLEDGE_REPO.curie('org'),
                   model_uri=INKIND_KNOWLEDGE_REPO.Campaign_org, domain=Campaign, range=Union[str, SocialOrganisationId])

slots.Campaign_lifecycle_state = Slot(uri=INKIND_KNOWLEDGE_REPO.lifecycle_state, name="Campaign_lifecycle_state", curie=INKIND_KNOWLEDGE_REPO.curie('lifecycle_state'),
                   model_uri=INKIND_KNOWLEDGE_REPO.Campaign_lifecycle_state, domain=Campaign, range=Union[str, "CampaignLifecycleEnum"])

slots.AccessoriesCategory_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.subcategory, name="AccessoriesCategory_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.AccessoriesCategory_subcategory, domain=None, range=Union[str, "AccessoriesSubcategoryEnum"])

slots.AccessoriesCategory_demographic = Slot(uri=INKIND_KNOWLEDGE_REPO.demographic, name="AccessoriesCategory_demographic", curie=INKIND_KNOWLEDGE_REPO.curie('demographic'),
                   model_uri=INKIND_KNOWLEDGE_REPO.AccessoriesCategory_demographic, domain=None, range=Optional[Union[str, "AccessoriesDemographicEnum"]])

slots.AccessoriesCategory_material = Slot(uri=INKIND_KNOWLEDGE_REPO.material, name="AccessoriesCategory_material", curie=INKIND_KNOWLEDGE_REPO.curie('material'),
                   model_uri=INKIND_KNOWLEDGE_REPO.AccessoriesCategory_material, domain=None, range=Optional[Union[str, "AccessoriesMaterialEnum"]])

slots.AccessoriesCategory_condition_grade = Slot(uri=INKIND_KNOWLEDGE_REPO.condition_grade, name="AccessoriesCategory_condition_grade", curie=INKIND_KNOWLEDGE_REPO.curie('condition_grade'),
                   model_uri=INKIND_KNOWLEDGE_REPO.AccessoriesCategory_condition_grade, domain=None, range=Optional[Union[str, "UsedConditionGradeEnum"]])

slots.ClothingCategory_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.subcategory, name="ClothingCategory_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ClothingCategory_subcategory, domain=None, range=Optional[Union[str, "ClothingSubcategoryEnum"]])

slots.ClothingCategory_tops_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.tops_subcategory, name="ClothingCategory_tops_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('tops_subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ClothingCategory_tops_subcategory, domain=None, range=Optional[Union[str, "TopsSubcategoryEnum"]])

slots.ClothingCategory_bottoms_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.bottoms_subcategory, name="ClothingCategory_bottoms_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('bottoms_subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ClothingCategory_bottoms_subcategory, domain=None, range=Optional[Union[str, "BottomsSubcategoryEnum"]])

slots.ClothingCategory_demographic = Slot(uri=INKIND_KNOWLEDGE_REPO.demographic, name="ClothingCategory_demographic", curie=INKIND_KNOWLEDGE_REPO.curie('demographic'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ClothingCategory_demographic, domain=None, range=Optional[Union[str, "DemographicEnum"]])

slots.ClothingCategory_size = Slot(uri=INKIND_KNOWLEDGE_REPO.size, name="ClothingCategory_size", curie=INKIND_KNOWLEDGE_REPO.curie('size'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ClothingCategory_size, domain=None, range=Optional[Union[Union[str, "ClothingSizeEnum"], list[Union[str, "ClothingSizeEnum"]]]])

slots.ClothingCategory_is_winter_suitable = Slot(uri=INKIND_KNOWLEDGE_REPO.is_winter_suitable, name="ClothingCategory_is_winter_suitable", curie=INKIND_KNOWLEDGE_REPO.curie('is_winter_suitable'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ClothingCategory_is_winter_suitable, domain=None, range=Optional[Union[bool, Bool]])

slots.ClothingCategory_season = Slot(uri=INKIND_KNOWLEDGE_REPO.season, name="ClothingCategory_season", curie=INKIND_KNOWLEDGE_REPO.curie('season'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ClothingCategory_season, domain=None, range=Optional[Union[Union[str, "SeasonEnum"], list[Union[str, "SeasonEnum"]]]])

slots.ClothingCategory_material = Slot(uri=INKIND_KNOWLEDGE_REPO.material, name="ClothingCategory_material", curie=INKIND_KNOWLEDGE_REPO.curie('material'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ClothingCategory_material, domain=None, range=Optional[Union[str, "ClothingMaterialEnum"]])

slots.ClothingCategory_condition_grade = Slot(uri=INKIND_KNOWLEDGE_REPO.condition_grade, name="ClothingCategory_condition_grade", curie=INKIND_KNOWLEDGE_REPO.curie('condition_grade'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ClothingCategory_condition_grade, domain=None, range=Optional[Union[str, "UsedConditionGradeEnum"]])

slots.FootwearCategory_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.subcategory, name="FootwearCategory_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.FootwearCategory_subcategory, domain=None, range=Union[str, "FootwearSubcategoryEnum"])

slots.FootwearCategory_demographic = Slot(uri=INKIND_KNOWLEDGE_REPO.demographic, name="FootwearCategory_demographic", curie=INKIND_KNOWLEDGE_REPO.curie('demographic'),
                   model_uri=INKIND_KNOWLEDGE_REPO.FootwearCategory_demographic, domain=None, range=Optional[Union[str, "DemographicEnum"]])

slots.FootwearCategory_is_winter_suitable = Slot(uri=INKIND_KNOWLEDGE_REPO.is_winter_suitable, name="FootwearCategory_is_winter_suitable", curie=INKIND_KNOWLEDGE_REPO.curie('is_winter_suitable'),
                   model_uri=INKIND_KNOWLEDGE_REPO.FootwearCategory_is_winter_suitable, domain=None, range=Optional[Union[bool, Bool]])

slots.FootwearCategory_season = Slot(uri=INKIND_KNOWLEDGE_REPO.season, name="FootwearCategory_season", curie=INKIND_KNOWLEDGE_REPO.curie('season'),
                   model_uri=INKIND_KNOWLEDGE_REPO.FootwearCategory_season, domain=None, range=Optional[Union[Union[str, "SeasonEnum"], list[Union[str, "SeasonEnum"]]]])

slots.FootwearCategory_material = Slot(uri=INKIND_KNOWLEDGE_REPO.material, name="FootwearCategory_material", curie=INKIND_KNOWLEDGE_REPO.curie('material'),
                   model_uri=INKIND_KNOWLEDGE_REPO.FootwearCategory_material, domain=None, range=Optional[Union[str, "FootwearMaterialEnum"]])

slots.FootwearCategory_condition_grade = Slot(uri=INKIND_KNOWLEDGE_REPO.condition_grade, name="FootwearCategory_condition_grade", curie=INKIND_KNOWLEDGE_REPO.curie('condition_grade'),
                   model_uri=INKIND_KNOWLEDGE_REPO.FootwearCategory_condition_grade, domain=None, range=Optional[Union[str, "UsedConditionGradeEnum"]])

slots.FurnitureCategory_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.subcategory, name="FurnitureCategory_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.FurnitureCategory_subcategory, domain=None, range=Union[str, "FurnitureSubcategoryEnum"])

slots.FurnitureCategory_material = Slot(uri=INKIND_KNOWLEDGE_REPO.material, name="FurnitureCategory_material", curie=INKIND_KNOWLEDGE_REPO.curie('material'),
                   model_uri=INKIND_KNOWLEDGE_REPO.FurnitureCategory_material, domain=None, range=Optional[Union[str, "FurnitureMaterialEnum"]])

slots.FurnitureAssessmentMixin_assessment_result = Slot(uri=INKIND_KNOWLEDGE_REPO.assessment_result, name="FurnitureAssessmentMixin_assessment_result", curie=INKIND_KNOWLEDGE_REPO.curie('assessment_result'),
                   model_uri=INKIND_KNOWLEDGE_REPO.FurnitureAssessmentMixin_assessment_result, domain=None, range=Optional[Union[str, "FurnitureAssessmentEnum"]])

slots.BeddingTextilesCategory_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.subcategory, name="BeddingTextilesCategory_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.BeddingTextilesCategory_subcategory, domain=None, range=Union[str, "BeddingTextilesSubcategoryEnum"])

slots.BeddingTextilesCategory_material = Slot(uri=INKIND_KNOWLEDGE_REPO.material, name="BeddingTextilesCategory_material", curie=INKIND_KNOWLEDGE_REPO.curie('material'),
                   model_uri=INKIND_KNOWLEDGE_REPO.BeddingTextilesCategory_material, domain=None, range=Optional[Union[str, "BeddingMaterialEnum"]])

slots.BeddingTextilesCategory_is_winter_suitable = Slot(uri=INKIND_KNOWLEDGE_REPO.is_winter_suitable, name="BeddingTextilesCategory_is_winter_suitable", curie=INKIND_KNOWLEDGE_REPO.curie('is_winter_suitable'),
                   model_uri=INKIND_KNOWLEDGE_REPO.BeddingTextilesCategory_is_winter_suitable, domain=None, range=Optional[Union[bool, Bool]])

slots.BeddingAssessmentMixin_assessment_result = Slot(uri=INKIND_KNOWLEDGE_REPO.assessment_result, name="BeddingAssessmentMixin_assessment_result", curie=INKIND_KNOWLEDGE_REPO.curie('assessment_result'),
                   model_uri=INKIND_KNOWLEDGE_REPO.BeddingAssessmentMixin_assessment_result, domain=None, range=Optional[Union[str, "BeddingAssessmentEnum"]])

slots.HouseholdCategory_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.subcategory, name="HouseholdCategory_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.HouseholdCategory_subcategory, domain=None, range=Union[str, "HouseholdSubcategoryEnum"])

slots.HouseholdCategory_material = Slot(uri=INKIND_KNOWLEDGE_REPO.material, name="HouseholdCategory_material", curie=INKIND_KNOWLEDGE_REPO.curie('material'),
                   model_uri=INKIND_KNOWLEDGE_REPO.HouseholdCategory_material, domain=None, range=Optional[Union[str, "HouseholdMaterialEnum"]])

slots.HouseholdCategory_condition_grade = Slot(uri=INKIND_KNOWLEDGE_REPO.condition_grade, name="HouseholdCategory_condition_grade", curie=INKIND_KNOWLEDGE_REPO.curie('condition_grade'),
                   model_uri=INKIND_KNOWLEDGE_REPO.HouseholdCategory_condition_grade, domain=None, range=Optional[Union[str, "UsedConditionGradeEnum"]])

slots.ElectronicsCategory_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.subcategory, name="ElectronicsCategory_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ElectronicsCategory_subcategory, domain=None, range=Union[str, "ElectronicsSubcategoryEnum"])

slots.ElectronicsAssessmentMixin_assessment_result = Slot(uri=INKIND_KNOWLEDGE_REPO.assessment_result, name="ElectronicsAssessmentMixin_assessment_result", curie=INKIND_KNOWLEDGE_REPO.curie('assessment_result'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ElectronicsAssessmentMixin_assessment_result, domain=None, range=Union[str, "ElectronicsAssessmentEnum"])

slots.ToysCategory_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.subcategory, name="ToysCategory_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ToysCategory_subcategory, domain=None, range=Union[str, "ToysSubcategoryEnum"])

slots.ToysCategory_age_range = Slot(uri=INKIND_KNOWLEDGE_REPO.age_range, name="ToysCategory_age_range", curie=INKIND_KNOWLEDGE_REPO.curie('age_range'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ToysCategory_age_range, domain=None, range=Optional[Union[str, "ToyAgeRangeEnum"]])

slots.ToysCategory_material = Slot(uri=INKIND_KNOWLEDGE_REPO.material, name="ToysCategory_material", curie=INKIND_KNOWLEDGE_REPO.curie('material'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ToysCategory_material, domain=None, range=Optional[Union[str, "ToysMaterialEnum"]])

slots.ToysCategory_condition_grade = Slot(uri=INKIND_KNOWLEDGE_REPO.condition_grade, name="ToysCategory_condition_grade", curie=INKIND_KNOWLEDGE_REPO.curie('condition_grade'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ToysCategory_condition_grade, domain=None, range=Optional[Union[str, "UsedConditionGradeEnum"]])

slots.SportsCategory_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.subcategory, name="SportsCategory_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.SportsCategory_subcategory, domain=None, range=Union[str, "SportsSubcategoryEnum"])

slots.SportsCategory_condition_grade = Slot(uri=INKIND_KNOWLEDGE_REPO.condition_grade, name="SportsCategory_condition_grade", curie=INKIND_KNOWLEDGE_REPO.curie('condition_grade'),
                   model_uri=INKIND_KNOWLEDGE_REPO.SportsCategory_condition_grade, domain=None, range=Optional[Union[str, "UsedConditionGradeEnum"]])

slots.SportsCategory_demographic = Slot(uri=INKIND_KNOWLEDGE_REPO.demographic, name="SportsCategory_demographic", curie=INKIND_KNOWLEDGE_REPO.curie('demographic'),
                   model_uri=INKIND_KNOWLEDGE_REPO.SportsCategory_demographic, domain=None, range=Optional[Union[str, "DemographicEnum"]])

slots.SportsProtectiveAssessmentMixin_assessment_result = Slot(uri=INKIND_KNOWLEDGE_REPO.assessment_result, name="SportsProtectiveAssessmentMixin_assessment_result", curie=INKIND_KNOWLEDGE_REPO.curie('assessment_result'),
                   model_uri=INKIND_KNOWLEDGE_REPO.SportsProtectiveAssessmentMixin_assessment_result, domain=None, range=Optional[Union[str, "SportsProtectiveAssessmentEnum"]])

slots.BooksCategory_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.subcategory, name="BooksCategory_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.BooksCategory_subcategory, domain=None, range=Union[str, "BooksSubcategoryEnum"])

slots.BooksCategory_age_range = Slot(uri=INKIND_KNOWLEDGE_REPO.age_range, name="BooksCategory_age_range", curie=INKIND_KNOWLEDGE_REPO.curie('age_range'),
                   model_uri=INKIND_KNOWLEDGE_REPO.BooksCategory_age_range, domain=None, range=Optional[Union[str, "BookAgeRangeEnum"]])

slots.BooksCategory_condition_grade = Slot(uri=INKIND_KNOWLEDGE_REPO.condition_grade, name="BooksCategory_condition_grade", curie=INKIND_KNOWLEDGE_REPO.curie('condition_grade'),
                   model_uri=INKIND_KNOWLEDGE_REPO.BooksCategory_condition_grade, domain=None, range=Optional[Union[str, "UsedConditionGradeEnum"]])

slots.StationeryCategory_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.subcategory, name="StationeryCategory_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.StationeryCategory_subcategory, domain=None, range=Union[str, "StationerySubcategoryEnum"])

slots.StationeryCategory_condition_grade = Slot(uri=INKIND_KNOWLEDGE_REPO.condition_grade, name="StationeryCategory_condition_grade", curie=INKIND_KNOWLEDGE_REPO.curie('condition_grade'),
                   model_uri=INKIND_KNOWLEDGE_REPO.StationeryCategory_condition_grade, domain=None, range=Optional[Union[str, "UsedConditionGradeEnum"]])

slots.PersonalCareCategory_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.subcategory, name="PersonalCareCategory_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.PersonalCareCategory_subcategory, domain=None, range=Union[str, "PersonalCareSubcategoryEnum"])

slots.PersonalCareCategory_is_sealed = Slot(uri=INKIND_KNOWLEDGE_REPO.is_sealed, name="PersonalCareCategory_is_sealed", curie=INKIND_KNOWLEDGE_REPO.curie('is_sealed'),
                   model_uri=INKIND_KNOWLEDGE_REPO.PersonalCareCategory_is_sealed, domain=None, range=Optional[Union[bool, Bool]])

slots.PersonalCareCategory_expiry_date = Slot(uri=INKIND_KNOWLEDGE_REPO.expiry_date, name="PersonalCareCategory_expiry_date", curie=INKIND_KNOWLEDGE_REPO.curie('expiry_date'),
                   model_uri=INKIND_KNOWLEDGE_REPO.PersonalCareCategory_expiry_date, domain=None, range=Optional[Union[str, XSDDate]])

slots.MobilityAidsCategory_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.subcategory, name="MobilityAidsCategory_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.MobilityAidsCategory_subcategory, domain=None, range=Union[str, "MobilityAidsSubcategoryEnum"])

slots.MobilityAssessmentMixin_assessment_result = Slot(uri=INKIND_KNOWLEDGE_REPO.assessment_result, name="MobilityAssessmentMixin_assessment_result", curie=INKIND_KNOWLEDGE_REPO.curie('assessment_result'),
                   model_uri=INKIND_KNOWLEDGE_REPO.MobilityAssessmentMixin_assessment_result, domain=None, range=Optional[Union[str, "MobilityAssessmentEnum"]])

slots.BabyInfantCategory_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.subcategory, name="BabyInfantCategory_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.BabyInfantCategory_subcategory, domain=None, range=Union[str, "BabyInfantSubcategoryEnum"])

slots.BabyInfantCategory_is_winter_suitable = Slot(uri=INKIND_KNOWLEDGE_REPO.is_winter_suitable, name="BabyInfantCategory_is_winter_suitable", curie=INKIND_KNOWLEDGE_REPO.curie('is_winter_suitable'),
                   model_uri=INKIND_KNOWLEDGE_REPO.BabyInfantCategory_is_winter_suitable, domain=None, range=Optional[Union[bool, Bool]])

slots.BabyInfantCategory_is_sealed = Slot(uri=INKIND_KNOWLEDGE_REPO.is_sealed, name="BabyInfantCategory_is_sealed", curie=INKIND_KNOWLEDGE_REPO.curie('is_sealed'),
                   model_uri=INKIND_KNOWLEDGE_REPO.BabyInfantCategory_is_sealed, domain=None, range=Optional[Union[bool, Bool]])

slots.BabyInfantCategory_condition_grade = Slot(uri=INKIND_KNOWLEDGE_REPO.condition_grade, name="BabyInfantCategory_condition_grade", curie=INKIND_KNOWLEDGE_REPO.curie('condition_grade'),
                   model_uri=INKIND_KNOWLEDGE_REPO.BabyInfantCategory_condition_grade, domain=None, range=Optional[Union[str, "UsedConditionGradeEnum"]])

slots.BabyInfantCategory_nappy_size = Slot(uri=INKIND_KNOWLEDGE_REPO.nappy_size, name="BabyInfantCategory_nappy_size", curie=INKIND_KNOWLEDGE_REPO.curie('nappy_size'),
                   model_uri=INKIND_KNOWLEDGE_REPO.BabyInfantCategory_nappy_size, domain=None, range=Optional[Union[str, "NappySizeEnum"]])

slots.BabyEquipmentAssessmentMixin_assessment_result = Slot(uri=INKIND_KNOWLEDGE_REPO.assessment_result, name="BabyEquipmentAssessmentMixin_assessment_result", curie=INKIND_KNOWLEDGE_REPO.curie('assessment_result'),
                   model_uri=INKIND_KNOWLEDGE_REPO.BabyEquipmentAssessmentMixin_assessment_result, domain=None, range=Optional[Union[str, "BabyEquipmentAssessmentEnum"]])

slots.FoodCategory_subcategory = Slot(uri=INKIND_KNOWLEDGE_REPO.subcategory, name="FoodCategory_subcategory", curie=INKIND_KNOWLEDGE_REPO.curie('subcategory'),
                   model_uri=INKIND_KNOWLEDGE_REPO.FoodCategory_subcategory, domain=None, range=Union[str, "FoodTypeEnum"])

slots.FoodCategory_packaging_intact = Slot(uri=INKIND_KNOWLEDGE_REPO.packaging_intact, name="FoodCategory_packaging_intact", curie=INKIND_KNOWLEDGE_REPO.curie('packaging_intact'),
                   model_uri=INKIND_KNOWLEDGE_REPO.FoodCategory_packaging_intact, domain=None, range=Union[bool, Bool])

slots.FoodCategory_storage_requirement = Slot(uri=INKIND_KNOWLEDGE_REPO.storage_requirement, name="FoodCategory_storage_requirement", curie=INKIND_KNOWLEDGE_REPO.curie('storage_requirement'),
                   model_uri=INKIND_KNOWLEDGE_REPO.FoodCategory_storage_requirement, domain=None, range=Union[str, "StorageRequirementEnum"])

slots.FoodCategory_expiry_date = Slot(uri=INKIND_KNOWLEDGE_REPO.expiry_date, name="FoodCategory_expiry_date", curie=INKIND_KNOWLEDGE_REPO.curie('expiry_date'),
                   model_uri=INKIND_KNOWLEDGE_REPO.FoodCategory_expiry_date, domain=None, range=Optional[Union[str, XSDDate]])

slots.OtherCategory_item_description = Slot(uri=INKIND_KNOWLEDGE_REPO.item_description, name="OtherCategory_item_description", curie=INKIND_KNOWLEDGE_REPO.curie('item_description'),
                   model_uri=INKIND_KNOWLEDGE_REPO.OtherCategory_item_description, domain=None, range=str)

slots.OtherCategory_condition_grade = Slot(uri=INKIND_KNOWLEDGE_REPO.condition_grade, name="OtherCategory_condition_grade", curie=INKIND_KNOWLEDGE_REPO.curie('condition_grade'),
                   model_uri=INKIND_KNOWLEDGE_REPO.OtherCategory_condition_grade, domain=None, range=Optional[Union[str, "UsedConditionGradeEnum"]])

slots.ProvenanceRecord_org = Slot(uri=INKIND_KNOWLEDGE_REPO.org, name="ProvenanceRecord_org", curie=INKIND_KNOWLEDGE_REPO.curie('org'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ProvenanceRecord_org, domain=ProvenanceRecord, range=Union[str, SocialOrganisationId])

slots.ProvenanceRecord_actor_role_ref = Slot(uri=INKIND_KNOWLEDGE_REPO.actor_role_ref, name="ProvenanceRecord_actor_role_ref", curie=INKIND_KNOWLEDGE_REPO.curie('actor_role_ref'),
                   model_uri=INKIND_KNOWLEDGE_REPO.ProvenanceRecord_actor_role_ref, domain=ProvenanceRecord, range=Union[str, "ActorRoleEnum"])
