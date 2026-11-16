using Acme.Orders.Contract.Reservations;
using Acme.Orders.Domain.Reservations;

namespace Acme.Orders.Application.Reservations;

public interface IReservations
{
    Task<Guid> ReserveAsync(string reference, int seats, CancellationToken cancellationToken);
    Task ChangeSeatsAsync(Guid id, int seats, CancellationToken cancellationToken);
    Task<ReservationDetails?> FindAsync(string reference, CancellationToken cancellationToken);
}

// Command-side access loads only this module's aggregate root, never query shapes.
public interface IReservationRepository
{
    void Add(Reservation reservation);
    Task<Reservation?> LoadAsync(Guid id, CancellationToken cancellationToken);
    Task SaveChangesAsync(CancellationToken cancellationToken);
}

public interface IReservationQueries
{
    Task<ReservationDetails?> FindAsync(string reference, CancellationToken cancellationToken);
}

public sealed class ReservationsService(IReservationRepository repository, IReservationQueries queries) : IReservations
{
    public async Task<Guid> ReserveAsync(string reference, int seats, CancellationToken cancellationToken)
    {
        var reservation = Reservation.Create(reference, seats);
        repository.Add(reservation);
        await repository.SaveChangesAsync(cancellationToken);
        return reservation.Id;
    }

    public async Task ChangeSeatsAsync(Guid id, int seats, CancellationToken cancellationToken)
    {
        var reservation = await repository.LoadAsync(id, cancellationToken)
            ?? throw new KeyNotFoundException("Reservation not found.");
        reservation.ChangeSeats(seats);
        await repository.SaveChangesAsync(cancellationToken);
    }

    public Task<ReservationDetails?> FindAsync(string reference, CancellationToken cancellationToken) =>
        queries.FindAsync(reference, cancellationToken);
}
