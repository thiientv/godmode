# Specialized test modes

| Mode | Trigger | Evidence | Stop condition |
| --- | --- | --- | --- |
| Exploratory charter | Unknown product risk or a changed workflow | Notes, time, data, reproducible discoveries | Charter answered or time box ends |
| Contract testing | Independent producer/consumer deployment | Versioned examples/schema and compatibility result | Every supported consumer can deploy |
| Flake investigation | Same test has inconsistent outcomes | Reproduction rate, category, owner, quarantine expiry | Root cause fixed and quarantine removed |
| Production smoke | Environment-specific critical path | Non-destructive public behavior and guardrail metrics | Critical clauses pass or abort fires |
| Chaos/resilience | Recovery claim or dependency failure risk | Steady state, injected fault, blast radius, recovery | Recovery objective is met safely |
| Agent evaluation | Stochastic model or tool behavior | Baseline/candidate runs, artifacts, rubric, variance, cost | Predefined quality gates pass |

Do not automate an exploratory observation until the expected behavior and
stable oracle are understood. Do not create a consumer contract from provider
implementation details.
