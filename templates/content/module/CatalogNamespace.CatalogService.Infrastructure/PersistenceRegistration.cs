using CatalogNamespace.CatalogService.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;

namespace CatalogNamespace.CatalogService.Infrastructure;

public static class PersistenceRegistration
{
    public static IServiceCollection AddCatalogServicePersistence(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddOptions<DatabaseOptions>().Bind(configuration.GetSection(DatabaseOptions.Section))
            .Validate(settings => settings.IsValid(), "Modules:CatalogService:Database:ConnectionString requires host, database, username and password.")
            .ValidateOnStart();
        services.AddDbContext<CatalogServiceDbContext>((provider, options) =>
            provider.GetRequiredService<IOptions<DatabaseOptions>>().Value.Configure(options));
        services.AddHealthChecks().AddCheck<DatabaseHealthCheck>("CatalogService-database", tags: ["ready"],
            timeout: TimeSpan.FromSeconds(3));
        return services;
    }
}
