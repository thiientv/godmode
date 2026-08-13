---
name: performance-optimization
description: >-
  Diagnoses and improves measured latency, throughput, memory, CPU, bundle,
  rendering, query, or resource performance by defining a target, profiling a
  representative workload, locating the bottleneck, making one change at a
  time, and comparing before/after evidence. Use for performance work or
  regressions. Not for guessing optimizations without a reproducible workload
  or for generic refactoring.
---

# Performance Optimization

Measure the bottleneck before optimizing it.

## Workflow

1. Define the user or system target: p50/p95/p99 latency, throughput, startup,
   memory ceiling, frame budget, bundle size, query cost, or error budget.
2. Build a representative and repeatable workload with realistic data,
   concurrency, cache state, network, and device assumptions.
3. Capture a baseline with profiler, trace, query plan, browser performance
   panel, bundle analyzer, or resource metrics. Record variance and warm/cold
   state.
4. Rank bottlenecks by user impact and cost. Form one falsifiable hypothesis.
5. Make the smallest change, rerun the same workload, and compare effect and
   regressions. Keep only improvements that meet the target without violating
   correctness, accessibility, cost, or operability.
6. Add a regression budget/check where the risk is likely to recur.

Read [measurement.md](references/measurement.md). Do not optimize a benchmark
that does not represent the user path, hide work by weakening correctness, or
claim improvement from one noisy run.

## Completion condition

The bottleneck, baseline, change, before/after result, variance, trade-offs,
and remaining limits are documented.
