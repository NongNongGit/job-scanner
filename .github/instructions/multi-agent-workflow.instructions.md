---
description: "Use when: planning multi-agent work, delegating implementation, validating a fix, or doing final review before sign-off. Covers workflow orchestration, handoffs, and self-correction loops."
---
# Multi-agent workflow guidelines

Use this repository's multi-agent pattern as a disciplined delivery loop, not as a freeform chat.

## Workflow contract
- Start with the `plan` agent for any non-trivial task.
- Keep the task scope explicit and bounded before implementation begins.
- `plan` owns sequencing, dependencies, risks, and acceptance criteria.
- `dev` owns implementation only.
- `test` owns verification only.
- `review` owns final correctness and requirement coverage.

## Handoff rules
- Never skip a stage without a justified reason and explicit acceptance criteria.
- Every handoff should include the expected outcome and the evidence required for the next stage.
- Use the repository handoff template in `.github/templates/handoff-template.md` for each transition.
- The `test` and `review` stages must return actionable defects, not vague comments.

## Requirement authoring pattern
- New requirements must be written in the same plan-first structure as this workflow.
- Each requirement should define scope, acceptance criteria, validation, and any risks or dependencies.
- Keep requirements small and testable; avoid vague requests that do not map to a stage or measurable outcome.
- If a request changes scope or introduces a new risk, update the plan and re-communicate the acceptance criteria before implementation continues.

## Self-correction loop
- If `test` or `review` finds a problem, the work re-enters the correction loop.
- `dev` must fix the exact defect and re-run the relevant validation.
- `plan` should be revisited only when the scope, risks, or sequencing materially change.
- Do not declare success without evidence from the relevant validation step.

## Best-practice guardrails
- Prefer narrow, specialized agents over broad "do everything" agents.
- Keep tools and permissions minimal for each role.
- Use explicit acceptance criteria and stage-specific outputs.
- Favor small, reviewable increments over large handoffs.
- Keep the final summary evidence-based and specific.
- Require relevant unit tests before handing a change to the `test` stage.
- Run the relevant tests locally in the repository's configured environment as a mandatory validation step; CI results or LLM review do not substitute for local execution.
- Include the exact local test command and its result in the handoff. If local execution is blocked, report the blocker and do not claim validation passed.
- After a successful `review`, create the pull request and push the branch when repository access permits it.
