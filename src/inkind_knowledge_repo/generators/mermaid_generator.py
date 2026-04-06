"""
Custom generator of mermaid diagrams.

author: Natalia Ruemmele
"""
from typing import List, Union
from dataclasses import dataclass
import os
import logging
from copy import copy


from linkml_runtime.linkml_model.meta import (
    ClassDefinitionName,
    ElementName,
    SlotDefinition,
    SlotDefinitionName
)
from linkml_runtime.utils.schemaview import SchemaView
import re
from linkml_runtime.utils.formatutils import underscore
from linkml.generators.erdiagramgen import ERDiagramGenerator
from linkml.generators.erdiagramgen import MERMAID_SERIALIZATION
from linkml.generators.erdiagramgen import ERDiagram
from linkml.generators.erdiagramgen import Entity
from linkml.generators.erdiagramgen import Relationship
from linkml.generators.erdiagramgen import RelationshipType
from linkml.generators.erdiagramgen import Cardinality
from linkml.generators.erdiagramgen import Attribute

CLASS_NAME = Union[ClassDefinitionName, str]
SLOT_NAME = Union[SlotDefinitionName, str]


def camelcase(txt: str) -> str:
    us_pattern = re.compile(r'_+')
    def _up(s: str):
        return s[0].upper() + (s[1:] if len(s) > 1 else '')
    constructed = ''.join([_up(word) for word in us_pattern.sub(' ', txt.strip().replace(',', '').replace('(', ' ').replace(')', ' ')).split()])
    return constructed


