# Migration patterns

| Pattern | Use when | Required proof | Common failure |
| --- | --- | --- | --- |
| Expand/contract | Producers and consumers cannot change atomically | Mixed-version reads and writes | Contracting before old usage is gone |
| Adapter | Old and new contracts can coexist behind translation | Round-trip and error equivalence | Losing null, ordering, or error semantics |
| Dual-write/read | State must stay available in two stores or shapes | Reconciliation and idempotency | Silent divergence |
| Shadow | New path can run without owning the result | Comparison under real input | Side effects escaping the shadow |
| Strangler | A large system can move capability by capability | Routing and fallback correctness | Two permanent sources of truth |
| Versioned contract | Consumers need an explicit support window | Consumer inventory and compatibility suite | Indefinite version proliferation |

For every phase record entry criteria, action, observable result, abort trigger,
rollback or forward-fix, owner, and cleanup date.
