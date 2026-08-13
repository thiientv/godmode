# Design intelligence helper

The bundled helper is a small, transparent catalog—not a replacement for
product judgment or a claim of universal design truth.

## Generate a brief

```bash
python3 skills/frontend-design/scripts/design_system.py \
  --product "developer analytics dashboard" \
  --tone technical --stack react --density dense
```

It returns a direction, type roles, palette roles, spacing, motion guidance,
stack note, and anti-patterns. Inspect the repository's existing tokens and
brand before adopting the result.

## Search a domain

```bash
python3 skills/frontend-design/scripts/design_system.py \
  --search "dark dashboard async loading" --domain all --limit 5
```

Supported domains are `style`, `color`, `typography`, `product`, `layout`,
`accessibility`, and `ux`. Results are original curated entries with tags and
rationale. A zero-result search is a signal to broaden the query or fall back
to the general workflow; never invent a match.

## Why the catalog is small

The reference UI/UX projects show that structured data helps when selection is
repetitive, but a large style database creates a maintenance and provenance
burden. Expand this catalog only with real use cases, source/author notes when
needed, and tests that catch malformed or duplicate entries.
