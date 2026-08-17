# Agent failure taxonomy

Use failure modes to design routing fixtures, behavior cases, and regression benchmarks. The taxonomy is intentionally small enough to remain actionable.

| ID | Failure mode | Typical prevention |
| --- | --- | --- |
| `F01` | premature implementation | `solution-design`, `implementation-planning` |
| `F02` | insufficient repository exploration | `codebase-orientation` |
| `F03` | requirement or constraint assumption | `solution-design`, `technical-research` |
| `F04` | missed edge case | `test-strategy`, TDD, domain skills |
| `F05` | missing regression coverage | TDD, `behavior-validation` |
| `F06` | false completion claim | `completion-verification`, evidence ledger |
| `F07` | weak or stale verification | `completion-verification` |
| `F08` | scope creep | task boundary and review |
| `F09` | unsafe migration or state transition | `safe-migrations` |
| `F10` | security omission | `security-and-hardening` |
| `F11` | unsupported tool or environment assumption | `codebase-orientation`, `technical-research` |
| `F12` | stale external knowledge | `technical-research` |
| `F13` | incomplete integration | `test-strategy`, `behavior-validation`, `completion-verification` |
| `F14` | review confirmation bias | independent `requesting-code-review` / `receiving-code-review` |
| `F15` | context-loss continuation error | engineering lifecycle recovery |

## Evaluation use

A behavior case can declare protected failure modes. A candidate should not receive full credit merely because its happy-path artifact exists when a protected failure mode is present.

Example:

```json
{
  "task": "add a database migration",
  "protect_against": ["F02", "F04", "F09", "F13"],
  "required_evidence": ["migration-test", "rollback-or-safety-analysis", "integration-test"]
}
```

The taxonomy is not a substitute for domain judgment. It is a shared vocabulary for measuring recurring agent mistakes across repositories and models.
