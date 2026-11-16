# Catalog

An ingredient is a decision area; an option is a named approach within it. High-level architecture describes system composition. Low-level architecture describes a module inside one deployable host. Cross-cutting choices identify their owning scope below. Use the [glossary](../../CONTEXT.md) for precise terms.

Follow the [selection route](selection.md), or browse the ingredients:

| Level / owning scope | Ingredient and options | Guidance |
| --- | --- | --- |
| High-level / system | Modular monolith; microservices | [Composition](structure.md#system-composition) |
| High-level / system and client-facing boundary | Public monolith host; browser BFF; machine audience API; optional gateway | [Client-facing composition](structure.md#client-facing-composition) |
| Low-level / microservice host | Flat single-module; modular | [Deployable layout](structure.md#deployable-layout) |
| Low-level / module | Five-project responsibilities; business-capability/use-case grouping | [Dependencies](modules.md#responsibilities-and-dependencies) |
| Low-level / module | Anemic; rich domain model | [Domain shape](modules.md#domain-model) |
| Low-level / module | Direct-service; CQRS application-flow profile | [Application flow](modules.md#application-flow) |
| Cross-cutting / data-owning module | EF Core writes; PostgreSQL or SQL Server; EF SQL-first, Dapper or LINQ reads | [Persistence](runtime.md#persistence-and-reads) |
| Cross-cutting / entry point and receiving module | Browser sessions; access tokens; user/application authority; token-carried permissions | [Security](runtime.md#identity-and-authorization) |
| Cross-cutting / publisher, subscriber and host | Durable local facts; published integration events; service-local copies | [Communication](runtime.md#communication-and-consistency) |
| Cross-cutting / operational boundary | Bounded HTTP; optional safe retries; process, configuration, local development and container baseline | [Operations](runtime.md#operational-baseline) |
| Delivery / solution and affected boundary | Native templates; AI creation; selection record; tests and evidence | [Delivery and support](delivery.md) |

## Compatibility and support are separate

Record conceptual compatibility as **compatible**, **requires a prerequisite**, **conflicts**, or **unresolved**. A missing decision is unresolved, not permission to generate an arbitrary combination. Compatibility says nothing about executed checks.

Use these separate support descriptions:

- **Documented:** guidance or a contract exists; this alone makes no runtime claim.
- **Planned generation:** retained in the implementation inventory, with a linked capability ticket. It is not available until delivered.
- **Verified executable support:** a specific release, selection and environment have passing applicable creation/runtime evidence. Package `0.1.0` verifies only [microservices solution scaffolding](microservices-solution.md); it has no application runtime combination.
- **Guidance-only:** useful architectural discussion outside initial executable scope; follow its deferred effort.

The [microservices solution page](microservices-solution.md) supplies its actual output tree, commands and bounded evidence. Other retained options remain documented guidance with planned implementation; their full pages, actual generated project/test trees and runtime evidence arrive with their capability tickets. Illustrative diagrams and trees elsewhere describe responsibilities. [Deferred options](deferred.md) remain guidance-only.

## Source precedence

The [ingredient model](https://github.com/lewan0996/arch-patterns/issues/5#issuecomment-5744277308) separates architecture from technology and support. The [page amendment](https://github.com/lewan0996/arch-patterns/issues/15#issuecomment-6882910738) allows concise baseline-linked alternatives while requiring full treatment for delivered initial options.

Apply the [scope review](https://github.com/lewan0996/arch-patterns/issues/38#issuecomment-6894667420), then the [final Wolverine integration decision](https://github.com/lewan0996/arch-patterns/issues/52#issuecomment-6900052949). The latter replaces earlier MediatR/MassTransit recipes and cross-module atomicity requirements. Modules commit independently; local subscribers run asynchronously. Research and older resolution comments remain historical evidence where superseded.

See the [decision map](https://github.com/lewan0996/arch-patterns/issues/1) for the complete source index, and [delivery](delivery.md#examples-and-evidence) for the two planned baselines and focused variations.
