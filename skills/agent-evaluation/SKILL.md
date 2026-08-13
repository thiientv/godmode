---
name: agent-evaluation
description: >-
  Designs and runs reproducible evaluations for AI agents, prompts, tools,
  skills, and model-backed workflows using realistic datasets, isolated
  baselines, objective assertions, rubric grading, trajectory analysis,
  cost/latency tracking, and regression comparison. Use when measuring agent
  quality, optimizing skill triggering, comparing prompts or models, or gating
  an AI feature release. Not for ordinary deterministic unit tests.
---

# Agent Evaluation

Build a quality flywheel that can distinguish a real improvement from a lucky
run.

## Define the evaluation contract

Name the target behavior, users, risks, baseline, candidate, environment,
stochastic settings, and decision threshold. Start with a few realistic cases,
including a boundary or failure case. Split trigger-query optimization into a
fixed training set and held-out validation set.

Use [eval-schema.md](references/eval-schema.md) for cases, assertions, timing,
and result records.

## Run isolated comparisons

1. Snapshot the baseline before changing the candidate.
2. Run baseline and candidate on identical inputs in fresh contexts with no
   leaked expected answer or previous trace.
3. Capture final artifacts, public transcript/tool summaries, duration, token
   or request cost, and failures.
4. Grade deterministic assertions first; use a blinded rubric or human review
   for qualities that cannot be measured mechanically.
5. Repeat stochastic cases enough to expose variance. Do not hide flakiness by
   dropping inconvenient runs.

Measure task success, instruction adherence, tool selection and arguments,
trajectory efficiency, grounding, safety, output quality, latency, and cost only
when relevant. A single aggregate score must not hide a release-blocking metric.

## Analyze and iterate

Cluster repeated failures by cause, change one owning layer, rerun the affected
cases, then run the regression set. Compare candidate against baseline and
reject improvements that regress a protected metric beyond its tolerance.

Use `writing-skills` for skill-specific authoring and `release-engineering` for
production promotion. Never claim a score that was not read from an actual
result artifact.

## Completion condition

Cases, environment, baseline, candidate, artifacts, graders, costs, and limits
are reproducible; the decision follows predefined thresholds rather than a
post-hoc interpretation of the preferred result.
