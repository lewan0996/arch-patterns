using System.Net;
using Acme.Orders.Application.Reservations;
using Acme.Orders.Infrastructure.Reservations;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Npgsql;

namespace Acme.Orders.IntegrationTests;

// Catalog-only example: nothing in this tree is included in the template package.
public sealed class PostgreSqlUseCaseTests
{
    [Fact]
    public async Task Public_direct_service_commits_and_queries_separate_read_shapes()
    {
        await using var factory = CreateHost();
        using var client = factory.CreateClient();
        Assert.Equal(HttpStatusCode.OK, (await client.GetAsync("/health/ready")).StatusCode);
        var reference = "catalog-' OR 1=1 --";
        Guid id;
        await using (var scope = factory.Services.CreateAsyncScope())
            id = await scope.ServiceProvider.GetRequiredService<IReservations>()
                .ReserveAsync(reference, 2, CancellationToken.None);
        // A new scope/context must see committed data; no shared EF tracked entity.
        await using (var scope = factory.Services.CreateAsyncScope())
        {
            var service = scope.ServiceProvider.GetRequiredService<IReservations>();
            var result = await service.FindAsync(reference, CancellationToken.None);
            Assert.NotNull(result);
            Assert.Equal(id, result.Id);
            Assert.Equal(2, result.Seats);
            Assert.Null(await service.FindAsync("' OR 1=1 --", CancellationToken.None));
        }
        Assert.Equal(1L, await CommittedCount(reference));
    }

    [Fact]
    public async Task Rejected_request_leaves_no_committed_state()
    {
        await using var factory = CreateHost();
        using var client = factory.CreateClient();
        var reference = "rejected";
        await using var scope = factory.Services.CreateAsyncScope();
        var service = scope.ServiceProvider.GetRequiredService<IReservations>();
        await Assert.ThrowsAsync<ArgumentOutOfRangeException>(() =>
            service.ReserveAsync(reference, 0, CancellationToken.None));
        Assert.Null(await service.FindAsync(reference, CancellationToken.None));
        Assert.Equal(0L, await CommittedCount(reference));
    }

    [Fact]
    public async Task Canceled_request_leaves_no_committed_state()
    {
        await using var factory = CreateHost();
        using var client = factory.CreateClient();
        await using var scope = factory.Services.CreateAsyncScope();
        var service = scope.ServiceProvider.GetRequiredService<IReservations>();
        using var cancellation = new CancellationTokenSource();
        cancellation.Cancel();
        await Assert.ThrowsAnyAsync<OperationCanceledException>(() =>
            service.ReserveAsync("canceled", 2, cancellation.Token));
        Assert.Equal(0L, await CommittedCount("canceled"));
    }

    private static WebApplicationFactory<Program> CreateHost() =>
        new WebApplicationFactory<Program>().WithWebHostBuilder(host =>
        {
            host.ConfigureAppConfiguration((_, configuration) => configuration.AddInMemoryCollection(
                new Dictionary<string, string?>
                {
                    ["Service:Deployment"] = "postgresql-fixture",
                    ["Database:ConnectionString"] = Environment.GetEnvironmentVariable("Database__ConnectionString")
                }));
            host.ConfigureServices(services =>
            {
                services.AddScoped<IReservations, ReservationsService>();
                services.AddScoped<IReservationStore, ReservationStore>();
                services.AddScoped<IReservationQueries, ReservationQueries>();
            });
        });

    private static async Task<long> CommittedCount(string reference)
    {
        await using var connection = new NpgsqlConnection(Environment.GetEnvironmentVariable("Database__ConnectionString"));
        await connection.OpenAsync();
        await using var command = new NpgsqlCommand("""
            SELECT count(*) FROM "Orders"."Reservations" WHERE "Reference" = $1
            """, connection);
        command.Parameters.AddWithValue(reference);
        return (long)(await command.ExecuteScalarAsync())!;
    }
}
