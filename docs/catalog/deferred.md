# Guidance-only and deferred capabilities

[Catalog](README.md) · [Selection route](selection.md) · [Current delivery contract](delivery.md)

These alternatives can inform design but do not extend the initial executable inventory. Choose them only with a separate implementation decision; reconsider when their extra infrastructure, state or maintenance cost exceeds the concrete benefit. Their historical designs do not certify runtime support.

| Alternative and scope | Choose / reconsider signal | Existing follow-up |
| --- | --- | --- |
| Shared CQRS policy declarations/support generator / module | Repeated policy plumbing might justify shared tooling; module-local authorization is retained initially | [#39](https://github.com/lewan0996/arch-patterns/issues/39) |
| Shared gateway/YARP / system | Multiple client APIs benefit from common routing; direct calls avoid the extra hop initially | [#40](https://github.com/lewan0996/arch-patterns/issues/40) |
| Shared internal API key / internal endpoint | Coarse trusted-system membership may suffice; it does not identify individual services | [#41](https://github.com/lewan0996/arch-patterns/issues/41) |
| Application-managed permissions/projections / system and receiver | Assignment control/freshness needs may exceed token permissions; extra synchronization/recovery required | [#42](https://github.com/lewan0996/arch-patterns/issues/42) |
| Configurable advanced delayed redelivery / message endpoint | Operations need more than bounded baseline retries; avoid extra schedules without that need | [#43](https://github.com/lewan0996/arch-patterns/issues/43) |
| Dedicated saga/workflow engine / participating owners | Long-running coordination needs explicit state/compensation; committed-fact choreography remains initial guidance | [#44](https://github.com/lewan0996/arch-patterns/issues/44) |
| Separate read database / data owner | Independent read storage merits synchronization cost; separate shapes in existing storage remain retained | [#45](https://github.com/lewan0996/arch-patterns/issues/45) |
| AsyncAPI generation/validation / contracts | Tooling adds value over clear payload/envelope documentation; HTTP/event docs remain required | [#46](https://github.com/lewan0996/arch-patterns/issues/46) |
| Platform workload identity / deployable | Prefer where platform and resource support it; concrete integration requires a selected platform | [#47](https://github.com/lewan0996/arch-patterns/issues/47) |
| Platform deployment automation / system | Selected platform warrants manifests/provisioning/pipelines; portable containers remain initial output | [#48](https://github.com/lewan0996/arch-patterns/issues/48) |
| Replication/rolling deployment/autoscaling profiles / operational boundary | Availability/load needs justify orchestration; baseline lifecycle/idempotency are prerequisites | [#49](https://github.com/lewan0996/arch-patterns/issues/49) |
| Add-aggregate/add-entity editing / existing module | Specific domain design may benefit from assisted edits; creation workflow cannot authorize arbitrary edits | [#50](https://github.com/lewan0996/arch-patterns/issues/50) |
| Additional agent clients/co-installation / project | Another client needs exercised compatibility; neutral source alone proves no client support | [#51](https://github.com/lewan0996/arch-patterns/issues/51) |
| Cross-module atomic transaction / shared host | Business requirement truly needs shared rollback; conflicts with claiming initial asynchronous subscribers share publisher transaction | [#53](https://github.com/lewan0996/arch-patterns/issues/53) |
| Contract compatibility tooling / public contract | Explicit consumer compatibility proof is required beyond initial checks | [#34](https://github.com/lewan0996/arch-patterns/issues/34) |
| Advanced metrics/tracing / operational boundary | Diagnosis needs exceed structured logs; backend/profile requires its own decision | [Research #23](https://github.com/lewan0996/arch-patterns/issues/23), [profiles #24](https://github.com/lewan0996/arch-patterns/issues/24) |
| Inbound traffic protection / entry point | Exposure/load requires a dedicated protection profile | [#25](https://github.com/lewan0996/arch-patterns/issues/25) |

Initial scope also excludes performance testing, paid live-agent CI obligations, production RabbitMQ, Quartz scheduling, custom per-attempt failure journals, permanent sent-event archives, generic use-case generators, automatic flat-to-modular conversion, arbitrary existing-service migration, personal/global skill installation, multi-region/disaster recovery and product-specific account-management workflows. See the [map exclusions](https://github.com/lewan0996/arch-patterns/issues/1) and [parent scope](https://github.com/lewan0996/arch-patterns/issues/54) for their authoritative boundaries. They do not acquire executable obligations through broad completion language.
