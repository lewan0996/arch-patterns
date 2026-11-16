# Rich domain / direct services

The selected rich domain model owns business invariants and domain events inside
this module's Domain project. Application capability interfaces expose separate
CQS methods for changes and queries, with acyclic service reuse. Their command
implementations load an aggregate root through an Application-owned aggregate-root
repository contract, invoke domain behavior, and commit explicitly. Infrastructure
implements that repository using the module-owned DbContext. Repositories return
aggregate roots, never arbitrary internal entities or query response shapes.

Use a separate Application-owned read-query contract returning public Contract
response shapes. Infrastructure implements parameterized SQL reads over this
module's schema; query methods do not belong in aggregate repositories. API owns
transport DTOs and mapping. Domain and Contract have no EF or dispatch dependency.

The scaffold invents no aggregate, repository, business service or endpoint. Add
the actual capability and its owner-local domain tests when requirements exist.
Register its repository, query adapter and Application service in API composition;
later protected use cases require their selected authorization decorator. The
catalog's rich/direct-service fixture exercises unrestricted Application calls,
aggregate invariants and separate reads against real PostgreSQL.
