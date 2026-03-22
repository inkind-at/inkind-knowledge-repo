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
                    'coordination. Defines the domain schema, category schemas '
                    'with constraint rules and dependent field maps, and '
                    'organization configuration instances.',
     'id': 'https://w3id.org/nruemmele/inkind-knowledge-repo',
     'imports': ['linkml:types'],
     'license': 'MIT',
     'name': 'inkind-knowledge-repo',
     'prefixes': {'PATO': {'prefix_prefix': 'PATO',
                           'prefix_reference': 'http://purl.obolibrary.org/obo/PATO_'},
                  'biolink': {'prefix_prefix': 'biolink',
                              'prefix_reference': 'https://w3id.org/biolink/'},
                  'example': {'prefix_prefix': 'example',
                              'prefix_reference': 'https://example.org/'},
                  'inkind_knowledge_repo': {'prefix_prefix': 'inkind_knowledge_repo',
                                            'prefix_reference': 'https://w3id.org/nruemmele/inkind-knowledge-repo/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'schema': {'prefix_prefix': 'schema',
                             'prefix_reference': 'http://schema.org/'}},
     'see_also': ['https://nruemmele.github.io/inkind-knowledge-repo'],
     'source_file': 'src/inkind_knowledge_repo/schema/inkind_knowledge_repo.yaml',
     'title': 'inkind-knowledge-repo'} )

class PersonStatus(str, Enum):
    ALIVE = "ALIVE"
    """
    the person is living
    """
    DEAD = "DEAD"
    """
    the person is deceased
    """
    UNKNOWN = "UNKNOWN"
    """
    the vital status is not known
    """



class NamedThing(ConfiguredBaseModel):
    """
    A generic grouping for any identifiable entity
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'schema:Thing',
         'from_schema': 'https://w3id.org/nruemmele/inkind-knowledge-repo'})

    id: str = Field(default=..., description="""A unique identifier for a thing""", json_schema_extra = { "linkml_meta": {'domain_of': ['NamedThing'], 'slot_uri': 'schema:identifier'} })
    name: Optional[str] = Field(default=None, description="""A human-readable name for a thing""", json_schema_extra = { "linkml_meta": {'domain_of': ['NamedThing'], 'slot_uri': 'schema:name'} })
    description: Optional[str] = Field(default=None, description="""A human-readable description for a thing""", json_schema_extra = { "linkml_meta": {'domain_of': ['NamedThing'], 'slot_uri': 'schema:description'} })


class Person(NamedThing):
    """
    Represents a Person
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/nruemmele/inkind-knowledge-repo',
         'slot_usage': {'primary_email': {'name': 'primary_email',
                                          'pattern': '^\\S+@[\\S+\\.]+\\S+'}}})

    primary_email: Optional[str] = Field(default=None, description="""The main email address of a person""", json_schema_extra = { "linkml_meta": {'domain_of': ['Person'], 'slot_uri': 'schema:email'} })
    birth_date: Optional[date] = Field(default=None, description="""Date on which a person is born""", json_schema_extra = { "linkml_meta": {'domain_of': ['Person'], 'slot_uri': 'schema:birthDate'} })
    age_in_years: Optional[int] = Field(default=None, description="""Number of years since birth""", json_schema_extra = { "linkml_meta": {'domain_of': ['Person']} })
    vital_status: Optional[PersonStatus] = Field(default=None, description="""living or dead status""", json_schema_extra = { "linkml_meta": {'domain_of': ['Person']} })
    id: str = Field(default=..., description="""A unique identifier for a thing""", json_schema_extra = { "linkml_meta": {'domain_of': ['NamedThing'], 'slot_uri': 'schema:identifier'} })
    name: Optional[str] = Field(default=None, description="""A human-readable name for a thing""", json_schema_extra = { "linkml_meta": {'domain_of': ['NamedThing'], 'slot_uri': 'schema:name'} })
    description: Optional[str] = Field(default=None, description="""A human-readable description for a thing""", json_schema_extra = { "linkml_meta": {'domain_of': ['NamedThing'], 'slot_uri': 'schema:description'} })

    @field_validator('primary_email')
    def pattern_primary_email(cls, v):
        pattern=re.compile(r"^\S+@[\S+\.]+\S+")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid primary_email format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid primary_email format: {v}"
            raise ValueError(err_msg)
        return v


class PersonCollection(ConfiguredBaseModel):
    """
    A holder for Person objects
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/nruemmele/inkind-knowledge-repo',
         'tree_root': True})

    people: Optional[list[Person]] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['PersonCollection']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
NamedThing.model_rebuild()
Person.model_rebuild()
PersonCollection.model_rebuild()
