# config.public.mk

# This file is public in git. No sensitive info allowed.

###### schema definition variables, used by justfile

# Note:
# - just works fine with quoted variables of dot-env files like this one
LINKML_SCHEMA_NAME="inkind_knowledge_repo"
LINKML_SCHEMA_AUTHOR="Natalia Ruemmele <natalia.ruemmele@inkind.at>"
LINKML_SCHEMA_DESCRIPTION="Formal knowledge representation for in-kind donation coordination. Defines the domain schema, category schemas with constraint rules and dependent field maps, and organization configuration instances."
LINKML_SCHEMA_SOURCE_DIR="src/inkind_knowledge_repo/schema"

###### linkml generator variables, used by justfile

## gen-project configuration file
LINKML_GENERATORS_CONFIG_YAML=config.yaml

## pass args if gendoc ignores config.yaml (i.e. --no-mergeimports)
LINKML_GENERATORS_DOC_ARGS="--template-directory docs/templates-linkml"

## pass args to workaround genowl rdfs config bug (linkml#1453)
##   (i.e. --no-type-objects --no-metaclasses --metadata-profile=rdfs)
# LINKML_GENERATORS_OWL_ARGS="--no-type-objects --no-metaclasses --metadata-profile=rdfs"
LINKML_GENERATORS_OWL_ARGS=

## pass args to pydantic generator which isn't supported by gen-project
## https://github.com/linkml/linkml/issues/2537
LINKML_GENERATORS_PYDANTIC_ARGS=
