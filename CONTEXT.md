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

**Contract layer**:
A module's public query requests, data transfer shapes and, where applicable, query interfaces used by its host or other modules. Commands and internal behavior are excluded.

**Anemic domain model**:
Data-only domain objects whose business behavior lives in application services.

**CQRS**:
An application-flow approach with separate command and query models.

**CQS**:
Command-query separation: methods that change state are separate from methods that retrieve data. It does not require separate command and query models.

**Read model**:
The data shape used to answer queries. It may be separate from the write model without being a domain model.

**Supported substitution**:
An explicitly documented and verified technology replacement for a selected architecture option.

**Recommended combination**:
A selection of compatible options across applicable ingredients, suggested for a stated project context.

**Client-facing API**:
The single public API a client uses to access a system without selecting its internal services. A browser or mobile BFF and a machine-facing audience API are variants.

**Backend for frontend (BFF)**:
A client-specific API for a user-facing application that shapes its API for that client's needs. A browser BFF also owns the browser session.

**API gateway**:
An optional routing entry point for a group of services. It can sit behind client-facing APIs to share routing among them; its authentication responsibilities are selected separately.

**Template**:
A reusable starting point that creates a new solution or a new service or module in a new folder.
