using Acme.Orders.Contract.Reservations;
using Acme.Orders.Domain.Reservations;

namespace Acme.Orders.Application.Reservations;

public interface IReservations
{
    Task<Guid> ReserveAsync(string reference, int seats, CancellationToken cancellationToken);
    Task<ReservationDetails?> FindAsync(string reference, CancellationToken cancellationToken);
}

public interface IReservationStore
{
    Task SaveAsync(Reservation reservation, CancellationToken cancellationToken);
}

public interface IReservationQueries
{
    Task<ReservationDetails?> FindAsync(string reference, CancellationToken cancellationToken);
}

public sealed class ReservationsService(IReservationStore store, IReservationQueries queries) : IReservations
{
    public async Task<Guid> ReserveAsync(string reference, int seats, CancellationToken cancellationToken)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(reference);
        ArgumentOutOfRangeException.ThrowIfLessThan(seats, 1);
        var reservation = new Reservation { Id = Guid.NewGuid(), Reference = reference, Seats = seats };
        await store.SaveAsync(reservation, cancellationToken);
        return reservation.Id;
    }

    public Task<ReservationDetails?> FindAsync(string reference, CancellationToken cancellationToken) =>
        queries.FindAsync(reference, cancellationToken);
}
