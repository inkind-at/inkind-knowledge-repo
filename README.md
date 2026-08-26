<a href="https://github.com/dalito/linkml-project-copier"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-teal.json" alt="Copier Badge" style="max-width:100%;"/></a>

# inkind-knowledge-repo

Formal knowledge representation for in-kind donation coordination. Defines the domain schema, category schemas with constraint rules and dependent field maps, and organization configuration instances.

The schema (LinkML, see below) models three areas:
- **Donation items** — `DonationItem` and its category-specific subclasses/mixins (clothing, footwear,
  furniture, electronics, food, etc.), each with a condition/assessment model split into two
  orthogonal dimensions (`usage`: new/used provenance; `condition_grade` or a category-specific
  structured `assessment_result`) and a `lifecycle_state` machine (`announced` → `received` →
  `sorting_in_progress` → `sorted` → `stored` → `distributed`/`shared`/`disposed`).
- **Demand signals** — `DemandSignal`, standing or one-off requests from organisations for specific
  categories/attributes of items, matched against sorted donation stock.
- **Social organisations** — `SocialOrganisation`, the operational tenant model: what an org does
  (`activity_areas`, grounded in ICNPO), who it serves (`population_served`, Candid-inspired),
  its `mission_statement`, its `sdg_alignment` (UN SDGs), and a `people_served_estimate` for
  social impact/ESG reporting when direct beneficiary-level data isn't collected (see
  [docs/social_organisation_taxonomy_research.md](docs/social_organisation_taxonomy_research.md)
  for the taxonomy/methodology research behind these fields).

## Documentation Website

[https://inkind-at.github.io/inkind-knowledge-repo](https://inkind-at.github.io/inkind-knowledge-repo)

## Repository Structure

* [docs/](docs/) - mkdocs-managed documentation
  * [elements/](docs/elements/) - generated schema documentation
* [examples/](examples/) - Examples of using the schema
* [project/](project/) - project files (these files are auto-generated, do not edit)
* [src/](src/) - source files (edit these)
  * [inkind_knowledge_repo](src/inkind_knowledge_repo)
    * [schema/](src/inkind_knowledge_repo/schema) -- LinkML schema
      (edit this)
    * [datamodel/](src/inkind_knowledge_repo/datamodel) -- generated
      Python datamodel
* [tests/](tests/) - Python tests
  * [data/](tests/data) - Example data (`valid/`, `invalid/`, `problem/{valid,invalid}/`)

## Modeling Conventions

The LinkML schema under `src/inkind_knowledge_repo/schema/` is the single source of truth; everything
else (`project/`, `docs/elements/`, generated Python/pydantic models) is derived from it and should
not be hand-edited. The schema follows a few conventions consistently — see
[CONTRIBUTING.md](CONTRIBUTING.md) for the full list, summarized here:

- **Enums are grounded in existing external taxonomies/ontologies, not invented from scratch.**
  Each schema file that defines a categorical enum documents which external standard(s) it aligns
  with (and where/why it deviates) in a header comment, and grounds individual permissible values via
  `meaning:` (a resolvable IRI, when one exists) and/or `see_also:` (a reference link, when it
  doesn't). Examples: item categories in `core.yaml` are grounded in COICOP 2018, UNHCR NFI Core
  Relief Standards, and the Open Eligibility taxonomy; `SocialOrganisation`'s activity/beneficiary/
  impact fields in `entities/organisation.yaml` are grounded in ICNPO, Candid's Population Served
  taxonomy, UN SDGs, and IRIS+ (see
  [docs/social_organisation_taxonomy_research.md](docs/social_organisation_taxonomy_research.md) for
  the research behind those choices).
- **Enums and supporting classes are colocated with the entity that uses them**, not centralized in a
  separate `taxonomies/`/`enums/` folder — e.g. `OrgActivityAreaEnum` lives in `entities/
  organisation.yaml` next to `SocialOrganisation`, not in `core.yaml`.
- **Every categorical enum value and most slots carry bilingual `label_en`/`label_de` annotations**
  (German is a first-class supported locale alongside English), via the `annotations:` block.
- **Every new schema element needs a valid and an invalid example** under `tests/data/`, following
  the `ClassName-###.yaml` naming convention (see [tests/data/README.md](tests/data/README.md));
  invalid examples must be invalid for exactly one documented reason.

## Developer Tools

There are several pre-defined command-recipes available.
They are written for the command runner [just](https://github.com/casey/just/). To list all pre-defined commands, run `just` or `just --list`.

Common commands used while developing the schema:
```bash
just test      # gen-project + Python/pydantic model build + example-data validation
just lint      # linkml-lint against src/inkind_knowledge_repo/schema
just gen-doc   # regenerate docs/elements/ and docs/schema/ from the current schema
just site      # gen-project + gen-doc, i.e. a full local rebuild
```

Generate UI descriptor files:

The `generate-ui-descriptors` CLI command (registered via `[project.scripts]` in `pyproject.toml`) generates the full set of UI descriptor JSON files in one run — one file per root (`DonationItem`, `StorageCollection`, `SortedCollection`, `DemandSignal`) plus one shared file per category dispatch target (bare Tier 1 and physical-item variants), plus merged `labels-en.json`/`labels-de.json`:
```bash
uv run generate-ui-descriptors src/inkind_knowledge_repo/schema/inkind_knowledge_repo.yaml examples/output/
```
Pass `--roots` to generate a subset, e.g. `--roots DonationItem`.

Running the test suite also regenerates `examples/output/` as a side effect, via `generate_all_ui_descriptors()`:
```bash
pytest tests/test_ui_descriptor.py
```

Generate aliases:
```bash
uv run run_gen.py
```

## Credits

This project uses the template [linkml-project-copier](https://github.com/dalito/linkml-project-copier) published as [doi:10.5281/zenodo.15163584](https://doi.org/10.5281/zenodo.15163584).
