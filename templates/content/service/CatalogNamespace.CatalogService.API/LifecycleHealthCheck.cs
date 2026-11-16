using Microsoft.Extensions.Diagnostics.HealthChecks;

namespace CatalogNamespace.CatalogService.API;

public sealed class LifecycleHealthCheck(IHostApplicationLifetime lifetime) : IHealthCheck
{
    public Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context, CancellationToken cancellationToken = default) =>
        Task.FromResult(lifetime.ApplicationStarted.IsCancellationRequested &&
                        !lifetime.ApplicationStopping.IsCancellationRequested
            ? HealthCheckResult.Healthy()
            : HealthCheckResult.Unhealthy("Host is starting or stopping."));
}
