"""
gen_yaml_fixed.py — drop-in replacement for `gen-yaml` that handles structured
annotations (JsonObj / Annotation objects) that the stock PyYAML representer
cannot serialise.

Background
----------
When LinkML merges the full import tree the shorthand annotation syntax:

    annotations:
      label_en: "Size"
      label_de: "Größe"

is inflated by linkml_runtime into Annotation objects stored inside a JsonObj
container:

    JsonObj(label_en=Annotation({'tag': 'label_en', 'value': 'Size'}), ...)

PyYAML's default representer has no handler for these types and raises:

    yaml.representer.RepresenterError: ('cannot represent an object', JsonObj(...))

Fix: register custom representers *before* the generator serialises anything so
that:
  - Annotation  → {tag: ..., value: ...}   (matches the expanded form already
                                            written for other annotations in the
                                            merged output)
  - JsonObj     → plain dict of its public attributes

The schema source files are correct and unchanged.

Usage (called by justfile _gen-yaml recipe)
-------------------------------------------
    uv run python gen_yaml_fixed.py <schema_path>
"""

import sys
import yaml

# ── 1. Register Annotation representer ───────────────────────────────────────
try:
    from linkml_runtime.linkml_model.meta import Annotation

    def _represent_annotation(dumper: yaml.Dumper, ann: Annotation) -> yaml.Node:
        return dumper.represent_dict({"tag": str(ann.tag), "value": str(ann.value)})

    yaml.add_representer(Annotation, _represent_annotation)
    yaml.add_representer(Annotation, _represent_annotation, Dumper=yaml.SafeDumper)
except ImportError:
    pass  # linkml_runtime not available — gen-yaml will surface its own error

# ── 2. Register JsonObj representer ──────────────────────────────────────────
try:
    from linkml_runtime.utils.yamlutils import JsonObj

    def _represent_jsonobj(dumper: yaml.Dumper, obj: JsonObj) -> yaml.Node:
        # Exclude private / dunder attributes injected by the runtime
        data = {k: v for k, v in vars(obj).items() if not k.startswith("_")}
        return dumper.represent_dict(data)

    yaml.add_representer(JsonObj, _represent_jsonobj)
    yaml.add_representer(JsonObj, _represent_jsonobj, Dumper=yaml.SafeDumper)
except ImportError:
    pass

# ── 3. Run the generator ──────────────────────────────────────────────────────
from linkml.generators.yamlgen import YAMLGenerator

if len(sys.argv) < 2:
    print("Usage: gen_yaml_fixed.py <schema_path>", file=sys.stderr)
    sys.exit(1)

gen = YAMLGenerator(sys.argv[1])
print(gen.serialize())
