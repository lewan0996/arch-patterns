using Acme.Orders.Application.Reservations;
using Acme.Orders.Infrastructure.Reservations;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Npgsql;

namespace Acme.Orders.IntegrationTests.Reservations;

// This catalog-owned behavior is never included in production scaffolds.
public sealed class RichDirectServiceUseCaseTests
{
    [Fact]
    public async Task Public_service_persists_aggregate_changes_and_returns_a_separate_read_shape()
    {
        await using var factory = CreateHost();
        using var client = factory.CreateClient();
        const string reference = "rich-' OR 1=1 --";
        Guid id;
        await using (var scope = factory.Services.CreateAsyncScope())
            id = await scope.ServiceProvider.GetRequiredService<IReservations>()
                .ReserveAsync(reference, 2, CancellationToken.None);
        // A fresh repository must materialize an aggregate and invoke its behavior.
        await using (var scope = factory.Services.CreateAsyncScope())
            await scope.ServiceProvider.GetRequiredService<IReservations>()
                .ChangeSeatsAsync(id, 4, CancellationToken.None);
        // The read contract returns a Contract shape, with no tracked aggregate reuse.
        await using (var scope = factory.Services.CreateAsyncScope())
        {
            var service = scope.ServiceProvider.GetRequiredService<IReservations>();
            var result = await service.FindAsync(reference, CancellationToken.None);
            Assert.NotNull(result);
            Assert.Equal(id, result.Id);
            Assert.Equal(4, result.Seats);
            Assert.Null(await service.FindAsync("' OR 1=1 --", CancellationToken.None));
        }
        Assert.Equal(4, await CommittedSeats(reference));
    }

    [Fact]
    public async Task Rejected_domain_change_leaves_committed_state_unchanged()
    {
        await using var factory = CreateHost();
        using var client = factory.CreateClient();
        const string reference = "rejected-rich-change";
        Guid id;
        await using (var scope = factory.Services.CreateAsyncScope())
            id = await scope.ServiceProvider.GetRequiredService<IReservations>()
                .ReserveAsync(reference, 2, CancellationToken.None);
        await using (var scope = factory.Services.CreateAsyncScope())
            await Assert.ThrowsAsync<ArgumentOutOfRangeException>(() =>
                scope.ServiceProvider.GetRequiredService<IReservations>()
                    .ChangeSeatsAsync(id, 9, CancellationToken.None));
        await using (var scope = factory.Services.CreateAsyncScope())
        {
            var result = await scope.ServiceProvider.GetRequiredService<IReservations>()
                .FindAsync(reference, CancellationToken.None);
            Assert.NotNull(result);
            Assert.Equal(2, result.Seats);
        }
        Assert.Equal(2, await CommittedSeats(reference));
    }

    private static WebApplicationFactory<Program> CreateHost() =>
        new WebApplicationFactory<Program>().WithWebHostBuilder(host =>
        {
            host.ConfigureAppConfiguration((_, configuration) => configuration.AddInMemoryCollection(
                new Dictionary<string, string?>
                {
                    ["Service:Deployment"] = "rich-direct-service-fixture",
                    ["Database:ConnectionString"] = Environment.GetEnvironmentVariable("Database__ConnectionString")
                }));
            host.ConfigureServices(services =>
            {
                services.AddScoped<IReservations, ReservationsService>();
                services.AddScoped<IReservationRepository, ReservationRepository>();
                services.AddScoped<IReservationQueries, ReservationQueries>();
            });
        });

    private static async Task<int?> CommittedSeats(string reference)
    {
        await using var connection = new NpgsqlConnection(Environment.GetEnvironmentVariable("Database__ConnectionString"));
        await connection.OpenAsync();
        await using var command = new NpgsqlCommand("""
            SELECT "Seats" FROM "Orders"."Reservations" WHERE "Reference" = $1
            """, connection);
        command.Parameters.AddWithValue(reference);
        return await command.ExecuteScalarAsync() is int seats ? seats : null;
    }
}
