import pathlib

fixes = {
    'src/inkind_knowledge_repo/schema/inkind_knowledge_repo.yaml': [
        ('  - ./shared_slots.yaml', '  - shared_slots'),
        ('  - ./entities/organisation.yaml', '  - entities/organisation'),
        ('  - ./entities/actor.yaml', '  - entities/actor'),
        ('  - ./entities/storage_location.yaml', '  - entities/storage_location'),
        ('  - ./entities/donation_source.yaml', '  - entities/donation_source'),
        ('  - ./entities/donation_collection.yaml', '  - entities/donation_collection'),
        ('  - ./entities/donation_item.yaml', '  - entities/donation_item'),
        ('  - ./entities/demand_signal.yaml', '  - entities/demand_signal'),
        ('  - ./entities/campaign.yaml', '  - entities/campaign'),
        ('  - ./categories/_base.yaml', '  - categories/_base'),
        ('  - ./categories/clothing.yaml', '  - categories/clothing'),
        ('  - ./categories/furniture.yaml', '  - categories/furniture'),
        ('  - ./categories/food.yaml', '  - categories/food'),
        ('  - ./process/step_type.yaml', '  - process/step_type'),
        ('  - ./process/process_template.yaml', '  - process/process_template'),
        ('  - ./ui/fragment_binding.yaml', '  - ui/fragment_binding'),
        ('  - ./provenance.yaml', '  - provenance'),
    ],
    'src/inkind_knowledge_repo/schema/categories/_base.yaml': [
        ('  - ../shared_slots.yaml', '  - shared_slots'),
        ('  - ../shared_slots', '  - shared_slots'),
    ],
    'src/inkind_knowledge_repo/schema/categories/clothing.yaml': [
        ('  - _base.yaml', '  - categories/_base'),
        ('  - _base', '  - categories/_base'),
    ],
    'src/inkind_knowledge_repo/schema/categories/food.yaml': [
        ('  - _base.yaml', '  - categories/_base'),
        ('  - _base', '  - categories/_base'),
    ],
    'src/inkind_knowledge_repo/schema/categories/furniture.yaml': [
        ('  - _base.yaml', '  - categories/_base'),
        ('  - _base', '  - categories/_base'),
    ],
    'src/inkind_knowledge_repo/schema/entities/actor.yaml': [
        ('  - ../shared_slots.yaml', '  - shared_slots'),
        ('  - ../shared_slots', '  - shared_slots'),
    ],
    'src/inkind_knowledge_repo/schema/entities/campaign.yaml': [
        ('  - ../shared_slots.yaml', '  - shared_slots'),
        ('  - ../shared_slots', '  - shared_slots'),
    ],
    'src/inkind_knowledge_repo/schema/entities/demand_signal.yaml': [
        ('  - ../shared_slots.yaml', '  - shared_slots'),
        ('  - ../shared_slots', '  - shared_slots'),
    ],
    'src/inkind_knowledge_repo/schema/entities/donation_collection.yaml': [
        ('  - ../shared_slots.yaml', '  - shared_slots'),
        ('  - ../shared_slots', '  - shared_slots'),
    ],
    'src/inkind_knowledge_repo/schema/entities/donation_item.yaml': [
        ('  - ../shared_slots.yaml', '  - shared_slots'),
        ('  - ../shared_slots', '  - shared_slots'),
    ],
    'src/inkind_knowledge_repo/schema/entities/donation_source.yaml': [
        ('  - ../shared_slots.yaml', '  - shared_slots'),
        ('  - ../shared_slots', '  - shared_slots'),
    ],
    'src/inkind_knowledge_repo/schema/entities/organisation.yaml': [
        ('  - ../shared_slots.yaml', '  - shared_slots'),
        ('  - ../shared_slots', '  - shared_slots'),
    ],
    'src/inkind_knowledge_repo/schema/entities/storage_location.yaml': [
        ('  - ../shared_slots.yaml', '  - shared_slots'),
        ('  - ../shared_slots', '  - shared_slots'),
    ],
    'src/inkind_knowledge_repo/schema/process/process_template.yaml': [
        ('  - ../shared_slots.yaml', '  - shared_slots'),
        ('  - ../shared_slots', '  - shared_slots'),
    ],
    'src/inkind_knowledge_repo/schema/process/step_type.yaml': [
        ('  - ../shared_slots.yaml', '  - shared_slots'),
        ('  - ../shared_slots', '  - shared_slots'),
    ],
    'src/inkind_knowledge_repo/schema/provenance.yaml': [
        ('  - ./shared_slots.yaml', '  - shared_slots'),
        ('  - ./shared_slots', '  - shared_slots'),
    ],
    'src/inkind_knowledge_repo/schema/ui/fragment_binding.yaml': [
        ('  - ../shared_slots.yaml', '  - shared_slots'),
        ('  - ../shared_slots', '  - shared_slots'),
    ],
}

for fpath, replacements in fixes.items():
    p = pathlib.Path(fpath)
    text = p.read_text(encoding='utf-8')
    original = text
    for old, new in replacements:
        text = text.replace(old, new)
    if text != original:
        p.write_text(text, encoding='utf-8')
        print('Fixed:', fpath)
    else:
        print('No change:', fpath)

print('Done.')
