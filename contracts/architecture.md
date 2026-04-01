# Architecture Notes

This document explains the maintained foundation architecture for Feature 1.

## Versioning

- `contracts/data_flow_architecture.mmd` is the source Mermaid file.
- Any update to an interface or ownership map must preserve canonical dataset paths.
- The architecture source must be updated before downstream features rely on new boundaries.

## Maintenance Rules

- Keep interface IDs stable once published.
- Record every canonical-path change in the path inventory first.
- Do not silently change business semantics to make downstream consumers fit.
- Use dataset readiness statuses to indicate unresolved conditions.

## Review Checklist

- Does the diagram still include all six governed datasets?
- Does every interface arrow have an ownership record?
- Are readiness blockers visible in the registry outputs?
