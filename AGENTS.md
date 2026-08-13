# Godmode contributor instructions

Godmode is a portable Agent Skills project. Read `docs/architecture.md` and
`docs/research.md` before changing the public catalog or its vocabulary.

## Working rules

- Keep the public catalog intentional. A public skill must represent a coherent
  engineering responsibility or workflow, not a single technique. Familiar
  names are preferred when they accurately describe a distinct responsibility;
  combine only when the boundary is genuinely clearer.
- Use the Agent Skills format: every public skill is a directory containing a
  `SKILL.md` with valid YAML frontmatter. Keep the body focused and move
  optional detail to one-level-deep `references/` files.
- Write behavior from first principles. Do not copy implementation text,
  datasets, scripts, or proprietary material from reference projects.
- Keep local research checkouts outside the runtime and package inputs.
- Prefer standard-library validation and deterministic tests. Do not add a
  runtime dependency for routing when native skill discovery is sufficient.
  Domain helpers may be dependency-free scripts when they produce repeatable
  artifacts or audits.
- Every workflow must identify what it needs to inspect, what it may change,
  and what evidence is required before a completion claim.
- Keep descriptions precise enough to route adjacent tasks without making
  unrelated skills compete.

## Verification

Run the complete local gate before reporting a change as complete:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

If a change affects a plugin manifest, also run the relevant native validator
when the client is installed:

```bash
claude plugin validate .
```

Codex compatibility must be checked through its local plugin help and
marketplace/plugin validation path when that client exposes one. Do not claim
that an agent loaded a skill unless a real session or native validator proves
it.
