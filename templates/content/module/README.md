# CatalogService: named module

This is a five-project anemic/direct-service PostgreSQL module, hosted by a
separate modular API host. Its API is a library exposing `AddCatalogServiceModule`
and `MapCatalogServiceEndpoints`; it does not start a process or invent business
endpoints. Initial and later modules use this same chain. Application owns
capability interfaces and persistence/read contracts; Infrastructure implements
them. Domain is data-only, Contract holds public query responses, and API owns
transport DTOs and mapping. Keep dependencies inward and reuse acyclic.

The caller validates unique PascalCase names, the explicit host namespace prefix,
supported profile, intended solution, modular layout and nonexistent output
before generation, including empty folders and dangling symlinks. Adding a module
to a flat service requires explicit conversion first. No conversion is performed.
Never use --force. Inspect and report partial output on failure.

## Deliberate host integration

Generation performs no discovery, post-actions, restore, migration or edits to
existing hosts/configuration/architecture records. From the intended solution
root, set the actual solution and host boundary deliberately (Commerce is an
example), then use ordinary tooling:

```bash
intended_solution=Commerce.slnx
host_boundary=src/Commerce
dotnet sln "$intended_solution" add "$host_boundary"/Modules/CatalogService/CatalogNamespace.CatalogService.*/*.csproj "$host_boundary"/Modules/CatalogService/tests/*/*.csproj
dotnet add "$host_boundary/CatalogNamespace.API/CatalogNamespace.API.csproj" reference "$host_boundary/Modules/CatalogService/CatalogNamespace.CatalogService.API/CatalogNamespace.CatalogService.API.csproj"
```

In the selected host's `Program.cs`, add `using CatalogNamespace.CatalogService.API;`,
call `builder.Services.AddCatalogServiceModule(builder.Configuration);` before
`builder.Build()`, and call `app.MapCatalogServiceEndpoints();` before
`app.RunAsync()`. Add actual capability registrations/adapters in the module's
registration hook and HTTP endpoints/DTO mappings in its mapping hook. The host
owns shared middleware and operations.

With absent, nested or ambiguous solutions, stop inferred discovery and select
the exact intended .slnx/.sln, or explicitly create a solution before adding
projects. No automatic integration is attempted. After successful integration,
maintain the root selection record manually; never record partial work as complete.
Update host test configuration for all registered module dependencies and adapt
host-wide readiness assertions. Domain-unit tests remain empty until real domain
behavior exists; module integration/architecture checks are already meaningful.

## Module-owned PostgreSQL

`CatalogServiceDbContext` owns schema CatalogService, discovers only this
Infrastructure assembly's mappings and owns its migration history.
`Modules__CatalogService__Database__ConnectionString` is required externally
injected configuration with host, database, username and password. Invalid/missing
configuration refuses startup without exposing values. Sensitive EF logging is
disabled. The uniquely named CatalogService-database health check contributes to
host readiness; process liveness stays independent.

The digest-pinned Compose dependency is `CatalogService-database`, with database
and username CatalogService and its own persistent named volume. Supply
`CatalogService_POSTGRES_PASSWORD` externally. Deliberately merge this module's
dependency with the solution Dev Container toolchain; repeat for later modules:

```bash
docker compose -f .devcontainer/compose.yaml -f src/Commerce/Modules/CatalogService/compose.postgresql.yaml up -d --wait
```

Inside the toolchain use the connection shape
`Host=CatalogService-database;Database=CatalogService;Username=CatalogService;Password=<injected>;Timeout=5`.
Never put secret values in source/images/logs. No workstation port is generated.
Use production TLS and a restricted runtime DML identity. Configuration changes
require host restart/replacement. Migrations are explicit operational work using
separate production DDL authority, never API startup work.

After adding real entities/mappings, from this module directory with its scoped
connection string configured:

```bash
dotnet tool restore
dotnet ef migrations add Initial --project CatalogNamespace.CatalogService.Infrastructure --context CatalogServiceDbContext --output-dir Persistence/Migrations/PostgreSql
dotnet ef migrations script --idempotent --project CatalogNamespace.CatalogService.Infrastructure --context CatalogServiceDbContext --output migrations.sql
dotnet ef database update --project CatalogNamespace.CatalogService.Infrastructure --context CatalogServiceDbContext
```

Default reads use parameterized `Database.SqlQuery<T>($"...")` with separate
Contract response shapes. Include owner/resource/tenant predicates explicitly;
global query filters do not protect unmapped raw SQL. EF LINQ projections are a
documented alternative. Never expose a context across module boundaries. Module
deployment shares a host, while data and transaction ownership stay independent.
Authorization, CQRS and durable facts require their later capability registrations;
this module makes no corresponding support claim.

From the solution root, restore/build explicitly and run this owner's checks:

```bash
dotnet restore "$intended_solution"
dotnet build "$intended_solution" --no-restore --warnaserror
dotnet test "$host_boundary/Modules/CatalogService/tests/CatalogNamespace.CatalogService.IntegrationTests" --no-build
dotnet test "$host_boundary/Modules/CatalogService/tests/CatalogNamespace.CatalogService.ArchitectureTests" --no-build
```

See the catalog modular-monolith guide for the actual two-module fixture,
creation safety checks, evidence and support limits.
