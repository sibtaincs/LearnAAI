---
name: debugging-and-validation
description: "Use when diagnosing a bug, failing test, unexpected behavior, or regression. Follow a disciplined workflow: reproduce the issue, isolate the root cause, add a failing check or minimal repro, implement the smallest safe fix, and verify with the relevant command before claiming success."
---

# Debugging and Validation Workflow

## When to use this skill

Use this skill for:

- failing unit or integration tests
- runtime exceptions or incorrect behavior
- regressions after a code change
- unclear bugs that need a reproducible root-cause investigation
- changes that should be validated with the smallest relevant command

## Core workflow

### 1. Reproduce the problem

Start by confirming the exact symptom.

- capture the failing command, stack trace, or user-visible behavior
- record the exact inputs, environment, and recent changes
- if the issue is not yet reproducible, reduce it to a minimal example

Decision point:
- if you cannot reproduce it reliably, gather facts before editing code
- if it is environment-related, document the external dependency or setup issue and verify that separately

### 2. Localize the root cause

Trace the data flow and narrow the problem to the specific component or layer.

- inspect the failure site and the adjacent code path
- check recent changes, assumptions, and data contracts
- prefer a single, evidence-based hypothesis over random edits

Good signs of a correct diagnosis:
- the failing behavior maps directly to the code path under inspection
- the root cause explains the observed symptom and the exact inputs involved

### 3. Create a failing check or minimal repro

Before changing production code, add or adjust the smallest validation that captures the bug.

- add a regression test when the issue is code-level and testable
- otherwise create a minimal script or reproduction that demonstrates the failure
- keep the check focused on the actual behavior, not mocks or synthetic test-only paths

This step matters because it proves the bug is real and prevents “fixes” that only appear to work.

### 4. Implement the smallest proven fix

Once the cause is identified, change only the minimal part needed.

- avoid broad cleanup during a bug fix
- keep the patch scoped to the root cause
- preserve existing contracts unless the bug clearly requires a breaking change

Decision point:
- if the issue spans multiple interdependent layers, fix the root cause first and keep any follow-up improvements separate
- if a workaround is necessary, document why and avoid hiding the underlying defect

### 5. Verify with the smallest relevant evidence

Run the smallest command that checks the changed behavior.

- prefer the exact test or script tied to the bug
- check exit status and relevant output
- only claim success with fresh verification output

Completion checks:
- the failing reproduction or test passes after the fix
- the relevant command exits successfully
- no new obvious errors appear in the targeted area

### 6. Summarize the result clearly

Communicate what changed and why.

- state the root cause in one sentence
- describe the fix briefly
- mention the evidence used to verify it
- call out any remaining risks or follow-up work when relevant

## Decision tree

- Is the bug reproducible? If not, collect more evidence first.
- Is the failure localized to a specific file or function? If yes, inspect that path and its inputs.
- Is the issue caused by an incorrect assumption, data mismatch, or external dependency? If yes, fix the root cause and document the constraint.
- Is there a test or minimal repro for the failure? If not, create one before patching.
- Does the fix pass the relevant verification? If not, iterate on the minimal hypothesis.

## Quality bar for completion

Do not consider the task finished until all of the following are true:

- the issue has been reproduced or clearly localized
- a root cause has been identified and explained
- the fix is as narrow as possible
- the relevant validation command has been run successfully
- the result is summarized with evidence, not just confidence

## Example prompts

- “Debug this failing test and tell me the root cause before patching.”
- “I’m seeing a runtime error in the data flow; reproduce it and isolate the issue.”
- “Create a failing regression for this bug, fix it, and verify with the smallest relevant test command.”
- “Investigate this behavior change and confirm whether it is a root-cause fix or a workaround.”

## Related customizations

- add a project instruction for test-first debugging in Python projects
- create a prompt for reproducing and isolating runtime issues
- pair this skill with a repo-specific validation command for linting, testing, or app launch
