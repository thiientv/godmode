# Contributing to Godmode

Godmode is a behavior layer for coding agents. A useful contribution changes
what an agent reliably does, not merely how many prompts the repository
contains.

## Before proposing a new capability

Read:

1. [the architecture](docs/architecture.md);
2. [the research and provenance record](docs/research.md);
3. the neighboring `SKILL.md` files and their descriptions.

Ask:

- Is this a recurring responsibility an engineer would recognize?
- Can the behavior fit inside an existing capability with a focused reference?
- Is the activation boundary distinct from existing descriptions?
- What observable failure does the capability prevent or what expert judgment
  does it add?
- What evidence will show that the capability helps rather than merely sounds
  plausible?

Prefer improving an existing capability when the boundary is the same. Do not
merge distinct workflow states merely to keep the directory count small;
solution-design, planning, execution, TDD, debugging, review, and verification
are intentionally separate because users and agents invoke them at different
moments. Micro-techniques belong in a relevant `references/` file.

## Capability authoring contract

Every public capability must:

- contain `SKILL.md` with Agent Skills-compatible frontmatter;
- keep `name` equal to its lowercase kebab-case directory name;
- describe both what it does and when it should activate;
- state at least one adjacent case where it should not activate;
- explain its safety boundary, completion condition, and evidence expectations;
- stay under the repository's 500-line body limit;
- link only to files that exist within its own directory;
- avoid copying reference text or vendor-specific material without a recorded
  license and attribution decision;
- include `evals/<name>.json` with at least three positive and two negative
  routing cases.

Behavior-changing workflow or helper contributions should also add or update a
case under `evals/behavior/`, then record an isolated baseline/candidate run
when a supported client can execute it. Keep raw artifacts and grader output
separate; do not commit credentials, private transcripts, or unredacted logs.

Move detail to a one-level-deep `references/` file when the main instructions
would otherwise become a handbook. Add a script only when it is deterministic,
repeatable, documented with `--help`, and tested independently.

## Verification workflow

Use a small red/green cycle when changing behavior:

1. Add or update the relevant routing/evaluation fixture or validator test.
2. Run it and observe the expected failure when practical.
3. Make the smallest change.
4. Run the focused test.
5. Run the full repository gate:

   ```bash
   python3 scripts/validate.py
   python3 scripts/behavior_eval.py validate evals/behavior/core-workflows.json
   python3 -m unittest discover -s tests -p 'test_*.py' -v
   ```

For plugin manifest changes, run:

```bash
claude plugin validate .
```

If Codex is available, verify the manifest through the local Codex plugin
workflow and report exactly what was observed. Do not claim that a skill was
auto-activated without a real session trace or client validator output.

For deterministic domain helpers, also run their `--help`, a representative
example, and the focused helper test. UI helpers are deliberately conservative:
they report evidence to investigate, not an absolute design score.

## Documentation and provenance

Update the README catalog and architecture notes when public behavior changes.
Update `docs/research.md` if a reference project influences a new decision.
Keep research clones in `examples/`; never import them or make runtime behavior
depend on their presence.

## Pull requests

Keep a pull request focused. Include:

- the problem or agent failure being addressed;
- the capability boundary and why an existing skill was insufficient;
- files changed and any license/provenance considerations;
- commands run and their fresh results;
- compatibility checks and known limits.

Do not commit generated evaluation output, credentials, private transcripts,
research clones, or unrelated formatting changes.
