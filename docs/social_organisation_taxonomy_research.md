# Social organisation taxonomy research

`SocialOrganisation` currently models only operational tenancy (`id`, `name`, `parent`, `geo_point`,
`is_active`, `config`) — see [organisation.yaml](../src/inkind_knowledge_repo/schema/entities/organisation.yaml).
It carries no information about what an org does, who it serves, or why — which blocks any future
estimation of social impact / ESG metrics on distributed in-kind donations. This document is an
exhaustive survey of existing taxonomies, vocabularies, and ontologies that could ground that
extension, organised by the four dimensions relevant to the modeling goal, followed by the adoption
decisions made for this repo.

`SocialOrganisation` already declares `class_uri: org:Organization` from the
[W3C Organization Ontology](https://www.w3.org/TR/vocab-org/) (`org:`), which defines exactly the
extension points needed: `org:purpose` (free-text literal — organisational purpose/mission) and
`org:classification` (a link to an external classification scheme). The ontology deliberately does
not prescribe which classification scheme to plug in — that choice is the subject of this research.

## 1. Activities / cause area — what the org does

| Taxonomy | Maintainer | Structure | Notes |
|---|---|---|---|
| **ICNPO** — International Classification of Nonprofit Organizations | Johns Hopkins Comparative Nonprofit Sector Project | 12 major groups / 24 subgroups (Culture & Recreation, Education & Research, Health, Social Services, Environment, Development & Housing, Law/Advocacy/Politics, Philanthropic Intermediaries & Voluntarism Promotion, International, Religion, Business/Professional Associations & Unions, Not Elsewhere Classified) | Built by extending ISIC to capture nonprofit-sector reality across 13 countries; adopted by the UN for nonprofit satellite accounts. International, compact, stable, non-proprietary. |
| NTEE — National Taxonomy of Exempt Entities | NCCS / IRS (US) | 10 broad categories, 26 major groups, decile/centile subdivisions | Very granular and actively used (every US 501(c) org gets a code), but US-specific and code-assignment is an IRS process, not self-declared. |
| Candid PCS "Subject" facet | Candid (formerly Foundation Center + GuideStar) | Hierarchical, evolved from NTEE over 3 decades | One of five PCS facets (Subject, Population, Organization Type, Transaction Type, Support Strategy). Rich and modern but served via a licensed Taxonomy API. |
| OECD DAC/CRS purpose codes | OECD Development Assistance Committee | 5-digit codes, first 3 digits = DAC5 category | Describes the *sector of aid flows*, not the identity of an organisation — donor/transaction-oriented rather than org-oriented. |
| German AO §52 catalogue of tax-privileged purposes (Zweckkatalog) | German Abgabenordnung | Enumerated list of legally privileged purposes | Legal/tax framing tied to German nonprofit registration (*Gemeinnützigkeit*), not an impact/activity framing. Could be cross-mapped later for German-market compliance reporting. |

**Selected: ICNPO.** International scope matches a platform not limited to one country, the group
count (12) is small enough to be a clean multivalued enum, it has no licensing friction, and it is
already the reference standard academic/UN nonprofit-sector statistics use — which matters for
comparing impact estimates against external benchmarks.

## 2. Beneficiaries / target population — who the org serves

| Taxonomy | Maintainer | Structure | Notes |
|---|---|---|---|
| **Candid "Population Served"** | Candid | Vulnerability/demographic categories (e.g. children & youth, seniors, people with disabilities, immigrants & refugees, people experiencing homelessness, LGBTQ+ people) | Widely used by funders and grant databases as the "who" counterpart to Subject's "what". Full hierarchy is served through Candid's licensed Taxonomy API (`taxonomy.candid.org`) — the complete leaf-level list is not freely republishable. |
| HXL (Humanitarian Exchange Language) population groups | UN OCHA Centre for Humanitarian Data | Hashtag/attribute system: `#population`, `#targeted`, `#inneed`, `#reached`, with `+f/+m/+i` (sex) and `+infants/+children/+adolescents/+adults/+elderly` (age) attributes | Statistical/quantitative — designed for headcount reporting in crisis response, not for tagging an organisation's mandate. Strong candidate for a later, more quantitative impact-measurement layer (e.g. "N individuals reached, broken down by age/sex"). |
| 211/AIRS Taxonomy of Human Services; Open Referral HSDS; **Open Eligibility (Aunt Bertha / findhelp.org)** | Alliance for Information and Referral Systems (AIRS) / Open Referral / findhelp.org | Service-and-eligibility taxonomy for information & referral (I&R) systems | Already the precedent used in this repo — `core.yaml`'s `BaseCategoryEnum` cites Open Eligibility to validate its goods-category coverage. It classifies *services offered* and *eligibility rules*, not beneficiary demographic identity, so it is a better fit for a future "services offered" facet than for "population served". |
| UNHCR NFI (Non-Food Item) Core Relief Standards | UNHCR | Item/kit standards for crisis relief | Also already referenced in `core.yaml`; describes items and kits, not beneficiary categories per se. |

**Selected: Candid Population Served, adapted.** Because Candid's full taxonomy is a licensed
product, this repo defines its own `OrgPopulationServedEnum` *inspired by* Candid's public category
names (grounded via `see_also` to `https://taxonomy.candid.org/populations`) rather than reproducing
its complete controlled hierarchy. HXL-style demographic breakdowns (age/sex/displacement status)
are noted as a natural Phase 2 addition once quantitative impact estimation (headcounts reached) is
in scope, rather than an org-level classification.

## 3. Org classification / ontology binding

| Vocabulary | Notes |
|---|---|
| **W3C Organization Ontology** (`org:`) | Already `SocialOrganisation`'s `class_uri`. `org:purpose` → free-text mission; `org:classification` → pointer to an external classification scheme (used here for the ICNPO-grounded activity enum). Deliberately schema-agnostic — provides the extension point without prescribing the vocabulary, which is why this research was needed. |
| schema.org `NGO`, `NonprofitType`, `nonprofitStatus` | Legal-status vocabulary (e.g. `Nonprofit501c3`, `NonprofitANBI` for Dutch ANBI status) — describes legal/tax status, not activities or beneficiaries. Out of scope for this pass but compatible if legal status is modeled later. |

## 4. ESG / social impact metric linkage

| Framework | Maintainer | Notes |
|---|---|---|
| **UN Sustainable Development Goals (SDGs)** | UN Statistics Division | 17 goals, 169 targets, 231 indicators. Each goal has a stable public URI (`https://metadata.un.org/sdg/{n}`). Globally recognised, simple, and already the alignment target most other frameworks (including IRIS+) cross-walk to. | 
| IRIS+ Thematic Taxonomy + Catalog of Metrics | Global Impact Investing Network (GIIN) | Broad-to-narrow hierarchy: Impact Category → Impact Theme → Delivery Model, purpose-built for impact-investing metrics, aligns to 50+ external frameworks and to SDG goals/targets. | Purpose-built for exactly the "estimate social impact" goal, but heavier to integrate (its own taxonomy + metric catalog) and best layered on top of a settled org shape. |
| GRI Standards (400 series — social topics) | Global Reporting Initiative | Topic standards: employment, labor relations, health & safety, diversity, non-discrimination, child/forced labor, security, etc. | Designed to assess an organisation's *own* operations/workforce/supply chain — wrong unit of analysis for a social org's *external* beneficiary impact. |
| B Impact Assessment | B Lab | 5 stakeholder-focused Impact Areas: Governance, Workers, Community, Environment, Customers | Same mismatch as GRI — assesses the assessed company's own practices, not downstream beneficiary impact. |
| EU Social Taxonomy (draft) | European Commission Platform on Sustainable Finance | Substantial Contribution / Do No Significant Harm criteria mirroring the EU environmental taxonomy | Shelved by the European Commission due to lack of agreement — not stable enough to build on now. |

**Selected: SDG alignment tagging only, for this pass.** A simple multivalued `SDGGoalEnum` gives a
lightweight, globally-recognised anchor for impact estimation without importing a full metrics
catalog. IRIS+ integration (metric catalog, richer theming) is deferred to a later phase, once the
org shape (activities + beneficiaries) is settled — IRIS+ itself cross-walks to SDGs, so the SDG tags
adopted now will still be usable as an anchor if/when IRIS+ is layered on top.

## Adoption summary

| Dimension | Adopted | Rationale |
|---|---|---|
| Activities / cause area | ICNPO (12 major groups) | International, compact, non-proprietary, UN-adopted statistical standard |
| Beneficiaries / population served | Candid Population Served, adapted (not verbatim — licensing) | Funder-recognised vocabulary for "who"; complements ICNPO's "what" |
| Mission | Free text (`org:purpose`) | No taxonomy fits free-form mission statements; matches the ontology's own modeling choice |
| ESG / impact linkage | SDG alignment tags only | Lightweight, stable, globally recognised; IRIS+/GRI/B Impact explicitly deferred |

See the schema implementation in
[organisation.yaml](../src/inkind_knowledge_repo/schema/entities/organisation.yaml) for the
resulting `OrgActivityAreaEnum`, `OrgPopulationServedEnum`, `SDGGoalEnum`, and the `mission_statement`,
`activity_areas`, `population_served`, `sdg_alignment` slots on `SocialOrganisation`.

## 5. Estimating people served without beneficiary-level data

This platform deliberately does not collect beneficiary-level data (privacy and operational
constraints), yet estimating social impact/ESG needs *some* figure for how many people an org
reaches. This section surveys how existing frameworks handle organisations that cannot produce an
exact unduplicated headcount.

**Closest existing standard metric: IRIS+ PI4060 "Client Individuals: Total"** (GIIN). Defined as an
*unduplicated* count of individuals served **during the reporting period**. Critically, IRIS+
explicitly anticipates organisations without direct client data (e.g. indirect distribution
channels, such as selling through local distributors) and endorses a **"best estimate"
methodology**: derive the count from a proxy (units distributed, capacity, etc.) and **footnote the
assumptions** used — exactly this platform's situation, since donation routing here doesn't capture
individual beneficiary identities either.

**Reporting period is annual, universally.** Every framework surveyed anchors "people served" to a
~12-month period, not a single month or a point-in-time snapshot:
- IRIS+ PI4060's "reporting period" convention.
- IRS Form 990 — the mandatory annual filing for US 501(c)(3) orgs includes narrative reporting on
  "how many people were served" per program, on an annual cadence.
- HUD's Annual Homeless Assessment Report (AHAR) — a defined 12-month window for sheltered-population
  counts, distinct from HUD's Point-In-Time (PIT) Count (a single night in January). The PIT count is
  a narrower, different-purpose metric (federal funding eligibility) and is known to *undercount*
  annual reach because it misses client turnover across the year — a caution against using any
  single-snapshot figure as a stand-in for annual reach.
- Social Value International's SROI guidance — "evaluative" SROI is conducted retrospectively over a
  defined reporting period using actual stakeholder data from that period.

**Why not monthly?** Nonprofit activity is seasonally skewed — over a third of annual nonprofit
revenue arrives in Q4 alone in aggregate giving data, and donation-based orgs in this platform's
domain see comparable seasonal swings (winter clothing, holiday food drives, back-to-school
supplies). A single month's figure is not representative of the year; if a monthly figure is wanted
for display, it must be computed as an *average across a full 12-month period*, not read off any one
month.

**Two concrete proxy-estimation methods recur in adjacent sectors** and map directly onto orgs this
platform already onboards:
- **Capacity/turnover-based** (HUD AHAR bed-utilization methodology): bed (or slot) utilization rate
  is calculated as people served over a period ÷ available bed-nights in that period; HUD's expected
  utilization range is roughly 65–105%. Converting capacity into an annual unique-individuals estimate
  follows the same logic: `beds × occupancy_rate × 365 ÷ average_length_of_stay_days`. Directly
  applicable to shelter-type orgs — e.g. Haus der Frau's 18-bed capacity.
- **Distribution-volume-based** (food-bank/food-pantry sector convention): food pantry clients visit
  on average roughly 8–12 times per year (frequently monthly), so `total distributions ÷
  typical_visits_per_person_per_year` approximates annual unique individuals. Applicable to food
  banks and other recurring-donation orgs — e.g. Wiener Tafel.
- Feeding America's own network reporting is commonly expressed as *unduplicated individuals served
  per month*, reflecting that food assistance is often a recurring, monthly-cadence need — but this
  is a sector-specific operational convention layered on top of (not a replacement for) the annual
  total used for cross-framework ESG comparison.
- Many orgs will simply **self-report** a figure they already compute for their own annual
  report/990 — `self_reported` must remain a first-class, equally valid method, not a fallback of
  last resort.

**Decisions**: annual reporting period only (`period_start`/`period_end`, no separately-stored
monthly figure — derive one at the application layer if needed); count individuals only (not
households, to compose directly with `sdg_alignment` without a conversion step — orgs that only
track households apply their own multiplier and document it); and require a documented
`estimation_method` (`self_reported`, `capacity_based`, `distribution_volume_based`,
`survey_sample_based`, `other`) plus optional free-text `method_note`, per IRIS+'s explicit
footnote-your-assumptions guidance. See `PeopleServedEstimate` and the `people_served_estimate` slot
in [organisation.yaml](../src/inkind_knowledge_repo/schema/entities/organisation.yaml).
