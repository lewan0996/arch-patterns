using System.Net;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Options;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using Microsoft.Extensions.Hosting;

namespace CatalogNamespace.CatalogService.IntegrationTests;

public sealed class HostTests
{
    [Fact]
    public async Task Unavailable_database_withdraws_readiness_but_keeps_process_live()
    {
        await using var factory = CreateHost("integration");
        using var client = factory.CreateClient();
        Assert.Equal(HttpStatusCode.OK, (await client.GetAsync("/health/live")).StatusCode);
        Assert.Equal(HttpStatusCode.ServiceUnavailable, (await client.GetAsync("/health/ready")).StatusCode);
        Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync("/orders")).StatusCode);
    }

    [Fact]
    public void Missing_required_configuration_refuses_startup()
    {
        using var factory = CreateHost("");
        Assert.Throws<OptionsValidationException>(() => factory.CreateClient());
    }

    [Theory]
    [InlineData("")]
    [InlineData("Host=localhost;Database=Orders;Username=Orders")]
    [InlineData("Host=localhost;Database=Orders;Username=Orders;Password=secret-canary;UnknownKey=value")]
    public void Invalid_database_credentials_refuse_startup_without_exposing_values(string connectionString)
    {
        using var factory = CreateHost("integration").WithWebHostBuilder(host =>
            host.ConfigureAppConfiguration((_, configuration) => configuration.AddInMemoryCollection(
                new Dictionary<string, string?> { ["Database:ConnectionString"] = connectionString })));
        var failure = Assert.Throws<OptionsValidationException>(() => factory.CreateClient());
        Assert.DoesNotContain("secret-canary", failure.ToString());
    }

    [Theory]
    [InlineData("0")]
    [InlineData("301")]
    public void Invalid_request_budget_refuses_startup(string seconds)
    {
        using var factory = CreateHost("integration").WithWebHostBuilder(host =>
            host.ConfigureAppConfiguration((_, configuration) => configuration.AddInMemoryCollection(
                new Dictionary<string, string?> { ["Service:RequestTimeoutSeconds"] = seconds })));
        Assert.Throws<OptionsValidationException>(() => factory.CreateClient());
    }

    [Fact]
    public async Task Stopping_host_withdraws_readiness()
    {
        await using var factory = CreateHost("integration");
        using var client = factory.CreateClient();
        var lifetime = factory.Services.GetRequiredService<IHostApplicationLifetime>();
        var health = factory.Services.GetRequiredService<HealthCheckService>();
        HealthStatus? status = null;
        using var registration = lifetime.ApplicationStopping.Register(() =>
            status = health.CheckHealthAsync(check => check.Name == "lifecycle")
                .GetAwaiter().GetResult().Status);
        lifetime.StopApplication();
        Assert.Equal(HealthStatus.Unhealthy, status);
    }

    private static WebApplicationFactory<Program> CreateHost(string deployment) =>
        new WebApplicationFactory<Program>().WithWebHostBuilder(host =>
            host.ConfigureAppConfiguration((_, configuration) => configuration.AddInMemoryCollection(
                new Dictionary<string, string?>
                {
                    ["Service:Deployment"] = deployment,
                    ["Database:ConnectionString"] = "Host=127.0.0.1;Port=1;Database=unavailable;Username=fixture;Password=fixture;Timeout=1"
                })));
}
