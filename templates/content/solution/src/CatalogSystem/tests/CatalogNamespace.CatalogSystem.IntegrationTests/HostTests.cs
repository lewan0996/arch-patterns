using System.Net;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Options;

namespace CatalogNamespace.CatalogSystem.IntegrationTests;

public sealed class HostTests
{
    [Fact]
    public async Task Public_host_exposes_process_probes_without_inventing_business_endpoints()
    {
        await using var factory = CreateHost("integration");
        using var client = factory.CreateClient();
        Assert.Equal(HttpStatusCode.OK, (await client.GetAsync("/health/live")).StatusCode);
        Assert.Equal(HttpStatusCode.OK, (await client.GetAsync("/health/ready")).StatusCode);
        Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync("/orders")).StatusCode);
    }

    [Fact]
    public void Missing_process_configuration_refuses_startup()
    {
        using var factory = CreateHost("");
        Assert.Throws<OptionsValidationException>(() => factory.CreateClient());
    }

    private static WebApplicationFactory<Program> CreateHost(string deployment) =>
        new WebApplicationFactory<Program>().WithWebHostBuilder(host =>
            host.ConfigureAppConfiguration((_, configuration) => configuration.AddInMemoryCollection(
                new Dictionary<string, string?> { ["Service:Deployment"] = deployment })));
}
