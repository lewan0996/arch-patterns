using Microsoft.EntityFrameworkCore;

namespace CatalogNamespace.CatalogService.Infrastructure.Persistence;

public sealed class CatalogServiceDbContext(DbContextOptions<CatalogServiceDbContext> options) : DbContext(options)
{
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.HasDefaultSchema("CatalogService");
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(CatalogServiceDbContext).Assembly);
    }
}
