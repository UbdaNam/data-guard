# Feature Specification: Contract Generation Engine

**Feature Branch**: `002-contract-generation-engine`  
**Created**: 2026-04-01  
**Status**: Draft  
**Input**: User description: "Create Feature 2: Contract Generation Engine for a production-grade Python platform called The Data Contract Enforcer"

## Clarifications

### Session 2026-04-01

- Q: What should the generator consume as authoritative foundation inputs? → A: It MUST consume Feature 1 artifacts directly: canonical dataset registry, dataset readiness inventory, interface registry, schema ownership map, data flow architecture references, and foundational domain/schema notes.
- Q: What must generated contract outputs include? → A: Generated contracts MUST include machine-readable contract YAML, dbt-compatible schema YAML, generation metadata, downstream context annotations, and schema snapshots or generation-ready schema representations where needed.
- Q: Which datasets are in scope for baseline generation? → A: The feature MUST generate baseline contracts for outputs/week3/extractions.jsonl and outputs/week5/events.jsonl, with an architecture that supports additional governed datasets without redesign.
- Q: Which datasets are required minimum support, and which are extension targets? → A: Feature 2 MUST fully support `outputs/week3/extractions.jsonl` and `outputs/week5/events.jsonl`; the architecture MUST also support extension to `outputs/week1/intent_records.jsonl`, `outputs/week2/verdicts.jsonl`, `outputs/week4/lineage_snapshots.jsonl`, and LangSmith trace records without changing the generator architecture.
- Q: How should generated contracts handle differences from canonical governed schemas? → A: Generated contracts MUST target the canonical governed schemas defined by the platform and explicitly document filename, shape, field, or semantic mismatches instead of silently rewriting meaning.

### Session 2026-04-02

- Q: What profiling and clause-generation scope must contract generation include, and what execution boundary should remain out of scope? → A: Contract generation MUST include structural profiling of fields and nested fields where feasible, statistical profiling for numeric values and contract-relevant distributions, and invariant generation for required fields, ranges, enums, patterns, positivity, monotonicity candidates, and referential relationships where inferable; it MUST preserve requirement-document constraints even when sample data does not currently violate them, and it MUST NOT execute validation against datasets yet.
- Q: What lineage-aware downstream context must be embedded in generated contracts when Feature 1 and Week 4 lineage/interface assets are available? → A: Generated contracts MUST embed downstream systems, fields consumed downstream, likely breaking fields, and consumer-facing change sensitivity, using available lineage data and interface metadata from Feature 1 and Week 4 assets; this context is required to support later blast radius and schema evolution capabilities, even though those capabilities are not implemented in this feature.
- Q: What output formats and portability guarantees must generation provide? → A: The primary output MUST be Bitol-compatible YAML contract files under `generated_contracts/`; each generated contract MUST also emit a dbt-compatible schema YAML counterpart for supported clauses (required/not null, accepted values/enums, relationships/referential integrity, uniqueness where applicable), and outputs MUST be deterministic enough for review and diffing across runs except for timestamps or explicitly versioned metadata.
- Q: How must generation handle fields whose business meaning is weakly inferable? → A: If business meaning cannot be inferred confidently from field name, neighboring fields, and sample values, the generator MUST avoid inventing unsupported meaning, MUST record uncertainty explicitly, MAY emit annotation placeholders or machine-readable uncertainty notes, and MUST preserve enough context for later human review or LLM-assisted enrichment; weak semantic confidence MUST NOT block structural contract baseline generation.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Baseline Contract Generation (Priority: P1)

As a platform engineer, I need repeatable contract generation for the core governed datasets so that later validation, attribution, and evolution features can rely on machine-checkable contracts rather than manual interpretations.

**Why this priority**: This is the foundational capability for all downstream contract enforcement and drift analysis features.

**Independent Test**: Can be fully tested by generating contracts from the governed week3 and week5 datasets and confirming the outputs exist in stable paths with the expected machine-readable structure.

**Acceptance Scenarios**:

