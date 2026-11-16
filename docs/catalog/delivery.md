# Delivery and support

[Catalog](README.md) · [Selection route](selection.md) · [Deferred capabilities](deferred.md)

## Creation chains

**Current support:** local package `ArchPatterns.Templates` `0.2.0` implements
[host-free microservices solutions](microservices-solution.md), [flat services](flat-service.md)
with the operational baseline, and [anemic/direct-service PostgreSQL persistence](direct-service-postgresql.md).
Installed-package, Linux OCI and real PostgreSQL fixture checks cover those paths;
see the [dependency/evidence review](../dependencies/service-increment.md). Modular
and client-facing components, creation skills and complete system examples remain planned.

| Selected structure | Native chain / status | Owning capability |
| --- | --- | --- |
| Microservices solution | [Implemented in 0.2.0](microservices-solution.md): `arch-solution --composition microservices`; no system-wide host | [#56](https://github.com/lewan0996/arch-patterns/issues/56) |
| Modular-monolith solution | `arch-solution` with explicit monolith composition creates public host; `arch-module` creates initial and later named modules | [#59](https://github.com/lewan0996/arch-patterns/issues/59) |
| Flat service | [Implemented in 0.2.0](flat-service.md): `arch-service --layout single --domainModel anemic --applicationFlow direct-service --database postgresql` | [#57](https://github.com/lewan0996/arch-patterns/issues/57) |
| Modular microservice | `arch-service` with modular layout, then `arch-module` for required initial module; same invocation chain for later modules | [#60](https://github.com/lewan0996/arch-patterns/issues/60) |
| Browser BFF | `arch-bff` in a fresh component folder | [#68](https://github.com/lewan0996/arch-patterns/issues/68) |
| Machine audience API | `arch-audience-api` in a fresh component folder | [#67](https://github.com/lewan0996/arch-patterns/issues/67) |

The completed native NuGet template package will expose exactly these five entry points; later capabilities extend the same package. There is no test, gateway or domain-editing generator. The [generation contract](https://github.com/lewan0996/arch-patterns/issues/14#issuecomment-5849731801) and [layout contract](https://github.com/lewan0996/arch-patterns/issues/28#issuecomment-6002994331) govern composition.

Require explicit composition, valid namespaces, unique PascalCase names, applicable selections, distinct fresh destinations and intended solution membership. Before each native invocation, reject occupied destinations and unsupported selections. A native template may add its newly generated projects to the intended solution; it makes no other edits to existing files. Ambiguous/nested solution discovery must not modify an unrelated solution. Provide precise manual integration instructions where automation is outside the contract. Adding a module to a flat service stops with a conversion prerequisite.

AI creation uses those same verified native chains. Its additional allowed edits are the root selection record and narrow integration of a newly created module into its intended existing modular host. No unrelated source/configuration rewrites or silent repair. Update current selections only after success and report partial work honestly. See [record #81](https://github.com/lewan0996/arch-patterns/issues/81), [initial actions #82](https://github.com/lewan0996/arch-patterns/issues/82), [modular actions #83](https://github.com/lewan0996/arch-patterns/issues/83) and [client-facing actions #84](https://github.com/lewan0996/arch-patterns/issues/84).

An explicit named invocation or natural-language action request may select a creation skill; discussion alone must not execute it. One agent-neutral source supplies self-contained project-local resources, with Codex CLI the initial integration to implement and verify. No personal/global configuration changes are included. Sources: [action amendment](https://github.com/lewan0996/arch-patterns/issues/19#issuecomment-6894475615) and [packaging amendment](https://github.com/lewan0996/arch-patterns/issues/27#issuecomment-6894475843). Other clients remain unverified [future work](deferred.md).

## Examples and evidence

| Planned example / variation | Selection and purpose | Delivery |
| --- | --- | --- |
| Modular-monolith baseline | One public host, anemic/direct-service and rich/CQRS named modules; owned data/contracts and asynchronous independent module transactions | [#85](https://github.com/lewan0996/arch-patterns/issues/85) |
| Microservice-system baseline | Independently deployed flat and modular services, initial/additional modules, both baseline profiles, applicable BFF/audience API, committed facts and recoverable local copy | [#86](https://github.com/lewan0996/arch-patterns/issues/86) |
| Rich/direct-service variation | [Implemented PostgreSQL variation](rich-direct-service.md): aggregate behavior and separate reads with capability-service invocation | [#61](https://github.com/lewan0996/arch-patterns/issues/61) |
| Anemic/CQRS variation | Data-only domain with explicit command/query dispatch | [#62](https://github.com/lewan0996/arch-patterns/issues/62) |
| SQL Server variation | Provider/migrations and persistence/messaging proof | [#76](https://github.com/lewan0996/arch-patterns/issues/76), [#77](https://github.com/lewan0996/arch-patterns/issues/77), [#78](https://github.com/lewan0996/arch-patterns/issues/78) |
| Dapper variation | Query tooling changes without changing flow profile | [#79](https://github.com/lewan0996/arch-patterns/issues/79) |

The [combination decision](https://github.com/lewan0996/arch-patterns/issues/17), [reduced verification contract](https://github.com/lewan0996/arch-patterns/issues/16#issuecomment-6899852467) and [final integration decision](https://github.com/lewan0996/arch-patterns/issues/52#issuecomment-6900052949) require a bounded set of meaningful fixtures, not all possible permutations.

Before claiming verified support, the owning implementation must supply:

- Package installation/discovery/help, actual retained generation chains, restore/build, references/registration, architecture rules and preservation of write boundaries.
- Boundary-owned domain unit tests where behavior exists, real-dependency application integration tests and architecture checks. Actual generated project/test trees and integration instructions must match those fixtures; empty test success is insufficient.
- Authorization before protected work for HTTP/non-HTTP, direct-service/CQRS, missing context/rules, concurrent caller isolation and background authority.
- Real PostgreSQL and SQL Server transaction/outbox/inbox checks, independent subscriber commits/failures, crash/restart, route/handler ownership, duplicate business idempotency beyond inbox retention and identity-preserving replay. Cross-module rollback is not a requirement.
- Actual managed Azure Service Bus delivery/recovery evidence for both persistence providers, including broker/failure-transfer outages and native failure destinations. RabbitMQ local smoke is reported separately.
- Health/lifecycle/configuration/secrets, bounded HTTP and selected retries, portable container behavior, selected local-copy freshness/recovery and generated Wolverine production Static startup.
- Separate installed-bundle manual Codex CLI evidence for named/natural-language/discussion behavior, supporting-resource resolution, allowed edits and reporting, with client/surface/version/date/limitations.

The [release ticket #87](https://github.com/lewan0996/arch-patterns/issues/87) consolidates evidence and package delivery. It also reviews a coherent .NET/ASP.NET Core/EF Core 10, provider, Wolverine and transport graph, direct/transitive licenses, service terms and maintenance for the actual release. A researched version or architectural compatibility is not a release certification.

## Documentation completion

Capability tickets add full initial option pages with intent, choose/reconsider guidance, compatibility separate from support, GitHub Mermaid diagrams, annotated actual project/test trees, dependencies and exact generation/integration/check steps. Useful alternatives may be concise baseline-linked variations. Follow the [page-format amendment](https://github.com/lewan0996/arch-patterns/issues/15#issuecomment-6882910738).

Keep the [selection worksheet](selection.md#selection-worksheet), examples, source decisions and support statements aligned as evidence arrives. Ordinary documentation and CI evidence are sufficient; no new reporting subsystem is required.
