# Anemic domain / direct services

Organize each business capability together. Its public Application-owned interface
exposes separate CQS methods for changes and reads. Implement it in Application;
keep service reuse acyclic. Put data-only entities in Domain, public read shapes
in Contract, transport DTOs/mapping in API, and capability-specific persistence
and read interfaces in Application. Infrastructure implements those interfaces
using the module-owned DbContext and parameterized EF `Database.SqlQuery<T>`.
Do not expose DbContext or an Infrastructure type through an Application interface.

The scaffold invents no business capability, repository or endpoint. Add actual
capability contracts and their tests when business requirements exist. See the
catalog's direct-service PostgreSQL fixture for an implemented CQS example.
