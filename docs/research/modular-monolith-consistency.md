# Consistency and transactions in a modular monolith

Research checked 2026-11-15 for [Investigate a minimal dispatcher, MediatR fork or Wolverine](https://github.com/lewan0996/arch-patterns/issues/37). The owner wants atomic monolith operations without eventual consistency or business compensation machinery. This note supplies precedents and trade-offs; it does not amend prior decisions, adopt a framework or claim runtime verification.

## Finding

Synchronous module interaction under one relational transaction is a documented approach. It trades independent transactional autonomy for atomic completion. A failed operation can be rolled back by the database; the application does not have to write inverse business operations for every participating module. The remaining integration task is ensuring that every participating context really uses the same transaction, and that effects outside that database are not performed before commit. [EF transaction documentation](https://learn.microsoft.com/en-us/ef/core/saving/transactions#cross-context-transaction).

The important design question is which operations belong to one consistency boundary. This catalog defines a module as an internal ownership boundary, so choosing a module does not inherently require giving it a separate database or independent commit boundary. This is an interpretation of the current [glossary](../../CONTEXT.md), not a new owner decision.

## Strong precedents

### ABP: in-process event handlers participate in the originating unit of work

ABP's official documentation describes its default `LocalDistributedEventBus` executing handlers in the publishing unit of work. An escaping handler exception rolls back that transaction. Without outbox/inbox, events normally run just before the unit of work completes; broker-backed operation has different boundaries. This closely matches the requested semantics. The API's “distributed” name does not mean that its default implementation crosses processes. [Transaction and exception handling](https://abp.io/docs/latest/framework/infrastructure/event-bus/distributed#transaction-and-exception-handling), [unit of work](https://abp.io/docs/latest/framework/architecture/domain-driven-design/unit-of-work).

ABP's EF implementation makes the mechanics explicit: find an active transaction by connection string, pass its existing connection into creation of the next context, then call `UseTransactionAsync` if the context actually reused that connection object. A context that ignores it instead gets another transaction; a unit-of-work label alone does not establish distributed atomicity. This source was inspected at commit `2936016f45bce86527c95f09e7e57c742cbeb241`, not exercised locally. [Pinned EF context provider](https://github.com/abpframework/abp/blob/2936016f45bce86527c95f09e7e57c742cbeb241/framework/src/Volo.Abp.EntityFrameworkCore/Volo/Abp/Uow/EntityFrameworkCore/UnitOfWorkDbContextProvider.cs#L232-L319).

### Spring Modulith: synchronous cross-module events preserve the transaction

The official example starts with an order operation calling Inventory, then replaces that dependency with an application event. Default synchronous dispatch preserves the transaction: order and inventory changes succeed together or neither does. The documented cost is a wider transaction and the ability of any listener to fail the operation. Asynchronous listeners are presented separately. This is a strong architectural precedent, but it is Java/Spring and does not prove Wolverine or EF integration. [Working with application events](https://docs.spring.io/spring-modulith/reference/events.html).

### Microsoft and Jimmy Bogard: dispatch before commit

Microsoft's domain-event guidance describes dispatch before or after commit. Before-commit handling can include side effects in the original transaction; its scoped example shares one EF context across repositories. It demonstrates aggregate coordination inside a domain, not automatic participation of distinct module-owned contexts. [Domain events: design and implementation](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/domain-events-design-implementation).

Jimmy Bogard's original pattern records events on entities and dispatches them before committing, separating event creation from its side effects while retaining one logical transaction. It also distinguishes that option from persisting events for later processing. It is conceptual guidance, not a multi-context transaction manager implementation. [A better domain events pattern](https://lostechies.com/jimmybogard/2014/05/13/a-better-domain-events-pattern/).

## Practical .NET articles and caveats

Milan Jovanović's multiple-context article uses separate schemas in one database and explicitly notes that shared transactions require `UseTransaction`. His newer schema-versus-database article treats shared transactions as an available escape hatch with schema isolation, while warning that they increase coupling. These are examples of a deliberate trade-off, rather than a rule that modularity requires eventual consistency. Connection-string equality in the registration examples is not sufficient transaction enlistment by itself. [Using multiple DbContexts](https://milanjovanovic.tech/blog/using-multiple-ef-core-dbcontext-in-single-application), [Schema-per-module versus database-per-module](https://milanjovanovic.tech/blog/schema-per-module-vs-database-per-module).

Anton Martyniuk demonstrates a scoped `TransactionManager`, module contexts using `UseTransactionAsync`, and one final commit. He explicitly identifies direct access to other modules' contexts as coupling that breaks his chosen module boundaries. The displayed sample does not show the shared physical-connection setup required by EF, so it should be read as an outline rather than copied as a complete recipe. It supports the existence of the approach, with important implementation and ownership caveats. [Transactions across database schemas in a modular monolith](https://antondevtips.com/blog/querying-and-performing-transactions-across-multiple-database-schemas-in-a-modular-monolith).

## The stricter autonomous-module alternative

Kamil Grzybek deliberately chooses stronger module autonomy: his sample integrates modules asynchronously and prohibits transactions across them. His integration-styles article distinguishes sharing a database from sharing its data, compares coupling/complexity/timeliness, and also recognizes direct calls when strong consistency matters more than maximum autonomy. Its direct-call section still excludes cross-module transactions, so direct calls alone must not be cited as an atomicity implementation. That architecture makes eventual consistency a conscious consequence of independence, not a universal definition of a monolith. [Sample architecture](https://github.com/kgrzybek/modular-monolith-with-ddd#37-modules-integration), [Integration styles](https://www.kamilgrzybek.com/blog/posts/modular-monolith-integration-styles).

## What Wolverine itself recommends

Wolverine's modular-monolith tutorial recognizes the simplicity of one database transaction and discourages introducing eventual consistency unnecessarily. Its preferred decision is to combine tightly related functionality into a larger module, or justify asynchronous communication; it generally discourages nested inline cross-module invocation. Its EF section explicitly says that multi-context work requires explicit code rather than its automatic transaction middleware. This supports reconsidering module granularity before building a general cross-module coordinator. [Eventual consistency between modules](https://wolverinefx.net/tutorials/modular-monolith.html#eventual-consistency-between-modules), [With EF Core](https://wolverinefx.net/tutorials/modular-monolith.html#with-ef-core).

## Interpretation for this catalog

The following is a recommendation inferred from the evidence and the owner's stated priorities:

1. Keep atomicity as an input to framework selection. A framework's convenient messaging model should not decide the product's consistency requirements.
2. First examine whether the frequently coordinated responsibilities belong to one larger module or persistence unit. Internal feature boundaries can still be maintained. This may simplify the transaction substantially, but adopting it would require revisiting the catalog's current module/context and migration commitments.
3. When separate module ownership is valuable, a shared-host unit of work can coordinate their contexts over one physical connection and transaction. Invoke module-owned behavior or immediate handlers through contracts; do not require an application handler to manipulate another module's context. This couples completion and failure without requiring shared access to tables or domain models.
4. Keep queued post-commit work for operations whose delayed completion is acceptable. It cannot satisfy an all-or-nothing requirement with the originating transaction. External email, payments or broker effects cannot be undone by rolling back a local database transaction.

This does not require saga compensation for the atomic local path. It does require one transaction owner, correct context enlistment, propagation of failures and bounded transaction duration. EF's `TransactionScope` option is not a shortcut around these constraints: provider support matters and distributed `System.Transactions` support is Windows-specific. The shared-connection recipe avoids needing a distributed transaction coordinator. [EF transactions and provider limitations](https://learn.microsoft.com/en-us/ef/core/saving/transactions).

No production coordinator or prototype was implemented, no framework adoption was recorded, and no recommendation here certifies runtime support.
