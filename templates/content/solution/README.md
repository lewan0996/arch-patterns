# CatalogSystem

Composition: **microservices**. Root namespace prefix: **CatalogNamespace**.

This is a host-free solution scaffold from ArchPatterns.Templates 0.2.0. Each
future service owns its deployment and data; no system-wide host is created.
Domain shape and application flow are independent selections in each module.
There is no application, database, broker or identity provider to run yet.

## Dev Container toolchain

Open this folder using a Dev Containers client on a workstation with Docker
Engine and Compose v2. `.devcontainer/compose.yaml` supplies the pinned .NET SDK
10.0.401 toolchain, with this folder mounted at `/workspace`. Run and debug future
applications inside this container. The container runs as root for development;
it is not a production image. No host SDK or global template installation is
required. Install any later template package **inside this Dev Container**.

The generated service supplies a PostgreSQL Compose dependency; its README
explains the deliberate merge with this toolchain. Add only explicitly selected, pinned dependency services to this
Compose project and use their Compose service names as DNS names from the
toolchain. `localhost` inside the toolchain refers to that container, not to a
database container or the workstation. Dependencies do not belong in the
toolchain image. No Docker socket is mounted; operate Compose from the workstation
or Dev Containers client. There are no dependency services to start in this
increment.

External configuration belongs to its owning process. Later services use typed,
startup-validated inputs such as `Database__ConnectionString`; addresses and secret
values come from the environment or externally mounted secret files. Keep local
secret files outside source control, never embed credentials in images, and
commit only sanitized configuration examples. The `.gitignore` excludes local
`.env` variants. Supply values separately to each consuming Compose service; a
Compose interpolation `.env` file does not automatically inject its values into
containers. Restart or replace the affected process after configuration changes.

## Verify and extend

Generation runs no restore or scripts. Run these explicitly inside the toolchain:

```bash
dotnet --version
dotnet sln CatalogSystem.slnx list
dotnet restore CatalogSystem.slnx
dotnet build CatalogSystem.slnx --no-restore
```

The empty solution has no projects to restore or compile and may emit a warning.
This proves scaffold validity only. It supplies no runtime or application-test
evidence. There are no project references, module hooks or configuration inputs
to wire at this stage.

This package includes a flat anemic/direct-service PostgreSQL service. Before
invoking it, follow the catalog's flat-service preflight for names, supported
selections, intended solution and a fresh destination. Then from this root:

```bash
dotnet new arch-service --name Orders --rootNamespace CatalogNamespace --layout single --domainModel anemic --applicationFlow direct-service --database postgresql --output src/Orders
dotnet sln CatalogSystem.slnx add src/Orders/CatalogNamespace.Orders.*/*.csproj src/Orders/tests/*/*.csproj
dotnet restore CatalogSystem.slnx
dotnet build CatalogSystem.slnx --no-restore
```

Use unique PascalCase boundary names and the explicit CatalogNamespace prefix.
Never use --force. Before each invocation reject occupied output (including an
empty directory or dangling symlink) and unsupported selections; inspect partial
work after failures and handle it manually. The service README explains its
Compose dependency, external credentials, migrations, runtime and tests.
`arch-service` performs no automatic solution discovery or post-actions: the
explicit `sln add` above is deliberate manual integration. Generation edits only
fresh output. Existing hosts, configuration and architecture-selection records
are untouched. Modular services/modules, BFFs, audience APIs and creation skills
remain planned. `architecture.json` records current identities and explicit
selections. Native service/module additions do not edit it: update it manually
only after successful integration and checks. Preserve IDs when renaming or
moving boundaries. Validate with the bundled `.architecture/validate.py` and its
pinned virtual-environment requirements. See the catalog's architecture-record
page for the full shape, supported combinations, commands and reconciliation
rules. Source owns actual dependency versions; Git owns history.

The catalog selection route and current support limits are at
https://github.com/lewan0996/arch-patterns/blob/main/docs/catalog/selection.md.
