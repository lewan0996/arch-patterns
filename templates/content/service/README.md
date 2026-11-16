# CatalogService: single-module service

The five projects own API/host startup, Application use cases and interfaces,
Domain behavior, Infrastructure adapters, and public Contract messages respectively.
API composes Application and Infrastructure. No business endpoints are generated.

Generation has no solution discovery, restore or script post-actions. Existing
solutions, hosts, configuration and selection records are untouched. Choose the
intended solution explicitly, check project/name collisions, then add all eight
projects (including the three separate test projects) with ordinary tooling:

```bash
# From the intended solution directory; replace the solution filename deliberately.
dotnet sln Commerce.slnx add src/CatalogService/CatalogNamespace.CatalogService.*/*.csproj src/CatalogService/tests/*/*.csproj
dotnet restore Commerce.slnx
dotnet build Commerce.slnx --no-restore
dotnet test src/CatalogService/tests/CatalogNamespace.CatalogService.IntegrationTests
dotnet test src/CatalogService/tests/CatalogNamespace.CatalogService.ArchitectureTests
Service__Deployment=local dotnet run --project src/CatalogService/CatalogNamespace.CatalogService.API
```

Paths assume this boundary is `src/CatalogService`; adapt only to its actual
fresh destination. With missing or ambiguous solutions stop inferred discovery:
select the exact intended `.slnx`/`.sln` yourself, or explicitly create a solution
before adding projects. Inspect partial output after failures; do not force or
silently delete it. The Domain.UnitTests project has no invented behavior/tests.

Set the required Database__ConnectionString externally before running (see below).
Run/debug within the solution Dev Container. Runtime settings use external
configuration: `Service__Deployment` labels the structured startup log and is required, `Service__RequestTimeoutSeconds`
is 1–300 (default 30), `Service__ShutdownTimeoutSeconds` is 1–300 (default 15).
`ASPNETCORE_URLS` or `ASPNETCORE_HTTP_PORTS` selects listening addresses. Changes
require replacement/restart. Do not put secrets into source, image layers or logs;
inject them using the runtime's environment/secret mount integration. The PostgreSQL adapter consumes externally injected credentials; never invent a shared API key.

`/health/live` checks only process responsiveness; `/health/ready` checks started,
not stopping and owned database connectivity. The host emits JSON `ILogger` logs, stops accepting traffic on
SIGTERM and cancels in-flight work within the explicit request/shutdown budgets.
Pass the endpoint CancellationToken into all downstream work. Platform routing
must honor readiness and allow a termination grace period exceeding the host
shutdown budget. Probes expose no configuration or credentials.

```bash
# Standalone OCI smoke run from this boundary, separate from the Dev Container profile.
# Supply POSTGRES_PASSWORD and Database__ConnectionString externally first.
# Use Host=database;Database=CatalogService;Username=CatalogService;Password=<injected>;Timeout=5
docker compose --project-name catalogservice --file compose.postgresql.yaml up -d --wait
docker build -t catalogservice .
docker run --rm --network catalogservice_default -p 8080:8080 \
  -e Service__Deployment=local -e Database__ConnectionString catalogservice
# Send SIGTERM using docker stop --time 20 <container>.
```

The image runs as a non-root user on a provider-neutral container platform.
Migrations, deployment provisioning, availability profiles and workload identity
integration remain explicit operational concerns, not automatic startup work.
Only the single layout is implemented. See the catalog flat-service guide for
preflight, exact support and verification limits before generation.

## Selected persistence profile

This boundary explicitly selects CatalogDomainModel domain, direct-service application flow
and PostgreSQL. The Application README describes the selected write-model rules.
Capability-oriented Application interfaces expose separate command and query
methods. Keep reuse acyclic.
Application owns capability-specific persistence/read contracts; Infrastructure
implements them. Public read shapes belong to Contract, HTTP DTOs remain in API.
No sample business service or endpoint is installed by generation.

`CatalogServiceDbContext` lives in Infrastructure, owns schema `CatalogService`,
and discovers that assembly's EF mappings. Add real entities/mappings before the
first migration. Use parameterized `Database.SqlQuery<T>($"...")` for SQL-first
reads mapped to separate response shapes. Never pre-interpolate SQL into a string
or assume global EF query filters protect unmapped raw SQL; explicitly include
resource/tenant predicates. EF LINQ projections with `AsNoTracking().Select(...)`
are a documented alternative, not a change to application flow.

Inject `Database__ConnectionString` with host, database, username and password.
Missing/malformed credentials refuse startup without including their values in
diagnostics. Sensitive EF data logging is disabled. `/health/ready` also checks
database connectivity (three-second health budget); database failure leaves
`/health/live` healthy. No schema changes occur on API startup. Readiness does not
replace schema rollout checks. Use TLS with server verification in production.

`compose.postgresql.yaml` supplies a digest-pinned database with an external
`POSTGRES_PASSWORD`, no published port and a persistent named volume. From the
solution directory, deliberately merge it with the Dev Container toolchain:

```bash
# Supply POSTGRES_PASSWORD securely in the invoking environment first.
docker compose -f .devcontainer/compose.yaml -f src/CatalogService/compose.postgresql.yaml up -d --wait
# In the attached Dev Container, set Database__ConnectionString externally to:
# Host=database;Database=CatalogService;Username=CatalogService;Password=<injected>;Timeout=5
cd src/CatalogService
dotnet tool restore
# After adding the actual model/mappings:
dotnet ef migrations add Initial --project CatalogNamespace.CatalogService.Infrastructure --output-dir Persistence/Migrations/PostgreSql --context CatalogServiceDbContext
dotnet ef migrations script --idempotent --project CatalogNamespace.CatalogService.Infrastructure --context CatalogServiceDbContext --output migrations.sql
dotnet ef database update --project CatalogNamespace.CatalogService.Infrastructure --context CatalogServiceDbContext
Service__Deployment=local dotnet run --project CatalogNamespace.CatalogService.API
```

Review/test migrations and run them as explicit operational work; use a separate
DDL identity in production and limit the API's runtime DML permissions. Design-time
creation also requires the external connection string. The local tool manifest
pins dotnet-ef and does not install globally or restore at generation time. See
`Persistence/Migrations/PostgreSql/README.md` in Infrastructure. Other providers,
Dapper, authorization, CQRS dispatch and reliable messaging remain later work.
The catalog-owned reservation fixture demonstrates committed writes, SQL-first
reads, rejection and cancellation against real PostgreSQL; it is not packaged.
