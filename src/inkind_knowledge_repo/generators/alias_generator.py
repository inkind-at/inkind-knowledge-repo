"""
Custom Alias generator for LinkML models.
Extracts aliases_de and aliases_en from annotations.

author: Natalia Ruemmele
"""

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List

from linkml.utils.generator import Generator


@dataclass
class AliasGenerator(Generator):
    """
    Generator for creating JSON files containing aliases for classes, slots, and enums.
    """

    # ClassVars
    generatorname = "alias_generator"
    generatorversion = "0.1.0"
    valid_formats = ["json"]
    uses_schemaloader = False

    SUPPORTED_LOCALES = ("en", "de")

    def generate(self) -> Dict[str, Dict[str, Any]]:
        """
        Produce a dictionary containing locale-specific alias mappings.
        """
        # This will store locale-specific data
        locales_data = {
            locale: {"classes": {}, "slots": {}, "enums": {}}
            for locale in self.SUPPORTED_LOCALES
        }

        sv = self.schemaview

        # Process Classes
        for class_name, cls_def in sv.all_classes().items():
            anns = getattr(cls_def, "annotations", {}) or {}
            for locale in self.SUPPORTED_LOCALES:
                aliases = self._get_aliases(anns, locale)
                if aliases:
                    locales_data[locale]["classes"][class_name] = aliases

        # Process Slots
        for slot_name, slot_def in sv.all_slots().items():
            anns = getattr(slot_def, "annotations", {}) or {}
            for locale in self.SUPPORTED_LOCALES:
                aliases = self._get_aliases(anns, locale)
                if aliases:
                    locales_data[locale]["slots"][slot_name] = aliases

        # Process Enums
        for enum_name, enum_def in sv.all_enums().items():
            for locale in self.SUPPORTED_LOCALES:
                enum_entry = {"permissible_values": {}}
                pvs = getattr(enum_def, "permissible_values", {}) or {}
                for pv_name, pv_def in pvs.items():
                    anns = getattr(pv_def, "annotations", {}) or {}
                    aliases = self._get_aliases(anns, locale)
                    # permissible values are included even if empty
                    enum_entry["permissible_values"][pv_name] = aliases
                locales_data[locale]["enums"][enum_name] = enum_entry

        return locales_data

    def _get_aliases(self, annotations: Dict, locale: str) -> List[str]:
        """
        Extract the list of aliases for a given locale from annotations.
        """
        if not annotations:
            return []
            
        key = f"aliases_{locale}"
        ann = annotations.get(key)
        if ann is None:
            return []

        # Support both direct value and Annotation object
        val = getattr(ann, "value", ann)

        if isinstance(val, list):
            return [str(v) for v in val if v]

        if isinstance(val, str):
            return [v.strip() for v in val.split(",") if v.strip()]

        return []

    def serialize(self, output_dir: str = ".", **kwargs) -> None:
        """
        Write locale-specific alias JSON files to output_dir.
        """
        os.makedirs(output_dir, exist_ok=True)
        data = self.generate()

        for locale in self.SUPPORTED_LOCALES:
            file_path = os.path.join(output_dir, f"aliases-{locale}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data[locale], f, indent=2, ensure_ascii=False)