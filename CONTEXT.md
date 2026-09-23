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
A module's public commands, queries, query response shapes and integration events. Handlers and internal application or domain behavior are excluded.

**Anemic domain model**:
Data-only domain objects whose business behavior lives in application services.

**CQRS**:
An application-flow approach with separate command and query models.

**CQS**:
Command-query separation: methods that change state are separate from methods that retrieve data. It does not require separate command and query models.

**Read model**:
The data shape used to answer queries. It may be separate from the write model without being a domain model.

**Data owner**:
A service or module that controls changes to its own data and schema. Other boundaries access that data through published queries or events.

**Transactional module event**:
An in-process fact handled across modules before their shared database transaction commits. A handler failure aborts the transaction.

**Published integration event**:
A fact about a committed change published outside its data owner for eventual processing.

**Permission projection**:
A service-held read representation of access-management assignments used for local authorization checks.

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

**Client credential/session profile**:
The way a caller proves its identity at a client-facing boundary, such as a browser session cookie or an OAuth access token.

**Protected resource**:
The logical API for which an access token is intended, identified by its audience. A protected resource may span multiple services in one trust domain.

**User authority**:
Authority delegated from an authenticated user and propagated to a downstream operation so that the user's permissions can be evaluated.

**Application authority**:
Authority exercised by a service, background job or other workload under its own identity rather than on behalf of a user.

**Permission claim**:
A token claim representing a coarse capability, such as a scope or role. It does not replace authorization based on a specific resource, tenant or business state.

**Identity provider**:
A replaceable OAuth 2.0 and OpenID Connect compatible system that authenticates users and issues tokens; the catalog does not require a particular vendor.

**Access management**:
The application-owned responsibility for mapping external identities and managing system-wide permission assignments. It is distinct from identity-provider authentication and from resource-specific authorization owned by a service or module.

**Token-carried permissions**:
An authorization profile in which a validated access token carries the caller's normalized permissions.

**Application-managed permissions**:
An authorization profile in which an access token identifies the caller while services or modules evaluate system-wide permission assignments supplied by access management.

**External identity**:
The identity-provider-specific pair of issuer and subject that identifies a caller within that provider.

**Internal user ID**:
A stable application-owned identifier to which one or more external identities may be mapped, allowing identity providers to be replaced without changing domain ownership data.

**Role**:
A named collection used to assign permissions. Application authorization checks permissions rather than depending directly on identity-provider roles or groups.

**Shared internal API key**:
A high-entropy secret used by designated internal endpoints as a coarse check that a caller belongs to the trusted system. It represents application authority but does not identify an individual calling service.

**Template**:
A reusable starting point that creates a new solution or a new service or module in a new folder.

**Operational boundary**:
The deployable process that owns runtime health, lifecycle, configuration consumption, resilience policy and telemetry emission. A microservice is one boundary; in a modular monolith the host is the boundary and modules contribute domain-specific signals.

**Local development profile**:
The supported developer runtime in which a Dev Container supplies the toolchain and runs or debugs the application, while Docker Compose supplies its runtime dependencies.

**Container platform**:
A production runtime that schedules and operates OCI containers, including exposed orchestrators such as Kubernetes and managed services that hide the underlying orchestration.

**Secret reference**:
A named configuration input whose value is supplied at runtime from outside the source repository and deployable image.

**Operational baseline**:
The minimum runtime contract required of every generated deployable: structured logging, health probes, graceful shutdown, validated external configuration and secrets, bounded remote calls and a portable container artifact.

**Operational job**:
A finite deployable process for rollout-related work such as a database migration, separate from long-running application replicas.

**Availability profile**:
The selected single-region replication and scaling behavior for a deployable: single-replica, replicated with rolling replacement, or autoscaled and replicated.

**Configuration update profile**:
The way a deployable adopts external configuration changes. Replacement or restart is the default; dynamic reload is optional.

**Credential delivery profile**:
The way a deployable obtains credentials for a downstream resource: a secret injected from outside the image or a platform-issued workload identity. Workload identity is preferred where the platform and resource support it; live secret rotation is optional.
