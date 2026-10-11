# Deriving pending EF model changes

`architecture.json` need not store a migration-generation-pending flag. EF Core provides `dotnet ef migrations has-pending-model-changes` to detect model changes since the last migration; the feature was introduced in EF Core 8. [Microsoft migration management](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/managing#checking-for-pending-model-changes).

In EF Core 10, the check compares the configured migration snapshot with the current design-time relational model, rather than querying the deployed database. It does not establish whether migrations have been applied or account for hand-written SQL outside the EF model. [EF 10 comparison](https://github.com/dotnet/efcore/blob/v10.0.0/src/EFCore.Relational/Migrations/Internal/Migrator.cs#L705-L708), [migration management](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/managing).

Run the check for each relevant context with the intended provider/model configuration. Select the target project, startup project and context explicitly when needed. The tooling must successfully create a design-time context; application initialization can impose additional requirements. [CLI options](https://learn.microsoft.com/en-us/ef/core/cli/dotnet#common-options), [design-time context creation](https://learn.microsoft.com/en-us/ef/core/cli/dbcontext-creation).

Distinguish detected pending changes from a failed check. The operation reports an error when changes are detected, but the EF executable also returns a nonzero exit for unrelated exceptions. A build, context-creation or configuration failure establishes neither pending nor clean status. [EF 10 operation](https://github.com/dotnet/efcore/blob/v10.0.0/src/EFCore.Design/Design/Internal/MigrationsOperations.cs#L240-L250), [EF 10 error handling](https://github.com/dotnet/efcore/blob/v10.0.0/src/ef/Program.cs#L20-L39).

This is documentation/source research for the architecture-selection-record decision. No generated application was exercised locally; the .NET CLI is not installed in this checkout's environment.
