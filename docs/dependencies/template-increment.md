# Template package 0.1.0 dependency and evidence review

Historical 0.1.0 review; see the [0.2.0 service/graph review](service-increment.md)
for current executable support.

Reviewed 2026-11-16 for [#56](https://github.com/lewan0996/arch-patterns/issues/56).
Scope: native package installation and a host-free microservices solution on
Linux. This is an incremental local package, not the completed catalog release.

## Selected graph

| Component | Pin / ownership | Licensing, terms and maintenance |
| --- | --- | --- |
| .NET SDK / MSBuild / native template engine | `10.0.401`, root and generated `global.json`, roll-forward disabled | .NET source is principally MIT with component-specific third-party notices. Use the distribution's notices; a top-level license does not relicense all bundled components. The selected major is .NET 10 LTS; patches require review and renewed verification. |
| SDK runtime / ASP.NET Core shared runtime | `10.0.12`, supplied by this SDK | No application is generated here. These installed shared frameworks are toolchain contents, not evidence of an ASP.NET application or EF/provider compatibility. |
| Dev Container SDK image | `mcr.microsoft.com/dotnet/sdk:10.0.401@sha256:e70cdb7f80b0348f5cb85f19a8f670fca061f033d57eed12fa003d58b0e06317` | Official Microsoft multi-platform manifest pinned by digest. It includes OS and SDK components under their respective licenses/notices; it is not covered solely by the .NET MIT license. No commercial library or managed service is introduced. Retain notices when redistributing images; revisit OS and SDK servicing when updating. |
| Template-package NuGet dependencies | None, direct or transitive | The SDK's built-in pack target creates a content-only `Template` package. No authoring-task NuGet dependency, test-framework NuGet dependency or runtime package is needed. Generated solution has no projects or NuGet graph yet. |
| Python test harness | Python 3 standard library; verification only | PSF license and bundled-component notices; no pip dependencies or install step. CI uses the Ubuntu runner's Python. This is not a generated application dependency. |
| Docker / Compose / Dev Containers client | External workstation/CI prerequisites | No workstation installation is performed. Docker Engine, Compose and editor/client distributions have their own licenses and product terms; Docker Desktop is optional and its subscription terms are separate. The scaffold needs Engine and Compose, not Desktop specifically. |
| GitHub Actions | Checkout, setup-dotnet and upload-artifact pinned to commit SHAs in [workflow](../../.github/workflows/templates.yml) | These actions use MIT licenses; hosted runner/artifact usage remains governed by GitHub service terms. Pins apply to these CI integrations, not to application support. |

SDK and image versions deliberately match. Keep both `global.json` files, the
image digest, fixtures and this review aligned on updates. No EF, provider,
Wolverine, broker or identity-provider packages/images are selected by this
increment. Their coherent graphs and actual runtime evidence belong to later
capabilities and the [final release review](https://github.com/lewan0996/arch-patterns/issues/87).

Primary references: [.NET license inventory](https://github.com/dotnet/core/blob/main/license-information.md),
[container license/notice locations](https://github.com/dotnet/dotnet-docker/blob/main/documentation/image-artifact-details.md),
[.NET support policy](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core),
[Python license](https://docs.python.org/3/license.html),
[Docker licensing](https://docs.docker.com/subscription/),
[checkout license](https://github.com/actions/checkout/blob/11d5960a326750d5838078e36cf38b85af677262/LICENSE),
[setup-dotnet license](https://github.com/actions/setup-dotnet/blob/67a3573c9a986a3f9c594539f4ab511d57bb3ce9/LICENSE),
[upload-artifact license](https://github.com/actions/upload-artifact/blob/ea165f8d65b6e75b540449e92b4886f43607fa02/LICENSE).

## Verification boundary

`tests/test_templates.py` packs and installs the actual `.nupkg` in a disposable
`DOTNET_CLI_HOME`, exercises list/help and input failures, generates host-free
workspaces with two namespace/name choices, and explicitly restores/builds the
empty solution. It executes the published Bash preflight for valid inputs,
invalid identity/namespace, empty/nonempty destinations and dangling symlinks.
Fixtures compare existing files around absent, ancestor, nested and ambiguous
solutions. No tests install templates into the user's CLI home.

Missing native required inputs generate no files but can leave an empty directory
on SDK 10.0.401. This is documented partial output, requiring manual handling;
native templates are not claimed to enforce the caller's fresh-folder check.

With `ARCH_TEST_CONTAINERS=1`, the same suite starts the generated Compose
toolchain, checks its exact SDK and restores/builds the generated solution inside
it, then removes its own Compose services/network/volumes. CI enables that check.
Dev Containers editor attachment/debugging is not exercised by the Compose smoke
check. Other OS/architectures and agent-client creation workflows are unverified.
An empty-solution build is not application runtime evidence. There is no verified
service/module generation or production runtime combination yet.

Reproduce from the checkout using Python 3, SDK 10.0.401 and, for the opt-in check,
a working Docker/Compose installation:

```bash
ARCH_TEST_CONTAINERS=1 python3 -m unittest discover -s tests -v
dotnet pack templates/ArchPatterns.Templates.csproj --configuration Release --output artifacts/packages
```

The CI path packages this same source and uploads the `.nupkg` as an artifact.
No NuGet publishing, global tool installation, restore/script post-action or
paid agent CI is part of this increment. The test harness is verification code;
all user generation commands remain ordinary `dotnet new` calls.