@dataclass
class CustomERDiagramGenerator(ERDiagramGenerator):
    """
    A generator for serializing schemas as Entity-Relationship diagrams.

    Currently this generates diagrams in mermaid syntax, but in future
    this could easily be extended to have for example a direct SVG or PNG
    generator using PyGraphViz, similar to erdantic.

    This class adds quotation marks to the names of classes and 
    relations to make it safer.
    """

    # ClassVars
    generatorname = os.path.basename(__file__)
    generatorversion = "0.0.1"
    valid_formats = ["markdown", "mermaid"]
    uses_schemaloader = False
    requires_metamodel = False

    structural: bool = True
    """If True, then only the tree_root and entities reachable from the root are drawn"""

    exclude_attributes: bool = False
    """If True, do not include attributes in entities"""

    genmeta: bool = False
    gen_classvars: bool = True
    gen_slots: bool = True
    no_types_dir: bool = False
    use_slot_uris: bool = False

    def __post_init__(self):
        self.schemaview = SchemaView(self.schema)
        super().__post_init__()

    
    def generate_diagram(self, **kwargs) -> ERDiagram:
        """
        Generate an ER Diagram object from the schema.

        :return: ERDiagram object
        """
        diagram = ERDiagram()
        for cn in self.schemaview.all_classes():
            self.add_class(cn, diagram)
        return diagram

    def serialize(self) -> MERMAID_SERIALIZATION:
        """
        Serialize a schema as an ER Diagram.

        If a tree_root is present in the schema, then only Entities traversable
        from here will be included. Otherwise, all Entities will be included.

        :return: mermaid string
        """
        sv = self.schemaview
        structural_roots = [cn for cn, c in sv.all_classes().items() if c.tree_root]
        if self.structural and structural_roots:
            return self.serialize_classes(structural_roots, follow_references=True)
        else:
            diagram = self.generate_diagram()
            return self.serialize_diagram(diagram)

    def serialize_classes(
        self,
        class_names: List[Union[str, ClassDefinitionName]],
        follow_references=False,
        max_hops: int = None,
    ) -> MERMAID_SERIALIZATION:
        """
        Serialize a list of classes as an ER Diagram.

        This will also traverse the reference graph and include any Entities reachable from the
        specified classes.

        By default, all reachable Entities are included, unless max_hops is specified.

        :param class_names: initial seed
        :param follow_references: if True, follow references even if not inlined
        :param max_hops: maximum number of hops to follow references
        :return:
        """
        visited = set()
        sv = self.schemaview
        stack = [(cn, 0) for cn in class_names]
        diagram = ERDiagram()
        while stack:
            cn, depth = stack.pop()
            if cn in visited:
                continue
            self.add_class(cn, diagram)
            visited.add(cn)
            if max_hops is not None and depth >= max_hops:
                continue
            
            cls = sv.get_class(cn)
            for mixin in cls.mixins:
                if mixin not in visited:
                    stack.append((mixin, depth + 1))

            for slot in sv.class_induced_slots(cn):
                ranges = self.retrieve_ranges_from_constraints(slot)
                for rng in ranges:
                    if rng in sv.all_classes():
                        if follow_references or sv.is_inlined(slot):
                            if rng not in visited:
                                stack.append((rng, depth + 1))
        return self.serialize_diagram(diagram)
    
    def add_class(self, class_name: ClassDefinitionName, diagram: ERDiagram) -> None:
        """
        Add a class to the ER Diagram.

        :param class_name: ClassDefinitionName
        :param diagram: ER Diagram
        :return:
        """
        sv = self.schemaview
        cls = sv.get_class(class_name)
        entity = Entity(name=camelcase(cls.name))
        diagram.entities.append(entity)
        for slot in self.class_induced_slots(class_name):
            ranges = self.retrieve_ranges_from_constraints(slot)
            if len(ranges)==0:
                slot.range = sv.schema.default_range or "string"
            else:
                for range in ranges:
                    if range in sv.all_classes():
                        self.add_relationship(entity, slot, range, diagram)
                    else:
                        self.add_attribute(entity, slot, range)

        for mixin in cls.mixins:
            rel_type = RelationshipType(
                right_cardinality=Cardinality(
                    required=True, multivalued=False, is_left=True
                    ),
                    left_cardinality=Cardinality(is_left=True),
                    )
            rel = Relationship(
                first_entity=entity.name,
                relationship_type=rel_type,
                second_entity=camelcase(sv.get_class(mixin).name),
                relationship_label="mixin"
                )
            diagram.relationships.append(rel)

    def add_relationship(self, entity: Entity, slot: SlotDefinition, range: Union[str, ElementName],  diagram: ERDiagram) -> None:
        """
        Add a relationship to the ER Diagram.

        :param class_name: ClassDefinitionName
        :param slot: SlotDefinition
        :param diagram: ER Diagram
        :return:
        """
        sv = self.schemaview
        rel_type = RelationshipType(
            right_cardinality=Cardinality(
                required=slot.required is True, multivalued=slot.multivalued is True, is_left=True
            ),
            left_cardinality=Cardinality(is_left=False),
        )
        rel = Relationship(
            first_entity=entity.name,
            relationship_type=rel_type,
            second_entity=camelcase(sv.get_class(range).name),
            relationship_label=slot.name,
        )
        diagram.relationships.append(rel)
    
    def add_attribute(self, entity: Entity, slot: SlotDefinition, range: Union[str, ElementName]) -> None:
        """
        Add an attribute to the ER Diagram.

        :param class_name: Class
        :param slot: SlotDefinition
        :return:
        """
        if self.exclude_attributes:
            return
        dt = range
        if slot.multivalued:
            # NOTE: mermaid does not support []s or *s in attribute types
            dt = f"{dt}List"
        attr = Attribute(name=underscore(slot.name), datatype=dt)
        entity.attributes.append(attr)

    def retrieve_ranges_from_constraints(self, slot: SlotDefinition) -> List[Union[str, ElementName]]:
        """Retrieve ranges from the slot definition."""
        ranges = []
        if slot.range is not None:
            ranges.append(slot.range)
        
        constraints = ["any_of", "exactly_one_of", "all_of"]
        for constr in constraints:
            if getattr(slot, constr):
                for spec in  getattr(slot, constr):
                    if spec.range is not None and spec.range not in ranges:
                        ranges.append(spec.range)
        return ranges


    def class_induced_slots(self, class_name: CLASS_NAME = None, imports=True) -> List[SlotDefinition]:
        """
        All slots that are asserted or inferred for a class, with their inferred semantics

        :param class_name:
        :param imports:
        :return: inferred slot definition
        """
        return [self.induced_slot(sn, class_name, imports=imports) for sn in self.schemaview.class_slots(class_name)]
    
    
    def is_range_constraint_present(self, constraint_specs: list) -> bool:
        """Return True if there are range constraints."""
        if constraint_specs:
            for spec in constraint_specs:
                if "range" in spec and spec.range is not None:
                    return True
        return False

    def propagate_attrs_to_constraints(self, slot_def: SlotDefinition ) -> SlotDefinition:
        """Propagate inlined, inlined_as_list to constraints."""
        constraints = ["any_of", "exactly_one_of", "all_of"]
        for constr in constraints:
            if getattr(slot_def, constr):
                new_specs = []
                for spec in  getattr(slot_def, constr):
                    new_spec = copy(spec)
                    if spec.range is not None:
                        if "inlined" not in spec or spec.inlined is None:
                            new_spec.inlined = slot_def.inlined
                        if "inlined_as_list" not in spec or spec.inlined_as_list is None:
                            if spec.inlined:
                                new_spec.inlined_as_list = slot_def.inlined_as_list
                    new_specs.append(new_spec)
                setattr(slot_def, constr, new_specs) 
        return slot_def

    def cleanup_range_constraints(self, slot_def: SlotDefinition ) -> SlotDefinition:
        """Propagate inlined, inlined_as_list to constraints."""
        constraints = ["any_of", "exactly_one_of", "all_of"]
        for constr in constraints:
            if getattr(slot_def, constr):
                new_specs = []
                for spec in getattr(slot_def, constr):
                    new_spec = copy(spec)
                    if "range" in new_spec and new_spec.range is None:
                        new_spec.range = None
                    new_specs.append(new_spec)
                setattr(slot_def, constr, new_specs) 
        return slot_def


    def induced_slot(self, slot_name: SLOT_NAME, class_name: CLASS_NAME = None, imports=True,
                     mangle_name=False) -> SlotDefinition:
        """
        Given a slot, in the context of a particular class, yield a dynamic SlotDefinition that
        has all properties materialized.

        This makes use of schema slots, such as attributes, slot_usage. It also uses ancestor relationships
        to infer missing values, for inheritable slots

        :param slot_name: slot to be queries
        :param class_name: class used as context
        :param imports: include imports closure
        :return: dynamic slot constructed by inference
        """
        if class_name:
            cls = self.schemaview.get_class(class_name, imports, strict=True)
        else:
            cls = None

        # attributes take priority over schema-level slot definitions, IF
        # the attributes is declared for the class or an ancestor
        slot_comes_from_attribute = False
        if cls:
            slot = self.schemaview.get_slot(slot_name, imports, attributes=False)
            # traverse ancestors (reflexive), starting with
            # the main class
            
            for an in self.schemaview.class_ancestors(class_name):
                a = self.schemaview.get_class(an, imports)
                if slot_name in a.attributes:
                    slot = a.attributes[slot_name]
                    slot_comes_from_attribute = True
                    break
        else:
            slot = self.schemaview.get_slot(slot_name, imports, attributes=True)

        if slot is None:
            raise ValueError(f"No such slot {slot_name} as an attribute of {class_name} ancestors "
                             "or as a slot definition in the schema")

        # copy the slot, as it will be modified
        induced_slot = copy(slot)
        if not slot_comes_from_attribute:
            slot_anc_names = self.schemaview.slot_ancestors(slot_name, reflexive=True)
            # inheritable slot: first propagate from ancestors
            for anc_sn in reversed(slot_anc_names):
                anc_slot = self.schemaview.get_slot(anc_sn, attributes=False)
                for metaslot_name in SlotDefinition._inherited_slots:
                    if getattr(anc_slot, metaslot_name, None):
                        setattr(induced_slot, metaslot_name, copy(getattr(anc_slot, metaslot_name)))
        COMBINE = {
            'maximum_value': lambda x, y: min(x, y),
            'minimum_value': lambda x, y: max(x, y),
        }
        if not cls:
            propagated_from = []
        else:
            propagated_from = self.schemaview.class_ancestors(class_name, reflexive=True, mixins=True)
        constraints = ["any_of", "exactly_one_of", "all_of"]
        # iterate through all metaslots, and potentially populate metaslot value for induced slot
        for metaslot_name in self.schemaview._metaslots_for_slot():
            # inheritance of slots; priority order
            #   slot-level assignment < ancestor slot_usage < self slot_usage
            v = getattr(induced_slot, metaslot_name, None)
            for an in reversed(propagated_from):
                induced_slot.owner = an
                a = self.schemaview.get_class(an, imports)
                anc_slot_usage = a.slot_usage.get(slot_name, {})
                v2 = getattr(anc_slot_usage, metaslot_name, None)                    
                if v is None:
                    v = v2
                else:
                    if metaslot_name in COMBINE:
                        if v2 is not None:
                            v = COMBINE[metaslot_name](v, v2)
                    else:
                        if v2 is not None:
                            v = v2
                            logging.debug(f'{v} takes precedence over {v2} for {induced_slot.name}.{metaslot_name}')
                if metaslot_name in constraints:
                    # if the slot usage constrains the range, then we need to set the range to None
                    if v is not None and self.is_range_constraint_present(v):
                        induced_slot.range = None
                        induced_slot = self.propagate_attrs_to_constraints(induced_slot)
                if metaslot_name == "range":        
                    # based on class ancestor range and range constraints
                    # range constraints need also to be cleaned up
                    induced_slot = self.cleanup_range_constraints(induced_slot)

            if v is None:
                if metaslot_name == 'range':
                    v = self.schema.default_range
            if v is not None:
                setattr(induced_slot, metaslot_name, v)
        if slot.inlined_as_list:
            slot.inlined = True
        if slot.identifier or slot.key:
            slot.required = True
        if mangle_name:
            mangled_name = f'{camelcase(class_name)}__{underscore(slot_name)}'
            induced_slot.name = mangled_name
        if not induced_slot.alias:
            induced_slot.alias = underscore(slot_name)
        induced_slot = self.propagate_attrs_to_constraints(induced_slot)
        for c in self.schemaview.all_classes().values():
            if induced_slot.name in c.slots or induced_slot.name in c.attributes:
                if c.name not in induced_slot.domain_of:
                    induced_slot.domain_of.append(c.name)
        
        return induced_slot