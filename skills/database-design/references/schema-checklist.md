# Schema and migration checklist

- [ ] Source of truth and ownership are named.
- [ ] Nullability, uniqueness, foreign-key/reference, and lifecycle invariants
      have tests or database constraints.
- [ ] Real query shapes and cardinalities are recorded.
- [ ] Indexes have a query and write-cost reason.
- [ ] Existing and new application versions can coexist during migration.
- [ ] Backfill is resumable, bounded, observable, and idempotent.
- [ ] Rollback or forward-fix behavior is explicit.
- [ ] Sensitive fields have access, retention, and deletion decisions.
- [ ] Backup/restore and migration rehearsal are part of the evidence map.
