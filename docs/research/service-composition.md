# Independent service architecture ingredients

Research for [Investigate independent service architecture ingredients](https://github.com/lewan0996/arch-patterns/issues/2), checked 2026-09-19. This report establishes distinctions and unresolved choices; it selects no template architecture. Sources are pattern authors, Microsoft documentation, and the Dapper project. Framework documentation demonstrates available mechanisms, not a validated implementation of this catalog.

## Dimensions and their relationships

The following decomposition is a research synthesis, not an adopted taxonomy. The cited definitions support separating these concerns rather than offering one mutually exclusive list of “Clean / DDD / CQRS / vertical slices.”

| Concern | Alternatives or distinctions | Evidence and constraint |
| --- | --- | --- |
| Dependency direction | Conventional downward layers; inward dependencies toward policy | [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) requires inner code to avoid outer implementation dependencies. [N-tier](https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/n-tier) distinguishes logical layers from physical tiers. |
| Organization of changes | Technical layers; use-case slices; explicitly defined hybrids | [Bogard's vertical slices](https://www.jimmybogard.com/vertical-slice-architecture/) group concerns around requests and minimize coupling between slices. |
| Location of business behavior | Transaction scripts; behavior-rich domain objects | [Transaction Script](https://martinfowler.com/eaaCatalog/transactionScript.html) organizes logic per request. [Fowler's anemia discussion](https://martinfowler.com/bliki/AnemicDomainModel.html) distinguishes procedural services from domain behavior. |
| Read/write modeling | Shared model; separate command and query models | [CQRS](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs) permits separate models over one database. |
| Persistence and query implementation | EF LINQ; EF SQL; Dapper; potentially distinct write and read tools | [EF querying](https://learn.microsoft.com/en-us/ef/core/querying/sql-queries) and [Dapper](https://github.com/DapperLib/Dapper) expose SQL-based options. |
| Hosting and endpoint ownership | Independent web host; module endpoints in a shared host | [Route groups](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/route-handlers?view=aspnetcore-10.0#route-groups) and [Application Parts](https://learn.microsoft.com/en-us/aspnet/core/mvc/advanced/app-parts?view=aspnetcore-10.0) support endpoint composition. |

## Layers, slices, and domain models

Clean Architecture specifies dependency direction and separates business policy from mechanisms. Its circles are schematic, not a mandatory count of projects. A feature folder alone neither establishes nor violates its dependency rule. Conversely, an inner application layer that directly references an outer persistence implementation conflicts with that rule, regardless of folder names. [Original definition](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html).

Bogard's formulation goes beyond organizing files by feature: each request may choose how it accesses data and implements logic, without a mandatory controller–service–repository chain. He explicitly allows starting with transaction scripts and introducing richer domain behavior when needed. Therefore, “vertical slices + rich domain” is plausible; “vertical slices + Clean Architecture” needs an explicit definition of which dependency constraints remain. That compatibility statement is an inference from the two authors, not a standardized hybrid. [Vertical Slice Architecture](https://www.jimmybogard.com/vertical-slice-architecture/), [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html).

“Anemic” carries a specific criticism: paying for an elaborate domain object model while moving its behavior into services. It should not automatically condemn an intentionally simple CRUD implementation. Fowler acknowledges that domain models are not always appropriate; Microsoft likewise distinguishes complex business services from simpler CRUD responsibilities. A service layer can coordinate a rich domain, so application services do not imply anemia. [Anemic Domain Model](https://martinfowler.com/bliki/AnemicDomainModel.html), [DDD-oriented microservices](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/ddd-oriented-microservice).

DDD also involves business language and boundaries, beyond selecting entity classes and aggregates. Consequently, “rich model” and “DDD” should not be assumed to mean exactly the same option. Logical layers do not themselves determine deployment boundaries. [Microsoft's DDD guidance](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/ddd-oriented-microservice).

## CQRS and invocation

CQRS separates read and write models; it does not inherently require separate databases, asynchronous commands, event sourcing, or a broker. Microsoft presents a single-store baseline and a separate-store extension; event synchronization introduces additional consistency concerns. Merely naming methods “command” and “query” is insufficient evidence of model separation. [CQRS pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs).

Inference: direct calls to injected services and dispatch through a mediator are invocation choices, not opposite ends of the CQRS choice. A direct service interface can expose separate models; a dispatcher can still send everything through one shared model. The catalog must specify actual contracts and model ownership rather than infer CQRS from a library dependency. This follows from Microsoft's model-based definition; no dispatcher library is selected here. [CQRS pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs).

## Domain richness does not choose the query tool

Microsoft's DDD example persists aggregate changes with EF Core while retrieving presentation data with Dapper, bypassing aggregate repository restrictions for those reads. This establishes one compatible combination, not a requirement for rich models. [Infrastructure persistence example](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-implementation-entity-framework-core).

EF LINQ can project only required columns; read operations need not load complete aggregate graphs. EF also supports no-tracking queries. Its performance guidance emphasizes generated SQL, indexes, result size, and round trips, so “EF is overkill for DDD reads” is not a conclusion the evidence supports without workload measurements. [Efficient Querying](https://learn.microsoft.com/en-us/ef/core/performance/efficient-querying).

EF SQL queries can return unmapped CLR result types from EF Core 8 onward. Dapper maps SQL results to objects and supports parameterized execution. Thus EF LINQ, EF SQL, and Dapper are distinct query implementation options; changing domain behavior need not automatically switch among them. The last sentence is a synthesis, not a benchmark claim. [EF SQL queries](https://learn.microsoft.com/en-us/ef/core/querying/sql-queries), [Dapper documentation](https://github.com/DapperLib/Dapper).

## Modules in one host

ASP.NET Core documents reusable route-mapping extension methods and route groups with shared prefixes and authorization metadata. MVC Application Parts can discover controllers in separate assemblies. Both provide mechanisms for module-owned endpoints exposed by one host. [Minimal API route groups](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/route-handlers?view=aspnetcore-10.0#route-groups), [Application Parts](https://learn.microsoft.com/en-us/aspnet/core/mvc/advanced/app-parts?view=aspnetcore-10.0).

Inference: hosting is therefore separable from module internals, but endpoint composition alone does not define data ownership, module contracts, or transaction boundaries. Those require catalog decisions. Keeping module endpoint ownership explicit avoids equating a shared executable with one centrally owned API implementation. These conclusions concern the documented composition mechanisms, not a promise that moving a module between hosts needs no changes.

## Newly sharp follow-up questions

- Which dependency rules define each supported layered, sliced, or hybrid option?
- May slices choose business-logic and query strategies individually, or only per service/module?
- What concrete model separation qualifies an option as CQRS, independently of dispatch tooling?
- Which read tools are supported substitutions, and what workload evidence justifies a recommendation?
- Do module contracts permit direct calls, shared transactions, or cross-module reads?
- Does create-only generation leave solution references and host registration as explicit manual steps?

These are decision questions for later tickets. No application code or template was generated or executed during this documentation investigation.
