# Test design notes

## Choose the seam

Prefer, in order: public behavior, domain/service boundary, adapter boundary,
then a small unit seam. A test that bypasses the failure path cannot protect
the contract.

## Check the test's power

Before keeping a test, ask:

- What production change should make it fail?
- Does it fail if the assertion is removed or inverted?
- Does the fixture exercise the real branch rather than a mock's configured
  answer?
- Is the failure message enough to locate the behavior?

## Useful cases

| Contract | Cases to consider |
| --- | --- |
| Input | empty, boundary, malformed, duplicate, oversized |
| State | first use, repeat use, retry, concurrent use, restart |
| Output | ordering, rounding, encoding, missing optional data |
| Failure | timeout, permission, dependency error, partial write |

Do not turn every row into a test automatically. Choose cases that can change
the risk of the requested behavior.
