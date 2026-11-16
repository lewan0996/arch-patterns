using Microsoft.Extensions.Diagnostics.HealthChecks;

namespace CatalogNamespace.CatalogService.Infrastructure.Persistence;

public sealed class DatabaseHealthCheck(CatalogServiceDbContext database) : IHealthCheck
{
    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context, CancellationToken cancellationToken = default) =>
        await database.Database.CanConnectAsync(cancellationToken)
            ? HealthCheckResult.Healthy()
            : HealthCheckResult.Unhealthy("Owned database is unavailable.");
}
