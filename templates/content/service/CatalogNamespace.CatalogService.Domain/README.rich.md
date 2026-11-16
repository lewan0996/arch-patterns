# Rich domain

Group business behavior by capability and aggregate. Aggregate roots enforce
their own invariants and encapsulate state changes; only Application-owned
aggregate-root repositories persist them. Keep internal entities and domain
events within this module. Domain events describe domain behavior and are not
published integration-event contracts or an implicit cross-module transaction.

Keep persistence mappings in Infrastructure, use-case coordination in Application,
public query responses in Contract and transport DTOs in API. Add meaningful
invariant tests in this boundary's Domain.UnitTests project, mirroring the domain
capability structure. No business model or placeholder passing test is generated.