1. **Given** the canonical dataset registry and readiness inventory from Feature 1, **When** the generator runs, **Then** it produces baseline contract artifacts for `outputs/week3/extractions.jsonl` and `outputs/week5/events.jsonl`.
2. **Given** a governed dataset with inferable structure and statistics, **When** generation completes, **Then** the resulting contract captures structural and statistical profiling results, including field and nested-field structure where feasible, numeric value distributions, required fields, range constraints, enum constraints, pattern constraints, positivity checks, monotonicity candidates, and referential relationships where inferable.
3. **Given** requirement-document constraints that are not yet violated by sample data, **When** generation completes, **Then** the resulting contract still preserves those constraints as governed expectations rather than omitting them because the current sample happens to comply.
4. **Given** a governed dataset with ambiguous fields, **When** the generator cannot determine semantics confidently from field name, neighboring fields, and sample values, **Then** it records explicit uncertainty and avoids inventing unsupported business meaning.
5. **Given** low confidence in business meaning for one or more fields, **When** generation runs, **Then** structural baseline contract generation still completes and preserves context for later human review or LLM-assisted enrichment.

---

### User Story 2 - Downstream Context Preservation (Priority: P2)

As a platform architect, I need generated contracts to preserve consumer, lineage, and ownership context so later features can validate, attribute, and assess blast radius without rediscovering dependencies.

**Why this priority**: Contract shape alone is insufficient; downstream context must be embedded at generation time to keep later features deterministic.

**Independent Test**: Can be tested by inspecting generated outputs and verifying that each contract includes lineage-aware downstream context and references to the canonical ownership surface.

**Acceptance Scenarios**:

1. **Given** the Feature 1 interface registry and schema ownership map, **When** the generator emits a contract, **Then** the contract includes downstream consumer context and ownership references.
2. **Given** a generated contract for a core governed dataset, **When** later features read it, **Then** they can identify the producing dataset, known consumers, and dependency context without reconstructing the source surface.
3. **Given** lineage data or interface metadata from Feature 1 and Week 4 assets, **When** generation completes, **Then** the contract embeds downstream systems, fields consumed downstream, likely breaking fields, and consumer-facing change sensitivity.
4. **Given** partial lineage coverage, **When** required context fields cannot be inferred confidently, **Then** the contract records explicit unknown/partial context annotations instead of omitting downstream-context structure.

---

### User Story 3 - Extensible Dual-Format Outputs (Priority: P3)

As a delivery lead, I need the generator to emit both contract YAML and dbt-compatible schema representations so the platform can support new governed datasets without changing architecture.

**Why this priority**: Supporting parallel output formats and extension points now reduces future rework and keeps the contract system adaptable.

**Independent Test**: Can be tested by generating both contract YAML and dbt-compatible schema YAML for the in-scope datasets and confirming the output paths and metadata are stable.

**Acceptance Scenarios**:

1. **Given** a supported governed dataset, **When** generation completes, **Then** the feature emits a primary Bitol-compatible YAML contract artifact under `generated_contracts/` and a dbt-compatible schema YAML counterpart.
2. **Given** future additional governed datasets, **When** they are added to the canonical surface, **Then** the generator architecture supports them without changing core path conventions or output semantics.
3. **Given** supported clauses in a generated contract, **When** dbt-compatible output is produced, **Then** required/not null, accepted values/enums, relationships/referential integrity, and uniqueness constraints are represented where applicable.
4. **Given** repeated generation runs with unchanged inputs, **When** outputs are compared, **Then** artifacts are deterministic enough for review and diffing except for timestamps or explicitly versioned metadata.

---

### Edge Cases

