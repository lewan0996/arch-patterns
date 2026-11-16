using Acme.Commerce.CatalogModule.Application.Reservations;
using Acme.Commerce.CatalogModule.Infrastructure.Reservations;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Microsoft.Extensions.DependencyInjection;

namespace Acme.Commerce.CatalogModule.API;

// Catalog-owned business fixture. Contract read responses remain independent of HTTP DTOs.
public sealed record ReservationDto(Guid Id, string Reference, int Seats);

public static class Reservations
{
    public static void Register(IServiceCollection services)
    {
        services.AddScoped<IReservations, ReservationsService>();
        services.AddScoped<IReservationStore, ReservationStore>();
        services.AddScoped<IReservationQueries, ReservationQueries>();
    }

    public static void Map(IEndpointRouteBuilder endpoints) =>
        endpoints.MapGet("/CatalogModule/reservations/{reference}",
            async (string reference, IReservations reservations, CancellationToken cancellationToken) =>
            {
                var details = await reservations.FindAsync(reference, cancellationToken);
                return details is null ? Results.NotFound() : Results.Ok(
                    new ReservationDto(details.Id, details.Reference, details.Seats));
            });
}
