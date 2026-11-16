# ArchPatterns.Templates 0.2.0

One native package currently provides:

- `arch-solution --composition microservices`: host-free solution and pinned Dev Container.
- `arch-service --layout single --domainModel anemic --applicationFlow direct-service --database postgresql`:
  five-project flat service, operational baseline, PostgreSQL context/mapping hooks,
  separate boundary-owned tests, portable container and explicit migration tooling.
  Select `--domainModel rich` independently for aggregate ownership and separate reads.

Install this local package in a disposable CLI home inside a Dev Container:

```bash
dotnet new install ./ArchPatterns.Templates.0.2.0.nupkg
dotnet new list arch-
dotnet new arch-service --help
```

Both commands require explicit PascalCase names, root namespaces and distinct
nonexistent output destinations. Follow the catalog caller preflight; never use
`--force`. Generation has no automatic solution discovery, restore or scripts;
service users explicitly add new projects to their intended solution.

Full instructions: [solution](https://github.com/lewan0996/arch-patterns/blob/main/docs/catalog/microservices-solution.md),
[flat service](https://github.com/lewan0996/arch-patterns/blob/main/docs/catalog/flat-service.md),
[PostgreSQL direct services](https://github.com/lewan0996/arch-patterns/blob/main/docs/catalog/direct-service-postgresql.md),
[rich/direct-service variation](https://github.com/lewan0996/arch-patterns/blob/main/docs/catalog/rich-direct-service.md).

Modular hosts/modules, client-facing components, security, dispatch, messaging,
creation skills and complete system examples remain planned. Installed-package,
Linux OCI and real PostgreSQL fixture evidence is bounded by the catalog review;
this local package is not the complete certified catalog release.