- A governed dataset is present but the readiness inventory marks it blocked or pending normalization.
- Structural profiling identifies a field with a stable name but ambiguous semantics across upstream records.
- Statistical profiling finds sparse or inconsistent values that cannot support a strong contract clause.
- Downstream lineage context exists for some fields but not for all fields in the same dataset.
- Week 4 lineage snapshots or interface metadata exist but only partially map field-level consumers, requiring explicit partial-context annotations.
- A supported dataset expands in the future; the architecture must allow a new contract output without renaming the existing stable paths.
- A dataset extension target (week1, week2, week4, or LangSmith traces) is introduced after the initial release and must fit the same generator surface.
- dbt-compatible schema output cannot be produced for a clause because the clause has no schema-level equivalent.
- Outputs generated from unchanged inputs differ for non-semantic reasons, reducing review and diffability.
- Multiple fields have weakly inferable semantics; uncertainty notes are required while structural contract generation must still proceed.
- Observed data differs from the canonical governed schema in filename, shape, field names, or field semantics.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The feature MUST generate baseline machine-checkable contracts from governed JSONL datasets.
- **FR-002**: The feature MUST support contract generation for at least `outputs/week3/extractions.jsonl` and `outputs/week5/events.jsonl`.
- **FR-002a**: The feature MUST support future extension to `outputs/week1/intent_records.jsonl`, `outputs/week2/verdicts.jsonl`, `outputs/week4/lineage_snapshots.jsonl`, and LangSmith trace records without changing the generator architecture.
- **FR-003**: The feature MUST read Feature 1 foundation artifacts directly, including canonical dataset registry, dataset readiness inventory, interface registry, schema ownership map, data flow architecture references, and foundational domain/schema notes.
- **FR-003a**: The feature MUST consume Week 4 lineage assets where available (including `outputs/week4/lineage_snapshots.jsonl`) to enrich downstream context annotations.
- **FR-004**: The feature MUST generate primary contracts as Bitol-compatible YAML files in stable paths under `generated_contracts/`, aligned to the requirement document.
- **FR-005**: The feature MUST include structural profiling of fields and nested fields where feasible, plus statistical profiling for numeric values and contract-relevant distributions, in the contract generation process.
- **FR-006**: The feature MUST generate contract clauses for required fields, ranges, enums, patterns, positivity, monotonicity candidates, referential relationships, and dataset-level checks where these are inferable or defined by the requirement document.
- **FR-007**: The feature MUST inject lineage-aware downstream context into generated contracts when available, including downstream systems, consumed fields, likely breaking fields, and consumer-facing change sensitivity.
- **FR-008**: When a field’s business meaning cannot be inferred confidently from field name, neighboring fields, and sample values, the feature MUST avoid inventing unsupported business meaning and MUST record uncertainty explicitly.
- **FR-008b**: For weakly inferable field meaning, the feature MAY emit annotation placeholders or machine-readable uncertainty notes and MUST preserve enough context for future human review or LLM-assisted enrichment.
- **FR-008c**: Weak confidence in semantic meaning MUST NOT prevent generation of the structural contract baseline.
- **FR-008a**: The feature MUST explicitly document mismatches when observed data differs from canonical governed schemas in filename, shape, field names, or field semantics.
- **FR-009**: The feature MUST generate dbt-compatible schema YAML outputs as counterparts to each generated contract for supported clauses.
- **FR-009a**: Supported counterpart clause mappings MUST include required/not null, accepted values/enums, relationships/referential integrity, and uniqueness where applicable.
- **FR-010**: The feature MUST emit generated contract artifacts into stable paths under `generated_contracts/` for later features to consume directly.
- **FR-011**: The feature MUST produce execution metadata or logs sufficient to trace when and how a contract artifact was generated.
- **FR-012**: The feature MUST preserve downstream consumer context so later validation, attribution, blast radius, and migration features can operate without rediscovering dependencies.
- **FR-013**: The feature MUST be extensible to additional governed datasets without changing the architecture or stable output conventions.
- **FR-014**: The feature MUST produce generated contracts that are usable as direct inputs for validation, drift detection, violation attribution, schema evolution intelligence, AI contract enforcement extensions where relevant, and operational report generation.
- **FR-015**: The feature MUST not implement validation execution against datasets, violation attribution, blast radius calculation/execution, schema evolution diffing/execution, AI drift analysis, or operational report generation behavior.
- **FR-015a**: Lineage-aware downstream context is included as generation metadata to support later blast radius and schema evolution capabilities, but those capabilities remain out of scope for this feature.
- **FR-016**: The feature MUST align generated contracts with the canonical governed data surface established in Feature 1.
- **FR-016a**: Generated contracts MUST target the canonical governed schemas defined by the platform even when observed data differs from expected schema or semantics.
- **FR-017**: The feature MUST identify canonical output file names and maintain them as durable generator targets.
- **FR-018**: The feature MUST record generated schema snapshots or generation-ready schema representations if required by later schema evolution work.
- **FR-019**: The feature MUST preserve a single canonical contract-generation architecture that serves the minimum supported datasets and future extension targets without per-dataset forks.
- **FR-020**: Generated outputs MUST be deterministic enough for human review and diffing across runs with unchanged inputs, except for timestamps or explicitly versioned metadata fields.

### Key Entities _(include if feature involves data)_

