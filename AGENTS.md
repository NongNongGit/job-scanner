# AGENTS.md

This repository uses a plan-first, looped workflow for all non-trivial work.

## Required workflow
- Start with the `plan` agent before implementation.
- The `plan` agent defines scope, milestones, risks, and delegation.
- The `plan` agent is an orchestrator, not an implementer: it must delegate all file edits (including documentation and agent-customization changes) to `dev`.
- `dev` implements only the approved scope.
- `test` validates the implementation with the smallest relevant checks.
- `review` checks final correctness and requirement coverage.
- When a later stage finds a problem, the issue must loop back to the relevant earlier stage for correction.

## Self-correction loop
1. `plan` creates the execution path and acceptance criteria.
2. `dev` implements the work.
3. `test` verifies behavior; if it fails, it returns a clear defect report and triggers `dev` to fix it.
4. `dev` corrects the issue and resubmits to `test`.
5. `review` confirms the final output meets the original request.
6. If `review` finds a gap, it sends a corrective brief back to `dev` and optionally `plan` if scope changes.

## Agent roles
- `plan`: orchestrates the work, sets milestones, and coordinates the loop.
- `dev`: implements code, fixes defects, and self-corrects based on test/review feedback.
- `test`: validates behavior and blocks success until evidence is clear.
- `review`: final quality gate; must identify missing requirements or regressions.

## Handoff template
- Each stage transition must use the template in `.github/templates/handoff-template.md`.
- The template captures objective, acceptance criteria, validation requirements, and risks.
- Handoffs should be explicit and brief so the next agent can act without re-discovering context.

## Requirement pattern for new work
- New requirements must follow this same plan-first structure: scope → acceptance criteria → validation → risk/dependency notes.
- Do not accept vague or open-ended requests that cannot be validated.
- If a requirement changes the task scope, update the plan before implementation continues.

## Testing requirement
- Every `dev` change must include or update unit tests covering the changed behavior before it is handed off to `test`.
- Tests should be focused on the changed logic and should be the minimum set needed to validate the fix or feature.
- Run relevant tests locally in the repository's configured Python environment before handoff; local test execution is mandatory and cannot be replaced by CI results or delegated LLM review.
- Report the exact local command and its pass/fail result. If tests cannot run locally, state the blocker and do not claim validation passed.
- If a change is not covered by a relevant unit test, the task is incomplete until one is added.

## GitHub delivery requirement
- After a successful `review`, the repository is expected to create a pull request and push the branch to GitHub when GitHub access and credentials are available.
- The PR should summarize the changes, testing evidence, and the acceptance criteria it satisfies.
- If GitHub push/PR creation is blocked by authentication, missing remote configuration, or policy, record the exact blocker and do not claim the release is complete.

## Delivery expectations
- Keep work scoped and evidence-based.
- Validate only relevant behavior.
- Never mark work complete without passing validation.
- Treat failed validation and review feedback as required corrective input, not as optional comments.
- Summarize the final state clearly before finishing.
