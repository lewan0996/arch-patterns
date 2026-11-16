using System.Net;
using CatalogNamespace.CatalogService.API;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Options;

namespace CatalogNamespace.CatalogService.IntegrationTests;

public sealed class ModuleTests
{
    [Fact]
    public async Task Registered_module_contributes_database_readiness_to_its_host()
    {
        var builder = CreateBuilder();
        builder.Configuration.AddInMemoryCollection(new Dictionary<string, string?>
        {
            ["Modules:CatalogService:Database:ConnectionString"] =
                "Host=127.0.0.1;Port=1;Database=fixture;Username=fixture;Password=fixture;Timeout=1"
        });
        builder.Services.AddCatalogServiceModule(builder.Configuration);
        await using var app = builder.Build();
        app.MapCatalogServiceEndpoints();
        app.MapHealthChecks("/health/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
        app.MapHealthChecks("/health/live", new HealthCheckOptions { Predicate = _ => false });
        await app.StartAsync();
        using var client = app.GetTestClient();
        Assert.Equal(HttpStatusCode.ServiceUnavailable, (await client.GetAsync("/health/ready")).StatusCode);
        Assert.Equal(HttpStatusCode.OK, (await client.GetAsync("/health/live")).StatusCode);
        Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync("/catalogservice")).StatusCode);
    }

    [Fact]
    public async Task Missing_module_database_configuration_refuses_host_startup()
    {
        var builder = CreateBuilder();
        builder.Services.AddCatalogServiceModule(builder.Configuration);
        await using var app = builder.Build();
        await Assert.ThrowsAsync<OptionsValidationException>(() => app.StartAsync());
    }

    private static WebApplicationBuilder CreateBuilder()
    {
        var builder = WebApplication.CreateBuilder(new WebApplicationOptions { EnvironmentName = Environments.Development });
        builder.Configuration.Sources.Clear();
        builder.WebHost.UseTestServer();
        return builder;
    }
}
