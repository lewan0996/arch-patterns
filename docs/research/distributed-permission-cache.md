# Distributed permission cache: correctness and fallback

Research for [#31](https://github.com/lewan0996/arch-patterns/issues/31), checked 2026-09-27. This report informs [permission-data freshness and fallback, #21](https://github.com/lewan0996/arch-patterns/issues/21). It selects neither a product nor the owner's final support policy. It follows the repository's `docs/research/` convention; no applicable ADR exists in the checked main revision (`6be59cd`).

## Finding and existing boundary

**Research synthesis:** a distributed permission cache can satisfy a bounded-staleness authorization contract, provided the implementation carries trustworthy source freshness through every update and refill, rejects expired evidence at authorization time, and fails closed when refresh fails. Reliable pushes improve typical freshness and hit rate; they cannot alone guarantee a maximum delay during an outage. Ordinary cache-aside does not establish this proof. [Microsoft cache-aside limitations](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside), [Redis expiration semantics](https://redis.io/docs/latest/commands/expire/).

The current [#11 resolution](https://github.com/lewan0996/arch-patterns/issues/11#issuecomment-5767173587) supports the cache and event-fed permission projection as equal microservice profiles, with a maximum lag and no immediate-revocation promise. Modular-monolith modules use an in-process Access Management Contract. [#31](https://github.com/lewan0996/arch-patterns/issues/31) reopens evidence and selection guidance because the owner prefers the projection. This report does not supersede that resolution.

## Reliable changes and complete values

Access Management remains the assignment authority. A source commit followed by an ordinary cache write has a failure window between those operations. An outbox records the update obligation in the source transaction; a worker retries after commit. Outbox delivery can duplicate messages, so consumers need idempotency and ordering treatment. CDC is another documented capture mechanism, subject to its retention and recovery guarantees. [AWS transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html).

**Candidate contract, inferred from those failure modes:** each affected cache key identifies tenant, internal user, permission scope and schema/policy interpretation. Its value is a complete replacement snapshot with source revision, source freshness evidence, and an explicit empty/disabled representation. Missing keys are unknown, not permission grants. The change record must durably identify all affected keys or a resumable fan-out job. A role edit, membership removal or policy change can affect many users; updating only the directly edited record is insufficient. A worker may recompute current values, but must label them with the revision and freshness of that computation, not the triggering old event. This is a proposed application protocol, not an outbox feature supplied automatically. [Outbox source](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html), [catalog permission-data scope](https://github.com/lewan0996/arch-patterns/issues/21).

Delivery acknowledgement must represent successful application or an explicitly superseded revision, with durable retry state for partial fan-out and failed handlers. Reconciliation should repair missing work and compare authoritative revisions; it remains a backstop. Redis Pub/Sub, for example, loses messages when delivery or handling fails and is explicitly at most once, so a bare publish cannot fulfill reliable delivery. [Redis Pub/Sub delivery semantics](https://redis.io/docs/latest/develop/pubsub/).

## Update, refill and invalidation races

The following are protocol counterexamples constructed for this research. They are reasoning scenarios, not executed provider tests. Microsoft documents stale cache-aside windows, and Redis documents delayed-read/invalidation races and atomic conditional writes. [Cache-aside](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside), [client-side caching races](https://redis.io/docs/latest/develop/reference/client-side-caching/), [transactions and CAS](https://redis.io/docs/latest/develop/using-commands/transactions/).

| Interleaving | Failure | Required treatment in a candidate implementation |
| --- | --- | --- |
| Replacement v12 arrives; retry v11 arrives later | Old grant overwrites revocation | Atomically compare and replace by source revision; reject older versions; duplicate processing must not renew freshness |
| Miss reads v11; v12 is committed and pushed; slow refill writes v11 | Refill undoes active push | Push and refill use the same conditional installation protocol; plain GET then SET is insufficient |
| Miss starts reading v11; v12 commits; invalidation deletes the key; old read returns | Delete leaves no version to compare | Use an invalidation generation/fence, or reject old fills using retained version metadata; deleting a value alone does not protect pending reads |
| v12 is installed; key and its version are evicted; delayed v11 arrives | Compare-on-present cannot remember v12 | Retain a trustworthy version floor through the in-flight/replay window, or revalidate after cache reset; bounded source age is still required |
| Cache failover restores an older value and version floor | Earlier guard state disappears | Treat recovered state according to documented rollback semantics; independently reject snapshots past their source deadline |

These treatments separate two properties: monotonic cache revisions and the maximum age of data used to authorize. A valid but older snapshot can still meet the latter inside the declared lag window. Preventing every within-window regression requires version/fence state that survives eviction and failover, or renewed source validation. A compare operation against an empty cache cannot prove that history. This is a logical consequence of the interleavings above; Redis CAS only detects changes to the state it watches, including eviction. [Redis WATCH semantics](https://redis.io/docs/latest/develop/using-commands/transactions/).

Complete replacement pushes can skip intermediate revisions when each snapshot includes every dependency required for that key; incremental grant/revoke patches need gap handling. Invalidation plus refill reduces replacement payload and avoids writing cold values, but puts the next reader on the source and needs the pending-refill fence. Neither choice removes reliable change capture, bounded age or recovery work. This comparison is an inference from the race table and [Microsoft's cache update guidance](https://learn.microsoft.com/en-us/azure/architecture/best-practices/caching).

## One system-wide maximum lag

**Proposed invariant:** configure one maximum `L` for permission data throughout the system. For each complete snapshot, Access Management attests a conservative time `s` through which its answer reflects committed assignments, including effective role/policy dependencies. At authorization time `n`, use the snapshot only when:

```text
(n - s) + E <= L
```

`E` bounds the combined timestamp and clock uncertainty. Future or unverifiable timestamps are errors. If that uncertainty cannot be bounded operationally, the timestamp proof is unavailable: require a fresh source path with defined consistency or deny. A revision orders changes but is not itself a measurement of elapsed time. This is a derived sufficient condition for #21's lag requirement, not a guarantee offered by cache APIs. A source change committed after `s` can be absent, but the snapshot stops authorizing by the declared bound. [Catalog bound](https://github.com/lewan0996/arch-patterns/issues/21), [clock-dependent expiration](https://redis.io/docs/latest/commands/expire/).

Use an absolute source deadline and set cache retention to no more than its remaining duration. Check that deadline after network waits and before authorization; a request-local or optional L1 copy inherits it. Do not reset it on a cache hit, retry, transfer, restore, refill completion or replay. An unchanged answer can acquire a new deadline only after a new authoritative validation. Source commit time and validation time are distinct: an unchanged user can remain valid without having a recent assignment change. These are proposed enforcement rules derived from the invariant, consistent with the distinction between storage expiration and source consistency in [Microsoft caching guidance](https://learn.microsoft.com/en-us/azure/architecture/best-practices/caching).

Counterexample: with `L = 60s`, a snapshot observed at second 0 arrives at second 50 and receives a new 60-second TTL. It can authorize at second 100 although a revocation at second 1 is 99 seconds old. Keeping the original deadline stops this case. Sliding expiration can repeat the extension. A source read from a stale database replica cannot be stamped as current merely because the HTTP response is new; the source's own lag belongs inside `L` or must be bypassed. [Source replica refill limitation](https://learn.microsoft.com/en-us/azure/architecture/best-practices/caching).

A heartbeat can renew a freshness claim only if it proves that **all** relevant changes through its watermark have been applied, across every relevant partition and fan-out job. “Newest event seen” or “consumer connected” is insufficient while an earlier revocation is missing. Otherwise re-read the source. The same issue applies to a local projection, whose rebuild needs a consistent snapshot plus change-stream handoff and a recorded completeness point before serving. This is a protocol inference from ordered delivery and stale materialized-view risks. [Outbox ordering](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html), [materialized-view refresh reliability](https://learn.microsoft.com/en-us/azure/architecture/patterns/materialized-view).

Redis is an example of why provider details matter: replication is asynchronous; even `WAIT` does not provide strong consistency and acknowledged writes can be lost on failover. Thus a successful push does not prove every subsequent replica read sees it. Reading a primary reduces one lag path but does not prove durable monotonic state after failover. Absolute source deadlines still bound the age of restored snapshots if their metadata and clock assumptions remain trustworthy. [Redis replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/).

## Outages, bounds and denial

The following matrix applies the existing fail-closed rule; “usable” includes identity/scope, integrity, complete value, compatible interpretation and the source-age check. An empty permission set is a valid deny answer; timeout and malformed data are unknown. It is a proposed runtime interpretation of the [#11 contract](https://github.com/lewan0996/arch-patterns/issues/11#issuecomment-5767173587).

| Cache result | Access Management result | Authorization behavior |
| --- | --- | --- |
| Usable snapshot | Unavailable or unneeded | Evaluate locally until its source deadline; no outage extension |
| Miss, eviction, expired, invalid or cache failure | Fresh authoritative snapshot | Evaluate source answer; best-effort conditional refill; a failed cache write need not invalidate that source answer |
| Unusable or unavailable | Timeout, circuit open, overload or unknown freshness | Deny protected operation; record dependency failure separately from a known permission denial |
| Usable explicit empty/disabled snapshot | Unneeded | Deny; retain normal freshness rules so later grants are eventually visible |

Fallback concentrates load on Access Management precisely when the cache fails. Declare total request deadline, cache-attempt budget, source-attempt budget, concurrency and queue limits, retry count and cancellation propagation. Coalesce concurrent misses per key with a bounded wait; avoid multiplying retries across layers. Load shedding must preserve denial when no trustworthy answer remains. .NET's resilience stack provides total and per-attempt timeout, concurrency limiting, retry with jitter and circuit breaking; its defaults are examples, not the catalog's chosen budgets. [Microsoft HTTP resilience](https://learn.microsoft.com/en-us/dotnet/core/resilience/http-resilience).

The lag contract governs the authorization decision instant. A long-running command or stream can outlive that decision; whether it rechecks permission before a later effect is a separate owner decision. Bounded lag does not promise immediate revocation of work already authorized. [Catalog's explicit no-immediate-revocation scope](https://github.com/lewan0996/arch-patterns/issues/11#issuecomment-5767173587).

## Permission-filtered lists

A complete bounded set of permitted tenant/project/resource IDs can be fetched once and used as a predicate in the service's own query, combined with its resource-specific rules. Apply it before ordering, pagination and counts. This avoids per-row remote calls without requiring a persistent permission projection. OpenFGA documents the analogous “list authorized IDs, then search” option. The application still owns its business data; a coarse capability such as `orders.read` alone cannot identify every visible order. [OpenFGA search with permissions](https://openfga.dev/docs/interacting/search-with-permissions), [catalog ownership and reads](https://github.com/lewan0996/arch-patterns/issues/11#issuecomment-5767173587).

Do not treat a truncated or partially materialized set as complete. OpenFGA's ListObjects documentation explicitly describes time and result limits. A cached list must establish completion and one coherent freshness basis; permission changes during pagination need a snapshot/restart protocol. The last requirement is an inference about assembling a complete set, not an assertion that OpenFGA supplies such a protocol. [OpenFGA relationship-query caveats](https://openfga.dev/docs/interacting/relationship-queries).

**Selection inference:** if the permission set or relationship expansion cannot fit bounded transfer/query costs, and the product requires complete database-side filtering, sorting and counts without remote checking of candidates, a local permission projection/index is needed within these two profiles. A specialized authorization query service could be a separate alternative. Small candidate pages can use a batch authorization call, but that changes the remote-dependency contract and may require further scanning to fill a page. OpenFGA describes batch checks and local indexes, including the stale-revocation risk; its example local-index design still checks results remotely. It is not evidence that any asynchronous local index is immediately current. [OpenFGA search alternatives](https://openfga.dev/docs/interacting/search-with-permissions).

## Alternatives and selection trade-offs

| Approach | Evidence-backed reason to consider it | Remaining cost or condition |
| --- | --- | --- |
| Complete replacement cache with source fallback | Reuses a compact permission snapshot across services; conditional updates can guard races | Reliable fan-out, shared cache request dependency, age enforcement and source capacity during misses |
| Invalidation plus refill | Avoids transporting full replacements to cold entries | Pending-read fencing and additional source work after invalidation |
| Event-fed local permission projection | Shapes local data for joins and repeated authorization without a shared cache call | Durable consumption, lag proof, gap recovery and rebuild per service |
| Direct authorization/source query | Centralizes evaluation and can bypass a result cache for a current read | Network latency, availability and source throughput on the request path |

The first two comparisons are research inferences grounded in [cache-aside](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside). The projection follows [materialized views](https://learn.microsoft.com/en-us/azure/architecture/patterns/materialized-view). OpenFGA's `HIGHER_CONSISTENCY` explicitly bypasses its cache for a database query, demonstrating the final option and its performance trade-off; this does not select OpenFGA or prove an arbitrary source's replica freshness. [OpenFGA consistency modes](https://openfga.dev/docs/interacting/consistency).

Cache support is most plausible for bounded, frequently reused sets where the shared cache dependency and tested fallback capacity are acceptable. Projection support fits richer filtering and autonomy during cache outages, but still stops authorizing after its own freshness bound. Neither profile wins universally, and neither has a verified implementation here. These are selection inferences from the preceding contracts, not measured performance findings.

## Minimum observable recovery and verification contract

The following is a **proposed acceptance suite for a future implementation**, derived from the counterexamples and cited contracts above. None of these runtime scenarios was executed in this documentation research.

| Scenario to inject | Binary success observable | Evidence to capture in the future template |
| --- | --- | --- |
| Crash after source commit, before push; then restart | Every affected key eventually reflects that revision or a newer one; no snapshot authorizes past `L` | Source commit, outbox/retry records, per-key applied revisions and decision timestamps |
| Duplicate/reorder pushes and overlap a slow refill | No unguarded regression; duplicate cannot extend original validity | Deterministic schedule, conditional-write results, value/deadline trace |
| Evict versions; replay old values; restore/fail over cache | No snapshot beyond its source deadline authorizes; any monotonic guarantee holds across the reset | Reset epoch/fence trace, provider topology and authorization outcomes |
| Pause a partition or fan-out while later heartbeats arrive | Incomplete progress cannot renew affected snapshots | Contiguous checkpoint, unresolved-work list and stale-data denials |
| Boundary at `L`, delayed reads, clock jumps and excessive uncertainty | Accept only inside the defined age budget; uncertain time fails closed | Controlled clock/read-delay trace and decision at each boundary |
| Cache outage, source outage and both together under peak load | Matrix holds; source attempts and total request time remain inside configured bounds | Dependency fault timeline, request/queue metrics, decisions and latency |
| Role/member/tenant changes and complete filtered paging | All affected sets refresh; forbidden rows/counts never escape the selected freshness contract | Source dependencies, result IDs/counts and snapshot revision per page |
| Full rebuild/reconciliation during changes | Serving resumes only with complete compatible state; backlog is observable | Snapshot/change handoff, revision comparison and recovery duration |

Observe oldest pending source work, source-to-application delay, rejected older revisions, cache age at decision, misses/evictions, fallback concurrency/timeouts and unknown-data denials. Alert before age exhaustion where possible. A low queue length or high cache hit ratio does not prove freshness. Proposed recovery ownership includes poison-message handling, replay retention, resumable fan-out and reconciliation, informed by [materialized-view reliability guidance](https://learn.microsoft.com/en-us/azure/architecture/patterns/materialized-view).

## Decisions still owned by the catalog owner

- Retain both supported microservice profiles, narrow cache support to bounded sets, or prefer only the projection? This research establishes conditions, not the answer.
- What is the one system-wide `L`, and does it bound only assignment data or also policy versions and long-running effects? How are configuration changes rolled out consistently?
- Are within-window version regressions acceptable, or is durable monotonicity also required? Which snapshot/fence/freshness protocol will be specified and verified?
- Which role fan-out sizes, complete-set sizes, query shapes, source budgets and outage objectives must the catalog support?
- For [technology ticket #13](https://github.com/lewan0996/arch-patterns/issues/13): require atomic conditional replacement with expiration, documented replication/failover/restore behavior, trustworthy time handling, durable delivery/replay, complete snapshot reads, bounded remote calls and fault-injection evidence before claiming a provider substitution.

Validation performed for this report: live primary-source retrieval, claim-to-source review, issue/context inspection, Markdown content/link checks and exact published-blob verification. No cache benchmark, runnable authorization implementation or production-readiness claim is made.
