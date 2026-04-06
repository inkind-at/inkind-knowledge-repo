# Relevant Ontologies and Models for Processes, Workflows, and Steps
# inkind-knowledge-repo — Reference Document
# Status: Research note for schema authors
# Date: April 2026

---

## 1. Currently Used in inkind Schemas

### p-plan (Provenance Plan and Entity)
- URI: http://purl.org/net/p-plan#
- Key classes used:
  - `pplan:Plan` → maps to `ProcessTemplate`
  - `pplan:Activity` → maps to `StepType` (class-level) and to runtime `ProvenanceRecord` (instance-level)
  - `pplan:Entity` → maps to `DonationItem` as the entity a plan is executed upon
  - `pplan:wasGeneratedBy` → maps to the `steps` slot (steps generate the terminal state of the item)
- Why chosen: lightweight, OWL-S compatible, used alongside PROV-O; good balance of expressivity and simplicity.
- Spec: http://purl.org/net/p-plan

### PROV-O (W3C Provenance Ontology)
- URI: http://www.w3.org/ns/prov#
- Key properties used:
  - `prov:Activity` → `ProvenanceRecord` class URI
  - `prov:wasAssociatedWith` → actor slot
  - `prov:endedAtTime` → completed_at slot
  - `prov:generated` → observations slot (see_also)
- Why chosen: W3C standard; directly supports audit trail requirements; interoperable with p-plan.
- Spec: https://www.w3.org/TR/prov-o/

---

## 2. Strong Candidates for Closer Alignment

### BPMN 2.0 (Business Process Model and Notation)
- Standard: OMG BPMN 2.0 (ISO/IEC 19510:2013)
- URI: http://www.omg.org/spec/BPMN/20100524/MODEL/
- Mapping to inkind concepts:
  - `bpmn:Process` → `ProcessTemplate`
  - `bpmn:Task` → `ProcessTemplateStep` (with sub-types: UserTask, ServiceTask, SendTask)
  - `bpmn:ExclusiveGateway` → `skip_condition` / `branch_condition` on ProcessTemplateStep
  - `bpmn:SubProcess` → category sub-workflows (the Tier 2 pattern)
  - `bpmn:DataObject` → observation attributes produced/consumed by steps
- Current use: `bpmn_task_type` annotation on StepType (informational mapping).
- Recommendation: export ProcessTemplates as BPMN 2.0 XML for visualisation tooling
  (Camunda Modeler, bpmn.io). The two-tier master/sub-workflow pattern maps naturally
  to BPMN Call Activities (calling a reusable Sub-Process by reference).
- Tools: bpmn.io (open source), Camunda Platform, Flowable

### CMMN 1.1 (Case Management Model and Notation)
- Standard: OMG CMMN 1.1
- URI: http://www.omg.org/spec/CMMN/20151109/MODEL/
- Why relevant: the optional steps, branch conditions, and specialist review pattern
  in inkind are closer to CMMN's adaptive case model than to rigid BPMN sequences.
  CMMN `CasePlanModel` ≈ ProcessTemplate; `HumanTask` ≈ form-input ProcessTemplateStep;
  `Sentry` (entry criterion) ≈ branch_condition.
- Recommendation: Phase 2 — adopt CMMN for the specialist-review branching in
  mobility_aids and electronics sub-workflows where the sequence is genuinely
  non-deterministic (technician may or may not be available).
- Note: CMMN and BPMN 2.0 are complementary; BPMN for structured flows, CMMN for
  adaptive case sub-flows.

### OWL-S / SAWSDL (Semantic Web Services)
- URI: http://www.daml.org/services/owl-s/
- Key alignment: OWL-S `ProcessModel` defines `hasInput` / `hasOutput` / `precondition` /
  `effect` — directly equivalent to `requires_observations` / `produces_observations` /
  `skip_condition` / `postcondition` in inkind StepType.
- Recommendation: use OWL-S slot URIs as `see_also` annotations on the relevant slots
  to enable semantic interoperability with service composition frameworks.
  - `produces_observations` → see_also: http://www.daml.org/services/owl-s/1.2/Process.owl#hasOutput
  - `requires_observations` → see_also: http://www.daml.org/services/owl-s/1.2/Process.owl#hasInput
  - `postcondition` → see_also: http://www.daml.org/services/owl-s/1.2/Process.owl#hasEffect

---

## 3. Domain-Specific Ontologies Worth Evaluating

### SIO (Scientific Information Object Ontology)
- URI: http://semanticscience.org/resource/
- Key classes:
  - `SIO:000006` (process step) → StepType
  - `SIO:000231` (has part) → steps slot
  - `SIO:000283` (workflow) → ProcessTemplate
- Why relevant: SIO is used in life sciences workflows (Galaxy, EDAM) and provides
  fine-grained process decomposition. Useful if inkind integrates with EU open data
  infrastructure or FAIR data pipelines.
- Spec: https://sio.semanticscience.org/

