"""
Custom UI descriptor generator for LinkML models.

author: Natalia Ruemmele
"""

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from linkml.utils.generator import Generator
from linkml_runtime.utils.schemaview import SchemaView
from linkml_runtime.linkml_model.meta import (
    AnonymousSlotExpression,
    ClassDefinition,
    ClassRule,
    SlotDefinition,
)


@dataclass
class UiDescriptorGenerator(Generator):
    """
    Generator for creating a UI descriptor from a LinkML model.
    """

    # ClassVars
    generatorname = "ui_descriptor"
    generatorversion = "0.2.0"
    valid_formats = ["json"]
    uses_schemaloader = False

    # object vars
    top_class: str = "DonationItem"

    SUPPORTED_LOCALES = ("en", "de")

    INTERNAL_SLOTS = {
        "id",
        "created_at",
        "updated_at",
        "attribute_completeness",
        "storage_unit",
        "lifecycle_state",
    }

    def _resolve_top_class(self) -> None:
        if self.top_class:
            if self.schemaview.get_class(self.top_class) is None:
                raise ValueError(f"top_class '{self.top_class}' not found in schema")
            return

        if self.schemaview.get_class("DonationItem") is not None:
            self.top_class = "DonationItem"
            return

        all_classes = list(self.schemaview.all_classes())
        if not all_classes:
            raise ValueError("Schema contains no classes")
        self.top_class = sorted(all_classes)[0]

    def generate(self) -> Dict[str, Any]:
        self._resolve_top_class()
        descriptors = {}
        for class_name in [self.top_class] + self._get_concrete_subclasses():
            descriptors[class_name] = self._build_descriptor(class_name)
        return descriptors

    def serialize(self, output_dir: str = ".", **kwargs) -> None:
        """
        Write three files to output_dir:
          <top_class>.ui.json  — the UI descriptor
          labels-en.json       — English labels keyed by element name
          labels-de.json       — German labels keyed by element name

        Labels are read from label_en / label_de annotations on schema
        elements. If an annotation is absent the element name is used
        as-is — no humanisation, no fallback transformation.
        """
        os.makedirs(output_dir, exist_ok=True)
        descriptor = self.generate()

        descriptor_path = os.path.join(
            output_dir, f"{self.top_class}.ui.json"
        )
        with open(descriptor_path, "w", encoding="utf-8") as f:
            json.dump(descriptor, f, indent=2, ensure_ascii=False)

        for locale in self.SUPPORTED_LOCALES:
            labels = self._collect_labels(descriptor, locale)
            labels_path = os.path.join(output_dir, f"labels-{locale}.json")
            with open(labels_path, "w", encoding="utf-8") as f:
                json.dump(labels, f, indent=2, ensure_ascii=False)

    # ── helpers ────────────────────────────────────────────────────────────

    def _is_internal_slot(self, slot_name: str) -> bool:
        return slot_name in self.INTERNAL_SLOTS

    def _get_concrete_subclasses(self) -> List[str]:
        result: List[str] = []
        for candidate in self.schemaview.class_descendants(self.top_class):
            try:
                cls = self.schemaview.get_class(candidate)
            except Exception:
                continue
            if candidate == self.top_class:
                continue
            if getattr(cls, "abstract", False):
                continue
            if getattr(cls, "mixin", False):
                continue
            if self.top_class not in self.schemaview.class_ancestors(candidate):
                continue
            result.append(candidate)
        return result

    def _map_slot_type(self, slot: SlotDefinition) -> str:
        # Preserve original range for enum lookup (case-sensitive);
        # lowercase only for primitive comparisons.
        slot_range_raw = getattr(slot, "range", None) or ""
        slot_range = slot_range_raw.lower()
        if slot_range in {"boolean", "bool"}:
            return "boolean"
        if slot_range in {"int", "integer"}:
            return "integer"
        if slot_range in {"date", "datetime"}:
            return "date"
        if slot_range == "string":
            return "string"
        try:
            # Use original casing — SchemaView enum lookup is case-sensitive
            enum_def = self.schemaview.get_enum(slot_range_raw)
            if enum_def is not None:
                return "enum"
        except Exception:
            pass
        return "string"

    def _get_enum_values(self, enum_name: Optional[str]) -> Optional[List[str]]:
        """Return permissible value name strings for enum_name."""
        if not enum_name:
            return None
        try:
            enum_def = self.schemaview.get_enum(enum_name)
        except Exception:
            return None
        if not enum_def or not getattr(enum_def, "permissible_values", None):
            return None
        return [pv.text for pv in enum_def.permissible_values.values()]

    def _parse_condition_values(self, field_name: str, condition: SlotDefinition) -> List[Any]:
        """
        Extract the list of values expressed by a slot condition expression.

        For none_of: returns the COMPLEMENT — all enum values for field_name
        minus the excluded ones. field_name must be the TARGET (postcondition)
        field so the correct enum is resolved.

        For any_of / equals_string / equals_number: returns the stated values.
        """
        if condition is None:
            return []

        target_values: List[Any] = []

        if getattr(condition, "equals_string", None) is not None:
            target_values = [condition.equals_string]
        elif getattr(condition, "equals_number", None) is not None:
            target_values = [condition.equals_number]
        elif getattr(condition, "any_of", None):
            for item in condition.any_of:
                if getattr(item, "equals_string", None) is not None:
                    target_values.append(item.equals_string)
                elif getattr(item, "equals_number", None) is not None:
                    target_values.append(item.equals_number)
        elif getattr(condition, "none_of", None):
            excluded: Set[Any] = set()
            for item in condition.none_of:
                if getattr(item, "equals_string", None) is not None:
                    excluded.add(item.equals_string)
                elif getattr(item, "equals_number", None) is not None:
                    excluded.add(item.equals_number)
            # Resolve complement against field_name's enum.
            # Caller must pass the TARGET field name here.
            slot_def = self.schemaview.get_slot(field_name)
            if slot_def and slot_def.range:
                enum_values = self._get_enum_values(slot_def.range)
                if enum_values is not None:
                    target_values = [v for v in enum_values if v not in excluded]
                else:
                    self.logger.warning(
                        f"none_of on field '{field_name}': enum '{slot_def.range}' "
                        f"could not be resolved — complement will be empty"
                    )
            else:
                self.logger.warning(
                    f"none_of on field '{field_name}': slot has no declared range "
                    f"— complement will be empty"
                )

        return [v for v in target_values if v is not None]

    def _translate_lifecycle_condition(self, cond: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
        if "lifecycle_state" in cond:
            new_values = []
            for v in cond["lifecycle_state"]:
                if str(v).lower() == "sorted":
                    new_values.append("sorting_in_progress")
                else:
                    new_values.append(v)
            cond["lifecycle_state"] = new_values
        return cond

    def _merge_conditions(
        self, existing: Dict[str, List[Any]], addition: Dict[str, List[Any]]
    ) -> Dict[str, List[Any]]:
        for key, values in addition.items():
            if key in existing:
                existing[key] = sorted(set(existing[key]).intersection(set(values)))
            else:
                existing[key] = list(values)
        return existing

    COMPLETENESS_KEYS = frozenset({
        "completeness_minimal",
        "completeness_standard",
        "completeness_detailed",
    })

    def _get_completeness(self, class_name: str) -> Dict[str, Set[str]]:
        """
        Return completeness tier sets for class_name by walking its ancestor
        list and finding the first class (mixin OR concrete) that declares at
        least one completeness tier annotation.

        Convention:
          - Category mixins (ClothingCategory, etc.) carry the completeness
            annotations for their concrete item subclasses.
          - The top class (e.g. DonationItem) carries its own completeness
            annotations directly — it is not a mixin.
          - CategoryMixin and other shared base mixins have no completeness
            annotations and are skipped naturally.

        Annotation values are comma-separated slot name strings stored as
        Annotation objects; .value is extracted explicitly.
        """
        for ancestor in self.schemaview.class_ancestors(class_name):
            try:
                cls = self.schemaview.get_class(ancestor)
            except Exception:
                continue
            a = getattr(cls, "annotations", None) or {}
            if not any(k in a for k in self.COMPLETENESS_KEYS):
                continue

            def parse(key: str) -> Set[str]:
                if key not in a:
                    return set()
                raw = getattr(a[key], "value", None) or str(a[key])
                return {item.strip() for item in raw.split(",") if item.strip()}

            return {
                "minimal":  parse("completeness_minimal"),
                "standard": parse("completeness_standard"),
                "detailed": parse("completeness_detailed"),
            }
        return {"minimal": set(), "standard": set(), "detailed": set()}

    def _collect_applicable_rules(self, class_name: str) -> List[ClassRule]:
        rules: List[ClassRule] = []
        for ancestor in self.schemaview.class_ancestors(class_name):
            try:
                cls = self.schemaview.get_class(ancestor)
            except Exception:
                continue
            rules.extend(getattr(cls, "rules", []) or [])
        return rules

    def _get_annotation_label(
        self, annotations: Dict, name: str, locale: str
    ) -> str:
        """
        Return the label for name in locale by reading the label_<locale>
        annotation. Falls back to name itself if the annotation is absent.
        No humanisation — the raw element name is the fallback.
        """
        key = f"label_{locale}"
        ann = annotations.get(key)
        if ann is None:
            return name
        return getattr(ann, "value", None) or str(ann) or name

    def _collect_labels(
        self, descriptor: Dict[str, Any], locale: str
    ) -> Dict[str, str]:
        """
        Walk the descriptor and collect {name: label} for every element
        that appears in it: class names, slot names, and enum value names.

        Labels are read from label_<locale> annotations on the corresponding
        schema elements. If the annotation is absent, the element name is
        used as the label value unchanged.

        Only elements referenced in the descriptor are included — internal
        slots, abstract classes, and unused enums are excluded.
        """
        labels: Dict[str, str] = {}

        for class_name, class_desc in descriptor.items():
            # Class label
            try:
                cls_def = self.schemaview.get_class(class_name)
                a = getattr(cls_def, "annotations", None) or {}
            except Exception:
                a = {}
            labels[class_name] = self._get_annotation_label(a, class_name, locale)

            # Slot labels
            for field_entry in class_desc.get("fields", []):
                slot_name = field_entry["name"]
                if slot_name not in labels:
                    slot_def = self.schemaview.get_slot(slot_name)
                    a = getattr(slot_def, "annotations", None) or {} \
                        if slot_def else {}
                    labels[slot_name] = self._get_annotation_label(
                        a, slot_name, locale
                    )

            # Enum value labels
            for enum_name, values in class_desc.get("enums", {}).items():
                try:
                    enum_def = self.schemaview.get_enum(enum_name)
                    pvs = getattr(enum_def, "permissible_values", {}) or {}
                except Exception:
                    pvs = {}
                for value in values:
                    if value not in labels:
                        pv = pvs.get(value)
                        a = getattr(pv, "annotations", None) or {} \
                            if pv else {}
                        labels[value] = self._get_annotation_label(
                            a, value, locale
                        )

        return labels

    # ── options_depend_on accumulator ──────────────────────────────────────

    def _accumulate_options_entry(
        self,
        accumulator: Dict[str, List[Dict[str, Any]]],
        target_field: str,
        conditions: Dict[str, List[Any]],
        allowed_values: List[Any],
    ) -> None:
        """
        Append one entry to the options_depend_on list for target_field.

        Format:
          {"when": {field: [v1, v2, ...], ...}, "options": [...allowed...]}

        conditions — all precondition fields (AND semantics).
          Each field maps to a list of triggering values (OR within the list).
        allowed_values — the permitted options for target_field when all
          when-conditions hold.

        Single-key precondition example:
          conditions = {"demographic": ["baby"]}
          → {"when": {"demographic": ["baby"]}, "options": ["baby_0_3m", ...]}

        Multi-key precondition example:
          conditions = {"subcategory": ["underwear"], "usage": ["used"]}
          → {"when": {"subcategory": ["underwear"], "usage": ["used"]},
             "options": [...]}

        Multi-value single-key example (vm-size-adult):
          conditions = {"demographic": ["adult_male", "adult_female", "unisex"]}
          → {"when": {"demographic": ["adult_male", "adult_female", "unisex"]},
             "options": ["xs", "s", ...]}
          — one entry covers all three demographics instead of three separate entries.
        """
        accumulator.setdefault(target_field, []).append({
            "when": {k: list(v) for k, v in conditions.items()},
            "options": list(allowed_values),
        })

    # ── rule builders ──────────────────────────────────────────────────────

    def _build_uc_entry(
        self, rule: ClassRule, conditions: Dict[str, List[Any]]
    ) -> Dict[str, Any]:
        description = (getattr(rule, "description", "") or "").strip()
        first_sentence = description.split(".")[0].strip()

        severity = "block"
        text = description.lower()
        if "warn" in text or "should not" in text:
            severity = "warn"

        message = first_sentence
        if "action:" in description:
            message = description

        return {
            "id": getattr(rule, "title", ""),
            "when": conditions,
            "severity": severity,
            "message": message,
        }

    # ── descriptor builders ────────────────────────────────────────────────

    def _build_descriptor(self, class_name: str) -> Dict[str, Any]:
        """
        Build a UI descriptor for any class — top class or subclass.
        No special-casing: the top class goes through exactly the same
        path as every concrete subclass.

        dispatches_to is emitted on any slot with designates_type: true,
        regardless of which class declares it.

        required_in_step is True when the slot is a direct slot of the
        top class (base operational fields) OR appears in completeness_minimal.

        enums are collected from all enum-typed fields in this descriptor.
        """
        slots = self.schemaview.class_induced_slots(class_name)
        completeness = self._get_completeness(class_name)

        # Accumulators
        lc_visible: Dict[str, Dict[str, List[Any]]] = {}
        # options_depend_on: target_field → list of {"when": {...}, "options": [...]}
        options_depend_on: Dict[str, List[Dict[str, Any]]] = {}
        auto_set_from: Dict[str, Dict[str, Dict[Any, Any]]] = {}
        uc_rules: List[Dict[str, Any]] = []

        for rule in self._collect_applicable_rules(class_name):
            title = (getattr(rule, "title", "") or "").lower()
            description = (getattr(rule, "description", "") or "").strip()
            pre = getattr(rule, "preconditions", None)
            post = getattr(rule, "postconditions", None)

            if not pre or not getattr(pre, "slot_conditions", None):
                continue

            # Build conditions dict: {field: [values]} from preconditions.
            # All fields are AND; values within each field are OR.
            conditions: Dict[str, List[Any]] = {}
            for slot_name, slot_cond in pre.slot_conditions.items():
                values = self._parse_condition_values(slot_name, slot_cond)
                if values:
                    conditions[slot_name] = values
            conditions = self._translate_lifecycle_condition(conditions)

            # ── lc-* → visible_when ────────────────────────────────────────
            if title.startswith("lc-") and post and getattr(post, "slot_conditions", None):
                for target, target_cond in post.slot_conditions.items():
                    if self._is_internal_slot(target):
                        continue
                    if not getattr(target_cond, "required", False):
                        continue
                    lc_visible.setdefault(target, {})
                    self._merge_conditions(lc_visible[target], conditions)
                continue

            # ── vm-* → options_depend_on or auto_set_from ──────────────────
            if title.startswith("vm-") and post and getattr(post, "slot_conditions", None):
                target_items = list(post.slot_conditions.items())
                if len(target_items) != 1:
                    self.logger.warning(
                        f"vm- rule '{title}' has {len(target_items)} postcondition "
                        f"slot_conditions (expected exactly 1) — skipped"
                    )
                    continue

                target_field, target_cond = target_items[0]
                has_none_of = bool(getattr(target_cond, "none_of", None))
                is_uc_text = (
                    "block" in description.lower()
                    or "must not" in description.lower()
                )

                if has_none_of and is_uc_text:
                    # Ambiguous: schema should use any_of for the allowlist instead.
                    self.logger.warning(
                        f"vm- rule '{title}' has none_of postcondition AND blocking "
                        f"description — ambiguous routing. Rewrite postcondition "
                        f"using any_of to express the allowed values explicitly. "
                        f"Rule skipped."
                    )
                    continue

                if has_none_of:
                    # none_of → options_depend_on complement.
                    # Pass target_field so the correct enum is resolved.
                    target_values = self._parse_condition_values(target_field, target_cond)
                elif is_uc_text:
                    # Blocking vm- rule (no none_of) → treat as UC.
                    uc_rules.append(self._build_uc_entry(rule, conditions))
                    continue
                else:
                    target_values = self._parse_condition_values(target_field, target_cond)

                target_slot = self.schemaview.get_slot(target_field)
                target_type = self._map_slot_type(target_slot or SlotDefinition({}))

                if target_type == "enum":
                    # Emit one options_depend_on entry for this rule.
                    # conditions may have one or more keys (multi-key support).
                    self._accumulate_options_entry(
                        options_depend_on, target_field, conditions, target_values
                    )
                else:
                    # auto_set_from: only valid for single-key preconditions.
                    if len(conditions) != 1:
                        self.logger.warning(
                            f"vm- rule '{title}' has multi-key precondition for "
                            f"non-enum target '{target_field}' — auto_set_from "
                            f"does not support multi-key conditions. Rule skipped."
                        )
                        continue
                    source_field, source_values = next(iter(conditions.items()))
                    auto_set_from.setdefault(target_field, {}).setdefault(source_field, {})
                    for sv in source_values:
                        derived = target_values[0] if target_values else None
                        if target_type == "boolean" and isinstance(derived, str):
                            derived = derived.lower() == "true"
                        auto_set_from[target_field][source_field][sv] = derived
                continue

            # ── uc-* → rules array ─────────────────────────────────────────
            if title.startswith("uc-"):
                uc_rules.append(self._build_uc_entry(rule, conditions))
                continue

        # ── assemble field entries ─────────────────────────────────────────
        field_entries: List[Dict[str, Any]] = []
        enum_registry: Dict[str, List[Any]] = {}
        # Built lazily — only when a designates_type slot is encountered.
        dispatch_map: Optional[Dict[str, str]] = None

        for slot in slots:
            if self._is_internal_slot(slot.name):
                continue
            field_entry: Dict[str, Any] = {
                "name": slot.name,
                "type": self._map_slot_type(slot),
                "required_in_step": slot.name in completeness["minimal"],
            }
            if field_entry["type"] == "enum":
                field_entry["enum"] = slot.range
                if slot.range and slot.range not in enum_registry:
                    values = self._get_enum_values(slot.range)
                    if values is not None:
                        enum_registry[slot.range] = values

            if getattr(slot, "multivalued", False):
                field_entry["multivalued"] = True

            if getattr(slot, "designates_type", False):
                if dispatch_map is None:
                    dispatch_map = {
                        sub: f"{sub}.ui.json"
                        for sub in self._get_concrete_subclasses()
                    }
                field_entry["dispatches_to"] = dispatch_map

            if slot.name in completeness["minimal"]:
                field_entry["completeness"] = "minimal"
            elif slot.name in completeness["standard"]:
                field_entry["completeness"] = "standard"
            elif slot.name in completeness["detailed"]:
                field_entry["completeness"] = "detailed"

            if slot.name in lc_visible:
                field_entry["visible_when"] = lc_visible[slot.name]

            if slot.name in options_depend_on:
                field_entry["options_depend_on"] = options_depend_on[slot.name]

            if slot.name in auto_set_from:
                field_entry["auto_set_from"] = auto_set_from[slot.name]

            if (
                "visible_when" not in field_entry
                and "completeness" not in field_entry
            ):
                self.logger.warning(
                    f"Field '{slot.name}' in {class_name} has no completeness "
                    f"and no visible_when — underdocumented schema slot"
                )

            field_entries.append(field_entry)

        return {
            "class": class_name,
            "fields": field_entries,
            "enums": enum_registry,
            "rules": uc_rules,
        }