---
name: test-strategy
description: >-
  Plans risk-based test coverage for a feature, service, release, or system by
  mapping user and business risk to test levels, environments, data, failure
  paths, automation, exploratory checks, and release gates. Use when choosing
  what to test or how much evidence is enough. Not for writing one test case,
  applying TDD to a single behavior, or debugging a failing test.
---

# Test Strategy

Coverage is a means; risk and failure detection are the decision criteria.

## Strategy loop

1. Identify critical user journeys, assets, contracts, dependencies, and recent
   change areas.
2. Score impact and likelihood; include data loss, privacy, money, access,
   safety, operational, and reputation failure modes.
3. Map each high-risk item to the cheapest test level that reaches the real
   failure: unit, contract, integration, component, browser, load, security,
   exploratory, or production monitoring.
4. Define fixtures, environment parity, deterministic data, test ownership,
   test oracle, and cleanup.
5. Set release gates and explicit exclusions. Include negative, boundary,
   retry, concurrency, migration, accessibility, and recovery paths when risk
   warrants them.
6. Reassess after incidents, architecture changes, dependency changes, and
   high-churn releases.

## Choose specialized test modes

- Use **exploratory charters** when risks or failure shapes are not understood;
  time-box the session, record observations, then convert repeatable discoveries
  into automated checks.
- Use **contract tests** at independently deployed consumer/provider seams;
  verify compatibility before deployment rather than duplicating implementation
  tests on both sides.
- Classify **flaky tests** by product race, test race, data, environment,
  dependency, resource contention, or selector drift. Quarantine only with an
  owner, evidence, expiry, and a still-visible signal; retries are not a fix.
- Use **production tests** only with non-destructive synthetic identities,
  blast-radius controls, monitoring, cleanup, and a tested abort path.
- Use **agent evaluation** for stochastic model-backed behavior; ordinary pass
  rates and snapshots do not capture variance, tool trajectory, cost, or
  grounding.

Read [risk-matrix.md](references/risk-matrix.md) and
[specialized-modes.md](references/specialized-modes.md). Avoid a universal
coverage percentage, brittle snapshots with no oracle, and tests that pass
only because they mock the behavior under test.

## Completion condition

The strategy connects risk to an executable check, names ownership and test
data, defines release gates, and makes untested risk visible.
