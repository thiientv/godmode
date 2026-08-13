---
name: documentation-and-adrs
description: >-
  Writes or updates engineering documentation and architecture decision records
  from repository facts, explicit assumptions, trade-offs, and verification
  links. Use for README changes, design docs, runbooks, ADRs, migration notes,
  and contributor documentation. Not for implementation planning alone or for
  copying external documentation without provenance.
---

# Documentation and ADRs

Document the decision a future maintainer needs, not the whole conversation.

## Documentation workflow

1. Identify the reader, decision or task, freshness owner, and expected action.
2. Inspect the source of truth, commands, configuration, and current behavior.
3. Separate facts, assumptions, examples, and recommendations. Mark version or
   environment-specific statements.
4. Put the shortest usable path first; move exhaustive details to a linked
   reference.
5. Test every command, code sample, relative link, and stated file path that
   the environment permits.

## ADR workflow

Use an ADR when a choice affects interfaces, architecture, data, operations,
security, or future contributors. Record context, decision, alternatives,
consequences, rejected options, migration/rollback, and status. Do not use an
ADR to hide an unresolved decision; mark it proposed or superseded honestly.

Read [adr-template.md](references/adr-template.md). Keep README content as a
front door and link to deeper docs; avoid stale feature walls and hardcoded
claims that the repository cannot verify.

## Completion condition

The intended reader can act from the document, links and examples resolve, and
the document's factual or verification limits are visible.
