# Evidence map

| Requirement | Exact check or observation | Fresh result | Remaining limit |
| --- | --- | --- | --- |
| User behavior | route / CLI / API / browser assertion | PASS / FAIL / BLOCKED |  |
| Implementation | focused tests, type check, static analysis | PASS / FAIL |  |
| Integration | build, package, migration, native validator | PASS / FAIL / BLOCKED |  |
| Regression | broader suite or independent review | PASS / FAIL |  |

Use exact commands and artifact names. Mark a row `BLOCKED` when the necessary
surface is unavailable; do not infer a pass from a neighboring check.
