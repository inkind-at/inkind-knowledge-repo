import pytest
import json
import os

from inkind_knowledge_repo.generators.ui_descriptor import UiDescriptorGenerator


def test_ui_descriptor_generation_basic():
    gen = UiDescriptorGenerator("src/inkind_knowledge_repo/schema/entities/donation_item.yaml", top_class="DonationItem")
    result = gen.generate()

    assert "DonationItem" in result
    base = result["DonationItem"]
    category_field = next((f for f in base["fields"] if f["name"] == "category"), None)
    assert category_field is not None
    assert "dispatches_to" in category_field
    assert "ClothingItem" in category_field["dispatches_to"]

    assert "ClothingItem" in result
    clothing = result["ClothingItem"]
    demo_field = next((f for f in clothing["fields"] if f["name"] == "demographic"), None)
    assert demo_field is not None
    assert demo_field.get("visible_when", {}).get("lifecycle_state") == ["sorting_in_progress"]

    winter_field = next((f for f in clothing["fields"] if f["name"] == "is_winter_suitable"), None)
    assert winter_field is not None
    assert "auto_set_from" in winter_field
    assert winter_field["auto_set_from"]["season"]["winter"] is True
    assert winter_field["auto_set_from"]["season"]["summer"] is False

    size_field = next((f for f in clothing["fields"] if f["name"] == "size"), None)
    assert size_field is not None
    assert "options_depend_on" in size_field

    assert any(r["id"].startswith("uc-") for r in clothing["rules"])
    assert "ClothingSizeEnum" in clothing["enums"]


def test_ui_descriptor_generation_top_class_any_schema_class():
    gen = UiDescriptorGenerator("src/inkind_knowledge_repo/schema/entities/donation_item.yaml", top_class="ClothingItem")
    result = gen.generate()

    assert "ClothingItem" in result
    assert result["ClothingItem"]["class"] == "ClothingItem"
    assert "DonationItem" not in result
    # ClothingItem is a leaf class in this hierarchy, so no subclass outputs expected
    assert len(result) == 1


def test_ui_descriptor_json_serialization():
    """Test that the generator produces valid JSON and can be serialized to files."""
    gen = UiDescriptorGenerator(
        "src/inkind_knowledge_repo/schema/entities/donation_item.yaml",
        top_class="DonationItem"
    )
    result = gen.generate()

    output_dir = "examples/output/"
    gen.serialize(output_dir=output_dir)

    # Descriptor file
    output_file = os.path.join(output_dir, "DonationItem.ui.json")
    assert os.path.exists(output_file)

    with open(output_file, "r", encoding="utf-8") as f:
        parsed = json.load(f)

    assert parsed == result
    assert "DonationItem" in parsed
    assert "ClothingItem" in parsed

    # Locale files
    for locale in ("en", "de"):
        labels_file = os.path.join(output_dir, f"labels-{locale}.json")
        assert os.path.exists(labels_file)

        with open(labels_file, "r", encoding="utf-8") as f:
            labels = json.load(f)

        assert isinstance(labels, dict)
        assert len(labels) > 0
        # Every key should be a non-empty string
        assert all(isinstance(k, str) and k for k in labels)
        assert all(isinstance(v, str) and v for v in labels.values())


def test_ui_descriptor_generation_basic():
    gen = UiDescriptorGenerator("src/inkind_knowledge_repo/schema/entities/donation_item.yaml", top_class="DonationItem")
    result = gen.generate()

    assert "DonationItem" in result
    base = result["DonationItem"]
    category_field = next((f for f in base["fields"] if f["name"] == "category"), None)
    assert category_field is not None
    assert "dispatches_to" in category_field
    assert "ClothingItem" in category_field["dispatches_to"]

    assert "ClothingItem" in result
    clothing = result["ClothingItem"]
    demo_field = next((f for f in clothing["fields"] if f["name"] == "demographic"), None)
    assert demo_field is not None
    assert demo_field.get("visible_when", {}).get("lifecycle_state") == ["sorting_in_progress"]

    winter_field = next((f for f in clothing["fields"] if f["name"] == "is_winter_suitable"), None)
    assert winter_field is not None
    assert "auto_set_from" in winter_field
    assert winter_field["auto_set_from"]["season"]["winter"] is True
    assert winter_field["auto_set_from"]["season"]["summer"] is False

    size_field = next((f for f in clothing["fields"] if f["name"] == "size"), None)
    assert size_field is not None
    assert "options_depend_on" in size_field

    assert any(r["id"].startswith("uc-") for r in clothing["rules"])
    assert "ClothingSizeEnum" in clothing["enums"]


def test_ui_descriptor_generation_top_class_any_schema_class():
    gen = UiDescriptorGenerator("src/inkind_knowledge_repo/schema/entities/donation_item.yaml", top_class="ClothingItem")
    result = gen.generate()

    assert "ClothingItem" in result
    assert result["ClothingItem"]["class"] == "ClothingItem"
    assert "DonationItem" not in result
    # ClothingItem is a leaf class in this hierarchy, so no subclass outputs expected
    assert len(result) == 1
