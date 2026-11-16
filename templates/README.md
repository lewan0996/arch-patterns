# ArchPatterns.Templates 0.1.0

Native .NET architecture catalog templates. This increment provides only
`arch-solution --composition microservices`: a host-free solution scaffold with
a pinned .NET SDK 10.0.401 Dev Container toolchain.

Install the local `.nupkg` inside a Dev Container using a disposable
`DOTNET_CLI_HOME`. No global workstation installation is required. Run
`dotnet new list arch-` and `dotnet new arch-solution --help` after installation.

Before generation, validate a unique PascalCase `--name`, a root namespace with
PascalCase segments, the explicit composition, and an explicit `--output` whose
destination does not exist, even as an empty directory or dangling symlink.
Never use `--force`. Native templates do not enforce all caller prerequisites.

Follow the [complete installation, preflight and check instructions](https://github.com/lewan0996/arch-patterns/blob/main/docs/catalog/microservices-solution.md).
The generated README supplies manual integration and external configuration
conventions. No restore or scripts run automatically. Service/module generation,
other compositions, creation skills and application runtime evidence remain
planned; later capabilities extend this same package.
