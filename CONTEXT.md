# Architecture Catalog

A catalog of architecture choices for .NET projects, intended for reuse across the owner's projects and future sharing.

## Language

**High-level architecture**:
The composition of a system and the relationships between its clients, entry points and services.

**Low-level architecture**:
The internal organization of one microservice or one modular-monolith module.

**Ingredient**:
An architecture decision area with named options, selected at system or service/module scope where applicable.

**Option**:
A named architecture approach within an ingredient. A service or module uses one consistent option per applicable ingredient.

**Application-flow profile**:
The service- or module-wide rules for invoking and coordinating use cases.

**Anemic domain model**:
Data-only domain objects whose business behavior lives in application services.

**CQRS**:
An application-flow approach with separate command and query models.

**Supported substitution**:
An explicitly documented and verified technology replacement for a selected architecture option.

**Recommended combination**:
A selection of compatible options across applicable ingredients, suggested for a stated project context.

**Template**:
A reusable starting point that creates a new solution or a new service or module in a new folder.
