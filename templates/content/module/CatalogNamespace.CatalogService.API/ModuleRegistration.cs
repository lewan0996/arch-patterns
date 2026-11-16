using CatalogNamespace.CatalogService.Infrastructure;
using Microsoft.AspNetCore.Routing;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace CatalogNamespace.CatalogService.API;

public static class ModuleRegistration
{
    public static IServiceCollection AddCatalogServiceModule(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddCatalogServicePersistence(configuration);
        // Register CatalogService Application capability interfaces and their adapters here.
        return services;
    }

    public static IEndpointRouteBuilder MapCatalogServiceEndpoints(this IEndpointRouteBuilder endpoints)
    {
        // Map CatalogService HTTP endpoints and transport DTOs here; no business endpoint is invented.
        return endpoints;
    }
}
