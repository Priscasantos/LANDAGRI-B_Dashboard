# conab-dashboard.prd.md

## Feature: Restore and Modernize CONAB Dashboard Interface

### Goal
Port the original CONAB dashboard interface into the modularized dashboard system, ensuring all original features and UI elements are preserved and compatible with the new architecture.

### Status
In Progress

### Description
- The CONAB dashboard interface was lost or altered during modularization and modernization efforts.
- The user provided the original interface code and requested it be restored in the new modular system.
- This task involves updating `dashboard/conab.py` with the provided code, validating its integration, and ensuring it works with the current data/session state.

### Requirements
- [x] Overwrite `dashboard/conab.py` with the user-provided original interface code.
- [ ] Validate that the dashboard loads and displays as expected.
- [ ] Ensure all metrics, tables, and placeholders render without error.
- [ ] Check for compatibility with the modern chart theme and session state.
- [ ] Document the change and update TODOs.

### Task Status
- Overwrite file: Done
- Validation: In Progress
- Documentation: In Progress

### Traceability
- User request: "consegue portar pra mim?" (Port the original CONAB dashboard interface)
- File: `dashboard/conab.py`

---

## Next Steps
- Validate dashboard operation and UI.
- Address any errors or regressions.
- Update TODO file accordingly.
