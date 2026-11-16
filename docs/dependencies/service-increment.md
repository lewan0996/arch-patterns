# Template package 0.2.0 dependency and evidence review

Reviewed 2026-11-16 for [#57](https://github.com/lewan0996/arch-patterns/issues/57)
and [#58](https://github.com/lewan0996/arch-patterns/issues/58), extending the
[0.1.0 toolchain review](template-increment.md). This is a local incremental
package, not the completed certified catalog release or NuGet publication.

## Pins and ownership

| Component | Selected pin / use | Review |
| --- | --- | --- |
| SDK / MSBuild / native templates | .NET SDK 10.0.401, runtime/shared framework 10.0.12 | Existing .NET 10 LTS line; exact SDK with roll-forward disabled. The content-only template package still has no NuGet dependency of its own. |
| SDK image | `mcr.microsoft.com/dotnet/sdk:10.0.401@sha256:e70cdb7f80b0348f5cb85f19a8f670fca061f033d57eed12fa003d58b0e06317` | Shared Dev Container and OCI build toolchain; platform manifest pinned. |
| ASP.NET runtime image | `mcr.microsoft.com/dotnet/aspnet:10.0.12@sha256:222759b391a1aaf241166672c8f99b2d4ada452e7b5319f3c6e8f265a37b5ad4` | Portable non-root final image; runtime matches SDK. Includes OS/runtime components and their bundled notices, not just the .NET license. |
| EF Core / Relational / Design / dotnet-ef | 10.0.12 | Writes, SQL-first reads, Infrastructure-owned design-time factory and explicit migrations. Relational is pinned explicitly so Design and runtime provider graphs agree. Design is private to Infrastructure; dotnet-ef is a local restored tool, never a global installation. |
| PostgreSQL EF provider / driver | Npgsql.EntityFrameworkCore.PostgreSQL 10.0.2 / resolved Npgsql 10.0.3 | PostgreSQL licenses; actual EF 10.0.12 integration and migration checks pass. This does not certify SQL Server, other providers or messaging. |
| PostgreSQL dependency image | `postgres:18@sha256:2ea8630df176ad090ec92136dee850397c5af8781e4bcf2e4162593691c61bbc` | Exercised version 18.7 (Debian); preserve database and distribution notices. Credentials external, no generated workstation port, persistent named volume. |
| Test graph | Microsoft.NET.Test.Sdk 17.14.1, xunit 2.9.3, xunit.runner.visualstudio 3.1.5, Microsoft.AspNetCore.Mvc.Testing 10.0.12 | Test-only dependencies, separate from production publish. Microsoft packages declare MIT; xUnit packages declare Apache-2.0 with component-specific notices. |
| Python / Docker / Compose / GitHub Actions | Existing standard-library harness, external local prerequisites, pinned CI actions | Same terms and ownership as the prior review. No paid core dependency, broker, identity provider or managed-service subscription is introduced. |

The pins above are selected for this exercised increment, not a claim to track
the latest releases indefinitely. Recheck servicing, provider compatibility,
licenses and evidence on updates. Keep both global.json files, SDK/runtime images,
EF packages/tool, fixtures and this review aligned. Npgsql and PostgreSQL have
independent release/support lifecycles. The current resolved API package graph
reported no known vulnerable packages from configured NuGet sources using
`dotnet list <API-project> package --vulnerable --include-transitive` on the review
date; that observation is neither a future guarantee nor a complete image audit.

## Direct and transitive NuGet inventory

Observed from restored `project.assets.json` files for the generated Infrastructure,
API and test projects plus the local tool, with license metadata read from the
actual packages' `.nuspec` files. Reproduce by generating the documented profile,
restoring its eight projects/local tool and inspecting each project graph with
`dotnet list <project> package --include-transitive`. Repeated names at different
versions belong to separate tooling/test graphs. The tables record declared
package licenses; retain embedded licenses/NOTICE/third-party notices when
redistributing. OS images and SDK/tool bundles have additional component notices.

The legacy xunit.abstractions package uses a `licenseUrl` rather than an SPDX
expression; its linked [upstream license](https://raw.githubusercontent.com/xunit/xunit/master/license.txt)
specifies Apache-2.0 and notes imported MIT components. Npgsql licenses are
available from the [driver](https://github.com/npgsql/npgsql/blob/main/LICENSE)
and [EF provider](https://github.com/npgsql/efcore.pg/blob/main/LICENSE).

| Package | Version | Declared license |
| --- | --- | --- |
| dotnet-ef | 10.0.12 | MIT |
| Humanizer.Core | 2.14.1 | MIT |
| Microsoft.AspNetCore.Mvc.Testing | 10.0.12 | MIT |
| Microsoft.AspNetCore.TestHost | 10.0.12 | MIT |
| Microsoft.Build.Framework | 18.0.2 | MIT |
| Microsoft.CodeAnalysis.Analyzers | 3.11.0 | MIT |
| Microsoft.CodeAnalysis.Common | 5.0.0 | MIT |
| Microsoft.CodeAnalysis.CSharp | 5.0.0 | MIT |
| Microsoft.CodeAnalysis.CSharp.Workspaces | 5.0.0 | MIT |
| Microsoft.CodeAnalysis.Workspaces.Common | 5.0.0 | MIT |
| Microsoft.CodeAnalysis.Workspaces.MSBuild | 5.0.0 | MIT |
| Microsoft.CodeCoverage | 17.14.1 | MIT |
| Microsoft.EntityFrameworkCore | 10.0.12 | MIT |
| Microsoft.EntityFrameworkCore.Abstractions | 10.0.12 | MIT |
| Microsoft.EntityFrameworkCore.Analyzers | 10.0.12 | MIT |
| Microsoft.EntityFrameworkCore.Design | 10.0.12 | MIT |
| Microsoft.EntityFrameworkCore.Relational | 10.0.12 | MIT |
| Microsoft.Extensions.Caching.Abstractions | 10.0.12 | MIT |
| Microsoft.Extensions.Caching.Memory | 10.0.12 | MIT |
| Microsoft.Extensions.Configuration | 10.0.12 | MIT |
| Microsoft.Extensions.Configuration.Abstractions | 10.0.12 | MIT |
| Microsoft.Extensions.Configuration.Binder | 10.0.12 | MIT |
| Microsoft.Extensions.Configuration.CommandLine | 10.0.12 | MIT |
| Microsoft.Extensions.Configuration.EnvironmentVariables | 10.0.12 | MIT |
| Microsoft.Extensions.Configuration.FileExtensions | 10.0.12 | MIT |
| Microsoft.Extensions.Configuration.Json | 10.0.12 | MIT |
| Microsoft.Extensions.Configuration.UserSecrets | 10.0.12 | MIT |
| Microsoft.Extensions.DependencyInjection | 10.0.12 | MIT |
| Microsoft.Extensions.DependencyInjection.Abstractions | 10.0.12 | MIT |
| Microsoft.Extensions.DependencyModel | 10.0.12 | MIT |
| Microsoft.Extensions.Diagnostics | 10.0.12 | MIT |
| Microsoft.Extensions.Diagnostics.Abstractions | 10.0.12 | MIT |
| Microsoft.Extensions.FileProviders.Abstractions | 10.0.12 | MIT |
| Microsoft.Extensions.FileProviders.Physical | 10.0.12 | MIT |
| Microsoft.Extensions.FileSystemGlobbing | 10.0.12 | MIT |
| Microsoft.Extensions.Hosting | 10.0.12 | MIT |
| Microsoft.Extensions.Hosting.Abstractions | 10.0.12 | MIT |
| Microsoft.Extensions.Logging | 10.0.12 | MIT |
| Microsoft.Extensions.Logging.Abstractions | 10.0.12 | MIT |
| Microsoft.Extensions.Logging.Configuration | 10.0.12 | MIT |
| Microsoft.Extensions.Logging.Console | 10.0.12 | MIT |
| Microsoft.Extensions.Logging.Debug | 10.0.12 | MIT |
| Microsoft.Extensions.Logging.EventLog | 10.0.12 | MIT |
| Microsoft.Extensions.Logging.EventSource | 10.0.12 | MIT |
| Microsoft.Extensions.Options | 10.0.12 | MIT |
| Microsoft.Extensions.Options.ConfigurationExtensions | 10.0.12 | MIT |
| Microsoft.Extensions.Primitives | 10.0.12 | MIT |
| Microsoft.NET.Test.Sdk | 17.14.1 | MIT |
| Microsoft.TestPlatform.ObjectModel | 17.14.1 | MIT |
| Microsoft.TestPlatform.TestHost | 17.14.1 | MIT |
| Microsoft.VisualStudio.SolutionPersistence | 1.0.52 | MIT |
| Mono.TextTemplating | 3.0.0 | MIT |
| Newtonsoft.Json | 13.0.4 | MIT |
| Newtonsoft.Json | 13.0.3 | MIT |
| Npgsql | 10.0.3 | PostgreSQL |
| Npgsql.EntityFrameworkCore.PostgreSQL | 10.0.2 | PostgreSQL |
| System.CodeDom | 6.0.0 | MIT |
| System.Composition | 9.0.0 | MIT |
| System.Composition.AttributedModel | 9.0.0 | MIT |
| System.Composition.Convention | 9.0.0 | MIT |
| System.Composition.Hosting | 9.0.0 | MIT |
| System.Composition.Runtime | 9.0.0 | MIT |
| System.Composition.TypedParts | 9.0.0 | MIT |
| System.Diagnostics.EventLog | 10.0.12 | MIT |
| xunit | 2.9.3 | Apache-2.0 |
| xunit.abstractions | 2.0.3 | Apache-2.0 via legacy licenseUrl |
| xunit.analyzers | 1.18.0 | Apache-2.0 |
| xunit.assert | 2.9.3 | Apache-2.0 |
| xunit.core | 2.9.3 | Apache-2.0 |
| xunit.extensibility.core | 2.9.3 | Apache-2.0 |
| xunit.extensibility.execution | 2.9.3 | Apache-2.0 |
| xunit.runner.visualstudio | 3.1.5 | Apache-2.0 |


## Verification boundary

The installed-package suite runs native generation, explicit intended solution
integration, build with warnings as errors, and generated meaningful host and
architecture checks. It executes published preflight refusal/success cases and
compares pre-existing files around intended, adjacent, nested, absent and
ambiguous solutions. No template has restore, script or solution-discovery
post-actions; the documented solution-add command is deliberate manual work.
Catalog fixtures verify prohibited dependencies, actual request-budget expiry,
SIGTERM cancellation, structured logs, non-root OCI execution and startup refusal.

The PostgreSQL fixture uses the generated Compose file and an ephemeral secret,
adds a catalog-owned capability outside the production template, runs local
migration tooling, and exercises the public Application interface with real
adapters. It checks parameterized SQL, rejection/cancellation, independently
observed committed state, readiness and rollback. A merged Dev Container/Compose
profile also builds and runs the generated API against that database. Test-only
ports use loopback and ephemeral allocation; cleanup removes only fixture resources.

Reproduce all checks (SDK 10.0.401, Python 3, Docker/Compose):

```bash
ARCH_TEST_CONTAINERS=1 python3 -m unittest discover -s tests -v
dotnet pack templates/ArchPatterns.Templates.csproj --configuration Release --output artifacts/packages
```

CI enables the same container gates and packages verified source as an artifact.
No template is installed into the user's CLI home. Real PostgreSQL/OCI evidence
covers the named Linux profile only. Editor attachment/debugging, other
OS/architectures, creation skills, production platforms, SQL Server, security,
CQRS, reliable facts and complete system baselines remain unverified/planned.
An empty Domain-unit scaffold is never counted as behavioral evidence.

Primary references: [EF license](https://github.com/dotnet/efcore/blob/main/LICENSE.txt),
[Microsoft container notices](https://github.com/dotnet/dotnet-docker/blob/main/documentation/image-artifact-details.md),
[.NET support](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core),
[PostgreSQL license](https://www.postgresql.org/about/licence/),
[PostgreSQL version policy](https://www.postgresql.org/support/versioning/),
[xUnit license](https://github.com/xunit/xunit/blob/main/license.txt),
and the preceding review's [CI/tooling references](template-increment.md).
