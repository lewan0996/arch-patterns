using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

namespace CatalogNamespace.CatalogService.Infrastructure.Persistence;

// Tooling stays in Infrastructure and never starts the API or migrates on startup.
public sealed class CatalogServiceDbContextFactory : IDesignTimeDbContextFactory<CatalogServiceDbContext>
{
    public CatalogServiceDbContext CreateDbContext(string[] args)
    {
        var settings = new DatabaseOptions
        {
            ConnectionString = Environment.GetEnvironmentVariable("Modules__CatalogService__Database__ConnectionString") ?? ""
        };
        if (!settings.IsValid())
            throw new InvalidOperationException("Supply Modules__CatalogService__Database__ConnectionString with host, database, username and password externally.");
        var options = new DbContextOptionsBuilder<CatalogServiceDbContext>();
        settings.Configure(options);
        return new CatalogServiceDbContext(options.Options);
    }
}
