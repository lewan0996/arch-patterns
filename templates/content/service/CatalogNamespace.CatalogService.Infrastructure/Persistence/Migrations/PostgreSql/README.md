# Owned PostgreSQL migrations

Add actual entities and IEntityTypeConfiguration mappings in this Infrastructure
assembly before creating the first migration. No sample table/empty migration is
shipped. From the boundary directory, restore the local dotnet-ef tool explicitly
and inject Database__ConnectionString externally, then:

```bash
dotnet tool restore
dotnet ef migrations add Initial --project CatalogNamespace.CatalogService.Infrastructure --output-dir Persistence/Migrations/PostgreSql --context CatalogServiceDbContext
dotnet ef migrations script --idempotent --project CatalogNamespace.CatalogService.Infrastructure --context CatalogServiceDbContext --output migrations.sql
dotnet ef database update --project CatalogNamespace.CatalogService.Infrastructure --context CatalogServiceDbContext
```

Review/test the migration and SQL before applying them. Production migration is
an explicit operational job using a separate DDL identity, not API replica startup.
Runtime credentials should have only the module's required DML permissions.
Other providers require separate migration sets and are not supported here yet.
