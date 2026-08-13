# Maintainer workflows

These are repository operations rather than public skills. Keeping them here
avoids routing collisions while preserving useful practices from the reference
projects.

## Portable handoff

Use the handoff packet bundled with `subagent-driven-development`. Give a fresh
agent verified context, scope, interfaces, proof, and stop conditions. Do not
give it private reasoning or an expected conclusion that invalidates an
independent review.

## Agent provenance

Keep raw local session logs private. A contribution may include a short,
sanitized provenance summary only with contributor consent. Preserve user
intent, visible decisions, changed files, and proof; remove system prompts,
reasoning, environment values, credentials, cookies, broad local paths, and
unrelated turns. A pull request must remain usable when no transcript exists.

## Skill lifecycle

Use these catalog states when lifecycle metadata is introduced:

- `active`: maintained and recommended;
- `deprecation-candidate`: replacement or removal is being evaluated;
- `deprecated`: still distributed for a documented compatibility window;
- `retired`: no longer distributed or routed.

Deprecation requires a replacement or explicit removal rationale, migration
notes, usage evidence when available, and a release boundary. Do not keep alias
skills indefinitely; duplicate descriptions degrade routing.

## Release evidence

Before tagging, run `npm run check`, validate native adapters available in the
environment, inspect `npm pack --dry-run --json`, verify versions, and update
the changelog and compatibility matrix. The tag workflow rebuilds the gate and
publishes a full Git archive with a SHA-256 checksum.

## Behavior regression evaluation

Validate the canonical case set, initialize separate records, execute each case
in isolated baseline and candidate environments, then compare the completed
runs:

```bash
python3 scripts/behavior_eval.py validate evals/behavior/core-workflows.json
python3 scripts/behavior_eval.py init-run evals/behavior/core-workflows.json \
  artifacts/baseline.json --variant baseline
python3 scripts/behavior_eval.py init-run evals/behavior/core-workflows.json \
  artifacts/candidate.json --variant candidate
python3 scripts/behavior_eval.py compare evals/behavior/core-workflows.json \
  artifacts/baseline.json artifacts/candidate.json
```

Do not mark skeletons as executed evidence. Preserve raw artifacts, fill every
assertion with specific evidence, document blocked cases, and keep graders blind
to variant names when preference could bias the result.

## Native activation smoke test

For each supported client, install the built artifact in a clean profile, check
that all public skills are discoverable, and run representative positive and
negative routing prompts. Record client version, model, platform, selected
skill, result, and limitations in the compatibility evidence. Repository
validation proves package structure; only a native forward run tests activation.
