# Skill evaluation loop

1. Write two or three realistic cases and expected observable outcomes.
2. Snapshot the old skill or choose a no-skill baseline.
3. Run baseline and candidate in isolated contexts with identical fixtures.
4. Record outputs, artifacts, public trace summaries, timing, and usage.
5. Add objective assertions after seeing the first outputs; avoid phrase-level
   assertions that reward one wording.
6. Blind any preference grader to variant identity.
7. Compare quality, failure modes, latency, and cost.
8. Revise the owning instruction or helper, rerun affected cases, then run the
   regression set.
9. Ask for human review where correctness depends on design taste, domain
   judgment, or organizational policy.

Keep raw run artifacts immutable. A skill that produces the same quality with
substantially more context or tool calls has not automatically improved.