- **Generated Contract**: A machine-checkable artifact describing field-level and dataset-level expectations for a governed JSONL dataset.
- **dbt-Compatible Schema Artifact**: A secondary schema representation that mirrors supported contract clauses in a dbt-friendly structure.
- **Contract Clause**: A rule or invariant such as requiredness, range, enum, pattern, relationship, or dataset-level quality condition.
- **Generator Execution Record**: Metadata describing the generation run, including source dataset, referenced foundation artifacts, and output paths.
- **Downstream Context Annotation**: A structured reference preserving producer, consumer, lineage, ownership, downstream systems, consumed fields, likely breaking fields, and consumer-facing change sensitivity for later features.
- **Canonical Schema Mismatch Record**: A documented difference between observed data and the canonical governed schema, including filename, shape, or semantic differences.

### Data Contract & Evidence Artifacts _(mandatory for this project)_

- **Generated Contract YAML**: Primary Bitol-compatible contract files for supported datasets, emitted under `generated_contracts/`.
- **dbt Schema YAML**: Parallel dbt-compatible schema YAML files as counterparts for supported generated clauses.
- **Generator Metadata/Logs**: Execution metadata sufficient to trace generation inputs, source foundation artifacts, and output locations.
- **Schema Snapshot or Generation-Ready Representation**: Optional artifacts for later schema evolution work when needed.
- **Foundation Inputs Consumed**: Canonical dataset registry, readiness inventory, interface registry, schema ownership map, data flow architecture references, and foundational domain/schema notes.
- **Mismatch Documentation**: Explicit records of observed-vs-canonical differences for any supported or future extension dataset.

### Downstream Impact _(mandatory for schema/interface changes)_

- **Affected Consumers**: Validation execution, drift detection, violation attribution, schema evolution intelligence, AI contract enforcement, and operational reporting features.
- **Blast Radius**: If generated contracts are incomplete or inconsistent, later features cannot reliably validate governed data, attribute violations, or assess downstream impact.
- **Migration Plan**: Generated contracts must expose schema and clause structure in a way later features can consume without schema rediscovery.
- **Compatibility Window**: The generator must preserve stable output paths and contract semantics across future dataset additions.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: The generator can produce contracts for both in-scope governed datasets from the canonical surface without manual schema reconstruction.
- **SC-002**: 100% of generated contracts include downstream consumer context when that context is available from foundation artifacts, including downstream systems, consumed fields, likely breaking fields, and consumer-facing change sensitivity.
- **SC-003**: 100% of ambiguous fields are either annotated or left explicitly unresolved rather than silently remapped.
- **SC-010**: 0% of runs fail structural contract baseline generation solely due to weak confidence in field business meaning.
- **SC-004**: 100% of generated outputs are written to stable, documented paths and are directly consumable by at least one later platform feature.
- **SC-005**: The generator supports additional governed datasets without changes to the stable architecture or output conventions.
- **SC-006**: For supported clauses, a parallel dbt-compatible schema artifact is generated alongside the primary contract artifact.
- **SC-007**: 100% of supported datasets that differ from the canonical governed schema have explicit mismatch documentation rather than silent reinterpretation.
- **SC-008**: The architecture can extend to week1, week2, week4, and LangSmith trace records without changing the core generation design.
- **SC-009**: For runs with unchanged inputs, generated artifacts are diff-stable except for timestamps or explicitly versioned metadata.

## Assumptions

- Feature 1 foundation artifacts are present and kept in sync with the canonical governed data surface.
- The two in-scope datasets provide enough structure and signal to generate a useful baseline contract without manual intervention.
- Later features will consume generated outputs directly and will not require a separate manual translation step.
- Supported clauses may differ by dataset, but output paths and architecture must remain stable.
- Ambiguous fields may remain partially annotated when the foundation artifacts do not support stronger inference.
- Canonical schema definitions from Feature 1 remain the source of truth even if observed source data varies.

## Canonical Structure Notes _(mandatory)_

- This feature preserves the Feature 1 canonical repository layout and uses the existing foundation artifacts as the authoritative source of truth.
- No new top-level directories are introduced beyond the contract output surface already established in the platform foundation.
- Generated contract paths must remain stable so downstream features can consume them without rediscovering structure.

## Implementation Prompt Integrity Checklist _(mandatory)_

- Prompt builds on Feature 1 approved specs and platform architecture.
- Prompt describes durable contract-generation capability, not temporary checkpoint milestones.
- Prompt preserves data contract first-class artifact expectations.
- Prompt keeps generated outputs stable and reusable by later features.
- Prompt prefers canonical governed schemas over observed upstream variance.
