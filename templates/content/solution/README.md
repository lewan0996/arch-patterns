# CatalogSystem

Composition: **microservices**. Root namespace prefix: **CatalogNamespace**.

This is a host-free solution scaffold from ArchPatterns.Templates 0.1.0. Each
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

Compose will also supply runtime dependencies when the relevant capability is
implemented. Add only explicitly selected, pinned dependency services to this
Compose project and use their Compose service names as DNS names from the
toolchain. `localhost` inside the toolchain refers to that container, not to a
database container or the workstation. Dependencies do not belong in the
toolchain image. No Docker socket is mounted; operate Compose from the workstation
or Dev Containers client. There are no dependency services to start in this
increment.

External configuration belongs to its owning process. Later services use typed,
startup-validated inputs such as `ConnectionStrings__Orders`; addresses and secret
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

Service generation is the next capability:
https://github.com/lewan0996/arch-patterns/issues/57. This package increment does
not yet include `arch-service`, `arch-module`, `arch-bff` or `arch-audience-api`.
Follow their exact release-specific creation/integration/check instructions when
available. Use `CatalogNamespace` as the prefix and unique PascalCase boundary
names. Before **each** native invocation, validate supported selections and check
that its explicitly resolved output destination does not exist, including an
empty directory or dangling symlink. Never use `--force`. Inspect failed partial
output and handle it manually; do not assume that failure undid writes.

The intended solution is `CatalogSystem.slnx`. When adding future components,
confirm that native solution discovery selects this exact, unambiguous file.
If discovery is absent, ambiguous or unintended, follow the component's manual
instructions and add its generated projects explicitly with
`dotnet sln CatalogSystem.slnx add <generated-project-path>`. Native generation may
only edit existing solution membership for newly generated projects; host,
configuration and architecture-selection-record integration are separate steps.
This increment edits no existing solution and creates no architecture.json.

The catalog selection route and current support limits are at
https://github.com/lewan0996/arch-patterns/blob/main/docs/catalog/selection.md.
