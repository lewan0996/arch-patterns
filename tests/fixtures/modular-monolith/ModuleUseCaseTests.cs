using System.Net;
using System.Net.Http.Json;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using OrdersReservations = Acme.Commerce.Orders.Application.Reservations.IReservations;
using BillingReservations = Acme.Commerce.Billing.Application.Reservations.IReservations;

namespace Acme.Commerce.IntegrationTests;

public sealed class ModuleUseCaseTests
{
    [Fact]
    public async Task Integrated_modules_persist_independently_and_map_contract_queries_to_transport_DTOs()
    {
        await using var host = new WebApplicationFactory<Program>().WithWebHostBuilder(builder =>
            builder.ConfigureAppConfiguration((_, configuration) => configuration.AddInMemoryCollection(
                new Dictionary<string, string?> { ["Service:Deployment"] = "integration" })));
        using var client = host.CreateClient();
        Guid ordersId;
        Guid billingId;
        using (var scope = host.Services.CreateScope())
        {
            var orders = scope.ServiceProvider.GetRequiredService<OrdersReservations>();
            var billing = scope.ServiceProvider.GetRequiredService<BillingReservations>();
            ordersId = await orders.ReserveAsync("same-reference", 2, CancellationToken.None);
            billingId = await billing.ReserveAsync("same-reference", 5, CancellationToken.None);
            await Assert.ThrowsAsync<ArgumentOutOfRangeException>(() => orders.ReserveAsync("rejected", 0, CancellationToken.None));
        }
        // A fresh scope/context observes committed state through the public query interfaces.
        using (var scope = host.Services.CreateScope())
        {
            var orders = scope.ServiceProvider.GetRequiredService<OrdersReservations>();
            var billing = scope.ServiceProvider.GetRequiredService<BillingReservations>();
            Assert.Equal(2, (await orders.FindAsync("same-reference", CancellationToken.None))!.Seats);
            Assert.Equal(5, (await billing.FindAsync("same-reference", CancellationToken.None))!.Seats);
            Assert.Null(await orders.FindAsync("rejected", CancellationToken.None));
        }
        var ordersDto = await client.GetFromJsonAsync<Acme.Commerce.Orders.API.ReservationDto>("/Orders/reservations/same-reference");
        var billingDto = await client.GetFromJsonAsync<Acme.Commerce.Billing.API.ReservationDto>("/Billing/reservations/same-reference");
        Assert.Equal(new Acme.Commerce.Orders.API.ReservationDto(ordersId, "same-reference", 2), ordersDto);
        Assert.Equal(new Acme.Commerce.Billing.API.ReservationDto(billingId, "same-reference", 5), billingDto);
        Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync("/Orders/reservations/missing")).StatusCode);
        Assert.Equal(HttpStatusCode.OK, (await client.GetAsync("/health/ready")).StatusCode);
    }
}