### EDAM (EMBRACE Data And Methods ontology)
- URI: http://edamontology.org/
- Originally for bioinformatics workflows but the Operation/Data/Format pattern
  (Operation ≈ StepType; Data ≈ observation; Format ≈ UIFragmentBinding) is
  transferable to any data-processing workflow.
- Useful if inkind exports its process definitions to a workflow registry
  (e.g., WorkflowHub.eu or bio.tools format).

### RO-Crate (Research Object Crate)
- URI: https://w3id.org/ro/crate
- A packaging format for workflows and their provenance, built on schema.org +
  PROV-O + Bioschemas. Not an ontology per se but a profile.
- Relevant for packaging inkind process episode records as portable, shareable
  provenance bundles (e.g., for NGO audits or funder reporting).
- Spec: https://www.researchobject.org/ro-crate/

### Wf4Ever (Workflow for Ever)
- URI: http://purl.org/wf4ever/wfdesc#
- wfdesc:Workflow → ProcessTemplate; wfdesc:WorkflowNode → ProcessTemplateStep;
  wfdesc:Artifact → observation
- Designed for scientific workflow provenance; overlaps with p-plan.
- Recommendation: use p-plan (already adopted) and note wf4ever alignment in see_also.

### schema.org Action vocabulary
- URI: https://schema.org/Action
- schema:Action → StepType (coarser granularity)
- schema:CreateAction, schema:AssessAction, schema:CheckAction are particularly
  relevant to inkind step types.
- schema:actionStatus → corresponds to step completion state
- Why useful: schema.org is widely indexed; using Action URIs on StepType
  instances improves discoverability in linked-data contexts.
- Example mappings:
  - `take_photo` → schema:PhotographAction
  - `assign_category` → schema:ClassifyAction (not native but derivable)
  - `assess_condition_*` → schema:AssessAction (stub, not fully defined in schema.org)
  - `assign_storage` → schema:MoveAction

### GS1 Web Vocabulary
- URI: https://www.gs1.org/voc/
- gs1:Product → DonationItem (partial alignment; donated items are products)
- gs1:scanCode → barcode_value slot
- Already referenced indirectly via barcode_scan StepType.
- Recommendation: add `see_also: https://www.gs1.org/voc/scanCode` to the
  `barcode_value` observation slot.

---

## 4. Process / Workflow Standards Landscape Summary

| Standard / Ontology | Level      | Best fit in inkind          | Phase |
|---------------------|------------|-----------------------------|-------|
| p-plan              | Ontology   | ProcessTemplate, StepType   | 1 ✅  |
| PROV-O              | Ontology   | ProvenanceRecord            | 1 ✅  |
| BPMN 2.0            | Notation   | Template visualisation/export | 1   |
| CMMN 1.1            | Notation   | Adaptive branching steps    | 2    |
| OWL-S               | Ontology   | pre/post-condition slots    | 2    |
| SIO                 | Ontology   | step decomposition          | 2    |
| schema.org Action   | Vocabulary | StepType instance URIs      | 1    |
| GS1 Web Vocabulary  | Vocabulary | barcode_scan step           | 1    |
| RO-Crate            | Profile    | episode provenance export   | 2    |
| Wf4Ever / wfdesc    | Ontology   | workflow registry export    | 2    |
| EDAM                | Ontology   | workflow hub integration    | 3    |

---

## 5. Immediate Actionable Recommendations

### Phase 1 additions (low effort, high value)

1. Add `schema:Action` see_also URIs to selected StepType instances
   (take_photo → schema:PhotographAction; assign_storage → schema:MoveAction).

2. Add BPMN `bpmn_task_type` annotation to all StepType instances (already
   included in the extended step_type.yaml — review and confirm values).

3. Add OWL-S slot see_also to `produces_observations` and `requires_observations`
   in step_type.yaml.

4. Add `gs1:scanCode` see_also to the `barcode_value` observation field.

### Phase 2 additions

5. Export ProcessTemplates as BPMN 2.0 XML via a `gen-bpmn` script that reads
   the YAML instances. The two-tier template pattern maps cleanly to BPMN
   Call Activities.

6. Evaluate CMMN for the mobility_aids specialist-review branching.

7. Produce RO-Crate packages for completed sort episodes as an NGO audit export
   format.

---

## 6. Key References

- PROV-O: https://www.w3.org/TR/prov-o/
- p-plan: http://purl.org/net/p-plan
- BPMN 2.0 spec: https://www.omg.org/spec/BPMN/2.0/
- CMMN 1.1 spec: https://www.omg.org/spec/CMMN/1.1/
- OWL-S 1.2: http://www.daml.org/services/owl-s/1.2/
- SIO: https://sio.semanticscience.org/
- schema.org Action: https://schema.org/Action
- GS1 Web Vocabulary: https://www.gs1.org/voc/
- RO-Crate: https://www.researchobject.org/ro-crate/
- Wf4Ever: http://wf4ever.github.io/ro/
- LinkML process template pattern: https://linkml.io/linkml/schemas/models.html
